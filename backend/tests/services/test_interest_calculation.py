"""
Tests for Interest Calculation Service.

Comprehensive test suite covering:
- Simple interest calculations
- Compound interest (monthly, quarterly, annually)
- Effective Annual Rate (EAR) calculations
- Annual interest projections
- Period interest calculations
- Edge cases and validation
"""

import pytest
from datetime import date
from decimal import Decimal

from services.interest_calculation import InterestCalculationService
from models.savings_account import SavingsAccount, InterestFrequency, AccountType, Currency, AccountCountry


class TestSimpleInterest:
    """Test suite for simple interest calculations."""

    def test_simple_interest_one_year(self):
        """Test simple interest for one full year."""
        # £10,000 at 5% for 365 days = £500
        interest = InterestCalculationService.calculate_simple_interest(
            principal=Decimal('10000.00'),
            annual_rate=Decimal('0.05'),
            days=365
        )
        assert interest == Decimal('500.00')

    def test_simple_interest_half_year(self):
        """Test simple interest for half a year."""
        # £10,000 at 5% for 182.5 days ≈ £250
        interest = InterestCalculationService.calculate_simple_interest(
            principal=Decimal('10000.00'),
            annual_rate=Decimal('0.05'),
            days=182
        )
        # 10000 × 0.05 × (182/365) = 249.32
        assert interest == Decimal('249.32')

    def test_simple_interest_one_month(self):
        """Test simple interest for approximately one month."""
        # £10,000 at 5% for 30 days
        interest = InterestCalculationService.calculate_simple_interest(
            principal=Decimal('10000.00'),
            annual_rate=Decimal('0.05'),
            days=30
        )
        # 10000 × 0.05 × (30/365) = 41.10
        assert interest == Decimal('41.10')

    def test_simple_interest_different_rates(self):
        """Test simple interest with various interest rates."""
        # 0.5% rate
        interest = InterestCalculationService.calculate_simple_interest(
            principal=Decimal('10000.00'),
            annual_rate=Decimal('0.005'),
            days=365
        )
        assert interest == Decimal('50.00')

        # 10% rate
        interest = InterestCalculationService.calculate_simple_interest(
            principal=Decimal('10000.00'),
            annual_rate=Decimal('0.10'),
            days=365
        )
        assert interest == Decimal('1000.00')

    def test_simple_interest_zero_principal(self):
        """Test simple interest with zero principal."""
        interest = InterestCalculationService.calculate_simple_interest(
            principal=Decimal('0.00'),
            annual_rate=Decimal('0.05'),
            days=365
        )
        assert interest == Decimal('0.00')

    def test_simple_interest_zero_rate(self):
        """Test simple interest with zero rate."""
        interest = InterestCalculationService.calculate_simple_interest(
            principal=Decimal('10000.00'),
            annual_rate=Decimal('0.00'),
            days=365
        )
        assert interest == Decimal('0.00')

    def test_simple_interest_zero_days(self):
        """Test simple interest with zero days."""
        interest = InterestCalculationService.calculate_simple_interest(
            principal=Decimal('10000.00'),
            annual_rate=Decimal('0.05'),
            days=0
        )
        assert interest == Decimal('0.00')

    def test_simple_interest_one_day(self):
        """Test simple interest for one day."""
        # £10,000 at 5% for 1 day
        interest = InterestCalculationService.calculate_simple_interest(
            principal=Decimal('10000.00'),
            annual_rate=Decimal('0.05'),
            days=1
        )
        # 10000 × 0.05 × (1/365) = 1.37
        assert interest == Decimal('1.37')

    def test_simple_interest_negative_principal_raises_error(self):
        """Test that negative principal raises ValueError."""
        with pytest.raises(ValueError, match="Principal cannot be negative"):
            InterestCalculationService.calculate_simple_interest(
                principal=Decimal('-1000.00'),
                annual_rate=Decimal('0.05'),
                days=365
            )

    def test_simple_interest_negative_rate_raises_error(self):
        """Test that negative rate raises ValueError."""
        with pytest.raises(ValueError, match="Interest rate cannot be negative"):
            InterestCalculationService.calculate_simple_interest(
                principal=Decimal('10000.00'),
                annual_rate=Decimal('-0.05'),
                days=365
            )

    def test_simple_interest_negative_days_raises_error(self):
        """Test that negative days raises ValueError."""
        with pytest.raises(ValueError, match="Days cannot be negative"):
            InterestCalculationService.calculate_simple_interest(
                principal=Decimal('10000.00'),
                annual_rate=Decimal('0.05'),
                days=-1
            )


