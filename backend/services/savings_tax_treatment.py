"""
Savings Interest Tax Treatment Service.

This service calculates tax treatment for savings interest income in both
UK and South Africa, including:
- UK: Personal Savings Allowance (PSA), starting rate for savings, ISA exclusions
- SA: Interest exemptions (age-based), TFSA exclusions

All calculations use Decimal for precision and round to 2 decimal places for currency.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Tuple

from models.savings_account import SavingsAccount


class SavingsTaxTreatmentService:
    """
    Service for calculating tax treatment of savings interest income.

    Handles UK and SA tax rules for savings interest, including allowances,
    exemptions, and tax-free accounts (ISA/TFSA).
    """

    # UK PSA (Personal Savings Allowance) by tax band
    UK_PSA_BASIC_RATE = Decimal('1000.00')      # £1,000 for basic rate taxpayers
    UK_PSA_HIGHER_RATE = Decimal('500.00')      # £500 for higher rate taxpayers
    UK_PSA_ADDITIONAL_RATE = Decimal('0.00')    # £0 for additional rate taxpayers

    # UK Starting Rate for Savings
    UK_STARTING_RATE_ALLOWANCE_MAX = Decimal('5000.00')    # £5,000 max
    UK_STARTING_RATE_THRESHOLD = Decimal('17570.00')       # £17,570 threshold
    UK_PERSONAL_ALLOWANCE = Decimal('12570.00')            # £12,570 personal allowance

    # SA Interest Exemptions
    SA_INTEREST_EXEMPTION_UNDER_65 = Decimal('23800.00')  # R23,800 under 65
    SA_INTEREST_EXEMPTION_65_PLUS = Decimal('34500.00')   # R34,500 65+

    # Tax rates
    UK_BASIC_RATE = Decimal('0.20')      # 20%
    UK_HIGHER_RATE = Decimal('0.40')     # 40%
    UK_ADDITIONAL_RATE = Decimal('0.45') # 45%

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
    def _to_decimal(value) -> Decimal:
        """
        Convert value to Decimal safely.

        Args:
            value: Value to convert (int, float, str, or Decimal)

        Returns:
            Decimal: Converted value
        """
        if isinstance(value, Decimal):
            return value
        return Decimal(str(value))

    @classmethod
    def calculate_uk_psa(cls, tax_band: str) -> Decimal:
        """
        Calculate UK Personal Savings Allowance based on tax band.

        Args:
            tax_band: Tax band ('BASIC', 'HIGHER', 'ADDITIONAL')

        Returns:
            Decimal: PSA amount (£1000, £500, or £0)

        Raises:
            ValueError: If tax_band is invalid
        """
        tax_band = tax_band.upper()

        if tax_band == 'BASIC':
            return cls.UK_PSA_BASIC_RATE
        elif tax_band == 'HIGHER':
            return cls.UK_PSA_HIGHER_RATE
        elif tax_band == 'ADDITIONAL':
            return cls.UK_PSA_ADDITIONAL_RATE
        else:
            raise ValueError(
                f"Invalid tax band: {tax_band}. "
                f"Must be one of: BASIC, HIGHER, ADDITIONAL"
            )

    @classmethod
    def calculate_uk_starting_rate_allowance(cls, non_savings_income: Decimal) -> Decimal:
        """
        Calculate UK starting rate for savings allowance.

        The starting rate for savings provides £5,000 tax-free if non-savings
        income is below £17,570. It reduces by £1 for every £1 of non-savings
        income over £12,570 (personal allowance).

        Formula: max(0, min(5000, 17570 - non_savings_income))

        Args:
            non_savings_income: Total non-savings income (before personal allowance)

        Returns:
            Decimal: Starting rate allowance (0 to £5,000)

        Raises:
            ValueError: If non_savings_income is negative
        """
        non_savings_income = cls._to_decimal(non_savings_income)

        if non_savings_income < 0:
            raise ValueError("Non-savings income cannot be negative")

        # If income >= threshold, no allowance
        if non_savings_income >= cls.UK_STARTING_RATE_THRESHOLD:
            return Decimal('0.00')

        # Calculate allowance: min(5000, 17570 - income)
        allowance = min(
            cls.UK_STARTING_RATE_ALLOWANCE_MAX,
            cls.UK_STARTING_RATE_THRESHOLD - non_savings_income
        )

        return cls._round_currency(max(Decimal('0'), allowance))

    @classmethod
    def calculate_uk_savings_tax(
        cls,
        total_interest: Decimal,
        isa_interest: Decimal,
        tax_band: str,
        non_savings_income: Decimal
    ) -> Dict:
        """
        Calculate UK savings interest tax.

        Applies tax rules in order:
        1. Exclude ISA interest (tax-free)
        2. Apply starting rate for savings (if eligible)
        3. Apply Personal Savings Allowance (PSA)
        4. Calculate tax on remaining interest at appropriate rate

        Args:
            total_interest: Total interest from all accounts
            isa_interest: Interest from ISA accounts (tax-free)
            tax_band: Tax band ('BASIC', 'HIGHER', 'ADDITIONAL')
            non_savings_income: Total non-savings income

        Returns:
            Dict containing:
            - total_interest: Total interest income
            - isa_interest_tax_free: ISA interest (excluded)
            - starting_rate_allowance: Starting rate allowance available
            - starting_rate_used: Amount of starting rate used
            - psa_allowance: PSA available
            - psa_used: Amount of PSA used
            - taxable_interest: Interest subject to tax
            - tax_rate: Tax rate applied (as decimal)
            - tax_due: Total tax due
            - tax_free_interest: Total tax-free interest

        Raises:
            ValueError: If inputs are invalid
        """
        # Convert to Decimal
        total_interest = cls._to_decimal(total_interest)
        isa_interest = cls._to_decimal(isa_interest)
        non_savings_income = cls._to_decimal(non_savings_income)

        # Validate inputs
        if total_interest < 0:
            raise ValueError("Total interest cannot be negative")
        if isa_interest < 0:
            raise ValueError("ISA interest cannot be negative")
        if isa_interest > total_interest:
            raise ValueError("ISA interest cannot exceed total interest")
        if non_savings_income < 0:
            raise ValueError("Non-savings income cannot be negative")

        # 1. Exclude ISA interest (tax-free)
        non_isa_interest = total_interest - isa_interest

        # 2. Apply starting rate for savings (if eligible)
        starting_rate_allowance = cls.calculate_uk_starting_rate_allowance(non_savings_income)
        starting_rate_used = min(starting_rate_allowance, non_isa_interest)

        # 3. Apply PSA
        psa_allowance = cls.calculate_uk_psa(tax_band)
        interest_after_starting_rate = non_isa_interest - starting_rate_used
        psa_used = min(psa_allowance, interest_after_starting_rate)

        # 4. Calculate taxable interest
        taxable_interest = interest_after_starting_rate - psa_used

        # 5. Determine tax rate based on band
        if tax_band.upper() == 'BASIC':
            tax_rate = cls.UK_BASIC_RATE
        elif tax_band.upper() == 'HIGHER':
            tax_rate = cls.UK_HIGHER_RATE
        elif tax_band.upper() == 'ADDITIONAL':
            tax_rate = cls.UK_ADDITIONAL_RATE
        else:
            raise ValueError(f"Invalid tax band: {tax_band}")

        # 6. Calculate tax
        tax_due = taxable_interest * tax_rate

        # 7. Calculate total tax-free interest
        tax_free_interest = isa_interest + starting_rate_used + psa_used

        return {
            'total_interest': cls._round_currency(total_interest),
            'isa_interest_tax_free': cls._round_currency(isa_interest),
            'starting_rate_allowance': cls._round_currency(starting_rate_allowance),
            'starting_rate_used': cls._round_currency(starting_rate_used),
            'psa_allowance': cls._round_currency(psa_allowance),
            'psa_used': cls._round_currency(psa_used),
            'taxable_interest': cls._round_currency(taxable_interest),
            'tax_rate': tax_rate,
            'tax_due': cls._round_currency(tax_due),
            'tax_free_interest': cls._round_currency(tax_free_interest)
        }

    @classmethod
    def calculate_sa_interest_exemption(cls, age: int) -> Decimal:
        """
        Calculate SA interest exemption based on age.

        Args:
            age: User's age

        Returns:
            Decimal: Interest exemption amount (R23,800 or R34,500)

        Raises:
            ValueError: If age is negative
        """
        if age < 0:
            raise ValueError("Age cannot be negative")

        if age >= 65:
            return cls.SA_INTEREST_EXEMPTION_65_PLUS
        else:
            return cls.SA_INTEREST_EXEMPTION_UNDER_65

    @classmethod
    def calculate_sa_savings_tax(
        cls,
        total_interest: Decimal,
        tfsa_interest: Decimal,
        age: int,
        marginal_rate: Decimal
    ) -> Dict:
        """
        Calculate SA savings interest tax.

        Applies tax rules in order:
        1. Exclude TFSA interest (tax-free)
        2. Apply interest exemption based on age
        3. Calculate tax on remaining interest at marginal rate

        Args:
            total_interest: Total interest from all accounts
            tfsa_interest: Interest from TFSA accounts (tax-free)
            age: User's age (for exemption calculation)
            marginal_rate: User's marginal tax rate (as decimal, e.g., 0.31 for 31%)

        Returns:
            Dict containing:
            - total_interest: Total interest income
            - tfsa_interest_tax_free: TFSA interest (excluded)
            - interest_exemption: Interest exemption available
            - exemption_used: Amount of exemption used
            - taxable_interest: Interest subject to tax
            - marginal_rate: Marginal tax rate applied
            - tax_due: Total tax due
            - tax_free_interest: Total tax-free interest

        Raises:
            ValueError: If inputs are invalid
        """
        # Convert to Decimal
        total_interest = cls._to_decimal(total_interest)
        tfsa_interest = cls._to_decimal(tfsa_interest)
        marginal_rate = cls._to_decimal(marginal_rate)

        # Validate inputs
        if total_interest < 0:
            raise ValueError("Total interest cannot be negative")
        if tfsa_interest < 0:
            raise ValueError("TFSA interest cannot be negative")
        if tfsa_interest > total_interest:
            raise ValueError("TFSA interest cannot exceed total interest")
        if age < 0:
            raise ValueError("Age cannot be negative")
        if marginal_rate < 0 or marginal_rate > 1:
            raise ValueError("Marginal rate must be between 0 and 1")

        # 1. Exclude TFSA interest (tax-free)
        non_tfsa_interest = total_interest - tfsa_interest

        # 2. Apply interest exemption
        interest_exemption = cls.calculate_sa_interest_exemption(age)
        exemption_used = min(interest_exemption, non_tfsa_interest)

        # 3. Calculate taxable interest
        taxable_interest = non_tfsa_interest - exemption_used

        # 4. Calculate tax at marginal rate
        tax_due = taxable_interest * marginal_rate

        # 5. Calculate total tax-free interest
        tax_free_interest = tfsa_interest + exemption_used

        return {
            'total_interest': cls._round_currency(total_interest),
            'tfsa_interest_tax_free': cls._round_currency(tfsa_interest),
            'interest_exemption': cls._round_currency(interest_exemption),
            'exemption_used': cls._round_currency(exemption_used),
            'taxable_interest': cls._round_currency(taxable_interest),
            'marginal_rate': marginal_rate,
            'tax_due': cls._round_currency(tax_due),
            'tax_free_interest': cls._round_currency(tax_free_interest)
        }

    @staticmethod
    def get_tax_free_interest_from_accounts(
        accounts: List[SavingsAccount]
    ) -> Tuple[Decimal, Decimal]:
        """
        Sum ISA and TFSA interest from account list.

        Args:
            accounts: List of SavingsAccount instances

        Returns:
            Tuple[Decimal, Decimal]: (isa_interest, tfsa_interest)
        """
        isa_interest = Decimal('0.00')
        tfsa_interest = Decimal('0.00')

        for account in accounts:
            # This is a placeholder - in real implementation, we'd need to
            # calculate projected interest for each account using InterestCalculationService
            # For now, this is just the structure
            pass

        return (
            SavingsTaxTreatmentService._round_currency(isa_interest),
            SavingsTaxTreatmentService._round_currency(tfsa_interest)
        )

    @classmethod
    def calculate_total_projected_interest(
        cls,
        accounts: List[SavingsAccount]
    ) -> Decimal:
        """
        Calculate total projected annual interest from all accounts.

        Uses InterestCalculationService to project interest for each account.

        Args:
            accounts: List of SavingsAccount instances

        Returns:
            Decimal: Total projected annual interest
        """
        from services.interest_calculation import InterestCalculationService

        total_interest = Decimal('0.00')

        for account in accounts:
            try:
                # Calculate projected annual interest for this account
                projection = InterestCalculationService.project_annual_interest(account)
                total_interest += projection['projected_interest']
            except (ValueError, AttributeError):
                # Skip accounts with missing/invalid data
                continue

        return cls._round_currency(total_interest)
