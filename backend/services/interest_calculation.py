"""
Interest Calculation Service for savings accounts.

This service provides comprehensive interest calculation functionality including:
- Simple interest calculations
- Compound interest with multiple frequencies (monthly, quarterly, annually)
- Effective Annual Rate (EAR) calculations
- Interest projections for accounts
- Period-based interest calculations

All calculations use Decimal for precision and round to 2 decimal places for currency.
"""

from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Optional

from models.savings_account import SavingsAccount, InterestFrequency


class InterestCalculationService:
    """
    Service for calculating interest on savings accounts.

    Uses Decimal arithmetic for precision and supports both simple
    and compound interest calculations with various payment frequencies.
    """

    # Constants
    DAYS_PER_YEAR = Decimal('365')
    MONTHLY_FREQUENCY = Decimal('12')
    QUARTERLY_FREQUENCY = Decimal('4')
    ANNUALLY_FREQUENCY = Decimal('1')

    @staticmethod
    def _round_currency(amount: Decimal) -> Decimal:
        """
        Round amount to 2 decimal places (currency precision).

        Args:
            amount: Decimal amount to round

        Returns:
            Decimal: Amount rounded to 2 decimal places
        """
        return amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    @staticmethod
    def _get_compounding_frequency(frequency: str) -> Decimal:
        """
        Get compounding frequency number from frequency string.

        Args:
            frequency: Frequency enum value ('MONTHLY', 'QUARTERLY', 'ANNUALLY')

        Returns:
            Decimal: Number of compounding periods per year

        Raises:
            ValueError: If frequency is invalid
        """
        frequency_map = {
            'MONTHLY': InterestCalculationService.MONTHLY_FREQUENCY,
            'QUARTERLY': InterestCalculationService.QUARTERLY_FREQUENCY,
            'ANNUALLY': InterestCalculationService.ANNUALLY_FREQUENCY,
        }

        if frequency not in frequency_map:
            raise ValueError(
                f"Invalid frequency: {frequency}. "
                f"Must be one of: MONTHLY, QUARTERLY, ANNUALLY"
            )

        return frequency_map[frequency]

    @classmethod
    def calculate_simple_interest(
        cls,
        principal: Decimal,
        annual_rate: Decimal,
        days: int
    ) -> Decimal:
        """
        Calculate simple interest for a given principal, rate, and time period.

        Formula: Interest = Principal × Rate × Time
        Where Time = days / 365

        Args:
            principal: Starting principal amount
            annual_rate: Annual interest rate as decimal (e.g., 0.05 for 5%)
            days: Number of days for interest calculation

        Returns:
            Decimal: Interest amount rounded to 2 decimal places

        Raises:
            ValueError: If principal is negative, rate is negative, or days is negative
        """
        # Validate inputs
        if principal < 0:
            raise ValueError("Principal cannot be negative")
        if annual_rate < 0:
            raise ValueError("Interest rate cannot be negative")
        if days < 0:
            raise ValueError("Days cannot be negative")

        # Edge case: zero principal, rate, or days
        if principal == 0 or annual_rate == 0 or days == 0:
            return Decimal('0.00')

        # Convert to Decimal for precision
        principal = Decimal(str(principal))
        annual_rate = Decimal(str(annual_rate))
        days_decimal = Decimal(str(days))

        # Calculate simple interest: P × R × (T/365)
        time_fraction = days_decimal / cls.DAYS_PER_YEAR
        interest = principal * annual_rate * time_fraction

        return cls._round_currency(interest)

    @classmethod
    def calculate_compound_interest(
        cls,
        principal: Decimal,
        annual_rate: Decimal,
        frequency: str,
        days: int
    ) -> Dict[str, Decimal]:
        """
        Calculate compound interest for a given principal, rate, frequency, and time.

        Formula: FV = P × (1 + R/n)^(n×t)
        Interest = FV - P

        Where:
        - P = Principal
        - R = Annual rate (as decimal)
        - n = Compounding frequency per year
        - t = Time in years (days/365)

        Args:
            principal: Starting principal amount
            annual_rate: Annual interest rate as decimal (e.g., 0.05 for 5%)
            frequency: Compounding frequency ('MONTHLY', 'QUARTERLY', 'ANNUALLY')
            days: Number of days for interest calculation

        Returns:
            Dict containing:
            - interest: Interest earned
            - future_value: Principal + interest
            - effective_rate: Effective annual rate

        Raises:
            ValueError: If inputs are invalid
        """
        # Validate inputs
        if principal < 0:
            raise ValueError("Principal cannot be negative")
        if annual_rate < 0:
            raise ValueError("Interest rate cannot be negative")
        if days < 0:
            raise ValueError("Days cannot be negative")

        # Edge case: zero principal, rate, or days
        if principal == 0 or annual_rate == 0 or days == 0:
            return {
                'interest': Decimal('0.00'),
                'future_value': cls._round_currency(Decimal(str(principal))),
                'effective_rate': Decimal('0.00')
            }

        # Convert to Decimal for precision
        principal = Decimal(str(principal))
        annual_rate = Decimal(str(annual_rate))
        days_decimal = Decimal(str(days))

        # Get compounding frequency
        n = cls._get_compounding_frequency(frequency)

        # Calculate time in years
        t = days_decimal / cls.DAYS_PER_YEAR

        # Calculate future value: FV = P × (1 + R/n)^(n×t)
        rate_per_period = annual_rate / n
        number_of_periods = n * t

        # (1 + R/n)^(n×t)
        growth_factor = (Decimal('1') + rate_per_period) ** number_of_periods
        future_value = principal * growth_factor

        # Calculate interest
        interest = future_value - principal

        # Calculate effective annual rate for full year
        ear = cls.calculate_effective_annual_rate(annual_rate, frequency)

        return {
            'interest': cls._round_currency(interest),
            'future_value': cls._round_currency(future_value),
            'effective_rate': cls._round_currency(ear * Decimal('100'))  # As percentage
        }

    @classmethod
    def calculate_effective_annual_rate(
        cls,
        annual_rate: Decimal,
        frequency: str
    ) -> Decimal:
        """
        Calculate Effective Annual Rate (EAR) based on compounding frequency.

        Formula: EAR = (1 + R/n)^n - 1

        Where:
        - R = Nominal annual rate
        - n = Compounding frequency per year

        Args:
            annual_rate: Annual interest rate as decimal (e.g., 0.05 for 5%)
            frequency: Compounding frequency ('MONTHLY', 'QUARTERLY', 'ANNUALLY')

        Returns:
            Decimal: Effective annual rate as decimal (e.g., 0.0512 for 5.12%)

        Raises:
            ValueError: If rate is negative or frequency is invalid
        """
        # Validate inputs
        if annual_rate < 0:
            raise ValueError("Interest rate cannot be negative")

        # Edge case: zero rate
        if annual_rate == 0:
            return Decimal('0.00')

        # Convert to Decimal
        annual_rate = Decimal(str(annual_rate))

        # Get compounding frequency
        n = cls._get_compounding_frequency(frequency)

        # Calculate EAR: (1 + R/n)^n - 1
        rate_per_period = annual_rate / n
        ear = (Decimal('1') + rate_per_period) ** n - Decimal('1')

        return ear

    @classmethod
    def project_annual_interest(
        cls,
        account: SavingsAccount
    ) -> Dict[str, Decimal]:
        """
        Project interest for the next 12 months based on account's current balance.

        Uses the account's interest rate and payment frequency to calculate
        projected interest for a full year (365 days).

        Args:
            account: SavingsAccount instance with balance, rate, and frequency

        Returns:
            Dict containing:
            - projected_interest: Interest for next 12 months
            - future_balance: Current balance + projected interest
            - effective_rate: Effective annual rate (percentage)

        Raises:
            ValueError: If account has invalid interest configuration
        """
        # Validate account has required fields
        if account.current_balance is None:
            raise ValueError("Account must have a current balance")
        if account.interest_rate is None:
            raise ValueError("Account must have an interest rate")
        if account.interest_payment_frequency is None:
            raise ValueError("Account must have an interest payment frequency")

        # Handle simple interest case (MATURITY frequency means simple interest)
        if account.interest_payment_frequency == InterestFrequency.MATURITY:
            # Use simple interest for maturity-based accounts
            projected_interest = cls.calculate_simple_interest(
                principal=account.current_balance,
                annual_rate=account.interest_rate / Decimal('100'),  # Convert percentage to decimal
                days=365
            )

            return {
                'projected_interest': projected_interest,
                'future_balance': cls._round_currency(account.current_balance + projected_interest),
                'effective_rate': account.interest_rate  # Same as nominal for simple interest
            }

        # Use compound interest for regular payment frequencies
        result = cls.calculate_compound_interest(
            principal=account.current_balance,
            annual_rate=account.interest_rate / Decimal('100'),  # Convert percentage to decimal
            frequency=account.interest_payment_frequency.value,
            days=365
        )

        return {
            'projected_interest': result['interest'],
            'future_balance': result['future_value'],
            'effective_rate': result['effective_rate']
        }

    @classmethod
    def calculate_interest_for_period(
        cls,
        account: SavingsAccount,
        start_date: date,
        end_date: date
    ) -> Dict[str, Decimal]:
        """
        Calculate interest earned between two dates for an account.

        Uses the account's current balance as the starting principal and
        calculates interest based on the number of days between dates.

        Args:
            account: SavingsAccount instance with balance, rate, and frequency
            start_date: Start date of period
            end_date: End date of period (inclusive)

        Returns:
            Dict containing:
            - interest_earned: Interest for the period
            - days: Number of days in period

        Raises:
            ValueError: If dates are invalid or account configuration is invalid
        """
        # Validate dates
        if end_date < start_date:
            raise ValueError("End date must be on or after start date")

        # Validate account
        if account.current_balance is None:
            raise ValueError("Account must have a current balance")
        if account.interest_rate is None:
            raise ValueError("Account must have an interest rate")
        if account.interest_payment_frequency is None:
            raise ValueError("Account must have an interest payment frequency")

        # Calculate days in period
        days = (end_date - start_date).days

        # Edge case: same date (0 days)
        if days == 0:
            return {
                'interest_earned': Decimal('0.00'),
                'days': 0
            }

        # Calculate interest based on payment frequency
        if account.interest_payment_frequency == InterestFrequency.MATURITY:
            # Simple interest
            interest = cls.calculate_simple_interest(
                principal=account.current_balance,
                annual_rate=account.interest_rate / Decimal('100'),
                days=days
            )
        else:
            # Compound interest
            result = cls.calculate_compound_interest(
                principal=account.current_balance,
                annual_rate=account.interest_rate / Decimal('100'),
                frequency=account.interest_payment_frequency.value,
                days=days
            )
            interest = result['interest']

        return {
            'interest_earned': interest,
            'days': days
        }
