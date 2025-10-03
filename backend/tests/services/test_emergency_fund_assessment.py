"""
Tests for Emergency Fund Assessment Service

Tests comprehensive emergency fund assessment logic including:
- Recommended amount calculation
- Current emergency fund calculation
- Status determination
- Recommendation generation
- Multi-currency support
- Edge cases
"""

import pytest
from decimal import Decimal
from datetime import datetime, date
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from services.emergency_fund_assessment import EmergencyFundAssessmentService
from models.savings_account import (
    SavingsAccount, AccountType, AccountPurpose,
    AccountCountry, Currency, InterestFrequency
)
from models.income import UserIncome, IncomeType, IncomeFrequency
from models.user import User


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    from models.user import UserStatus, CountryPreference
    from datetime import datetime

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
def assessment_service(db_session: AsyncSession) -> EmergencyFundAssessmentService:
    """Create assessment service instance."""
    return EmergencyFundAssessmentService(db_session)


class TestCalculateRecommendedEmergencyFund:
    """Test recommended emergency fund calculation."""

    def test_standard_calculation(self, assessment_service):
        """Test standard 6 months calculation."""
        monthly_expenses = Decimal('2000.00')
        recommended = assessment_service.calculate_recommended_emergency_fund(monthly_expenses)

        assert recommended == Decimal('12000.00')

    def test_zero_expenses(self, assessment_service):
        """Test with zero monthly expenses."""
        monthly_expenses = Decimal('0.00')
        recommended = assessment_service.calculate_recommended_emergency_fund(monthly_expenses)

        assert recommended == Decimal('0.00')

    def test_high_expenses(self, assessment_service):
        """Test with high monthly expenses."""
        monthly_expenses = Decimal('10000.00')
        recommended = assessment_service.calculate_recommended_emergency_fund(monthly_expenses)

        assert recommended == Decimal('60000.00')


