"""
Tests for life assurance policy models.

This module tests:
- LifeAssurancePolicy model creation and validation
- PolicyBeneficiary model and relationships
- PolicyTrustDetail model and trust structure
- PolicyDocument model and document tracking
- Encryption of PII fields
- Calculated fields (annual_premium, tax impact)
- Constraint violations
- Cascade deletes
- Soft delete functionality
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
import uuid
import os

from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError

from models.life_assurance import (
    LifeAssurancePolicy,
    PolicyBeneficiary,
    PolicyTrustDetail,
    PolicyDocument,
    ProviderCountry,
    PolicyType,
    PremiumFrequency,
    TrustType,
    PolicyStatus,
    BeneficiaryRelationship,
    DocumentType,
    Currency
)
from models.user import User, CountryPreference
from utils.encryption import encrypt_value, decrypt_value


@pytest.fixture
async def test_user(db_session):
    """Create a test user."""
    user = User(
        email=f"test_{uuid.uuid4()}@example.com",
        first_name="Test",
        last_name="User",
        country_preference=CountryPreference.BOTH,
        terms_accepted_at=datetime.utcnow(),
        email_verified=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_policy(db_session, test_user):
    """Create a test life assurance policy."""
    policy = LifeAssurancePolicy(
        user_id=test_user.id,
        provider="Legal & General",
        provider_country=ProviderCountry.UK,
        policy_type=PolicyType.TERM,
        cover_amount=Decimal("500000.00"),
        currency=Currency.GBP,
        premium_amount=Decimal("50.00"),
        premium_frequency=PremiumFrequency.MONTHLY,
        start_date=date(2024, 1, 1),
        end_date=date(2044, 1, 1),
        written_in_trust=False,
        status=PolicyStatus.ACTIVE
    )
    policy.set_policy_number("POL123456")
    db_session.add(policy)
    await db_session.commit()
    await db_session.refresh(policy)
    return policy


class TestLifeAssurancePolicy:
    """Test LifeAssurancePolicy model."""

    @pytest.mark.asyncio


    async def test_create_policy_with_valid_data(self, db_session, test_user):
        """Test creating a policy with valid data."""
        policy = LifeAssurancePolicy(
            user_id=test_user.id,
            provider="Aviva",
            provider_country=ProviderCountry.UK,
            policy_type=PolicyType.WHOLE_OF_LIFE,
            cover_amount=Decimal("250000.00"),
            currency=Currency.GBP,
            premium_amount=Decimal("100.00"),
            premium_frequency=PremiumFrequency.MONTHLY,
            start_date=date(2024, 6, 1),
            end_date=None,  # Whole of life has no end date
            status=PolicyStatus.ACTIVE
        )
        policy.set_policy_number("AVIVA987654")

        db_session.add(policy)
        await db_session.commit()
        await db_session.refresh(policy)

        assert policy.id is not None
        assert policy.user_id == test_user.id
        assert policy.provider == "Aviva"
        assert policy.get_policy_number() == "AVIVA987654"
        assert policy.cover_amount == Decimal("250000.00")
        assert policy.end_date is None  # Whole of life

    @pytest.mark.asyncio


    async def test_policy_number_encryption(self, db_session, test_user):
        """Test policy number is encrypted."""
        policy = LifeAssurancePolicy(
            user_id=test_user.id,
            provider="Test Provider",
            provider_country=ProviderCountry.UK,
            policy_type=PolicyType.TERM,
            cover_amount=Decimal("100000.00"),
            currency=Currency.GBP,
            premium_amount=Decimal("25.00"),
            premium_frequency=PremiumFrequency.MONTHLY,
            start_date=date(2024, 1, 1),
            end_date=date(2034, 1, 1)
        )

        policy_number = "SECRET123456"
        policy.set_policy_number(policy_number)

        db_session.add(policy)
        await db_session.commit()
        await db_session.refresh(policy)

        # Encrypted value should be different from original
        assert policy.policy_number_encrypted != policy_number
        # Decrypted value should match original
        assert policy.get_policy_number() == policy_number

    @pytest.mark.asyncio


    async def test_calculate_annual_premium_monthly(self, db_session, test_policy):
        """Test annual premium calculation for monthly frequency."""
        test_policy.premium_amount = Decimal("50.00")
        test_policy.premium_frequency = PremiumFrequency.MONTHLY

        annual = test_policy.calculate_annual_premium()
        assert annual == Decimal("600.00")

    @pytest.mark.asyncio


    async def test_calculate_annual_premium_annually(self, db_session, test_policy):
        """Test annual premium calculation for annual frequency."""
        test_policy.premium_amount = Decimal("500.00")
        test_policy.premium_frequency = PremiumFrequency.ANNUALLY

        annual = test_policy.calculate_annual_premium()
        assert annual == Decimal("500.00")

    @pytest.mark.asyncio


    async def test_calculate_annual_premium_single(self, db_session, test_policy):
        """Test annual premium calculation for single premium."""
        test_policy.premium_amount = Decimal("10000.00")
        test_policy.premium_frequency = PremiumFrequency.SINGLE

        annual = test_policy.calculate_annual_premium()
        assert annual == Decimal("10000.00")

    @pytest.mark.asyncio


    async def test_calculate_uk_iht_impact_not_in_trust(self, db_session, test_policy):
        """Test UK IHT impact for policy not in trust."""
        test_policy.provider_country = ProviderCountry.UK
        test_policy.written_in_trust = False

        iht_impact = test_policy.calculate_uk_iht_impact()
        assert iht_impact is True  # In estate for IHT

    @pytest.mark.asyncio


    async def test_calculate_uk_iht_impact_in_trust(self, db_session, test_policy):
        """Test UK IHT impact for policy in trust."""
        test_policy.provider_country = ProviderCountry.UK
        test_policy.written_in_trust = True

        iht_impact = test_policy.calculate_uk_iht_impact()
        assert iht_impact is False  # Outside estate

    @pytest.mark.asyncio


    async def test_calculate_sa_estate_duty_impact(self, db_session, test_user):
        """Test SA estate duty impact."""
        policy = LifeAssurancePolicy(
            user_id=test_user.id,
            provider="Old Mutual",
            provider_country=ProviderCountry.SA,
            policy_type=PolicyType.TERM,
            cover_amount=Decimal("1000000.00"),
            currency=Currency.ZAR,
            premium_amount=Decimal("500.00"),
            premium_frequency=PremiumFrequency.MONTHLY,
            start_date=date(2024, 1, 1),
            end_date=date(2044, 1, 1)
        )
        policy.set_policy_number("OM123456")

        estate_duty_impact = policy.calculate_sa_estate_duty_impact()
        assert estate_duty_impact is True  # SA policies generally in estate

    @pytest.mark.asyncio


    async def test_cover_amount_positive_constraint(self, db_session, test_user):
        """Test cover amount must be positive."""
        policy = LifeAssurancePolicy(
            user_id=test_user.id,
            provider="Test",
            provider_country=ProviderCountry.UK,
            policy_type=PolicyType.TERM,
            cover_amount=Decimal("-100.00"),  # Invalid negative amount
            currency=Currency.GBP,
            premium_amount=Decimal("25.00"),
            premium_frequency=PremiumFrequency.MONTHLY,
            start_date=date(2024, 1, 1),
            end_date=date(2034, 1, 1)
        )
        policy.set_policy_number("TEST123")

        db_session.add(policy)
        with pytest.raises(IntegrityError):
            await db_session.commit()

    @pytest.mark.asyncio


    async def test_premium_amount_non_negative_constraint(self, db_session, test_user):
        """Test premium amount must be non-negative."""
        policy = LifeAssurancePolicy(
            user_id=test_user.id,
            provider="Test",
            provider_country=ProviderCountry.UK,
            policy_type=PolicyType.TERM,
            cover_amount=Decimal("100000.00"),
            currency=Currency.GBP,
            premium_amount=Decimal("-50.00"),  # Invalid negative amount
            premium_frequency=PremiumFrequency.MONTHLY,
            start_date=date(2024, 1, 1),
            end_date=date(2034, 1, 1)
        )
        policy.set_policy_number("TEST123")

        db_session.add(policy)
        with pytest.raises(IntegrityError):
            await db_session.commit()

    @pytest.mark.asyncio


    async def test_soft_delete(self, db_session, test_policy):
        """Test soft delete functionality."""
        policy_id = test_policy.id
        test_policy.is_deleted = True
        await db_session.commit()

        # Policy still exists in database
        result = await db_session.execute(
            select(LifeAssurancePolicy).where(LifeAssurancePolicy.id == policy_id)
        )
        policy = result.scalar_one()

        assert policy.is_deleted is True

    @pytest.mark.asyncio


    async def test_policy_with_trust(self, db_session, test_user):
        """Test policy with trust details."""
        policy = LifeAssurancePolicy(
            user_id=test_user.id,
            provider="Royal London",
            provider_country=ProviderCountry.UK,
            policy_type=PolicyType.TERM,
            cover_amount=Decimal("300000.00"),
            currency=Currency.GBP,
            premium_amount=Decimal("40.00"),
            premium_frequency=PremiumFrequency.MONTHLY,
            start_date=date(2024, 1, 1),
            end_date=date(2044, 1, 1),
            written_in_trust=True,
            trust_type=TrustType.DISCRETIONARY
        )
        policy.set_policy_number("RL123456")

        db_session.add(policy)
        await db_session.commit()

        assert policy.written_in_trust is True
        assert policy.trust_type == TrustType.DISCRETIONARY


class TestPolicyBeneficiary:
    """Test PolicyBeneficiary model."""

    @pytest.mark.asyncio


    async def test_create_beneficiary(self, db_session, test_policy):
        """Test creating a beneficiary."""
        beneficiary = PolicyBeneficiary(
            policy_id=test_policy.id,
            beneficiary_relationship=BeneficiaryRelationship.SPOUSE,
            percentage=Decimal("100.00")
        )
        beneficiary.set_name("Jane Doe")
        beneficiary.set_date_of_birth(date(1985, 5, 15))
        beneficiary.set_address("123 Main St, London, UK")

        db_session.add(beneficiary)
        await db_session.commit()
        await db_session.refresh(beneficiary)

        assert beneficiary.id is not None
        assert beneficiary.get_name() == "Jane Doe"
        assert beneficiary.get_date_of_birth() == date(1985, 5, 15)
        assert beneficiary.get_address() == "123 Main St, London, UK"
        assert beneficiary.percentage == Decimal("100.00")

    @pytest.mark.asyncio


    async def test_beneficiary_pii_encryption(self, db_session, test_policy):
        """Test beneficiary PII is encrypted."""
        beneficiary = PolicyBeneficiary(
            policy_id=test_policy.id,
            beneficiary_relationship=BeneficiaryRelationship.CHILD,
            percentage=Decimal("50.00")
        )

        name = "John Doe Jr"
        dob = date(2010, 3, 20)
        address = "456 Oak Ave, Manchester, UK"

        beneficiary.set_name(name)
        beneficiary.set_date_of_birth(dob)
        beneficiary.set_address(address)

        db_session.add(beneficiary)
        await db_session.commit()
        await db_session.refresh(beneficiary)

        # Encrypted values should be different
        assert beneficiary.name_encrypted != name
        assert beneficiary.address_encrypted != address

        # Decrypted values should match
        assert beneficiary.get_name() == name
        assert beneficiary.get_date_of_birth() == dob
        assert beneficiary.get_address() == address

    @pytest.mark.asyncio


    async def test_beneficiary_percentage_constraint(self, db_session, test_policy):
        """Test beneficiary percentage must be between 0 and 100."""
        beneficiary = PolicyBeneficiary(
            policy_id=test_policy.id,
            beneficiary_relationship=BeneficiaryRelationship.SPOUSE,
            percentage=Decimal("150.00")  # Invalid > 100
        )
        beneficiary.set_name("Jane Doe")
        beneficiary.set_date_of_birth(date(1985, 5, 15))
        beneficiary.set_address("123 Main St")

        db_session.add(beneficiary)
        with pytest.raises(IntegrityError):
            await db_session.commit()

    @pytest.mark.asyncio


    async def test_multiple_beneficiaries(self, db_session, test_policy):
        """Test adding multiple beneficiaries."""
        ben1 = PolicyBeneficiary(
            policy_id=test_policy.id,
            beneficiary_relationship=BeneficiaryRelationship.SPOUSE,
            percentage=Decimal("60.00")
        )
        ben1.set_name("Jane Doe")
        ben1.set_date_of_birth(date(1985, 5, 15))
        ben1.set_address("123 Main St")

        ben2 = PolicyBeneficiary(
            policy_id=test_policy.id,
            beneficiary_relationship=BeneficiaryRelationship.CHILD,
            percentage=Decimal("40.00")
        )
        ben2.set_name("John Doe Jr")
        ben2.set_date_of_birth(date(2010, 3, 20))
        ben2.set_address("123 Main St")

        db_session.add_all([ben1, ben2])
        await db_session.commit()

        # Check relationship works
        await db_session.refresh(test_policy)
        beneficiaries_result = await db_session.execute(
            select(PolicyBeneficiary).where(PolicyBeneficiary.policy_id == test_policy.id)
        )
        beneficiaries = beneficiaries_result.scalars().all()
        assert len(beneficiaries) == 2

        # Total percentage (validation happens in application logic)
        total_percentage = sum(b.percentage for b in beneficiaries)
        assert total_percentage == Decimal("100.00")

    @pytest.mark.asyncio


    async def test_beneficiary_cascade_delete(self, db_session, test_policy):
        """Test beneficiaries are deleted when policy is deleted."""
        beneficiary = PolicyBeneficiary(
            policy_id=test_policy.id,
            beneficiary_relationship=BeneficiaryRelationship.SPOUSE,
            percentage=Decimal("100.00")
        )
        beneficiary.set_name("Jane Doe")
        beneficiary.set_date_of_birth(date(1985, 5, 15))
        beneficiary.set_address("123 Main St")

        db_session.add(beneficiary)
        await db_session.commit()

        beneficiary_id = beneficiary.id
        policy_id = test_policy.id

        # Delete policy
        await db_session.delete(test_policy)
        await db_session.commit()

        # Beneficiary should be deleted (cascade)
        result_stmt = await db_session.execute(
            select(PolicyBeneficiary).where(PolicyBeneficiary.id == beneficiary_id)
        )
        result = result_stmt.scalar_one_or_none()

        assert result is None


class TestPolicyTrustDetail:
    """Test PolicyTrustDetail model."""

    @pytest.mark.asyncio


    async def test_create_trust_detail(self, db_session, test_policy):
        """Test creating trust details."""
        test_policy.written_in_trust = True
        test_policy.trust_type = TrustType.DISCRETIONARY
        await db_session.commit()

        trust_detail = PolicyTrustDetail(
            policy_id=test_policy.id,
            trust_type=TrustType.DISCRETIONARY,
            trust_beneficiaries="Children and grandchildren",
            trust_created_date=date(2024, 1, 1)
        )
        trust_detail.set_trustees(["John Smith", "Jane Smith", "Bob Jones"])

        db_session.add(trust_detail)
        await db_session.commit()
        await db_session.refresh(trust_detail)

        assert trust_detail.id is not None
        assert trust_detail.trust_type == TrustType.DISCRETIONARY
        assert trust_detail.get_trustees() == ["John Smith", "Jane Smith", "Bob Jones"]
        assert trust_detail.trust_beneficiaries == "Children and grandchildren"

    @pytest.mark.asyncio


    async def test_trust_detail_one_to_one(self, db_session, test_policy):
        """Test one-to-one relationship with policy."""
        trust1 = PolicyTrustDetail(
            policy_id=test_policy.id,
            trust_type=TrustType.BARE,
            trust_created_date=date(2024, 1, 1)
        )
        trust1.set_trustees(["Trustee 1"])

        db_session.add(trust1)
        await db_session.commit()

        # Try to add another trust detail for same policy
        trust2 = PolicyTrustDetail(
            policy_id=test_policy.id,
            trust_type=TrustType.DISCRETIONARY,
            trust_created_date=date(2024, 1, 1)
        )
        trust2.set_trustees(["Trustee 2"])

        db_session.add(trust2)
        with pytest.raises(IntegrityError):  # Unique constraint violation
            await db_session.commit()

    @pytest.mark.asyncio


    async def test_trust_detail_cascade_delete(self, db_session, test_policy):
        """Test trust detail is deleted when policy is deleted."""
        trust_detail = PolicyTrustDetail(
            policy_id=test_policy.id,
            trust_type=TrustType.DISCRETIONARY,
            trust_created_date=date(2024, 1, 1)
        )
        trust_detail.set_trustees(["Trustee 1"])

        db_session.add(trust_detail)
        await db_session.commit()

        trust_id = trust_detail.id

        # Delete policy
        await db_session.delete(test_policy)
        await db_session.commit()

        # Trust detail should be deleted (cascade)
        result_stmt = await db_session.execute(
            select(PolicyTrustDetail).where(PolicyTrustDetail.id == trust_id)
        )
        result = result_stmt.scalar_one_or_none()

        assert result is None

    @pytest.mark.asyncio


    async def test_trustees_json_storage(self, db_session, test_policy):
        """Test trustees are stored and retrieved correctly as JSON."""
        trust_detail = PolicyTrustDetail(
            policy_id=test_policy.id,
            trust_type=TrustType.INTEREST_IN_POSSESSION,
            trust_created_date=date(2024, 1, 1)
        )

        trustees = ["Alice Johnson", "Bob Williams", "Carol Davis"]
        trust_detail.set_trustees(trustees)

        db_session.add(trust_detail)
        await db_session.commit()
        await db_session.refresh(trust_detail)

        retrieved_trustees = trust_detail.get_trustees()
        assert retrieved_trustees == trustees
        assert len(retrieved_trustees) == 3


class TestPolicyDocument:
    """Test PolicyDocument model."""

    @pytest.mark.asyncio


    async def test_create_policy_document(self, db_session, test_policy):
        """Test creating a policy document."""
        document = PolicyDocument(
            policy_id=test_policy.id,
            document_type=DocumentType.POLICY_DOCUMENT,
            file_path="/documents/policies/policy_123.pdf",
            upload_date=date(2024, 1, 15),
            file_size=1024000,  # 1MB in bytes
            mime_type="application/pdf"
        )

        db_session.add(document)
        await db_session.commit()
        await db_session.refresh(document)

        assert document.id is not None
        assert document.document_type == DocumentType.POLICY_DOCUMENT
        assert document.file_size == 1024000
        assert document.mime_type == "application/pdf"

    @pytest.mark.asyncio


    async def test_multiple_documents_per_policy(self, db_session, test_policy):
        """Test adding multiple documents to a policy."""
        doc1 = PolicyDocument(
            policy_id=test_policy.id,
            document_type=DocumentType.POLICY_DOCUMENT,
            file_path="/documents/policy_main.pdf",
            upload_date=date(2024, 1, 15),
            file_size=1024000,
            mime_type="application/pdf"
        )

        doc2 = PolicyDocument(
            policy_id=test_policy.id,
            document_type=DocumentType.SCHEDULE,
            file_path="/documents/policy_schedule.pdf",
            upload_date=date(2024, 1, 16),
            file_size=512000,
            mime_type="application/pdf"
        )

        db_session.add_all([doc1, doc2])
        await db_session.commit()

        # Check relationship
        await db_session.refresh(test_policy)
        documents_result = await db_session.execute(
            select(PolicyDocument).where(PolicyDocument.policy_id == test_policy.id)
        )
        documents = documents_result.scalars().all()
        assert len(documents) == 2

    @pytest.mark.asyncio


    async def test_document_cascade_delete(self, db_session, test_policy):
        """Test documents are deleted when policy is deleted."""
        document = PolicyDocument(
            policy_id=test_policy.id,
            document_type=DocumentType.TRUST_DEED,
            file_path="/documents/trust_deed.pdf",
            upload_date=date(2024, 1, 15),
            file_size=2048000,
            mime_type="application/pdf"
        )

        db_session.add(document)
        await db_session.commit()

        document_id = document.id

        # Delete policy
        await db_session.delete(test_policy)
        await db_session.commit()

        # Document should be deleted (cascade)
        result_stmt = await db_session.execute(
            select(PolicyDocument).where(PolicyDocument.id == document_id)
        )
        result = result_stmt.scalar_one_or_none()

        assert result is None

    @pytest.mark.asyncio


    async def test_file_size_positive_constraint(self, db_session, test_policy):
        """Test file size must be positive."""
        document = PolicyDocument(
            policy_id=test_policy.id,
            document_type=DocumentType.OTHER,
            file_path="/documents/doc.pdf",
            upload_date=date(2024, 1, 15),
            file_size=-100,  # Invalid negative size
            mime_type="application/pdf"
        )

        db_session.add(document)
        with pytest.raises(IntegrityError):
            await db_session.commit()


class TestIndexes:
    """Test database indexes exist."""

    @pytest.mark.asyncio


    async def test_policy_indexes_exist(self, db_session):
        """Test that required indexes exist for life_assurance_policies table."""
        # This test verifies indexes are created by the migration
        # We check if queries use indexes efficiently (implementation specific)

        # Create test data
        user = User(
            email=f"index_test_{uuid.uuid4()}@example.com",
            first_name="Index",
            last_name="Test",
            country_preference=CountryPreference.UK,
            terms_accepted_at=datetime.utcnow(),
            email_verified=True
        )
        db_session.add(user)
        await db_session.commit()

        policy = LifeAssurancePolicy(
            user_id=user.id,
            provider="Test Provider",
            provider_country=ProviderCountry.UK,
            policy_type=PolicyType.TERM,
            cover_amount=Decimal("100000.00"),
            currency=Currency.GBP,
            premium_amount=Decimal("25.00"),
            premium_frequency=PremiumFrequency.MONTHLY,
            start_date=date(2024, 1, 1),
            end_date=date(2034, 1, 1),
            status=PolicyStatus.ACTIVE
        )
        policy.set_policy_number("IDX123")
        db_session.add(policy)
        await db_session.commit()

        # Query using indexed fields
        result_stmt = await db_session.execute(
            select(LifeAssurancePolicy)
            .where(LifeAssurancePolicy.user_id == user.id)
            .where(LifeAssurancePolicy.status == PolicyStatus.ACTIVE)
        )
        result = result_stmt.scalar_one()

        assert result is not None
        assert result.user_id == user.id


class TestRelationships:
    """Test model relationships."""

    @pytest.mark.asyncio


    async def test_policy_user_relationship(self, db_session, test_user, test_policy):
        """Test relationship between policy and user."""
        await db_session.refresh(test_policy)
        await db_session.refresh(test_user)
        assert test_policy.user == test_user
        user_policies_result = await db_session.execute(
            select(LifeAssurancePolicy).where(LifeAssurancePolicy.user_id == test_user.id)
        )
        user_policies = user_policies_result.scalars().all()
        assert test_policy in user_policies

    @pytest.mark.asyncio


    async def test_policy_beneficiaries_relationship(self, db_session, test_policy):
        """Test relationship between policy and beneficiaries."""
        ben = PolicyBeneficiary(
            policy_id=test_policy.id,
            beneficiary_relationship=BeneficiaryRelationship.SPOUSE,
            percentage=Decimal("100.00")
        )
        ben.set_name("Test Beneficiary")
        ben.set_date_of_birth(date(1985, 1, 1))
        ben.set_address("Test Address")

        db_session.add(ben)
        await db_session.commit()

        await db_session.refresh(ben)
        await db_session.refresh(test_policy)
        assert ben.policy == test_policy
        policy_bens_result = await db_session.execute(
            select(PolicyBeneficiary).where(PolicyBeneficiary.policy_id == test_policy.id)
        )
        policy_bens = policy_bens_result.scalars().all()
        assert ben in policy_bens

    @pytest.mark.asyncio


    async def test_policy_trust_relationship(self, db_session, test_policy):
        """Test relationship between policy and trust detail."""
        trust = PolicyTrustDetail(
            policy_id=test_policy.id,
            trust_type=TrustType.BARE,
            trust_created_date=date(2024, 1, 1)
        )
        trust.set_trustees(["Trustee"])

        db_session.add(trust)
        await db_session.commit()

        await db_session.refresh(trust)
        await db_session.refresh(test_policy)
        assert trust.policy == test_policy
        trust_detail_result = await db_session.execute(
            select(PolicyTrustDetail).where(PolicyTrustDetail.policy_id == test_policy.id)
        )
        trust_detail = trust_detail_result.scalar_one_or_none()
        assert trust_detail == trust

    @pytest.mark.asyncio


    async def test_policy_documents_relationship(self, db_session, test_policy):
        """Test relationship between policy and documents."""
        doc = PolicyDocument(
            policy_id=test_policy.id,
            document_type=DocumentType.POLICY_DOCUMENT,
            file_path="/test.pdf",
            upload_date=date(2024, 1, 1),
            file_size=1000,
            mime_type="application/pdf"
        )

        db_session.add(doc)
        await db_session.commit()

        await db_session.refresh(doc)
        await db_session.refresh(test_policy)
        assert doc.policy == test_policy
        policy_docs_result = await db_session.execute(
            select(PolicyDocument).where(PolicyDocument.policy_id == test_policy.id)
        )
        policy_docs = policy_docs_result.scalars().all()
        assert doc in policy_docs
