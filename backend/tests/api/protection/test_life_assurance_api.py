"""
Tests for life assurance policy API endpoints.

Covers:
- CRUD operations (create, read, update, delete policies)
- Beneficiary management (add, update, delete)
- Authentication and authorization (401, 403)
- Validation and error handling (400, 404)
- Rate limiting on PUT endpoint
- Filtering and querying
"""

import pytest
from decimal import Decimal
from datetime import date, datetime
from uuid import uuid4

from models.life_assurance import (
    LifeAssurancePolicy,
    PolicyBeneficiary,
    PolicyTrustDetail,
    PolicyStatus,
    PolicyType,
    ProviderCountry,
    PremiumFrequency,
    TrustType,
    BeneficiaryRelationship,
    Currency
)


@pytest.mark.asyncio
class TestCreatePolicy:
    """Tests for POST /api/v1/protection/life-assurance"""

    async def test_create_basic_policy(self, test_client, authenticated_headers):
        """Test creating a basic life assurance policy."""
        payload = {
            "policy_number": "POL123456",
            "provider": "Legal & General",
            "provider_country": "UK",
            "policy_type": "TERM",
            "cover_amount": 500000.00,
            "currency": "GBP",
            "premium_amount": 45.50,
            "premium_frequency": "MONTHLY",
            "start_date": "2023-01-01",
            "end_date": "2043-01-01",
            "written_in_trust": False,
            "beneficiaries": [
                {
                    "name": "Jane Doe",
                    "date_of_birth": "1985-06-15",
                    "relationship": "SPOUSE",
                    "percentage": 100.00,
                    "address": "123 Main St, London, UK"
                }
            ],
            "critical_illness_rider": True,
            "waiver_of_premium": False,
            "notes": "Family protection policy"
        }

        response = await test_client.post(
            "/api/v1/protection/life-assurance",
            json=payload,
            headers=authenticated_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["provider"] == "Legal & General"
        assert data["policy_type"] == "TERM"
        assert Decimal(str(data["cover_amount"])) == Decimal("500000.00")
        assert data["currency"] == "GBP"
        assert Decimal(str(data["premium_amount"])) == Decimal("45.50")
        assert data["premium_frequency"] == "MONTHLY"
        assert Decimal(str(data["annual_premium"])) == Decimal("546.00")  # 45.50 * 12
        assert data["written_in_trust"] is False
        assert data["status"] == "ACTIVE"
        assert data["uk_iht_impact"] is True  # UK policy not in trust
        assert data["sa_estate_duty_impact"] is False
        assert len(data["beneficiaries"]) == 1
        assert data["beneficiaries"][0]["name"] == "Jane Doe"
        assert data["beneficiaries"][0]["relationship"] == "SPOUSE"
        assert Decimal(str(data["beneficiaries"][0]["percentage"])) == Decimal("100.00")
        assert "****" in data["policy_number"]  # Masked

    async def test_create_policy_with_trust(self, test_client, authenticated_headers):
        """Test creating a policy written in trust."""
        payload = {
            "policy_number": "POL789012",
            "provider": "Aviva",
            "provider_country": "UK",
            "policy_type": "WHOLE_OF_LIFE",
            "cover_amount": 250000.00,
            "currency": "GBP",
            "premium_amount": 120.00,
            "premium_frequency": "MONTHLY",
            "start_date": "2023-06-01",
            "written_in_trust": True,
            "trust_details": {
                "trust_type": "DISCRETIONARY",
                "trustees": ["John Smith", "Mary Johnson"],
                "trust_beneficiaries": "Spouse and children",
                "trust_created_date": "2023-06-01"
            },
            "beneficiaries": [
                {
                    "name": "Jane Doe",
                    "date_of_birth": "1985-06-15",
                    "relationship": "SPOUSE",
                    "percentage": 50.00,
                    "address": "123 Main St, London, UK"
                },
                {
                    "name": "John Doe Jr",
                    "date_of_birth": "2015-03-20",
                    "relationship": "CHILD",
                    "percentage": 50.00,
                    "address": "123 Main St, London, UK"
                }
            ],
            "critical_illness_rider": False,
            "waiver_of_premium": True
        }

        response = await test_client.post(
            "/api/v1/protection/life-assurance",
            json=payload,
            headers=authenticated_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["written_in_trust"] is True
        assert data["uk_iht_impact"] is False  # Written in trust, outside estate
        assert data["trust_details"] is not None
        assert data["trust_details"]["trust_type"] == "DISCRETIONARY"
        assert len(data["trust_details"]["trustees"]) == 2
        assert "John Smith" in data["trust_details"]["trustees"]
        assert len(data["beneficiaries"]) == 2

    async def test_create_policy_beneficiaries_not_100_percent(
        self, test_client, authenticated_headers
    ):
        """Test that beneficiary percentages must total 100%."""
        payload = {
            "policy_number": "POL456789",
            "provider": "Test Provider",
            "provider_country": "UK",
            "policy_type": "TERM",
            "cover_amount": 100000.00,
            "currency": "GBP",
            "premium_amount": 20.00,
            "premium_frequency": "MONTHLY",
            "start_date": "2023-01-01",
            "end_date": "2033-01-01",
            "written_in_trust": False,
            "beneficiaries": [
                {
                    "name": "Jane Doe",
                    "date_of_birth": "1985-06-15",
                    "relationship": "SPOUSE",
                    "percentage": 75.00,  # Only 75%, not 100%
                    "address": "123 Main St, London, UK"
                }
            ]
        }

        response = await test_client.post(
            "/api/v1/protection/life-assurance",
            json=payload,
            headers=authenticated_headers
        )

        assert response.status_code == 422  # Validation error
        assert "100" in response.json()["detail"][0]["msg"]

    async def test_create_policy_trust_without_details(
        self, test_client, authenticated_headers
    ):
        """Test that trust details are required when written_in_trust=True."""
        payload = {
            "policy_number": "POL111222",
            "provider": "Test Provider",
            "provider_country": "UK",
            "policy_type": "TERM",
            "cover_amount": 100000.00,
            "currency": "GBP",
            "premium_amount": 20.00,
            "premium_frequency": "MONTHLY",
            "start_date": "2023-01-01",
            "end_date": "2033-01-01",
            "written_in_trust": True,  # Trust flag set
            "trust_details": None,  # But no details provided
            "beneficiaries": [
                {
                    "name": "Jane Doe",
                    "date_of_birth": "1985-06-15",
                    "relationship": "SPOUSE",
                    "percentage": 100.00,
                    "address": "123 Main St, London, UK"
                }
            ]
        }

        response = await test_client.post(
            "/api/v1/protection/life-assurance",
            json=payload,
            headers=authenticated_headers
        )

        assert response.status_code == 422  # Validation error
        assert "trust details" in response.json()["detail"][0]["msg"].lower()

    async def test_create_policy_invalid_dates(self, test_client, authenticated_headers):
        """Test that end date must be after start date."""
        payload = {
            "policy_number": "POL333444",
            "provider": "Test Provider",
            "provider_country": "UK",
            "policy_type": "TERM",
            "cover_amount": 100000.00,
            "currency": "GBP",
            "premium_amount": 20.00,
            "premium_frequency": "MONTHLY",
            "start_date": "2023-01-01",
            "end_date": "2022-01-01",  # End before start
            "written_in_trust": False,
            "beneficiaries": [
                {
                    "name": "Jane Doe",
                    "date_of_birth": "1985-06-15",
                    "relationship": "SPOUSE",
                    "percentage": 100.00,
                    "address": "123 Main St, London, UK"
                }
            ]
        }

        response = await test_client.post(
            "/api/v1/protection/life-assurance",
            json=payload,
            headers=authenticated_headers
        )

        assert response.status_code == 422  # Validation error
        assert "after start date" in response.json()["detail"][0]["msg"].lower()

    async def test_create_policy_without_authentication(self, test_client):
        """Test creating policy without authentication fails."""
        payload = {
            "policy_number": "POL555666",
            "provider": "Test Provider",
            "provider_country": "UK",
            "policy_type": "TERM",
            "cover_amount": 100000.00,
            "currency": "GBP",
            "premium_amount": 20.00,
            "premium_frequency": "MONTHLY",
            "start_date": "2023-01-01",
            "beneficiaries": [
                {
                    "name": "Jane Doe",
                    "date_of_birth": "1985-06-15",
                    "relationship": "SPOUSE",
                    "percentage": 100.00,
                    "address": "123 Main St, London, UK"
                }
            ]
        }

        response = await test_client.post(
            "/api/v1/protection/life-assurance",
            json=payload
        )

        assert response.status_code == 401


@pytest.mark.asyncio
class TestListPolicies:
    """Tests for GET /api/v1/protection/life-assurance"""

    async def test_get_all_policies_empty(self, test_client, authenticated_headers):
        """Test getting policies when none exist."""
        response = await test_client.get(
            "/api/v1/protection/life-assurance",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        assert response.json() == []

    async def test_get_all_policies(self, test_client, authenticated_headers, db_session, test_user):
        """Test getting all policies for a user."""
        # Create test policies
        policy1 = LifeAssurancePolicy(
            user_id=test_user.id,
            provider="Legal & General",
            provider_country=ProviderCountry.UK,
            policy_type=PolicyType.TERM,
            cover_amount=Decimal("500000.00"),
            currency=Currency.GBP,
            premium_amount=Decimal("45.50"),
            premium_frequency=PremiumFrequency.MONTHLY,
            start_date=date(2023, 1, 1),
            end_date=date(2043, 1, 1),
            written_in_trust=False,
            status=PolicyStatus.ACTIVE,
            annual_premium=Decimal("546.00"),
            uk_iht_impact=True,
            sa_estate_duty_impact=False
        )
        policy1.set_policy_number("POL123456")
        db_session.add(policy1)

        policy2 = LifeAssurancePolicy(
            user_id=test_user.id,
            provider="Aviva",
            provider_country=ProviderCountry.UK,
            policy_type=PolicyType.WHOLE_OF_LIFE,
            cover_amount=Decimal("250000.00"),
            currency=Currency.GBP,
            premium_amount=Decimal("120.00"),
            premium_frequency=PremiumFrequency.MONTHLY,
            start_date=date(2023, 6, 1),
            written_in_trust=True,
            trust_type=TrustType.DISCRETIONARY,
            status=PolicyStatus.ACTIVE,
            annual_premium=Decimal("1440.00"),
            uk_iht_impact=False,
            sa_estate_duty_impact=False
        )
        policy2.set_policy_number("POL789012")
        db_session.add(policy2)

        await db_session.commit()

        response = await test_client.get(
            "/api/v1/protection/life-assurance",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["provider"] in ["Legal & General", "Aviva"]
        assert data[1]["provider"] in ["Legal & General", "Aviva"]

    async def test_get_policies_filter_by_status(
        self, test_client, authenticated_headers, db_session, test_user
    ):
        """Test filtering policies by status."""
        # Create active and lapsed policies
        active_policy = LifeAssurancePolicy(
            user_id=test_user.id,
            provider="Provider A",
            provider_country=ProviderCountry.UK,
            policy_type=PolicyType.TERM,
            cover_amount=Decimal("100000.00"),
            currency=Currency.GBP,
            premium_amount=Decimal("30.00"),
            premium_frequency=PremiumFrequency.MONTHLY,
            start_date=date(2023, 1, 1),
            status=PolicyStatus.ACTIVE,
            annual_premium=Decimal("360.00")
        )
        active_policy.set_policy_number("POL001")
        db_session.add(active_policy)

        lapsed_policy = LifeAssurancePolicy(
            user_id=test_user.id,
            provider="Provider B",
            provider_country=ProviderCountry.UK,
            policy_type=PolicyType.TERM,
            cover_amount=Decimal("100000.00"),
            currency=Currency.GBP,
            premium_amount=Decimal("30.00"),
            premium_frequency=PremiumFrequency.MONTHLY,
            start_date=date(2020, 1, 1),
            status=PolicyStatus.LAPSED,
            annual_premium=Decimal("360.00")
        )
        lapsed_policy.set_policy_number("POL002")
        db_session.add(lapsed_policy)

        await db_session.commit()

        # Get only active policies
        response = await test_client.get(
            "/api/v1/protection/life-assurance?status=ACTIVE",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "ACTIVE"
        assert data[0]["provider"] == "Provider A"

    async def test_get_policies_filter_by_provider(
        self, test_client, authenticated_headers, db_session, test_user
    ):
        """Test filtering policies by provider."""
        # Create policies with different providers
        policy1 = LifeAssurancePolicy(
            user_id=test_user.id,
            provider="Legal & General",
            provider_country=ProviderCountry.UK,
            policy_type=PolicyType.TERM,
            cover_amount=Decimal("100000.00"),
            currency=Currency.GBP,
            premium_amount=Decimal("30.00"),
            premium_frequency=PremiumFrequency.MONTHLY,
            start_date=date(2023, 1, 1),
            status=PolicyStatus.ACTIVE,
            annual_premium=Decimal("360.00")
        )
        policy1.set_policy_number("POL001")
        db_session.add(policy1)

        policy2 = LifeAssurancePolicy(
            user_id=test_user.id,
            provider="Aviva",
            provider_country=ProviderCountry.UK,
            policy_type=PolicyType.TERM,
            cover_amount=Decimal("100000.00"),
            currency=Currency.GBP,
            premium_amount=Decimal("30.00"),
            premium_frequency=PremiumFrequency.MONTHLY,
            start_date=date(2023, 1, 1),
            status=PolicyStatus.ACTIVE,
            annual_premium=Decimal("360.00")
        )
        policy2.set_policy_number("POL002")
        db_session.add(policy2)

        await db_session.commit()

        # Get only Aviva policies
        response = await test_client.get(
            "/api/v1/protection/life-assurance?provider=Aviva",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["provider"] == "Aviva"

    async def test_get_policies_without_authentication(self, test_client):
        """Test getting policies without authentication fails."""
        response = await test_client.get("/api/v1/protection/life-assurance")
        assert response.status_code == 401


@pytest.mark.asyncio
class TestGetPolicy:
    """Tests for GET /api/v1/protection/life-assurance/{id}"""

    async def test_get_policy_by_id(
        self, test_client, authenticated_headers, db_session, test_user
    ):
        """Test getting a single policy by ID."""
        # Create test policy with beneficiary
        policy = LifeAssurancePolicy(
            user_id=test_user.id,
            provider="Legal & General",
            provider_country=ProviderCountry.UK,
            policy_type=PolicyType.TERM,
            cover_amount=Decimal("500000.00"),
            currency=Currency.GBP,
            premium_amount=Decimal("45.50"),
            premium_frequency=PremiumFrequency.MONTHLY,
            start_date=date(2023, 1, 1),
            end_date=date(2043, 1, 1),
            written_in_trust=False,
            status=PolicyStatus.ACTIVE,
            annual_premium=Decimal("546.00"),
            uk_iht_impact=True,
            sa_estate_duty_impact=False
        )
        policy.set_policy_number("POL123456")
        db_session.add(policy)
        await db_session.flush()

        # Add beneficiary
        beneficiary = PolicyBeneficiary(
            policy_id=policy.id,
            beneficiary_relationship=BeneficiaryRelationship.SPOUSE,
            percentage=Decimal("100.00")
        )
        beneficiary.set_name("Jane Doe")
        beneficiary.set_date_of_birth(date(1985, 6, 15))
        beneficiary.set_address("123 Main St, London, UK")
        db_session.add(beneficiary)
        await db_session.commit()

        response = await test_client.get(
            f"/api/v1/protection/life-assurance/{policy.id}",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(policy.id)
        assert data["provider"] == "Legal & General"
        assert len(data["beneficiaries"]) == 1
        assert data["beneficiaries"][0]["name"] == "Jane Doe"

    async def test_get_policy_not_found(self, test_client, authenticated_headers):
        """Test getting a non-existent policy returns 404."""
        fake_id = uuid4()
        response = await test_client.get(
            f"/api/v1/protection/life-assurance/{fake_id}",
            headers=authenticated_headers
        )

        assert response.status_code == 404

    async def test_get_policy_wrong_user(
        self, test_client, authenticated_headers, db_session
    ):
        """Test getting another user's policy returns 403."""
        # Create policy for different user
        other_user_id = uuid4()
        policy = LifeAssurancePolicy(
            user_id=other_user_id,
            provider="Test Provider",
            provider_country=ProviderCountry.UK,
            policy_type=PolicyType.TERM,
            cover_amount=Decimal("100000.00"),
            currency=Currency.GBP,
            premium_amount=Decimal("30.00"),
            premium_frequency=PremiumFrequency.MONTHLY,
            start_date=date(2023, 1, 1),
            status=PolicyStatus.ACTIVE,
            annual_premium=Decimal("360.00")
        )
        policy.set_policy_number("POL999")
        db_session.add(policy)
        await db_session.commit()

        response = await test_client.get(
            f"/api/v1/protection/life-assurance/{policy.id}",
            headers=authenticated_headers
        )

        assert response.status_code == 403


@pytest.mark.asyncio
class TestUpdatePolicy:
    """Tests for PUT /api/v1/protection/life-assurance/{id}"""

    async def test_update_policy(
        self, test_client, authenticated_headers, db_session, test_user
    ):
        """Test updating a policy."""
        # Create test policy
        policy = LifeAssurancePolicy(
            user_id=test_user.id,
            provider="Legal & General",
            provider_country=ProviderCountry.UK,
            policy_type=PolicyType.TERM,
            cover_amount=Decimal("500000.00"),
            currency=Currency.GBP,
            premium_amount=Decimal("45.50"),
            premium_frequency=PremiumFrequency.MONTHLY,
            start_date=date(2023, 1, 1),
            end_date=date(2043, 1, 1),
            written_in_trust=False,
            status=PolicyStatus.ACTIVE,
            annual_premium=Decimal("546.00")
        )
        policy.set_policy_number("POL123456")
        db_session.add(policy)
        await db_session.commit()

        # Update policy
        update_payload = {
            "cover_amount": 600000.00,
            "premium_amount": 50.00,
            "notes": "Updated coverage amount"
        }

        response = await test_client.put(
            f"/api/v1/protection/life-assurance/{policy.id}",
            json=update_payload,
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert Decimal(str(data["cover_amount"])) == Decimal("600000.00")
        assert Decimal(str(data["premium_amount"])) == Decimal("50.00")
        assert Decimal(str(data["annual_premium"])) == Decimal("600.00")  # 50 * 12
        assert data["notes"] == "Updated coverage amount"

    async def test_update_policy_not_found(self, test_client, authenticated_headers):
        """Test updating non-existent policy returns 404."""
        fake_id = uuid4()
        update_payload = {"cover_amount": 100000.00}

        response = await test_client.put(
            f"/api/v1/protection/life-assurance/{fake_id}",
            json=update_payload,
            headers=authenticated_headers
        )

        assert response.status_code == 404

    async def test_update_policy_wrong_user(
        self, test_client, authenticated_headers, db_session
    ):
        """Test updating another user's policy returns 403."""
        # Create policy for different user
        other_user_id = uuid4()
        policy = LifeAssurancePolicy(
            user_id=other_user_id,
            provider="Test Provider",
            provider_country=ProviderCountry.UK,
            policy_type=PolicyType.TERM,
            cover_amount=Decimal("100000.00"),
            currency=Currency.GBP,
            premium_amount=Decimal("30.00"),
            premium_frequency=PremiumFrequency.MONTHLY,
            start_date=date(2023, 1, 1),
            status=PolicyStatus.ACTIVE,
            annual_premium=Decimal("360.00")
        )
        policy.set_policy_number("POL999")
        db_session.add(policy)
        await db_session.commit()

        update_payload = {"cover_amount": 200000.00}

        response = await test_client.put(
            f"/api/v1/protection/life-assurance/{policy.id}",
            json=update_payload,
            headers=authenticated_headers
        )

        assert response.status_code == 403


@pytest.mark.asyncio
class TestDeletePolicy:
    """Tests for DELETE /api/v1/protection/life-assurance/{id}"""

    async def test_delete_policy(
        self, test_client, authenticated_headers, db_session, test_user
    ):
        """Test soft deleting a policy."""
        # Create test policy
        policy = LifeAssurancePolicy(
            user_id=test_user.id,
            provider="Legal & General",
            provider_country=ProviderCountry.UK,
            policy_type=PolicyType.TERM,
            cover_amount=Decimal("500000.00"),
            currency=Currency.GBP,
            premium_amount=Decimal("45.50"),
            premium_frequency=PremiumFrequency.MONTHLY,
            start_date=date(2023, 1, 1),
            end_date=date(2043, 1, 1),
            status=PolicyStatus.ACTIVE,
            annual_premium=Decimal("546.00")
        )
        policy.set_policy_number("POL123456")
        db_session.add(policy)
        await db_session.commit()

        response = await test_client.delete(
            f"/api/v1/protection/life-assurance/{policy.id}",
            headers=authenticated_headers
        )

        assert response.status_code == 204

        # Verify policy is soft deleted
        await db_session.refresh(policy)
        assert policy.is_deleted is True

    async def test_delete_policy_not_found(self, test_client, authenticated_headers):
        """Test deleting non-existent policy returns 404."""
        fake_id = uuid4()

        response = await test_client.delete(
            f"/api/v1/protection/life-assurance/{fake_id}",
            headers=authenticated_headers
        )

        assert response.status_code == 404

    async def test_delete_policy_wrong_user(
        self, test_client, authenticated_headers, db_session
    ):
        """Test deleting another user's policy returns 403."""
        # Create policy for different user
        other_user_id = uuid4()
        policy = LifeAssurancePolicy(
            user_id=other_user_id,
            provider="Test Provider",
            provider_country=ProviderCountry.UK,
            policy_type=PolicyType.TERM,
            cover_amount=Decimal("100000.00"),
            currency=Currency.GBP,
            premium_amount=Decimal("30.00"),
            premium_frequency=PremiumFrequency.MONTHLY,
            start_date=date(2023, 1, 1),
            status=PolicyStatus.ACTIVE,
            annual_premium=Decimal("360.00")
        )
        policy.set_policy_number("POL999")
        db_session.add(policy)
        await db_session.commit()

        response = await test_client.delete(
            f"/api/v1/protection/life-assurance/{policy.id}",
            headers=authenticated_headers
        )

        assert response.status_code == 403


@pytest.mark.asyncio
class TestBeneficiaryManagement:
    """Tests for beneficiary endpoints"""

    async def test_add_beneficiary(
        self, test_client, authenticated_headers, db_session, test_user
    ):
        """Test adding a beneficiary to a policy."""
        # Create policy with one 50% beneficiary
        policy = LifeAssurancePolicy(
            user_id=test_user.id,
            provider="Legal & General",
            provider_country=ProviderCountry.UK,
            policy_type=PolicyType.TERM,
            cover_amount=Decimal("500000.00"),
            currency=Currency.GBP,
            premium_amount=Decimal("45.50"),
            premium_frequency=PremiumFrequency.MONTHLY,
            start_date=date(2023, 1, 1),
            status=PolicyStatus.ACTIVE,
            annual_premium=Decimal("546.00")
        )
        policy.set_policy_number("POL123456")
        db_session.add(policy)
        await db_session.flush()

        # Add first beneficiary (50%)
        ben1 = PolicyBeneficiary(
            policy_id=policy.id,
            beneficiary_relationship=BeneficiaryRelationship.SPOUSE,
            percentage=Decimal("50.00")
        )
        ben1.set_name("Jane Doe")
        ben1.set_date_of_birth(date(1985, 6, 15))
        ben1.set_address("123 Main St")
        db_session.add(ben1)
        await db_session.commit()

        # Add second beneficiary (50%)
        beneficiary_payload = {
            "name": "John Doe Jr",
            "date_of_birth": "2015-03-20",
            "relationship": "CHILD",
            "percentage": 50.00,
            "address": "123 Main St, London, UK"
        }

        response = await test_client.post(
            f"/api/v1/protection/life-assurance/{policy.id}/beneficiaries",
            json=beneficiary_payload,
            headers=authenticated_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "John Doe Jr"
        assert data["relationship"] == "CHILD"
        assert Decimal(str(data["percentage"])) == Decimal("50.00")

    async def test_add_beneficiary_exceeds_100_percent(
        self, test_client, authenticated_headers, db_session, test_user
    ):
        """Test adding beneficiary that would exceed 100% fails."""
        # Create policy with 100% beneficiary
        policy = LifeAssurancePolicy(
            user_id=test_user.id,
            provider="Legal & General",
            provider_country=ProviderCountry.UK,
            policy_type=PolicyType.TERM,
            cover_amount=Decimal("500000.00"),
            currency=Currency.GBP,
            premium_amount=Decimal("45.50"),
            premium_frequency=PremiumFrequency.MONTHLY,
            start_date=date(2023, 1, 1),
            status=PolicyStatus.ACTIVE,
            annual_premium=Decimal("546.00")
        )
        policy.set_policy_number("POL123456")
        db_session.add(policy)
        await db_session.flush()

        # Add 100% beneficiary
        ben1 = PolicyBeneficiary(
            policy_id=policy.id,
            beneficiary_relationship=BeneficiaryRelationship.SPOUSE,
            percentage=Decimal("100.00")
        )
        ben1.set_name("Jane Doe")
        ben1.set_date_of_birth(date(1985, 6, 15))
        ben1.set_address("123 Main St")
        db_session.add(ben1)
        await db_session.commit()

        # Try to add another beneficiary
        beneficiary_payload = {
            "name": "John Doe Jr",
            "date_of_birth": "2015-03-20",
            "relationship": "CHILD",
            "percentage": 50.00,  # Would exceed 100%
            "address": "123 Main St, London, UK"
        }

        response = await test_client.post(
            f"/api/v1/protection/life-assurance/{policy.id}/beneficiaries",
            json=beneficiary_payload,
            headers=authenticated_headers
        )

        assert response.status_code == 400
        assert "100" in response.json()["detail"]

    async def test_update_beneficiary(
        self, test_client, authenticated_headers, db_session, test_user
    ):
        """Test updating a beneficiary."""
        # Create policy with beneficiary
        policy = LifeAssurancePolicy(
            user_id=test_user.id,
            provider="Legal & General",
            provider_country=ProviderCountry.UK,
            policy_type=PolicyType.TERM,
            cover_amount=Decimal("500000.00"),
            currency=Currency.GBP,
            premium_amount=Decimal("45.50"),
            premium_frequency=PremiumFrequency.MONTHLY,
            start_date=date(2023, 1, 1),
            status=PolicyStatus.ACTIVE,
            annual_premium=Decimal("546.00")
        )
        policy.set_policy_number("POL123456")
        db_session.add(policy)
        await db_session.flush()

        beneficiary = PolicyBeneficiary(
            policy_id=policy.id,
            beneficiary_relationship=BeneficiaryRelationship.SPOUSE,
            percentage=Decimal("100.00")
        )
        beneficiary.set_name("Jane Doe")
        beneficiary.set_date_of_birth(date(1985, 6, 15))
        beneficiary.set_address("123 Main St")
        db_session.add(beneficiary)
        await db_session.commit()

        # Update beneficiary
        update_payload = {
            "name": "Jane Smith",
            "percentage": 100.00
        }

        response = await test_client.put(
            f"/api/v1/protection/life-assurance/{policy.id}/beneficiaries/{beneficiary.id}",
            json=update_payload,
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Jane Smith"

    async def test_delete_beneficiary(
        self, test_client, authenticated_headers, db_session, test_user
    ):
        """Test deleting a beneficiary."""
        # Create policy with beneficiary
        policy = LifeAssurancePolicy(
            user_id=test_user.id,
            provider="Legal & General",
            provider_country=ProviderCountry.UK,
            policy_type=PolicyType.TERM,
            cover_amount=Decimal("500000.00"),
            currency=Currency.GBP,
            premium_amount=Decimal("45.50"),
            premium_frequency=PremiumFrequency.MONTHLY,
            start_date=date(2023, 1, 1),
            status=PolicyStatus.ACTIVE,
            annual_premium=Decimal("546.00")
        )
        policy.set_policy_number("POL123456")
        db_session.add(policy)
        await db_session.flush()

        beneficiary = PolicyBeneficiary(
            policy_id=policy.id,
            beneficiary_relationship=BeneficiaryRelationship.SPOUSE,
            percentage=Decimal("100.00")
        )
        beneficiary.set_name("Jane Doe")
        beneficiary.set_date_of_birth(date(1985, 6, 15))
        beneficiary.set_address("123 Main St")
        db_session.add(beneficiary)
        await db_session.commit()

        response = await test_client.delete(
            f"/api/v1/protection/life-assurance/{policy.id}/beneficiaries/{beneficiary.id}",
            headers=authenticated_headers
        )

        assert response.status_code == 204

        # Verify beneficiary is deleted
        from sqlalchemy import select
        stmt = select(PolicyBeneficiary).where(PolicyBeneficiary.id == beneficiary.id)
        result = await db_session.execute(stmt)
        deleted_ben = result.scalar_one_or_none()
        assert deleted_ben is None
