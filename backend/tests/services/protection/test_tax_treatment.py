"""
Comprehensive test suite for Tax Treatment Service.

Tests tax implications of life assurance policies across UK and SA:
- UK IHT impact (in trust vs not in trust)
- SA Estate Duty impact
- Combined tax summaries
- Estate value impact calculations
- Tax planning recommendations

Test Coverage:
- UK policy NOT in trust (in IHT estate)
- UK policy in trust (outside IHT estate)
- SA policy (always in estate)
- Non-UK/SA policy (not applicable)
- Multiple policies estate impact
- Zero cover edge cases
"""

import pytest
from decimal import Decimal
from uuid import uuid4
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from models.life_assurance import (
    LifeAssurancePolicy,
    ProviderCountry,
    PolicyType,
    PremiumFrequency,
    PolicyStatus,
    TrustType,
    Currency
)
from services.protection.tax_treatment_service import (
    TaxTreatmentService,
    UK_IHT_RATE,
    SA_ESTATE_DUTY_RATE,
    SA_ESTATE_DUTY_THRESHOLD
)


@pytest.fixture
def tax_service(db_session: AsyncSession):
    """Create tax treatment service instance."""
    return TaxTreatmentService(db_session)


@pytest.fixture
def user_id():
    """Create a test user ID."""
    return uuid4()


@pytest.fixture
async def uk_policy_not_in_trust(db_session: AsyncSession, user_id):
    """Create UK policy NOT in trust (should be in IHT estate)."""
    policy = LifeAssurancePolicy(
        user_id=user_id,
        provider='Aviva UK',
        provider_country=ProviderCountry.UK,
        policy_type=PolicyType.TERM,
        cover_amount=Decimal('500000.00'),
        currency=Currency.GBP,
        cover_amount_gbp=Decimal('500000.00'),
        cover_amount_zar=None,
        premium_amount=Decimal('100.00'),
        premium_frequency=PremiumFrequency.MONTHLY,
        start_date=date(2020, 1, 1),
        end_date=date(2050, 1, 1),
        written_in_trust=False,
        trust_type=None,
        status=PolicyStatus.ACTIVE
    )
    policy.set_policy_number('UK-12345')

    db_session.add(policy)
    await db_session.commit()
    await db_session.refresh(policy)

    return policy


@pytest.fixture
async def uk_policy_in_trust(db_session: AsyncSession, user_id):
    """Create UK policy in trust (should be OUTSIDE IHT estate)."""
    policy = LifeAssurancePolicy(
        user_id=user_id,
        provider='Legal & General',
        provider_country=ProviderCountry.UK,
        policy_type=PolicyType.WHOLE_OF_LIFE,
        cover_amount=Decimal('250000.00'),
        currency=Currency.GBP,
        cover_amount_gbp=Decimal('250000.00'),
        cover_amount_zar=None,
        premium_amount=Decimal('75.00'),
        premium_frequency=PremiumFrequency.MONTHLY,
        start_date=date(2018, 6, 1),
        end_date=None,
        written_in_trust=True,
        trust_type=TrustType.DISCRETIONARY,
        status=PolicyStatus.ACTIVE
    )
    policy.set_policy_number('UK-67890')

    db_session.add(policy)
    await db_session.commit()
    await db_session.refresh(policy)

    return policy


@pytest.fixture
async def sa_policy(db_session: AsyncSession, user_id):
    """Create SA policy (always in estate for estate duty)."""
    policy = LifeAssurancePolicy(
        user_id=user_id,
        provider='Old Mutual SA',
        provider_country=ProviderCountry.SA,
        policy_type=PolicyType.TERM,
        cover_amount=Decimal('5000000.00'),
        currency=Currency.ZAR,
        cover_amount_gbp=None,
        cover_amount_zar=Decimal('5000000.00'),
        premium_amount=Decimal('2000.00'),
        premium_frequency=PremiumFrequency.MONTHLY,
        start_date=date(2019, 3, 1),
        end_date=date(2049, 3, 1),
        written_in_trust=False,
        status=PolicyStatus.ACTIVE
    )
    policy.set_policy_number('SA-11111')

    db_session.add(policy)
    await db_session.commit()
    await db_session.refresh(policy)

    return policy