class TestCompoundInterest:
    """Test suite for compound interest calculations."""

    def test_compound_interest_monthly_one_year(self):
        """Test compound interest with monthly compounding for one year."""
        # £10,000 at 5% compounded monthly for 365 days
        result = InterestCalculationService.calculate_compound_interest(
            principal=Decimal('10000.00'),
            annual_rate=Decimal('0.05'),
            frequency='MONTHLY',
            days=365
        )

        # FV = 10000 × (1 + 0.05/12)^12 = 10511.62
        # Interest = 511.62
        assert result['interest'] == Decimal('511.62')
        assert result['future_value'] == Decimal('10511.62')
        # EAR should be approximately 5.12%
        assert Decimal('5.11') <= result['effective_rate'] <= Decimal('5.13')

    def test_compound_interest_quarterly_one_year(self):
        """Test compound interest with quarterly compounding for one year."""
        # £10,000 at 5% compounded quarterly for 365 days
        result = InterestCalculationService.calculate_compound_interest(
            principal=Decimal('10000.00'),
            annual_rate=Decimal('0.05'),
            frequency='QUARTERLY',
            days=365
        )

        # FV = 10000 × (1 + 0.05/4)^4 = 10509.45
        # Interest = 509.45
        assert result['interest'] == Decimal('509.45')
        assert result['future_value'] == Decimal('10509.45')
        # EAR should be approximately 5.09%
        assert Decimal('5.08') <= result['effective_rate'] <= Decimal('5.10')

    def test_compound_interest_annually_one_year(self):
        """Test compound interest with annual compounding for one year."""
        # £10,000 at 5% compounded annually for 365 days
        result = InterestCalculationService.calculate_compound_interest(
            principal=Decimal('10000.00'),
            annual_rate=Decimal('0.05'),
            frequency='ANNUALLY',
            days=365
        )

        # FV = 10000 × (1 + 0.05)^1 = 10500.00
        # Interest = 500.00
        assert result['interest'] == Decimal('500.00')
        assert result['future_value'] == Decimal('10500.00')
        # EAR equals nominal rate for annual compounding
        assert result['effective_rate'] == Decimal('5.00')

    def test_compound_interest_monthly_half_year(self):
        """Test compound interest with monthly compounding for half year."""
        # £10,000 at 5% compounded monthly for 182 days
        result = InterestCalculationService.calculate_compound_interest(
            principal=Decimal('10000.00'),
            annual_rate=Decimal('0.05'),
            frequency='MONTHLY',
            days=182
        )

        # FV = 10000 × (1 + 0.05/12)^(12 × 182/365)
        # Approximately £10,251.92
        assert Decimal('251.00') <= result['interest'] <= Decimal('253.00')
        assert Decimal('10251.00') <= result['future_value'] <= Decimal('10253.00')

    def test_compound_interest_different_rates(self):
        """Test compound interest with various rates."""
        # 0.5% rate
        result = InterestCalculationService.calculate_compound_interest(
            principal=Decimal('10000.00'),
            annual_rate=Decimal('0.005'),
            frequency='MONTHLY',
            days=365
        )
        assert Decimal('50.00') <= result['interest'] <= Decimal('51.00')

        # 10% rate
        result = InterestCalculationService.calculate_compound_interest(
            principal=Decimal('10000.00'),
            annual_rate=Decimal('0.10'),
            frequency='MONTHLY',
            days=365
        )
        # FV = 10000 × (1 + 0.10/12)^12 ≈ 11047.13
        assert Decimal('1045.00') <= result['interest'] <= Decimal('1050.00')

    def test_compound_interest_zero_principal(self):
        """Test compound interest with zero principal."""
        result = InterestCalculationService.calculate_compound_interest(
            principal=Decimal('0.00'),
            annual_rate=Decimal('0.05'),
            frequency='MONTHLY',
            days=365
        )
        assert result['interest'] == Decimal('0.00')
        assert result['future_value'] == Decimal('0.00')
        assert result['effective_rate'] == Decimal('0.00')

    def test_compound_interest_zero_rate(self):
        """Test compound interest with zero rate."""
        result = InterestCalculationService.calculate_compound_interest(
            principal=Decimal('10000.00'),
            annual_rate=Decimal('0.00'),
            frequency='MONTHLY',
            days=365
        )
        assert result['interest'] == Decimal('0.00')
        assert result['future_value'] == Decimal('10000.00')
        assert result['effective_rate'] == Decimal('0.00')

    def test_compound_interest_zero_days(self):
        """Test compound interest with zero days."""
        result = InterestCalculationService.calculate_compound_interest(
            principal=Decimal('10000.00'),
            annual_rate=Decimal('0.05'),
            frequency='MONTHLY',
            days=0
        )
        assert result['interest'] == Decimal('0.00')
        assert result['future_value'] == Decimal('10000.00')
        assert result['effective_rate'] == Decimal('0.00')

    def test_compound_interest_one_day(self):
        """Test compound interest for one day."""
        result = InterestCalculationService.calculate_compound_interest(
            principal=Decimal('10000.00'),
            annual_rate=Decimal('0.05'),
            frequency='MONTHLY',
            days=1
        )
        # Very small amount for 1 day
        assert result['interest'] < Decimal('2.00')
        assert result['interest'] > Decimal('0.00')

    def test_compound_interest_invalid_frequency_raises_error(self):
        """Test that invalid frequency raises ValueError."""
        with pytest.raises(ValueError, match="Invalid frequency"):
            InterestCalculationService.calculate_compound_interest(
                principal=Decimal('10000.00'),
                annual_rate=Decimal('0.05'),
                frequency='INVALID',
                days=365
            )

    def test_compound_interest_negative_principal_raises_error(self):
        """Test that negative principal raises ValueError."""
        with pytest.raises(ValueError, match="Principal cannot be negative"):
            InterestCalculationService.calculate_compound_interest(
                principal=Decimal('-10000.00'),
                annual_rate=Decimal('0.05'),
                frequency='MONTHLY',
                days=365
            )

    def test_compound_interest_negative_rate_raises_error(self):
        """Test that negative rate raises ValueError."""
        with pytest.raises(ValueError, match="Interest rate cannot be negative"):
            InterestCalculationService.calculate_compound_interest(
                principal=Decimal('10000.00'),
                annual_rate=Decimal('-0.05'),
                frequency='MONTHLY',
                days=365
            )

    def test_compound_interest_negative_days_raises_error(self):
        """Test that negative days raises ValueError."""
        with pytest.raises(ValueError, match="Days cannot be negative"):
            InterestCalculationService.calculate_compound_interest(
                principal=Decimal('10000.00'),
                annual_rate=Decimal('0.05'),
                frequency='MONTHLY',
                days=-1
            )


