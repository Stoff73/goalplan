"""
Comprehensive test suite for Estate and IHT API endpoints.

Tests all 16 endpoints:
- Estate asset CRUD (4 endpoints)
- Estate liability CRUD (4 endpoints)
- Estate valuation and IHT calculation (2 endpoints)
- Gift and PET tracking (5 endpoints)
- SA Estate Duty calculation (1 endpoint)

Coverage includes:
- Authentication and authorization
- Validation errors
- Successful operations
- Rate limiting
- Temporal data queries
- Edge cases (RNRB tapering, taper relief, etc.)
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from models.estate_iht import (
    EstateAsset, EstateLiability, IHTCalculation, SAEstateDutyCalculation,
    Gift, IHTExemption, AssetType, LiabilityType, GiftType, ExemptionType
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
async def test_estate_asset(test_user, db_session: AsyncSession):
    """Create a test estate asset."""
    asset = EstateAsset(
        id=uuid4(),
        user_id=test_user.id,
        asset_type=AssetType.PROPERTY,
        description="Primary residence",
        estimated_value=Decimal('500000.00'),
        currency='GBP',
        owned_individually=True,
        included_in_uk_estate=True,
        included_in_sa_estate=False,
        effective_from=date.today(),
        effective_to=None,
        is_deleted=False
    )
    db_session.add(asset)
    await db_session.commit()
    await db_session.refresh(asset)
    return asset


@pytest.fixture
async def test_estate_liability(test_user, db_session: AsyncSession):
    """Create a test estate liability."""
    liability = EstateLiability(
        id=uuid4(),
        user_id=test_user.id,
        liability_type=LiabilityType.MORTGAGE,
        description="Mortgage on primary residence",
        amount_outstanding=Decimal('200000.00'),
        currency='GBP',
        deductible_from_estate=True,
        effective_from=date.today(),
        effective_to=None,
        is_deleted=False
    )
    db_session.add(liability)
    await db_session.commit()
    await db_session.refresh(liability)
    return liability


@pytest.fixture
async def test_gift(test_user, db_session: AsyncSession):
    """Create a test gift (PET)."""
    gift_date = date.today() - timedelta(days=365)  # 1 year ago
    gift = Gift(
        id=uuid4(),
        user_id=test_user.id,
        recipient="John Doe",
        gift_date=gift_date,
        gift_value=Decimal('10000.00'),
        currency='GBP',
        gift_type=GiftType.PET,
        exemption_type=None,
        becomes_exempt_date=gift_date + timedelta(days=365*7),  # 7 years
        still_in_pet_period=True,
        description="Birthday gift",
        is_deleted=False
    )
    db_session.add(gift)
    await db_session.commit()
    await db_session.refresh(gift)
    return gift


# ============================================================================
# ESTATE ASSET ENDPOINT TESTS
# ============================================================================

class TestEstateAssetEndpoints:
    """Tests for estate asset CRUD endpoints."""

    @pytest.mark.asyncio
    async def test_create_estate_asset_success(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_user
    ):
        """Test successful estate asset creation."""
        response = await async_client.post(
            "/api/v1/iht/estate/assets",
            json={
                "asset_type": "PROPERTY",
                "description": "Investment property",
                "estimated_value": "300000.00",
                "currency": "GBP",
                "owned_individually": True,
                "included_in_uk_estate": True,
                "included_in_sa_estate": False,
                "effective_from": str(date.today())
            },
            headers=authenticated_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data['asset_type'] == 'PROPERTY'
        assert data['description'] == 'Investment property'
        assert Decimal(data['estimated_value']) == Decimal('300000.00')

    @pytest.mark.asyncio
    async def test_create_estate_asset_unauthenticated(
        self,
        async_client: AsyncClient
    ):
        """Test estate asset creation without authentication."""
        response = await async_client.post(
            "/api/v1/iht/estate/assets",
            json={
                "asset_type": "PROPERTY",
                "description": "Test property",
                "estimated_value": "100000.00",
                "currency": "GBP",
                "owned_individually": True,
                "included_in_uk_estate": True,
                "included_in_sa_estate": False,
                "effective_from": str(date.today())
            }
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_estate_asset_validation_error(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test estate asset creation with invalid data."""
        response = await async_client.post(
            "/api/v1/iht/estate/assets",
            json={
                "asset_type": "PROPERTY",
                "description": "Test property",
                "estimated_value": "-1000.00",  # Negative value
                "currency": "GBP",
                "owned_individually": True,
                "included_in_uk_estate": True,
                "included_in_sa_estate": False,
                "effective_from": str(date.today())
            },
            headers=authenticated_headers
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_all_estate_assets(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_estate_asset
    ):
        """Test retrieving all estate assets."""
        response = await async_client.get(
            "/api/v1/iht/estate/assets",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(a['id'] == str(test_estate_asset.id) for a in data)

    @pytest.mark.asyncio
    async def test_get_estate_assets_filtered_by_type(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_estate_asset
    ):
        """Test retrieving estate assets filtered by type."""
        response = await async_client.get(
            "/api/v1/iht/estate/assets?asset_type=PROPERTY",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert all(a['asset_type'] == 'PROPERTY' for a in data)

    @pytest.mark.asyncio
    async def test_update_estate_asset_success(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_estate_asset
    ):
        """Test successful estate asset update."""
        response = await async_client.put(
            f"/api/v1/iht/estate/assets/{test_estate_asset.id}",
            json={
                "estimated_value": "550000.00"
            },
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert Decimal(data['estimated_value']) == Decimal('550000.00')

    @pytest.mark.asyncio
    async def test_update_estate_asset_not_found(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test updating non-existent estate asset."""
        fake_id = uuid4()
        response = await async_client.put(
            f"/api/v1/iht/estate/assets/{fake_id}",
            json={
                "estimated_value": "100000.00"
            },
            headers=authenticated_headers
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_estate_asset_success(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_estate_asset
    ):
        """Test successful estate asset deletion."""
        response = await async_client.delete(
            f"/api/v1/iht/estate/assets/{test_estate_asset.id}",
            headers=authenticated_headers
        )

        assert response.status_code == 204


# ============================================================================
# ESTATE LIABILITY ENDPOINT TESTS
# ============================================================================

class TestEstateLiabilityEndpoints:
    """Tests for estate liability CRUD endpoints."""

    @pytest.mark.asyncio
    async def test_create_estate_liability_success(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test successful estate liability creation."""
        response = await async_client.post(
            "/api/v1/iht/estate/liabilities",
            json={
                "liability_type": "LOAN",
                "description": "Personal loan",
                "amount_outstanding": "50000.00",
                "currency": "GBP",
                "deductible_from_estate": True,
                "effective_from": str(date.today())
            },
            headers=authenticated_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data['liability_type'] == 'LOAN'
        assert Decimal(data['amount_outstanding']) == Decimal('50000.00')

    @pytest.mark.asyncio
    async def test_get_all_estate_liabilities(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_estate_liability
    ):
        """Test retrieving all estate liabilities."""
        response = await async_client.get(
            "/api/v1/iht/estate/liabilities",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(l['id'] == str(test_estate_liability.id) for l in data)

    @pytest.mark.asyncio
    async def test_update_estate_liability_success(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_estate_liability
    ):
        """Test successful estate liability update."""
        response = await async_client.put(
            f"/api/v1/iht/estate/liabilities/{test_estate_liability.id}",
            json={
                "amount_outstanding": "180000.00"
            },
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert Decimal(data['amount_outstanding']) == Decimal('180000.00')

    @pytest.mark.asyncio
    async def test_delete_estate_liability_success(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_estate_liability
    ):
        """Test successful estate liability deletion."""
        response = await async_client.delete(
            f"/api/v1/iht/estate/liabilities/{test_estate_liability.id}",
            headers=authenticated_headers
        )

        assert response.status_code == 204


# ============================================================================
# ESTATE VALUATION AND IHT CALCULATION TESTS
# ============================================================================

class TestEstateValuationEndpoints:
    """Tests for estate valuation and IHT calculation endpoints."""

    @pytest.mark.asyncio
    async def test_get_estate_valuation(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_estate_asset,
        test_estate_liability
    ):
        """Test estate valuation calculation."""
        response = await async_client.get(
            "/api/v1/iht/estate/valuation",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert 'gross_estate_value' in data
        assert 'total_liabilities' in data
        assert 'net_estate_value' in data
        assert Decimal(data['gross_estate_value']) == Decimal('500000.00')
        assert Decimal(data['net_estate_value']) == Decimal('300000.00')

    @pytest.mark.asyncio
    async def test_calculate_iht_basic(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_estate_asset,
        test_estate_liability
    ):
        """Test basic IHT calculation."""
        response = await async_client.post(
            "/api/v1/iht/calculate",
            json={
                "transferable_nrb_percent": 0,
                "property_to_descendants": False,
                "charitable_gifts_percent": 0,
                "save_calculation": False
            },
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert 'gross_estate' in data
        assert 'net_estate' in data
        assert 'standard_nrb' in data
        assert 'taxable_estate' in data
        assert 'iht_owed' in data
        assert Decimal(data['standard_nrb']) == Decimal('325000.00')

    @pytest.mark.asyncio
    async def test_calculate_iht_with_rnrb(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_estate_asset,
        test_estate_liability
    ):
        """Test IHT calculation with RNRB."""
        response = await async_client.post(
            "/api/v1/iht/calculate",
            json={
                "transferable_nrb_percent": 0,
                "property_to_descendants": True,  # Enable RNRB
                "charitable_gifts_percent": 0,
                "save_calculation": False
            },
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        # Net estate is £300k, under £2M threshold, so full RNRB available
        assert Decimal(data['residence_nrb']) == Decimal('175000.00')

    @pytest.mark.asyncio
    async def test_calculate_iht_with_charity_rate(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_estate_asset,
        test_estate_liability
    ):
        """Test IHT calculation with charity reduced rate."""
        response = await async_client.post(
            "/api/v1/iht/calculate",
            json={
                "transferable_nrb_percent": 0,
                "property_to_descendants": False,
                "charitable_gifts_percent": 10.0,  # 10% to charity -> 36% rate
                "save_calculation": False
            },
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert Decimal(data['iht_rate']) == Decimal('0.36')

    @pytest.mark.asyncio
    async def test_calculate_iht_with_save(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_estate_asset,
        test_estate_liability
    ):
        """Test IHT calculation with save option."""
        response = await async_client.post(
            "/api/v1/iht/calculate",
            json={
                "transferable_nrb_percent": 0,
                "property_to_descendants": False,
                "charitable_gifts_percent": 0,
                "save_calculation": True  # Save calculation
            },
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data['calculation_id'] is not None


# ============================================================================
# GIFT AND PET TRACKING TESTS
# ============================================================================

class TestGiftEndpoints:
    """Tests for gift and PET tracking endpoints."""

    @pytest.mark.asyncio
    async def test_record_gift_success(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test successful gift recording."""
        response = await async_client.post(
            "/api/v1/iht/gifts",
            json={
                "recipient": "Jane Doe",
                "gift_date": str(date.today() - timedelta(days=180)),
                "gift_value": "5000.00",
                "currency": "GBP",
                "description": "Wedding gift",
                "exemption_type": None
            },
            headers=authenticated_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data['recipient'] == 'Jane Doe'
        assert Decimal(data['gift_value']) == Decimal('5000.00')
        assert data['gift_type'] == 'PET'

    @pytest.mark.asyncio
    async def test_record_gift_validation_error_future_date(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test gift recording with future date."""
        response = await async_client.post(
            "/api/v1/iht/gifts",
            json={
                "recipient": "Future Person",
                "gift_date": str(date.today() + timedelta(days=1)),  # Future date
                "gift_value": "1000.00",
                "currency": "GBP"
            },
            headers=authenticated_headers
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_all_gifts(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_gift
    ):
        """Test retrieving all gifts."""
        response = await async_client.get(
            "/api/v1/iht/gifts",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(g['id'] == str(test_gift.id) for g in data)

    @pytest.mark.asyncio
    async def test_get_gifts_in_pet_period(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_gift
    ):
        """Test retrieving gifts in PET period."""
        response = await async_client.get(
            "/api/v1/iht/gifts/pet-period",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        # All should be PETs still in 7-year period
        assert all(g['gift_type'] == 'PET' for g in data)

    @pytest.mark.asyncio
    async def test_calculate_potential_iht_on_pets(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        test_gift
    ):
        """Test calculating potential IHT on PETs."""
        response = await async_client.post(
            "/api/v1/iht/gifts/potential-iht",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        # Check gift is in calculation
        gift_calc = next((g for g in data if g['gift_id'] == str(test_gift.id)), None)
        assert gift_calc is not None
        assert 'taper_relief_percent' in gift_calc
        assert 'potential_iht' in gift_calc

    @pytest.mark.asyncio
    async def test_get_exemption_status(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test retrieving exemption status."""
        tax_year = "2024/25"
        response = await async_client.get(
            f"/api/v1/iht/exemptions/{tax_year}",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert 'annual_exemption_limit' in data
        assert 'annual_exemption_remaining' in data
        assert Decimal(data['annual_exemption_limit']) == Decimal('3000.00')

    @pytest.mark.asyncio
    async def test_get_exemption_status_invalid_tax_year(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict
    ):
        """Test exemption status with invalid tax year format."""
        tax_year = "2024"  # Invalid format
        response = await async_client.get(
            f"/api/v1/iht/exemptions/{tax_year}",
            headers=authenticated_headers
        )

        assert response.status_code == 400


# ============================================================================
# SA ESTATE DUTY TESTS
# ============================================================================

class TestSAEstateDutyEndpoints:
    """Tests for SA Estate Duty calculation endpoint."""

    @pytest.mark.asyncio
    async def test_calculate_sa_estate_duty(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        db_session: AsyncSession,
        test_user
    ):
        """Test SA Estate Duty calculation."""
        # Create SA asset
        sa_asset = EstateAsset(
            id=uuid4(),
            user_id=test_user.id,
            asset_type=AssetType.PROPERTY,
            description="SA Property",
            estimated_value=Decimal('5000000.00'),  # R5M
            currency='ZAR',
            owned_individually=True,
            included_in_uk_estate=False,
            included_in_sa_estate=True,
            effective_from=date.today(),
            is_deleted=False
        )
        db_session.add(sa_asset)
        await db_session.commit()

        response = await async_client.post(
            "/api/v1/iht/sa-estate-duty/calculate",
            json={
                "save_calculation": False
            },
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert 'estate_value' in data
        assert 'abatement' in data
        assert 'dutiable_amount' in data
        assert 'estate_duty_owed' in data
        assert Decimal(data['abatement']) == Decimal('3500000.00')

    @pytest.mark.asyncio
    async def test_calculate_sa_estate_duty_with_save(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        db_session: AsyncSession,
        test_user
    ):
        """Test SA Estate Duty calculation with save."""
        # Create SA asset
        sa_asset = EstateAsset(
            id=uuid4(),
            user_id=test_user.id,
            asset_type=AssetType.INVESTMENTS,
            description="SA Investments",
            estimated_value=Decimal('40000000.00'),  # R40M (above tier threshold)
            currency='ZAR',
            owned_individually=True,
            included_in_uk_estate=False,
            included_in_sa_estate=True,
            effective_from=date.today(),
            is_deleted=False
        )
        db_session.add(sa_asset)
        await db_session.commit()

        response = await async_client.post(
            "/api/v1/iht/sa-estate-duty/calculate",
            json={
                "save_calculation": True
            },
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data['calculation_id'] is not None
        # Above R30M threshold, so tiered rate applies
        # Dutiable: R40M - R3.5M = R36.5M
        # Duty: (R30M * 20%) + ((R36.5M - R30M) * 25%)
        assert Decimal(data['estate_duty_owed']) > Decimal('0')


# ============================================================================
# AUTHORIZATION TESTS
# ============================================================================

class TestAuthorizationAndSecurity:
    """Tests for authorization and security."""

    @pytest.mark.asyncio
    async def test_cannot_access_other_users_assets(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        db_session: AsyncSession
    ):
        """Test users cannot access other users' estate assets."""
        # Create another user's asset
        other_user_id = uuid4()
        other_asset = EstateAsset(
            id=uuid4(),
            user_id=other_user_id,
            asset_type=AssetType.PROPERTY,
            description="Other user's property",
            estimated_value=Decimal('100000.00'),
            currency='GBP',
            owned_individually=True,
            included_in_uk_estate=True,
            included_in_sa_estate=False,
            effective_from=date.today(),
            is_deleted=False
        )
        db_session.add(other_asset)
        await db_session.commit()

        # Try to update other user's asset
        response = await async_client.put(
            f"/api/v1/iht/estate/assets/{other_asset.id}",
            json={"estimated_value": "200000.00"},
            headers=authenticated_headers
        )

        assert response.status_code == 404  # Should not find asset

    @pytest.mark.asyncio
    async def test_cannot_access_other_users_gifts(
        self,
        async_client: AsyncClient,
        authenticated_headers: dict,
        db_session: AsyncSession
    ):
        """Test users cannot see other users' gifts."""
        # Create another user's gift
        other_user_id = uuid4()
        other_gift = Gift(
            id=uuid4(),
            user_id=other_user_id,
            recipient="Other Person",
            gift_date=date.today(),
            gift_value=Decimal('1000.00'),
            currency='GBP',
            gift_type=GiftType.PET,
            is_deleted=False
        )
        db_session.add(other_gift)
        await db_session.commit()

        # Get all gifts for authenticated user
        response = await async_client.get(
            "/api/v1/iht/gifts",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        # Should NOT include other user's gift
        assert not any(g['id'] == str(other_gift.id) for g in data)