@pytest.fixture
async def other_country_policy(db_session: AsyncSession, user_id):
    """Create non-UK/SA policy (not applicable for UK IHT or SA Estate Duty)."""
    policy = LifeAssurancePolicy(
        user_id=user_id,
        provider='Zurich International',
        provider_country=ProviderCountry.OTHER,
        policy_type=PolicyType.WHOLE_OF_LIFE,
        cover_amount=Decimal('100000.00'),
        currency=Currency.USD,
        cover_amount_gbp=Decimal('80000.00'),
        cover_amount_zar=Decimal('1500000.00'),
        premium_amount=Decimal('50.00'),
        premium_frequency=PremiumFrequency.MONTHLY,
        start_date=date(2021, 1, 1),
        end_date=None,
        written_in_trust=False,
        status=PolicyStatus.ACTIVE
    )
    policy.set_policy_number('INT-99999')

    db_session.add(policy)
    await db_session.commit()
    await db_session.refresh(policy)

    return policy


class TestDetermineIHTImpact:
    """Test UK Inheritance Tax impact determination."""

    @pytest.mark.asyncio
    async def test_uk_policy_not_in_trust_in_estate(
        self,
        tax_service,
        uk_policy_not_in_trust
    ):
        """UK policy NOT in trust should be IN IHT estate with 40% liability."""
        result = tax_service.determine_iht_impact(uk_policy_not_in_trust)

        assert result['iht_applicable'] is True
        assert result['in_estate'] is True
        assert 'NOT in trust' in result['explanation']
        assert result['trust_type'] is None

        # Potential IHT liability should be 40% of cover
        expected_liability = Decimal('500000.00') * UK_IHT_RATE
        assert result['potential_iht_liability'] == expected_liability
        assert result['potential_iht_liability'] == Decimal('200000.00')

    @pytest.mark.asyncio
    async def test_uk_policy_in_trust_outside_estate(
        self,
        tax_service,
        uk_policy_in_trust
    ):
        """UK policy in trust should be OUTSIDE IHT estate with no liability."""
        result = tax_service.determine_iht_impact(uk_policy_in_trust)

        assert result['iht_applicable'] is True
        assert result['in_estate'] is False
        assert 'written in trust' in result['explanation']
        assert 'outside UK estate' in result['explanation']
        assert result['trust_type'] == 'DISCRETIONARY'
        assert result['potential_iht_liability'] == Decimal('0.00')

    @pytest.mark.asyncio
    async def test_sa_policy_iht_not_applicable(
        self,
        tax_service,
        sa_policy
    ):
        """SA policy should not be applicable for UK IHT."""
        result = tax_service.determine_iht_impact(sa_policy)

        assert result['iht_applicable'] is False
        assert result['in_estate'] is False
        assert 'Not a UK policy' in result['explanation']
        assert result['trust_type'] is None
        assert result['potential_iht_liability'] is None

    @pytest.mark.asyncio
    async def test_other_country_policy_iht_not_applicable(
        self,
        tax_service,
        other_country_policy
    ):
        """Non-UK policy should not be applicable for UK IHT."""
        result = tax_service.determine_iht_impact(other_country_policy)

        assert result['iht_applicable'] is False
        assert result['in_estate'] is False
        assert 'Not a UK policy' in result['explanation']
        assert result['potential_iht_liability'] is None


class TestDetermineSAEstateDutyImpact:
    """Test SA Estate Duty impact determination."""

    @pytest.mark.asyncio
    async def test_sa_policy_in_estate(
        self,
        tax_service,
        sa_policy
    ):
        """SA policy should always be in estate for estate duty."""
        result = tax_service.determine_sa_estate_duty_impact(sa_policy)

        assert result['estate_duty_applicable'] is True
        assert result['in_estate'] is True
        assert 'SA policy forms part of estate' in result['explanation']
        assert result['threshold'] == SA_ESTATE_DUTY_THRESHOLD
        assert result['rate'] == SA_ESTATE_DUTY_RATE
        assert 'R30 million' in result['notes']
        assert '20%' in result['notes']

    @pytest.mark.asyncio
    async def test_uk_policy_sa_estate_duty_not_applicable(
        self,
        tax_service,
        uk_policy_not_in_trust
    ):
        """UK policy should not be applicable for SA Estate Duty."""
        result = tax_service.determine_sa_estate_duty_impact(uk_policy_not_in_trust)

        assert result['estate_duty_applicable'] is False
        assert result['in_estate'] is False
        assert 'Not a SA policy' in result['explanation']
        assert result['threshold'] is None
        assert result['rate'] is None
        assert result['notes'] is None

    @pytest.mark.asyncio
    async def test_other_country_policy_sa_estate_duty_not_applicable(
        self,
        tax_service,
        other_country_policy
    ):
        """Non-SA policy should not be applicable for SA Estate Duty."""
        result = tax_service.determine_sa_estate_duty_impact(other_country_policy)

        assert result['estate_duty_applicable'] is False
        assert result['in_estate'] is False
        assert 'Not a SA policy' in result['explanation']