class TestEffectiveAnnualRate:
    """Test suite for Effective Annual Rate (EAR) calculations."""

    def test_ear_monthly_compounding(self):
        """Test EAR calculation with monthly compounding."""
        # 5% nominal with monthly compounding
        ear = InterestCalculationService.calculate_effective_annual_rate(
            annual_rate=Decimal('0.05'),
            frequency='MONTHLY'
        )
        # EAR = (1 + 0.05/12)^12 - 1 = 0.051162
        assert Decimal('0.0511') <= ear <= Decimal('0.0513')

    def test_ear_quarterly_compounding(self):
        """Test EAR calculation with quarterly compounding."""
        # 5% nominal with quarterly compounding
        ear = InterestCalculationService.calculate_effective_annual_rate(
            annual_rate=Decimal('0.05'),
            frequency='QUARTERLY'
        )
        # EAR = (1 + 0.05/4)^4 - 1 = 0.050945
        assert Decimal('0.0509') <= ear <= Decimal('0.0510')

    def test_ear_annual_compounding(self):
        """Test EAR calculation with annual compounding."""
        # 5% nominal with annual compounding
        ear = InterestCalculationService.calculate_effective_annual_rate(
            annual_rate=Decimal('0.05'),
            frequency='ANNUALLY'
        )
        # EAR equals nominal rate for annual compounding
        assert ear == Decimal('0.05')

    def test_ear_zero_rate(self):
        """Test EAR with zero interest rate."""
        ear = InterestCalculationService.calculate_effective_annual_rate(
            annual_rate=Decimal('0.00'),
            frequency='MONTHLY'
        )
        assert ear == Decimal('0.00')

    def test_ear_different_rates(self):
        """Test EAR with various interest rates."""
        # 10% with monthly compounding
        ear = InterestCalculationService.calculate_effective_annual_rate(
            annual_rate=Decimal('0.10'),
            frequency='MONTHLY'
        )
        # EAR = (1 + 0.10/12)^12 - 1 ≈ 0.10471
        assert Decimal('0.104') <= ear <= Decimal('0.106')

        # 1% with monthly compounding
        ear = InterestCalculationService.calculate_effective_annual_rate(
            annual_rate=Decimal('0.01'),
            frequency='MONTHLY'
        )
        # EAR = (1 + 0.01/12)^12 - 1 ≈ 0.01005
        assert Decimal('0.010') <= ear <= Decimal('0.011')

    def test_ear_negative_rate_raises_error(self):
        """Test that negative rate raises ValueError."""
        with pytest.raises(ValueError, match="Interest rate cannot be negative"):
            InterestCalculationService.calculate_effective_annual_rate(
                annual_rate=Decimal('-0.05'),
                frequency='MONTHLY'
            )

    def test_ear_invalid_frequency_raises_error(self):
        """Test that invalid frequency raises ValueError."""
        with pytest.raises(ValueError, match="Invalid frequency"):
            InterestCalculationService.calculate_effective_annual_rate(
                annual_rate=Decimal('0.05'),
                frequency='INVALID'
            )