class TestGetCurrentEmergencyFund:
    """Test current emergency fund calculation."""

    async def test_no_emergency_fund_accounts(
        self,
        db_session: AsyncSession,
        test_user: User,
        assessment_service: EmergencyFundAssessmentService
    ):
        """Test with no emergency fund accounts."""
        current = await assessment_service.get_current_emergency_fund(
            test_user.id,
            base_currency="GBP"
        )

        assert current == Decimal('0.00')

    async def test_single_emergency_fund_account(
        self,
        db_session: AsyncSession,
        test_user: User,
        assessment_service: EmergencyFundAssessmentService
    ):
        """Test with single emergency fund account."""
        # Create emergency fund account
        account = SavingsAccount(
            id=uuid4(),
            user_id=test_user.id,
            bank_name="Test Bank",
            account_name="Emergency Fund",
            account_number_encrypted="encrypted_1234",
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=Decimal('10000.00'),
            purpose=AccountPurpose.EMERGENCY_FUND,
            country=AccountCountry.UK,
            is_active=True
        )
        db_session.add(account)
        await db_session.commit()

        current = await assessment_service.get_current_emergency_fund(
            test_user.id,
            base_currency="GBP"
        )

        assert current == Decimal('10000.00')

    async def test_multiple_emergency_fund_accounts(
        self,
        db_session: AsyncSession,
        test_user: User,
        assessment_service: EmergencyFundAssessmentService
    ):
        """Test with multiple emergency fund accounts."""
        # Create two emergency fund accounts
        account1 = SavingsAccount(
            id=uuid4(),
            user_id=test_user.id,
            bank_name="Test Bank 1",
            account_name="Emergency Fund 1",
            account_number_encrypted="encrypted_1234",
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=Decimal('5000.00'),
            purpose=AccountPurpose.EMERGENCY_FUND,
            country=AccountCountry.UK,
            is_active=True
        )
        account2 = SavingsAccount(
            id=uuid4(),
            user_id=test_user.id,
            bank_name="Test Bank 2",
            account_name="Emergency Fund 2",
            account_number_encrypted="encrypted_5678",
            account_type=AccountType.CURRENT,
            currency=Currency.GBP,
            current_balance=Decimal('7000.00'),
            purpose=AccountPurpose.EMERGENCY_FUND,
            country=AccountCountry.UK,
            is_active=True
        )
        db_session.add_all([account1, account2])
        await db_session.commit()

        current = await assessment_service.get_current_emergency_fund(
            test_user.id,
            base_currency="GBP"
        )

        assert current == Decimal('12000.00')

    async def test_excludes_inactive_accounts(
        self,
        db_session: AsyncSession,
        test_user: User,
        assessment_service: EmergencyFundAssessmentService
    ):
        """Test that inactive accounts are excluded."""
        # Create active account
        active_account = SavingsAccount(
            id=uuid4(),
            user_id=test_user.id,
            bank_name="Test Bank Active",
            account_name="Emergency Fund Active",
            account_number_encrypted="encrypted_1234",
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=Decimal('5000.00'),
            purpose=AccountPurpose.EMERGENCY_FUND,
            country=AccountCountry.UK,
            is_active=True
        )
        # Create inactive account
        inactive_account = SavingsAccount(
            id=uuid4(),
            user_id=test_user.id,
            bank_name="Test Bank Inactive",
            account_name="Emergency Fund Inactive",
            account_number_encrypted="encrypted_5678",
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=Decimal('10000.00'),
            purpose=AccountPurpose.EMERGENCY_FUND,
            country=AccountCountry.UK,
            is_active=False
        )
        db_session.add_all([active_account, inactive_account])
        await db_session.commit()

        current = await assessment_service.get_current_emergency_fund(
            test_user.id,
            base_currency="GBP"
        )

        assert current == Decimal('5000.00')

    async def test_excludes_deleted_accounts(
        self,
        db_session: AsyncSession,
        test_user: User,
        assessment_service: EmergencyFundAssessmentService
    ):
        """Test that soft-deleted accounts are excluded."""
        # Create active account
        active_account = SavingsAccount(
            id=uuid4(),
            user_id=test_user.id,
            bank_name="Test Bank Active",
            account_name="Emergency Fund Active",
            account_number_encrypted="encrypted_1234",
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=Decimal('5000.00'),
            purpose=AccountPurpose.EMERGENCY_FUND,
            country=AccountCountry.UK,
            is_active=True
        )
        # Create deleted account
        deleted_account = SavingsAccount(
            id=uuid4(),
            user_id=test_user.id,
            bank_name="Test Bank Deleted",
            account_name="Emergency Fund Deleted",
            account_number_encrypted="encrypted_5678",
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=Decimal('10000.00'),
            purpose=AccountPurpose.EMERGENCY_FUND,
            country=AccountCountry.UK,
            is_active=True,
            deleted_at=datetime.utcnow()
        )
        db_session.add_all([active_account, deleted_account])
        await db_session.commit()

        current = await assessment_service.get_current_emergency_fund(
            test_user.id,
            base_currency="GBP"
        )

        assert current == Decimal('5000.00')

    async def test_excludes_non_emergency_accounts(
        self,
        db_session: AsyncSession,
        test_user: User,
        assessment_service: EmergencyFundAssessmentService
    ):
        """Test that non-emergency fund accounts are excluded."""
        # Create emergency fund account
        emergency_account = SavingsAccount(
            id=uuid4(),
            user_id=test_user.id,
            bank_name="Test Bank Emergency",
            account_name="Emergency Fund",
            account_number_encrypted="encrypted_1234",
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=Decimal('5000.00'),
            purpose=AccountPurpose.EMERGENCY_FUND,
            country=AccountCountry.UK,
            is_active=True
        )
        # Create general savings account
        general_account = SavingsAccount(
            id=uuid4(),
            user_id=test_user.id,
            bank_name="Test Bank General",
            account_name="General Savings",
            account_number_encrypted="encrypted_5678",
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=Decimal('10000.00'),
            purpose=AccountPurpose.GENERAL,
            country=AccountCountry.UK,
            is_active=True
        )
        db_session.add_all([emergency_account, general_account])
        await db_session.commit()

        current = await assessment_service.get_current_emergency_fund(
            test_user.id,
            base_currency="GBP"
        )

        assert current == Decimal('5000.00')


class TestStatusDetermination:
    """Test emergency fund status determination."""

    async def test_status_adequate(
        self,
        db_session: AsyncSession,
        test_user: User,
        assessment_service: EmergencyFundAssessmentService
    ):
        """Test ADEQUATE status (current >= recommended)."""
        # Create emergency fund with 6+ months
        account = SavingsAccount(
            id=uuid4(),
            user_id=test_user.id,
            bank_name="Test Bank",
            account_name="Emergency Fund",
            account_number_encrypted="encrypted_1234",
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=Decimal('15000.00'),  # 7.5 months
            purpose=AccountPurpose.EMERGENCY_FUND,
            country=AccountCountry.UK,
            is_active=True
        )
        db_session.add(account)
        await db_session.commit()

        monthly_expenses = Decimal('2000.00')
        assessment = await assessment_service.assess_emergency_fund(
            test_user.id,
            monthly_expenses,
            base_currency="GBP"
        )

        assert assessment["status"] == "ADEQUATE"
        assert assessment["ratio"] >= 1.0
        assert assessment["months_covered"] == 7.5

    async def test_status_insufficient(
        self,
        db_session: AsyncSession,
        test_user: User,
        assessment_service: EmergencyFundAssessmentService
    ):
        """Test INSUFFICIENT status (0 < current < recommended)."""
        # Create emergency fund with 5 months
        account = SavingsAccount(
            id=uuid4(),
            user_id=test_user.id,
            bank_name="Test Bank",
            account_name="Emergency Fund",
            account_number_encrypted="encrypted_1234",
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=Decimal('10000.00'),  # 5 months
            purpose=AccountPurpose.EMERGENCY_FUND,
            country=AccountCountry.UK,
            is_active=True
        )
        db_session.add(account)
        await db_session.commit()

        monthly_expenses = Decimal('2000.00')
        assessment = await assessment_service.assess_emergency_fund(
            test_user.id,
            monthly_expenses,
            base_currency="GBP"
        )

        assert assessment["status"] == "INSUFFICIENT"
        assert 0 < assessment["ratio"] < 1.0
        assert assessment["months_covered"] == 5.0

    async def test_status_none(
        self,
        db_session: AsyncSession,
        test_user: User,
        assessment_service: EmergencyFundAssessmentService
    ):
        """Test NONE status (no emergency fund)."""
        # No emergency fund accounts created
        monthly_expenses = Decimal('2000.00')
        assessment = await assessment_service.assess_emergency_fund(
            test_user.id,
            monthly_expenses,
            base_currency="GBP"
        )

        assert assessment["status"] == "NONE"
        assert assessment["ratio"] == 0.0
        assert assessment["months_covered"] == 0.0


