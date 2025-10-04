"""
Tests for Policy Management Service

Tests comprehensive policy CRUD operations including:
- Policy creation with validation
- Policy updates
- Soft delete
- Beneficiary management
- Encryption/decryption
- Authorization checks
- Percentage validation
- Trust details handling
"""

import pytest
from decimal import Decimal
from datetime import date, datetime
from uuid import uuid4, UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from services.protection.policy_service import PolicyService
from services.protection.exceptions import (
    PolicyValidationError,
    PolicyNotFoundError,
    PolicyPermissionError
)
from models.life_assurance import (
    LifeAssurancePolicy,
    PolicyBeneficiary,
    PolicyTrustDetail,
    PolicyStatus,
    PremiumFrequency,
    ProviderCountry,
    PolicyType,
    TrustType,
    BeneficiaryRelationship,
    Currency
)
from models.user import User


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    from models.user import UserStatus, CountryPreference

    user = User(
        id=uuid4(),
        email=f"testuser_{uuid4()}@example.com",
        password_hash="hashed_password",
        first_name="Test",
        last_name="User",
        status=UserStatus.ACTIVE,
        email_verified=True,
        country_preference=CountryPreference.UK,
        terms_accepted_at=datetime.utcnow()
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def other_user(db_session: AsyncSession) -> User:
    """Create another test user for permission tests."""
    from models.user import UserStatus, CountryPreference

    user = User(
        id=uuid4(),
        email=f"otheruser_{uuid4()}@example.com",
        password_hash="hashed_password",
        first_name="Other",
        last_name="User",
        status=UserStatus.ACTIVE,
        email_verified=True,
        country_preference=CountryPreference.UK,
        terms_accepted_at=datetime.utcnow()
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def policy_service(db_session: AsyncSession) -> PolicyService:
    """Create policy service instance."""
    return PolicyService(db_session)


@pytest.fixture
def valid_policy_data() -> dict:
    """Create valid policy data for testing."""
    return {
        'policy_number': 'POL123456',
        'provider': 'Legal & General',
        'provider_country': ProviderCountry.UK,
        'policy_type': PolicyType.TERM,
        'cover_amount': Decimal('500000.00'),
        'currency': Currency.GBP,
        'premium_amount': Decimal('50.00'),
        'premium_frequency': PremiumFrequency.MONTHLY,
        'start_date': date(2024, 1, 1),
        'end_date': date(2044, 1, 1),
        'written_in_trust': False,
        'beneficiaries': [
            {
                'name': 'Jane Doe',
                'date_of_birth': date(1985, 5, 15),
                'address': '123 Main Street, London',
                'relationship': BeneficiaryRelationship.SPOUSE,
                'percentage': Decimal('100.00')
            }
        ],
        'critical_illness_rider': True,
        'waiver_of_premium': False,
        'notes': 'Primary life insurance policy'
    }


@pytest.fixture
def valid_trust_policy_data() -> dict:
    """Create valid policy data with trust."""
    return {
        'policy_number': 'TRUST789',
        'provider': 'Aviva',
        'provider_country': ProviderCountry.UK,
        'policy_type': PolicyType.WHOLE_OF_LIFE,
        'cover_amount': Decimal('1000000.00'),
        'currency': Currency.GBP,
        'premium_amount': Decimal('100.00'),
        'premium_frequency': PremiumFrequency.MONTHLY,
        'start_date': date(2024, 1, 1),
        'end_date': None,  # Whole of life
        'written_in_trust': True,
        'trust_type': TrustType.DISCRETIONARY,
        'trust_details': {
            'trust_type': TrustType.DISCRETIONARY,
            'trustees': ['John Smith', 'Sarah Jones'],
            'trust_beneficiaries': 'Spouse and children',
            'trust_created_date': date(2024, 1, 1)
        },
        'beneficiaries': [
            {
                'name': 'Jane Doe',
                'date_of_birth': date(1985, 5, 15),
                'address': '123 Main Street, London',
                'relationship': BeneficiaryRelationship.SPOUSE,
                'percentage': Decimal('50.00')
            },
            {
                'name': 'John Doe Jr',
                'date_of_birth': date(2010, 3, 20),
                'address': '123 Main Street, London',
                'relationship': BeneficiaryRelationship.CHILD,
                'percentage': Decimal('50.00')
            }
        ]
    }


class TestCreatePolicy:
    """Test policy creation."""

    async def test_create_policy_success(
        self,
        db_session: AsyncSession,
        test_user: User,
        policy_service: PolicyService,
        valid_policy_data: dict
    ):
        """Test successful policy creation."""
        policy = await policy_service.create_policy(
            user_id=test_user.id,
            policy_data=valid_policy_data
        )

        assert policy.id is not None
        assert policy.user_id == test_user.id
        assert policy.provider == 'Legal & General'
        assert policy.cover_amount == Decimal('500000.00')
        assert policy.annual_premium == Decimal('600.00')  # 50 * 12
        assert policy.status == PolicyStatus.ACTIVE
        assert policy.is_deleted is False

        # Check encryption
        assert policy.policy_number_encrypted is not None
        assert policy.get_policy_number() == 'POL123456'

        # Check beneficiaries
        assert len(policy.beneficiaries) == 1
        ben = policy.beneficiaries[0]
        assert ben.get_name() == 'Jane Doe'
        assert ben.percentage == Decimal('100.00')

        # Check tax impacts
        assert policy.uk_iht_impact is True  # UK policy not in trust
        assert policy.sa_estate_duty_impact is False

    async def test_create_policy_with_trust(
        self,
        db_session: AsyncSession,
        test_user: User,
        policy_service: PolicyService,
        valid_trust_policy_data: dict
    ):
        """Test policy creation with trust details."""
        policy = await policy_service.create_policy(
            user_id=test_user.id,
            policy_data=valid_trust_policy_data
        )

        assert policy.written_in_trust is True
        assert policy.trust_type == TrustType.DISCRETIONARY
        assert policy.uk_iht_impact is False  # In trust, outside estate

        # Check trust details
        assert policy.trust_detail is not None
        assert policy.trust_detail.trust_type == TrustType.DISCRETIONARY
        trustees = policy.trust_detail.get_trustees()
        assert len(trustees) == 2
        assert 'John Smith' in trustees

        # Check beneficiaries
        assert len(policy.beneficiaries) == 2

    async def test_create_policy_invalid_beneficiary_percentage(
        self,
        db_session: AsyncSession,
        test_user: User,
        policy_service: PolicyService,
        valid_policy_data: dict
    ):
        """Test policy creation with invalid beneficiary percentages."""
        # Modify beneficiaries to total 80%
        valid_policy_data['beneficiaries'][0]['percentage'] = Decimal('80.00')

        with pytest.raises(PolicyValidationError) as exc_info:
            await policy_service.create_policy(
                user_id=test_user.id,
                policy_data=valid_policy_data
            )

        assert "must total exactly 100%" in str(exc_info.value)

    async def test_create_policy_invalid_cover_amount(
        self,
        db_session: AsyncSession,
        test_user: User,
        policy_service: PolicyService,
        valid_policy_data: dict
    ):
        """Test policy creation with invalid cover amount."""
        valid_policy_data['cover_amount'] = Decimal('-100.00')

        with pytest.raises(PolicyValidationError) as exc_info:
            await policy_service.create_policy(
                user_id=test_user.id,
                policy_data=valid_policy_data
            )

        assert "Cover amount must be > 0" in str(exc_info.value)

    async def test_create_policy_invalid_dates(
        self,
        db_session: AsyncSession,
        test_user: User,
        policy_service: PolicyService,
        valid_policy_data: dict
    ):
        """Test policy creation with invalid dates."""
        valid_policy_data['start_date'] = date(2044, 1, 1)
        valid_policy_data['end_date'] = date(2024, 1, 1)

        with pytest.raises(PolicyValidationError) as exc_info:
            await policy_service.create_policy(
                user_id=test_user.id,
                policy_data=valid_policy_data
            )

        assert "End date must be after start date" in str(exc_info.value)

    async def test_create_policy_trust_without_details(
        self,
        db_session: AsyncSession,
        test_user: User,
        policy_service: PolicyService,
        valid_policy_data: dict
    ):
        """Test policy creation with trust but no trust details."""
        valid_policy_data['written_in_trust'] = True
        # Don't provide trust_details

        with pytest.raises(PolicyValidationError) as exc_info:
            await policy_service.create_policy(
                user_id=test_user.id,
                policy_data=valid_policy_data
            )

        assert "Trust details are required" in str(exc_info.value)


class TestUpdatePolicy:
    """Test policy updates."""

    async def test_update_policy_success(
        self,
        db_session: AsyncSession,
        test_user: User,
        policy_service: PolicyService,
        valid_policy_data: dict
    ):
        """Test successful policy update."""
        # Create policy
        policy = await policy_service.create_policy(
            user_id=test_user.id,
            policy_data=valid_policy_data
        )

        # Update policy
        update_data = {
            'provider': 'Prudential',
            'premium_amount': Decimal('60.00')
        }

        updated_policy = await policy_service.update_policy(
            policy_id=policy.id,
            user_id=test_user.id,
            update_data=update_data
        )

        assert updated_policy.provider == 'Prudential'
        assert updated_policy.premium_amount == Decimal('60.00')
        assert updated_policy.annual_premium == Decimal('720.00')  # 60 * 12

    async def test_update_policy_not_found(
        self,
        db_session: AsyncSession,
        test_user: User,
        policy_service: PolicyService
    ):
        """Test updating non-existent policy."""
        with pytest.raises(PolicyNotFoundError):
            await policy_service.update_policy(
                policy_id=uuid4(),
                user_id=test_user.id,
                update_data={'provider': 'Test'}
            )

    async def test_update_policy_permission_denied(
        self,
        db_session: AsyncSession,
        test_user: User,
        other_user: User,
        policy_service: PolicyService,
        valid_policy_data: dict
    ):
        """Test updating another user's policy."""
        # Create policy for test_user
        policy = await policy_service.create_policy(
            user_id=test_user.id,
            policy_data=valid_policy_data
        )

        # Try to update with other_user
        with pytest.raises(PolicyPermissionError):
            await policy_service.update_policy(
                policy_id=policy.id,
                user_id=other_user.id,
                update_data={'provider': 'Hacker'}
            )


class TestDeletePolicy:
    """Test policy deletion."""

    async def test_delete_policy_success(
        self,
        db_session: AsyncSession,
        test_user: User,
        policy_service: PolicyService,
        valid_policy_data: dict
    ):
        """Test successful soft delete."""
        # Create policy
        policy = await policy_service.create_policy(
            user_id=test_user.id,
            policy_data=valid_policy_data
        )

        # Delete policy
        result = await policy_service.delete_policy(
            policy_id=policy.id,
            user_id=test_user.id
        )

        assert result is True

        # Verify soft delete
        stmt = select(LifeAssurancePolicy).where(
            LifeAssurancePolicy.id == policy.id
        )
        result = await db_session.execute(stmt)
        deleted_policy = result.scalar_one_or_none()

        assert deleted_policy is not None
        assert deleted_policy.is_deleted is True

    async def test_delete_policy_permission_denied(
        self,
        db_session: AsyncSession,
        test_user: User,
        other_user: User,
        policy_service: PolicyService,
        valid_policy_data: dict
    ):
        """Test deleting another user's policy."""
        # Create policy
        policy = await policy_service.create_policy(
            user_id=test_user.id,
            policy_data=valid_policy_data
        )

        # Try to delete with other_user
        with pytest.raises(PolicyPermissionError):
            await policy_service.delete_policy(
                policy_id=policy.id,
                user_id=other_user.id
            )


class TestGetUserPolicies:
    """Test fetching user policies."""

    async def test_get_user_policies_empty(
        self,
        db_session: AsyncSession,
        test_user: User,
        policy_service: PolicyService
    ):
        """Test getting policies for user with none."""
        policies = await policy_service.get_user_policies(test_user.id)
        assert len(policies) == 0

    async def test_get_user_policies_with_data(
        self,
        db_session: AsyncSession,
        test_user: User,
        policy_service: PolicyService,
        valid_policy_data: dict
    ):
        """Test getting policies for user."""
        # Create 2 policies
        await policy_service.create_policy(
            user_id=test_user.id,
            policy_data=valid_policy_data
        )

        policy_data_2 = valid_policy_data.copy()
        policy_data_2['policy_number'] = 'POL999'
        await policy_service.create_policy(
            user_id=test_user.id,
            policy_data=policy_data_2
        )

        policies = await policy_service.get_user_policies(test_user.id)
        assert len(policies) == 2

    async def test_get_user_policies_exclude_deleted(
        self,
        db_session: AsyncSession,
        test_user: User,
        policy_service: PolicyService,
        valid_policy_data: dict
    ):
        """Test that deleted policies are excluded by default."""
        # Create policy
        policy = await policy_service.create_policy(
            user_id=test_user.id,
            policy_data=valid_policy_data
        )

        # Delete it
        await policy_service.delete_policy(policy.id, test_user.id)

        # Get policies
        policies = await policy_service.get_user_policies(test_user.id)
        assert len(policies) == 0

        # Get with include_deleted
        policies = await policy_service.get_user_policies(
            test_user.id,
            include_deleted=True
        )
        assert len(policies) == 1

    async def test_get_user_policies_filter_by_provider(
        self,
        db_session: AsyncSession,
        test_user: User,
        policy_service: PolicyService,
        valid_policy_data: dict
    ):
        """Test filtering policies by provider."""
        # Create 2 policies with different providers
        await policy_service.create_policy(
            user_id=test_user.id,
            policy_data=valid_policy_data
        )

        policy_data_2 = valid_policy_data.copy()
        policy_data_2['policy_number'] = 'POL999'
        policy_data_2['provider'] = 'Aviva'
        await policy_service.create_policy(
            user_id=test_user.id,
            policy_data=policy_data_2
        )

        # Filter by provider
        policies = await policy_service.get_user_policies(
            test_user.id,
            provider='Aviva'
        )
        assert len(policies) == 1
        assert policies[0].provider == 'Aviva'


class TestGetPolicyById:
    """Test getting specific policy."""

    async def test_get_policy_by_id_success(
        self,
        db_session: AsyncSession,
        test_user: User,
        policy_service: PolicyService,
        valid_policy_data: dict
    ):
        """Test getting policy by ID."""
        # Create policy
        created_policy = await policy_service.create_policy(
            user_id=test_user.id,
            policy_data=valid_policy_data
        )

        # Get policy
        policy = await policy_service.get_policy_by_id(
            policy_id=created_policy.id,
            user_id=test_user.id
        )

        assert policy.id == created_policy.id
        assert policy.beneficiaries is not None
        assert len(policy.beneficiaries) == 1

    async def test_get_policy_by_id_permission_denied(
        self,
        db_session: AsyncSession,
        test_user: User,
        other_user: User,
        policy_service: PolicyService,
        valid_policy_data: dict
    ):
        """Test getting another user's policy."""
        # Create policy
        policy = await policy_service.create_policy(
            user_id=test_user.id,
            policy_data=valid_policy_data
        )

        # Try to get with other_user
        with pytest.raises(PolicyPermissionError):
            await policy_service.get_policy_by_id(
                policy_id=policy.id,
                user_id=other_user.id
            )


class TestBeneficiaryManagement:
    """Test beneficiary CRUD operations."""

    async def test_add_beneficiary_success(
        self,
        db_session: AsyncSession,
        test_user: User,
        policy_service: PolicyService,
        valid_policy_data: dict
    ):
        """Test adding a beneficiary."""
        # Create policy with one beneficiary (100%)
        policy = await policy_service.create_policy(
            user_id=test_user.id,
            policy_data=valid_policy_data
        )

        # Remove the existing beneficiary to make room
        await policy_service.delete_beneficiary(
            beneficiary_id=policy.beneficiaries[0].id,
            user_id=test_user.id
        )

        # Add new beneficiary
        beneficiary_data = {
            'name': 'John Doe',
            'date_of_birth': date(1980, 1, 1),
            'address': '456 Oak Avenue',
            'relationship': BeneficiaryRelationship.SIBLING,
            'percentage': Decimal('100.00')
        }

        beneficiary = await policy_service.add_beneficiary(
            policy_id=policy.id,
            user_id=test_user.id,
            beneficiary_data=beneficiary_data
        )

        assert beneficiary.id is not None
        assert beneficiary.get_name() == 'John Doe'
        assert beneficiary.percentage == Decimal('100.00')

    async def test_add_beneficiary_exceeds_100_percent(
        self,
        db_session: AsyncSession,
        test_user: User,
        policy_service: PolicyService,
        valid_policy_data: dict
    ):
        """Test adding beneficiary that would exceed 100%."""
        # Create policy with one beneficiary (100%)
        policy = await policy_service.create_policy(
            user_id=test_user.id,
            policy_data=valid_policy_data
        )

        # Try to add another at 50%
        beneficiary_data = {
            'name': 'John Doe',
            'date_of_birth': date(1980, 1, 1),
            'address': '456 Oak Avenue',
            'relationship': BeneficiaryRelationship.SIBLING,
            'percentage': Decimal('50.00')
        }

        with pytest.raises(PolicyValidationError) as exc_info:
            await policy_service.add_beneficiary(
                policy_id=policy.id,
                user_id=test_user.id,
                beneficiary_data=beneficiary_data
            )

        assert "would exceed 100%" in str(exc_info.value)

    async def test_update_beneficiary_success(
        self,
        db_session: AsyncSession,
        test_user: User,
        policy_service: PolicyService,
        valid_policy_data: dict
    ):
        """Test updating a beneficiary."""
        # Create policy
        policy = await policy_service.create_policy(
            user_id=test_user.id,
            policy_data=valid_policy_data
        )

        beneficiary = policy.beneficiaries[0]

        # Update beneficiary
        update_data = {
            'name': 'Jane Smith',
            'percentage': Decimal('100.00')
        }

        updated_beneficiary = await policy_service.update_beneficiary(
            beneficiary_id=beneficiary.id,
            user_id=test_user.id,
            update_data=update_data
        )

        assert updated_beneficiary.get_name() == 'Jane Smith'
        assert updated_beneficiary.percentage == Decimal('100.00')

    async def test_update_beneficiary_invalid_percentage(
        self,
        db_session: AsyncSession,
        test_user: User,
        policy_service: PolicyService,
        valid_trust_policy_data: dict
    ):
        """Test updating beneficiary with invalid percentage."""
        # Create policy with 2 beneficiaries (50% each)
        policy = await policy_service.create_policy(
            user_id=test_user.id,
            policy_data=valid_trust_policy_data
        )

        beneficiary = policy.beneficiaries[0]

        # Try to update to 60% (would make total 110%)
        update_data = {
            'percentage': Decimal('60.00')
        }

        with pytest.raises(PolicyValidationError) as exc_info:
            await policy_service.update_beneficiary(
                beneficiary_id=beneficiary.id,
                user_id=test_user.id,
                update_data=update_data
            )

        assert "would exceed 100%" in str(exc_info.value)

    async def test_delete_beneficiary_success(
        self,
        db_session: AsyncSession,
        test_user: User,
        policy_service: PolicyService,
        valid_policy_data: dict
    ):
        """Test deleting a beneficiary."""
        # Create policy
        policy = await policy_service.create_policy(
            user_id=test_user.id,
            policy_data=valid_policy_data
        )

        beneficiary = policy.beneficiaries[0]

        # Delete beneficiary
        result = await policy_service.delete_beneficiary(
            beneficiary_id=beneficiary.id,
            user_id=test_user.id
        )

        assert result is True

        # Verify deletion
        stmt = select(PolicyBeneficiary).where(
            PolicyBeneficiary.id == beneficiary.id
        )
        result = await db_session.execute(stmt)
        deleted_ben = result.scalar_one_or_none()

        assert deleted_ben is None

    async def test_beneficiary_permission_denied(
        self,
        db_session: AsyncSession,
        test_user: User,
        other_user: User,
        policy_service: PolicyService,
        valid_policy_data: dict
    ):
        """Test beneficiary operations with wrong user."""
        # Create policy
        policy = await policy_service.create_policy(
            user_id=test_user.id,
            policy_data=valid_policy_data
        )

        beneficiary = policy.beneficiaries[0]

        # Try to update with other_user
        with pytest.raises(PolicyPermissionError):
            await policy_service.update_beneficiary(
                beneficiary_id=beneficiary.id,
                user_id=other_user.id,
                update_data={'name': 'Hacker'}
            )

        # Try to delete with other_user
        with pytest.raises(PolicyPermissionError):
            await policy_service.delete_beneficiary(
                beneficiary_id=beneficiary.id,
                user_id=other_user.id
            )


class TestBeneficiaryPercentageValidation:
    """Test beneficiary percentage validation."""

    def test_validate_percentages_valid(self, policy_service: PolicyService):
        """Test valid percentage totaling 100%."""
        beneficiaries = [
            {'percentage': Decimal('50.00')},
            {'percentage': Decimal('50.00')}
        ]

        # Should not raise
        policy_service.validate_beneficiary_percentages(beneficiaries)

    def test_validate_percentages_invalid_total(self, policy_service: PolicyService):
        """Test invalid percentage total."""
        beneficiaries = [
            {'percentage': Decimal('50.00')},
            {'percentage': Decimal('40.00')}
        ]

        with pytest.raises(PolicyValidationError) as exc_info:
            policy_service.validate_beneficiary_percentages(beneficiaries)

        assert "must total exactly 100%" in str(exc_info.value)

    def test_validate_percentages_empty_list(self, policy_service: PolicyService):
        """Test with empty beneficiary list."""
        beneficiaries = []

        # Should not raise
        policy_service.validate_beneficiary_percentages(beneficiaries)


class TestEncryptionDecryption:
    """Test PII encryption and decryption."""

    async def test_policy_number_encryption(
        self,
        db_session: AsyncSession,
        test_user: User,
        policy_service: PolicyService,
        valid_policy_data: dict
    ):
        """Test policy number is encrypted in database."""
        policy = await policy_service.create_policy(
            user_id=test_user.id,
            policy_data=valid_policy_data
        )

        # Encrypted value should be different from original
        assert policy.policy_number_encrypted != 'POL123456'

        # Decryption should return original value
        assert policy.get_policy_number() == 'POL123456'

    async def test_beneficiary_pii_encryption(
        self,
        db_session: AsyncSession,
        test_user: User,
        policy_service: PolicyService,
        valid_policy_data: dict
    ):
        """Test beneficiary PII is encrypted."""
        policy = await policy_service.create_policy(
            user_id=test_user.id,
            policy_data=valid_policy_data
        )

        beneficiary = policy.beneficiaries[0]

        # Encrypted values should be different
        assert beneficiary.name_encrypted != 'Jane Doe'
        assert beneficiary.address_encrypted != '123 Main Street, London'

        # Decryption should return original values
        assert beneficiary.get_name() == 'Jane Doe'
        assert beneficiary.get_address() == '123 Main Street, London'
        assert beneficiary.get_date_of_birth() == date(1985, 5, 15)


class TestTaxImpactCalculation:
    """Test tax impact calculations."""

    async def test_uk_policy_not_in_trust(
        self,
        db_session: AsyncSession,
        test_user: User,
        policy_service: PolicyService,
        valid_policy_data: dict
    ):
        """Test UK policy not in trust is in IHT estate."""
        policy = await policy_service.create_policy(
            user_id=test_user.id,
            policy_data=valid_policy_data
        )

        assert policy.uk_iht_impact is True
        assert policy.sa_estate_duty_impact is False

    async def test_uk_policy_in_trust(
        self,
        db_session: AsyncSession,
        test_user: User,
        policy_service: PolicyService,
        valid_trust_policy_data: dict
    ):
        """Test UK policy in trust is outside IHT estate."""
        policy = await policy_service.create_policy(
            user_id=test_user.id,
            policy_data=valid_trust_policy_data
        )

        assert policy.uk_iht_impact is False  # Outside estate due to trust
        assert policy.sa_estate_duty_impact is False

    async def test_sa_policy_estate_duty(
        self,
        db_session: AsyncSession,
        test_user: User,
        policy_service: PolicyService,
        valid_policy_data: dict
    ):
        """Test SA policy is subject to estate duty."""
        valid_policy_data['provider_country'] = ProviderCountry.SA
        valid_policy_data['currency'] = Currency.ZAR
        valid_policy_data['cover_amount'] = Decimal('5000000.00')

        policy = await policy_service.create_policy(
            user_id=test_user.id,
            policy_data=valid_policy_data
        )

        assert policy.uk_iht_impact is False
        assert policy.sa_estate_duty_impact is True