class TestProjectAnnualInterest:
    """Test suite for annual interest projection on accounts."""

    def test_project_annual_interest_monthly_compounding(self):
        """Test annual interest projection with monthly compounding."""
        # Create mock account
        account = SavingsAccount(
            bank_name='Test Bank',
            account_name='Test Account',
            account_number_encrypted='encrypted',
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=Decimal('10000.00'),
            interest_rate=Decimal('5.00'),  # 5% as percentage
            interest_payment_frequency=InterestFrequency.MONTHLY,
            country=AccountCountry.UK
        )

        result = InterestCalculationService.project_annual_interest(account)

        # Should match compound interest calculation
        assert result['projected_interest'] == Decimal('511.62')
        assert result['future_balance'] == Decimal('10511.62')
        assert Decimal('5.11') <= result['effective_rate'] <= Decimal('5.13')

    def test_project_annual_interest_quarterly_compounding(self):
        """Test annual interest projection with quarterly compounding."""
        account = SavingsAccount(
            bank_name='Test Bank',
            account_name='Test Account',
            account_number_encrypted='encrypted',
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=Decimal('10000.00'),
            interest_rate=Decimal('5.00'),
            interest_payment_frequency=InterestFrequency.QUARTERLY,
            country=AccountCountry.UK
        )

        result = InterestCalculationService.project_annual_interest(account)

        assert result['projected_interest'] == Decimal('509.45')
        assert result['future_balance'] == Decimal('10509.45')
        assert Decimal('5.08') <= result['effective_rate'] <= Decimal('5.10')

    def test_project_annual_interest_annually_compounding(self):
        """Test annual interest projection with annual compounding."""
        account = SavingsAccount(
            bank_name='Test Bank',
            account_name='Test Account',
            account_number_encrypted='encrypted',
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=Decimal('10000.00'),
            interest_rate=Decimal('5.00'),
            interest_payment_frequency=InterestFrequency.ANNUALLY,
            country=AccountCountry.UK
        )

        result = InterestCalculationService.project_annual_interest(account)

        assert result['projected_interest'] == Decimal('500.00')
        assert result['future_balance'] == Decimal('10500.00')
        assert result['effective_rate'] == Decimal('5.00')

    def test_project_annual_interest_maturity_simple(self):
        """Test annual interest projection with maturity frequency (simple interest)."""
        account = SavingsAccount(
            bank_name='Test Bank',
            account_name='Test Account',
            account_number_encrypted='encrypted',
            account_type=AccountType.FIXED_DEPOSIT,
            currency=Currency.GBP,
            current_balance=Decimal('10000.00'),
            interest_rate=Decimal('5.00'),
            interest_payment_frequency=InterestFrequency.MATURITY,
            country=AccountCountry.UK
        )

        result = InterestCalculationService.project_annual_interest(account)

        # Should use simple interest for maturity accounts
        assert result['projected_interest'] == Decimal('500.00')
        assert result['future_balance'] == Decimal('10500.00')
        assert result['effective_rate'] == Decimal('5.00')

    def test_project_annual_interest_no_balance_raises_error(self):
        """Test that account without balance raises ValueError."""
        account = SavingsAccount(
            bank_name='Test Bank',
            account_name='Test Account',
            account_number_encrypted='encrypted',
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=None,
            interest_rate=Decimal('5.00'),
            interest_payment_frequency=InterestFrequency.MONTHLY,
            country=AccountCountry.UK
        )

        with pytest.raises(ValueError, match="Account must have a current balance"):
            InterestCalculationService.project_annual_interest(account)

    def test_project_annual_interest_no_rate_raises_error(self):
        """Test that account without interest rate raises ValueError."""
        account = SavingsAccount(
            bank_name='Test Bank',
            account_name='Test Account',
            account_number_encrypted='encrypted',
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=Decimal('10000.00'),
            interest_rate=None,
            interest_payment_frequency=InterestFrequency.MONTHLY,
            country=AccountCountry.UK
        )

        with pytest.raises(ValueError, match="Account must have an interest rate"):
            InterestCalculationService.project_annual_interest(account)

    def test_project_annual_interest_no_frequency_raises_error(self):
        """Test that account without payment frequency raises ValueError."""
        account = SavingsAccount(
            bank_name='Test Bank',
            account_name='Test Account',
            account_number_encrypted='encrypted',
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=Decimal('10000.00'),
            interest_rate=Decimal('5.00'),
            interest_payment_frequency=None,
            country=AccountCountry.UK
        )

        with pytest.raises(ValueError, match="Account must have an interest payment frequency"):
            InterestCalculationService.project_annual_interest(account)