class TestRecommendations:
    """Test recommendation generation."""

    async def test_recommendations_adequate(
        self,
        db_session: AsyncSession,
        test_user: User,
        assessment_service: EmergencyFundAssessmentService
    ):
        """Test recommendations for ADEQUATE status."""
        # Create adequate emergency fund
        account = SavingsAccount(
            id=uuid4(),
            user_id=test_user.id,
            bank_name="Test Bank",
            account_name="Emergency Fund",
            account_number_encrypted="encrypted_1234",
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=Decimal('12000.00'),
            purpose=AccountPurpose.EMERGENCY_FUND,
            country=AccountCountry.UK,
            is_active=True
        )
        db_session.add(account)
        await db_session.commit()

        monthly_expenses = Decimal('2000.00')
        assessment = await assessment_service.assess_emergency_fund(
            test_user.id,
            monthly_expenses,
            base_currency="GBP"
        )

        recommendations = assessment["recommendations"]
        assert len(recommendations) == 2
        assert "Great job!" in recommendations[0]
        assert "Review your fund annually" in recommendations[1]

    async def test_recommendations_insufficient(
        self,
        db_session: AsyncSession,
        test_user: User,
        assessment_service: EmergencyFundAssessmentService
    ):
        """Test recommendations for INSUFFICIENT status."""
        # Create insufficient emergency fund
        account = SavingsAccount(
            id=uuid4(),
            user_id=test_user.id,
            bank_name="Test Bank",
            account_name="Emergency Fund",
            account_number_encrypted="encrypted_1234",
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=Decimal('8000.00'),
            purpose=AccountPurpose.EMERGENCY_FUND,
            country=AccountCountry.UK,
            is_active=True
        )
        db_session.add(account)
        await db_session.commit()

        monthly_expenses = Decimal('2000.00')
        assessment = await assessment_service.assess_emergency_fund(
            test_user.id,
            monthly_expenses,
            base_currency="GBP"
        )

        recommendations = assessment["recommendations"]
        assert len(recommendations) == 3
        assert "months covered" in recommendations[0]
        assert "automatic transfers" in recommendations[1]
        assert "instant-access" in recommendations[2]

    async def test_recommendations_none(
        self,
        db_session: AsyncSession,
        test_user: User,
        assessment_service: EmergencyFundAssessmentService
    ):
        """Test recommendations for NONE status."""
        monthly_expenses = Decimal('2000.00')
        assessment = await assessment_service.assess_emergency_fund(
            test_user.id,
            monthly_expenses,
            base_currency="GBP"
        )

        recommendations = assessment["recommendations"]
        assert len(recommendations) == 4
        assert "500" in recommendations[0] or "1,000" in recommendations[0]
        assert "Gradually build up" in recommendations[1]
        assert "Mark a savings account" in recommendations[2]
        assert "Keep emergency funds separate" in recommendations[3]