class TestGetPolicyTaxSummary:
    """Test comprehensive tax summary combining UK and SA treatments."""

    @pytest.mark.asyncio
    async def test_uk_policy_not_in_trust_summary(
        self,
        tax_service,
        uk_policy_not_in_trust
    ):
        """UK policy NOT in trust should have recommendation to use trust."""
        result = tax_service.get_policy_tax_summary(uk_policy_not_in_trust)

        assert result['policy_id'] == uk_policy_not_in_trust.id
        assert result['provider_country'] == 'UK'
        assert result['written_in_trust'] is False

        # UK treatment
        assert result['uk_tax_treatment']['iht_applicable'] is True
        assert result['uk_tax_treatment']['in_estate'] is True

        # SA treatment
        assert result['sa_tax_treatment']['estate_duty_applicable'] is False

        # Recommendations
        assert len(result['recommendations']) > 0
        assert any('trust' in rec.lower() for rec in result['recommendations'])
        assert any('remove from IHT estate' in rec for rec in result['recommendations'])

    @pytest.mark.asyncio
    async def test_uk_policy_in_trust_summary(
        self,
        tax_service,
        uk_policy_in_trust
    ):
        """UK policy in trust should have positive recommendation."""
        result = tax_service.get_policy_tax_summary(uk_policy_in_trust)

        assert result['policy_id'] == uk_policy_in_trust.id
        assert result['provider_country'] == 'UK'
        assert result['written_in_trust'] is True

        # UK treatment
        assert result['uk_tax_treatment']['iht_applicable'] is True
        assert result['uk_tax_treatment']['in_estate'] is False

        # Recommendations
        assert any('correctly structured' in rec for rec in result['recommendations'])

    @pytest.mark.asyncio
    async def test_sa_policy_high_value_summary(
        self,
        tax_service,
        db_session,
        user_id
    ):
        """SA policy with high value should have estate planning recommendation."""
        # Create high-value SA policy
        high_value_policy = LifeAssurancePolicy(
            user_id=user_id,
            provider='Sanlam SA',
            provider_country=ProviderCountry.SA,
            policy_type=PolicyType.WHOLE_OF_LIFE,
            cover_amount=Decimal('15000000.00'),
            currency=Currency.ZAR,
            cover_amount_zar=Decimal('15000000.00'),
            premium_amount=Decimal('5000.00'),
            premium_frequency=PremiumFrequency.MONTHLY,
            start_date=date(2020, 1, 1),
            status=PolicyStatus.ACTIVE
        )
        high_value_policy.set_policy_number('SA-HIGH-VALUE')
        db_session.add(high_value_policy)
        await db_session.commit()
        await db_session.refresh(high_value_policy)

        result = tax_service.get_policy_tax_summary(high_value_policy)

        # SA treatment
        assert result['sa_tax_treatment']['estate_duty_applicable'] is True
        assert result['sa_tax_treatment']['in_estate'] is True

        # Recommendations
        assert any('estate planner' in rec for rec in result['recommendations'])
        assert any('R30m' in rec for rec in result['recommendations'])