class TestCalculateInterestForPeriod:
    """Test suite for period-based interest calculations."""

    def test_calculate_interest_for_period_one_month(self):
        """Test interest calculation for one month period."""
        account = SavingsAccount(
            bank_name='Test Bank',
            account_name='Test Account',
            account_number_encrypted='encrypted',
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=Decimal('10000.00'),
            interest_rate=Decimal('5.00'),
            interest_payment_frequency=InterestFrequency.MONTHLY,
            country=AccountCountry.UK
        )

        result = InterestCalculationService.calculate_interest_for_period(
            account=account,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31)
        )

        # 30 days of interest
        assert result['days'] == 30
        assert Decimal('40.00') <= result['interest_earned'] <= Decimal('45.00')

    def test_calculate_interest_for_period_one_year(self):
        """Test interest calculation for one year period."""
        account = SavingsAccount(
            bank_name='Test Bank',
            account_name='Test Account',
            account_number_encrypted='encrypted',
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=Decimal('10000.00'),
            interest_rate=Decimal('5.00'),
            interest_payment_frequency=InterestFrequency.MONTHLY,
            country=AccountCountry.UK
        )

        result = InterestCalculationService.calculate_interest_for_period(
            account=account,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31)
        )

        # 365 days of interest (2024 is leap year but we're not including Feb 29)
        assert result['days'] == 365
        # Should be close to annual projection
        assert Decimal('510.00') <= result['interest_earned'] <= Decimal('513.00')

    def test_calculate_interest_for_period_simple_interest(self):
        """Test period interest calculation with simple interest (maturity)."""
        account = SavingsAccount(
            bank_name='Test Bank',
            account_name='Test Account',
            account_number_encrypted='encrypted',
            account_type=AccountType.FIXED_DEPOSIT,
            currency=Currency.GBP,
            current_balance=Decimal('10000.00'),
            interest_rate=Decimal('5.00'),
            interest_payment_frequency=InterestFrequency.MATURITY,
            country=AccountCountry.UK
        )

        result = InterestCalculationService.calculate_interest_for_period(
            account=account,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31)
        )

        # Simple interest for 365 days
        assert result['days'] == 365
        assert result['interest_earned'] == Decimal('500.00')

    def test_calculate_interest_for_period_same_date(self):
        """Test interest calculation when start and end dates are the same."""
        account = SavingsAccount(
            bank_name='Test Bank',
            account_name='Test Account',
            account_number_encrypted='encrypted',
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=Decimal('10000.00'),
            interest_rate=Decimal('5.00'),
            interest_payment_frequency=InterestFrequency.MONTHLY,
            country=AccountCountry.UK
        )

        result = InterestCalculationService.calculate_interest_for_period(
            account=account,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 1)
        )

        assert result['days'] == 0
        assert result['interest_earned'] == Decimal('0.00')

    def test_calculate_interest_for_period_end_before_start_raises_error(self):
        """Test that end date before start date raises ValueError."""
        account = SavingsAccount(
            bank_name='Test Bank',
            account_name='Test Account',
            account_number_encrypted='encrypted',
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=Decimal('10000.00'),
            interest_rate=Decimal('5.00'),
            interest_payment_frequency=InterestFrequency.MONTHLY,
            country=AccountCountry.UK
        )

        with pytest.raises(ValueError, match="End date must be on or after start date"):
            InterestCalculationService.calculate_interest_for_period(
                account=account,
                start_date=date(2024, 12, 31),
                end_date=date(2024, 1, 1)
            )

    def test_calculate_interest_for_period_no_balance_raises_error(self):
        """Test that account without balance raises ValueError."""
        account = SavingsAccount(
            bank_name='Test Bank',
            account_name='Test Account',
            account_number_encrypted='encrypted',
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=None,
            interest_rate=Decimal('5.00'),
            interest_payment_frequency=InterestFrequency.MONTHLY,
            country=AccountCountry.UK
        )

        with pytest.raises(ValueError, match="Account must have a current balance"):
            InterestCalculationService.calculate_interest_for_period(
                account=account,
                start_date=date(2024, 1, 1),
                end_date=date(2024, 12, 31)
            )