class TestAssessmentMetrics:
    """Test assessment metric calculations."""

    async def test_months_covered_calculation(
        self,
        db_session: AsyncSession,
        test_user: User,
        assessment_service: EmergencyFundAssessmentService
    ):
        """Test months covered calculation."""
        # Create emergency fund
        account = SavingsAccount(
            id=uuid4(),
            user_id=test_user.id,
            bank_name="Test Bank",
            account_name="Emergency Fund",
            account_number_encrypted="encrypted_1234",
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=Decimal('9000.00'),
            purpose=AccountPurpose.EMERGENCY_FUND,
            country=AccountCountry.UK,
            is_active=True
        )
        db_session.add(account)
        await db_session.commit()

        monthly_expenses = Decimal('2000.00')
        assessment = await assessment_service.assess_emergency_fund(
            test_user.id,
            monthly_expenses,
            base_currency="GBP"
        )

        assert assessment["months_covered"] == 4.5
        assert assessment["current_emergency_fund"] == 9000.00
        assert assessment["recommended_emergency_fund"] == 12000.00

    async def test_ratio_calculation(
        self,
        db_session: AsyncSession,
        test_user: User,
        assessment_service: EmergencyFundAssessmentService
    ):
        """Test ratio calculation."""
        # Create emergency fund at 83.33% of recommended
        account = SavingsAccount(
            id=uuid4(),
            user_id=test_user.id,
            bank_name="Test Bank",
            account_name="Emergency Fund",
            account_number_encrypted="encrypted_1234",
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=Decimal('10000.00'),
            purpose=AccountPurpose.EMERGENCY_FUND,
            country=AccountCountry.UK,
            is_active=True
        )
        db_session.add(account)
        await db_session.commit()

        monthly_expenses = Decimal('2000.00')
        assessment = await assessment_service.assess_emergency_fund(
            test_user.id,
            monthly_expenses,
            base_currency="GBP"
        )

        # 10000 / 12000 = 0.8333...
        assert 0.83 <= assessment["ratio"] <= 0.84


class TestEdgeCases:
    """Test edge cases and error handling."""

    async def test_zero_monthly_expenses(
        self,
        db_session: AsyncSession,
        test_user: User,
        assessment_service: EmergencyFundAssessmentService
    ):
        """Test with zero monthly expenses."""
        monthly_expenses = Decimal('0.00')
        assessment = await assessment_service.assess_emergency_fund(
            test_user.id,
            monthly_expenses,
            base_currency="GBP"
        )

        assert assessment["recommended_emergency_fund"] == 0.00
        assert assessment["months_covered"] == 0.00

    async def test_negative_monthly_expenses(
        self,
        db_session: AsyncSession,
        test_user: User,
        assessment_service: EmergencyFundAssessmentService
    ):
        """Test with negative monthly expenses raises error."""
        monthly_expenses = Decimal('-1000.00')

        with pytest.raises(ValueError, match="Monthly expenses cannot be negative"):
            await assessment_service.assess_emergency_fund(
                test_user.id,
                monthly_expenses,
                base_currency="GBP"
            )

    async def test_very_high_monthly_expenses(
        self,
        db_session: AsyncSession,
        test_user: User,
        assessment_service: EmergencyFundAssessmentService
    ):
        """Test with very high monthly expenses."""
        # Create emergency fund
        account = SavingsAccount(
            id=uuid4(),
            user_id=test_user.id,
            bank_name="Test Bank",
            account_name="Emergency Fund",
            account_number_encrypted="encrypted_1234",
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=Decimal('100000.00'),
            purpose=AccountPurpose.EMERGENCY_FUND,
            country=AccountCountry.UK,
            is_active=True
        )
        db_session.add(account)
        await db_session.commit()

        monthly_expenses = Decimal('50000.00')
        assessment = await assessment_service.assess_emergency_fund(
            test_user.id,
            monthly_expenses,
            base_currency="GBP"
        )

        assert assessment["recommended_emergency_fund"] == 300000.00
        assert assessment["status"] == "INSUFFICIENT"


class TestGetEmergencyFundAccounts:
    """Test getting emergency fund accounts."""

    async def test_get_accounts(
        self,
        db_session: AsyncSession,
        test_user: User,
        assessment_service: EmergencyFundAssessmentService
    ):
        """Test getting all emergency fund accounts."""
        # Create multiple accounts
        account1 = SavingsAccount(
            id=uuid4(),
            user_id=test_user.id,
            bank_name="Test Bank 1",
            account_name="Emergency Fund 1",
            account_number_encrypted="encrypted_1234",
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=Decimal('5000.00'),
            purpose=AccountPurpose.EMERGENCY_FUND,
            country=AccountCountry.UK,
            is_active=True
        )
        account2 = SavingsAccount(
            id=uuid4(),
            user_id=test_user.id,
            bank_name="Test Bank 2",
            account_name="Emergency Fund 2",
            account_number_encrypted="encrypted_5678",
            account_type=AccountType.CURRENT,
            currency=Currency.GBP,
            current_balance=Decimal('7000.00'),
            purpose=AccountPurpose.EMERGENCY_FUND,
            country=AccountCountry.UK,
            is_active=True
        )
        db_session.add_all([account1, account2])
        await db_session.commit()

        accounts = await assessment_service.get_emergency_fund_accounts(test_user.id)

        assert len(accounts) == 2
        assert all(acc.purpose == AccountPurpose.EMERGENCY_FUND for acc in accounts)