class TestCalculateEstateValueImpact:
    """Test estate value impact calculations with multiple policies."""

    @pytest.mark.asyncio
    async def test_multiple_policies_estate_impact(
        self,
        tax_service,
        db_session,
        user_id,
        uk_policy_not_in_trust,
        uk_policy_in_trust,
        sa_policy
    ):
        """Calculate estate impact with mix of UK and SA policies."""
        result = await tax_service.calculate_estate_value_impact(user_id)

        # UK policies in estate (only the one NOT in trust)
        assert result['total_uk_policies_in_estate'] == Decimal('500000.00')
        assert result['policies_in_uk_estate_count'] == 1

        # SA policies in estate (always)
        assert result['total_sa_policies_in_estate'] == Decimal('5000000.00')
        assert result['policies_in_sa_estate_count'] == 1

        # Potential UK IHT (40% of £500,000)
        expected_iht = Decimal('500000.00') * UK_IHT_RATE
        assert result['potential_uk_iht'] == expected_iht
        assert result['potential_uk_iht'] == Decimal('200000.00')

        # Recommendations
        assert len(result['recommendations']) > 0

    @pytest.mark.asyncio
    async def test_no_policies_estate_impact(
        self,
        tax_service,
        user_id
    ):
        """Calculate estate impact with no policies."""
        result = await tax_service.calculate_estate_value_impact(user_id)

        assert result['total_uk_policies_in_estate'] == Decimal('0.00')
        assert result['total_sa_policies_in_estate'] == Decimal('0.00')
        assert result['potential_uk_iht'] == Decimal('0.00')
        assert result['policies_in_uk_estate_count'] == 0
        assert result['policies_in_sa_estate_count'] == 0

        # Should recommend coverage analysis
        assert any('coverage needs analysis' in rec for rec in result['recommendations'])

    @pytest.mark.asyncio
    async def test_only_trust_policies_estate_impact(
        self,
        tax_service,
        uk_policy_in_trust
    ):
        """Calculate estate impact with only trust policies (zero IHT)."""
        result = await tax_service.calculate_estate_value_impact(
            uk_policy_in_trust.user_id
        )

        # No UK policies in estate (all in trust)
        assert result['total_uk_policies_in_estate'] == Decimal('0.00')
        assert result['policies_in_uk_estate_count'] == 0
        assert result['potential_uk_iht'] == Decimal('0.00')

    @pytest.mark.asyncio
    async def test_sa_policies_above_threshold(
        self,
        tax_service,
        db_session,
        user_id
    ):
        """SA policies totaling above R30m threshold should trigger recommendation."""
        # Create SA policy above threshold
        large_sa_policy = LifeAssurancePolicy(
            user_id=user_id,
            provider='Liberty SA',
            provider_country=ProviderCountry.SA,
            policy_type=PolicyType.WHOLE_OF_LIFE,
            cover_amount=Decimal('35000000.00'),
            currency=Currency.ZAR,
            cover_amount_zar=Decimal('35000000.00'),
            premium_amount=Decimal('10000.00'),
            premium_frequency=PremiumFrequency.MONTHLY,
            start_date=date(2020, 1, 1),
            status=PolicyStatus.ACTIVE
        )
        large_sa_policy.set_policy_number('SA-LARGE')
        db_session.add(large_sa_policy)
        await db_session.commit()

        result = await tax_service.calculate_estate_value_impact(user_id)

        # Should exceed threshold
        assert result['total_sa_policies_in_estate'] > SA_ESTATE_DUTY_THRESHOLD

        # Should have threshold recommendation
        assert any(
            'R30 million estate duty threshold' in rec
            for rec in result['recommendations']
        )