class TestEdgeCases:
    """Test suite for edge cases and precision."""

    def test_very_small_principal(self):
        """Test calculations with very small principal amounts."""
        interest = InterestCalculationService.calculate_simple_interest(
            principal=Decimal('1.00'),
            annual_rate=Decimal('0.05'),
            days=365
        )
        assert interest == Decimal('0.05')

    def test_very_high_rate(self):
        """Test calculations with high interest rates."""
        interest = InterestCalculationService.calculate_simple_interest(
            principal=Decimal('10000.00'),
            annual_rate=Decimal('0.20'),  # 20%
            days=365
        )
        assert interest == Decimal('2000.00')

    def test_very_low_rate(self):
        """Test calculations with very low interest rates."""
        interest = InterestCalculationService.calculate_simple_interest(
            principal=Decimal('10000.00'),
            annual_rate=Decimal('0.001'),  # 0.1%
            days=365
        )
        assert interest == Decimal('10.00')

    def test_large_principal(self):
        """Test calculations with large principal amounts."""
        interest = InterestCalculationService.calculate_simple_interest(
            principal=Decimal('1000000.00'),  # £1M
            annual_rate=Decimal('0.05'),
            days=365
        )
        assert interest == Decimal('50000.00')

    def test_precision_rounding(self):
        """Test that results are properly rounded to 2 decimal places."""
        # Amount that would have more than 2 decimal places
        interest = InterestCalculationService.calculate_simple_interest(
            principal=Decimal('10000.00'),
            annual_rate=Decimal('0.05'),
            days=100
        )
        # 10000 × 0.05 × (100/365) = 136.9863...
        assert interest == Decimal('136.99')

    def test_compound_vs_simple_interest_difference(self):
        """Test that compound interest is higher than simple interest."""
        principal = Decimal('10000.00')
        rate = Decimal('0.05')
        days = 365

        simple = InterestCalculationService.calculate_simple_interest(
            principal=principal,
            annual_rate=rate,
            days=days
        )

        compound = InterestCalculationService.calculate_compound_interest(
            principal=principal,
            annual_rate=rate,
            frequency='MONTHLY',
            days=days
        )

        # Compound should be higher than simple
        assert compound['interest'] > simple