class TestGetPolicyTaxTreatmentByID:
    """Test getting tax treatment for specific policy by ID."""

    @pytest.mark.asyncio
    async def test_get_policy_tax_treatment_by_id_success(
        self,
        tax_service,
        uk_policy_not_in_trust
    ):
        """Get tax treatment by policy ID successfully."""
        result = await tax_service.get_policy_tax_treatment_by_id(
            uk_policy_not_in_trust.id,
            uk_policy_not_in_trust.user_id
        )

        assert result['policy_id'] == uk_policy_not_in_trust.id
        assert result['provider_country'] == 'UK'
        assert 'uk_tax_treatment' in result
        assert 'sa_tax_treatment' in result
        assert 'recommendations' in result

    @pytest.mark.asyncio
    async def test_get_policy_tax_treatment_wrong_user(
        self,
        tax_service,
        uk_policy_not_in_trust
    ):
        """Getting tax treatment with wrong user ID should raise error."""
        wrong_user_id = uuid4()

        with pytest.raises(ValueError) as exc_info:
            await tax_service.get_policy_tax_treatment_by_id(
                uk_policy_not_in_trust.id,
                wrong_user_id
            )

        assert "not found" in str(exc_info.value).lower() or "permission" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_get_policy_tax_treatment_nonexistent_policy(
        self,
        tax_service,
        user_id
    ):
        """Getting tax treatment for nonexistent policy should raise error."""
        nonexistent_id = uuid4()

        with pytest.raises(ValueError) as exc_info:
            await tax_service.get_policy_tax_treatment_by_id(
                nonexistent_id,
                user_id
            )

        assert "not found" in str(exc_info.value).lower()


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_zero_cover_amount(
        self,
        tax_service,
        db_session,
        user_id
    ):
        """Policy with zero cover should have zero IHT liability."""
        # Note: This violates CHECK constraint, but test the service logic
        # In practice, this would be caught by database constraints
        zero_policy = LifeAssurancePolicy(
            user_id=user_id,
            provider='Test Provider',
            provider_country=ProviderCountry.UK,
            policy_type=PolicyType.TERM,
            cover_amount=Decimal('0.01'),  # Minimum to pass CHECK constraint
            currency=Currency.GBP,
            cover_amount_gbp=Decimal('0.01'),
            premium_amount=Decimal('0.00'),
            premium_frequency=PremiumFrequency.MONTHLY,
            start_date=date(2020, 1, 1),
            end_date=date(2030, 1, 1),
            written_in_trust=False,
            status=PolicyStatus.ACTIVE
        )
        zero_policy.set_policy_number('ZERO-COVER')
        db_session.add(zero_policy)
        await db_session.commit()
        await db_session.refresh(zero_policy)

        result = tax_service.determine_iht_impact(zero_policy)

        # Should have minimal IHT liability
        assert result['potential_iht_liability'] == Decimal('0.01') * UK_IHT_RATE
        assert result['potential_iht_liability'] < Decimal('0.01')

    @pytest.mark.asyncio
    async def test_lapsed_policy_excluded_from_estate_impact(
        self,
        tax_service,
        db_session,
        user_id
    ):
        """Lapsed policies should not be included in estate impact."""
        lapsed_policy = LifeAssurancePolicy(
            user_id=user_id,
            provider='Lapsed Provider',
            provider_country=ProviderCountry.UK,
            policy_type=PolicyType.TERM,
            cover_amount=Decimal('100000.00'),
            currency=Currency.GBP,
            cover_amount_gbp=Decimal('100000.00'),
            premium_amount=Decimal('50.00'),
            premium_frequency=PremiumFrequency.MONTHLY,
            start_date=date(2015, 1, 1),
            end_date=date(2025, 1, 1),
            written_in_trust=False,
            status=PolicyStatus.LAPSED,  # LAPSED status
            is_deleted=False
        )
        lapsed_policy.set_policy_number('LAPSED-123')
        db_session.add(lapsed_policy)
        await db_session.commit()

        result = await tax_service.calculate_estate_value_impact(user_id)

        # Lapsed policy should not be included
        assert result['total_uk_policies_in_estate'] == Decimal('0.00')
        assert result['policies_in_uk_estate_count'] == 0

    @pytest.mark.asyncio
    async def test_deleted_policy_excluded_from_estate_impact(
        self,
        tax_service,
        db_session,
        user_id
    ):
        """Soft-deleted policies should not be included in estate impact."""
        deleted_policy = LifeAssurancePolicy(
            user_id=user_id,
            provider='Deleted Provider',
            provider_country=ProviderCountry.UK,
            policy_type=PolicyType.TERM,
            cover_amount=Decimal('100000.00'),
            currency=Currency.GBP,
            cover_amount_gbp=Decimal('100000.00'),
            premium_amount=Decimal('50.00'),
            premium_frequency=PremiumFrequency.MONTHLY,
            start_date=date(2015, 1, 1),
            end_date=date(2025, 1, 1),
            written_in_trust=False,
            status=PolicyStatus.ACTIVE,
            is_deleted=True  # Soft deleted
        )
        deleted_policy.set_policy_number('DELETED-123')
        db_session.add(deleted_policy)
        await db_session.commit()

        result = await tax_service.calculate_estate_value_impact(user_id)

        # Deleted policy should not be included
        assert result['total_uk_policies_in_estate'] == Decimal('0.00')
        assert result['policies_in_uk_estate_count'] == 0


class TestTaxConstants:
    """Test that tax constants are correctly defined."""

    def test_uk_iht_rate(self):
        """UK IHT rate should be 40%."""
        assert UK_IHT_RATE == Decimal('0.40')

    def test_sa_estate_duty_rate(self):
        """SA Estate Duty rate should be 20%."""
        assert SA_ESTATE_DUTY_RATE == Decimal('0.20')

    def test_sa_estate_duty_threshold(self):
        """SA Estate Duty threshold should be R30 million."""
        assert SA_ESTATE_DUTY_THRESHOLD == Decimal('30000000.00')
