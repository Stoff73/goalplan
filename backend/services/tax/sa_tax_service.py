"""
South Africa Tax Calculation Service

This service provides comprehensive SA tax calculations for the 2024/25 tax year,
including Income Tax, Capital Gains Tax, and Dividend Withholding Tax.

All calculations follow SARS specifications and use high-precision decimal arithmetic
to ensure accuracy in financial calculations.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Literal


class SATaxService:
    """
    Service for calculating South African taxes for the 2024/25 tax year.

    Supports:
    - Income Tax with age-based rebates
    - Capital Gains Tax (inclusion rate method)
    - Dividend Withholding Tax
    """

    # 2024/25 Tax Year Constants (March 1, 2024 - February 28, 2025)

    # Age-based Rebates (Primary, Secondary, Tertiary)
    PRIMARY_REBATE = Decimal("17235.00")  # Under 65
    SECONDARY_REBATE = Decimal("9444.00")  # Additional for 65-74
    TERTIARY_REBATE = Decimal("3145.00")   # Additional for 75+

    # Total rebates by age group
    REBATE_UNDER_65 = PRIMARY_REBATE  # R17,235
    REBATE_65_TO_74 = PRIMARY_REBATE + SECONDARY_REBATE  # R26,679
    REBATE_75_PLUS = PRIMARY_REBATE + SECONDARY_REBATE + TERTIARY_REBATE  # R29,824

    # Capital Gains Tax
    CGT_ANNUAL_EXCLUSION = Decimal("40000.00")  # R40,000
    CGT_INCLUSION_RATE_INDIVIDUAL = Decimal("0.40")  # 40%
    CGT_INCLUSION_RATE_COMPANY = Decimal("0.80")  # 80%

    # Dividend Tax
    DIVIDEND_TAX_RATE = Decimal("0.20")  # 20%
    DIVIDEND_EXEMPTION = Decimal("23800.00")  # R23,800 per year

    # Income Tax Bands (2024/25)
    # These are defined as tuples: (lower_limit, upper_limit, rate, base_tax)
    # Base tax is the cumulative tax at the start of each band
    INCOME_TAX_BANDS = [
        {
            "lower": Decimal("0"),
            "upper": Decimal("237100"),
            "rate": Decimal("0.18"),
            "base_tax": Decimal("0")
        },
        {
            "lower": Decimal("237100"),
            "upper": Decimal("370500"),
            "rate": Decimal("0.26"),
            "base_tax": Decimal("42678")  # 18% of 237,100
        },
        {
            "lower": Decimal("370500"),
            "upper": Decimal("512800"),
            "rate": Decimal("0.31"),
            "base_tax": Decimal("77362")  # 42,678 + 26% of 133,400
        },
        {
            "lower": Decimal("512800"),
            "upper": Decimal("673000"),
            "rate": Decimal("0.36"),
            "base_tax": Decimal("121475")  # 77,362 + 31% of 142,300
        },
        {
            "lower": Decimal("673000"),
            "upper": Decimal("1817000"),
            "rate": Decimal("0.39"),
            "base_tax": Decimal("179147")  # 121,475 + 36% of 160,200
        },
        {
            "lower": Decimal("1817000"),
            "upper": None,  # No upper limit (infinity)
            "rate": Decimal("0.45"),
            "base_tax": Decimal("625607")  # 179,147 + 39% of 1,144,000
        }
    ]

    @staticmethod
    def _round_currency(amount: Decimal) -> Decimal:
        """Round to 2 decimal places using banker's rounding."""
        return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def _round_percentage(rate: Decimal) -> Decimal:
        """Round percentage to 2 decimal places."""
        return rate.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _get_rebate_for_age(self, age: Optional[int]) -> Decimal:
        """
        Get the appropriate tax rebate based on age.

        Args:
            age: Age of the taxpayer (None defaults to under 65)

        Returns:
            Total rebate amount
        """
        if age is None or age < 65:
            return self.REBATE_UNDER_65
        elif age < 75:
            return self.REBATE_65_TO_74
        else:
            return self.REBATE_75_PLUS

    def calculate_income_tax(
        self,
        income: Decimal,
        age: Optional[int] = None,
        tax_year: str = "2024/25"
    ) -> Dict:
        """
        Calculate SA Income Tax for a given income.

        SA Income Tax uses a progressive tax system with age-based rebates.
        Tax is calculated on gross income, then rebates are subtracted.

        Args:
            income: Gross taxable income
            age: Age of taxpayer (for rebate calculation)
            tax_year: Tax year (currently only 2024/25 supported)

        Returns:
            Dictionary containing:
            - tax_owed: Total tax payable (after rebates)
            - effective_rate: Effective tax rate as percentage
            - rebates_applied: Total rebate amount
            - breakdown: List of tax by band
        """
        if tax_year != "2024/25":
            raise ValueError(f"Tax year {tax_year} not supported. Only 2024/25 available.")

        # Convert to Decimal
        income = Decimal(str(income))

        if income < 0:
            raise ValueError("Income cannot be negative")

        # Calculate tax by progressive bands
        breakdown = []
        total_tax = Decimal("0")

        for band in self.INCOME_TAX_BANDS:
            lower = band["lower"]
            upper = band["upper"]
            rate = band["rate"]

            # Determine taxable amount in this band
            if income <= lower:
                # Income doesn't reach this band
                break

            if upper is None:
                # Top band (no upper limit)
                taxable_in_band = income - lower
            else:
                # Middle bands
                taxable_in_band = min(income, upper) - lower

            if taxable_in_band <= 0:
                continue

            # Calculate tax for this band
            tax_in_band = self._round_currency(taxable_in_band * rate)
            total_tax += tax_in_band

            breakdown.append({
                "bracket": f"R{int(lower):,} - R{int(upper):,}" if upper else f"R{int(lower):,}+",
                "amount": self._round_currency(taxable_in_band),
                "rate": float(rate * 100),
                "tax": tax_in_band
            })

        # Apply age-based rebate
        rebate = self._get_rebate_for_age(age)
        tax_after_rebate = max(total_tax - rebate, Decimal("0"))

        # Calculate effective rate
        effective_rate = Decimal("0")
        if income > 0:
            effective_rate = self._round_percentage((tax_after_rebate / income) * 100)

        return {
            "tax_owed": self._round_currency(tax_after_rebate),
            "effective_rate": float(effective_rate),
            "rebates_applied": self._round_currency(rebate),
            "breakdown": breakdown,
            "gross_income": self._round_currency(income),
            "gross_tax_before_rebates": self._round_currency(total_tax)
        }

    def calculate_cgt(
        self,
        total_gains: Decimal,
        annual_exclusion_used: Decimal = Decimal("0"),
        inclusion_rate: Decimal = None,
        taxable_income: Decimal = Decimal("0"),
        age: Optional[int] = None
    ) -> Dict:
        """
        Calculate SA Capital Gains Tax using the inclusion rate method.

        SA CGT works differently from UK:
        1. Apply annual exclusion (R40,000)
        2. Apply inclusion rate (40% for individuals, 80% for companies)
        3. Add included amount to taxable income
        4. Tax the included amount at marginal income tax rates

        Args:
            total_gains: Total capital gains for the year
            annual_exclusion_used: Amount of exclusion already used
            inclusion_rate: Inclusion rate (defaults to 40% for individuals)
            taxable_income: Existing taxable income (to determine marginal rate)
            age: Age of taxpayer (for income tax calculation)

        Returns:
            Dictionary containing:
            - cgt_owed: Total CGT payable
            - taxable_gain: Gain after exclusion
            - included_amount: Amount included in taxable income (after inclusion rate)
            - exclusion_used: Annual exclusion applied
            - effective_cgt_rate: Effective CGT rate as percentage of total gain
        """
        # Convert to Decimal
        total_gains = Decimal(str(total_gains))
        annual_exclusion_used = Decimal(str(annual_exclusion_used))
        taxable_income = Decimal(str(taxable_income))

        if total_gains < 0:
            raise ValueError("Total gains cannot be negative")

        if annual_exclusion_used < 0:
            raise ValueError("Annual exclusion used cannot be negative")

        # Default inclusion rate to 40% (individuals)
        if inclusion_rate is None:
            inclusion_rate = self.CGT_INCLUSION_RATE_INDIVIDUAL
        else:
            inclusion_rate = Decimal(str(inclusion_rate))

        # Calculate remaining annual exclusion
        remaining_exclusion = max(
            self.CGT_ANNUAL_EXCLUSION - annual_exclusion_used,
            Decimal("0")
        )

        # Apply exclusion
        exclusion_used = min(total_gains, remaining_exclusion)
        gain_after_exclusion = max(total_gains - exclusion_used, Decimal("0"))

        # Apply inclusion rate
        included_amount = self._round_currency(gain_after_exclusion * inclusion_rate)

        if included_amount == 0:
            return {
                "cgt_owed": Decimal("0.00"),
                "taxable_gain": self._round_currency(gain_after_exclusion),
                "included_amount": Decimal("0.00"),
                "exclusion_used": self._round_currency(exclusion_used),
                "effective_cgt_rate": float(Decimal("0")),
                "total_gains": self._round_currency(total_gains),
                "inclusion_rate": float(inclusion_rate * 100)
            }

        # Calculate tax on income + included gain
        tax_with_gain = self.calculate_income_tax(
            taxable_income + included_amount,
            age=age
        )["tax_owed"]

        # Calculate tax on income only
        tax_without_gain = self.calculate_income_tax(
            taxable_income,
            age=age
        )["tax_owed"]

        # CGT is the difference
        cgt_owed = tax_with_gain - tax_without_gain

        # Calculate effective CGT rate (as % of total gain, not included amount)
        effective_cgt_rate = Decimal("0")
        if total_gains > 0:
            effective_cgt_rate = self._round_percentage((cgt_owed / total_gains) * 100)

        return {
            "cgt_owed": self._round_currency(cgt_owed),
            "taxable_gain": self._round_currency(gain_after_exclusion),
            "included_amount": self._round_currency(included_amount),
            "exclusion_used": self._round_currency(exclusion_used),
            "effective_cgt_rate": float(effective_cgt_rate),
            "total_gains": self._round_currency(total_gains),
            "inclusion_rate": float(inclusion_rate * 100)
        }

    def calculate_dividend_tax(
        self,
        dividend_income: Decimal,
        exemption_used: Decimal = Decimal("0")
    ) -> Dict:
        """
        Calculate SA Dividend Withholding Tax.

        SA dividends from local companies are subject to 20% withholding tax.
        There is an exemption for the first R23,800 per year.

        Args:
            dividend_income: Total dividend income
            exemption_used: Amount of exemption already used

        Returns:
            Dictionary containing:
            - dividend_tax_owed: Total dividend tax payable
            - taxable_dividends: Dividends after exemption
            - exemption_used: Exemption amount applied
        """
        # Convert to Decimal
        dividend_income = Decimal(str(dividend_income))
        exemption_used = Decimal(str(exemption_used))

        if dividend_income < 0:
            raise ValueError("Dividend income cannot be negative")

        if exemption_used < 0:
            raise ValueError("Exemption used cannot be negative")

        # Calculate remaining exemption
        remaining_exemption = max(
            self.DIVIDEND_EXEMPTION - exemption_used,
            Decimal("0")
        )

        # Apply exemption
        exemption_applied = min(dividend_income, remaining_exemption)
        taxable_dividends = max(dividend_income - exemption_applied, Decimal("0"))

        # Calculate dividend tax (20%)
        dividend_tax = self._round_currency(taxable_dividends * self.DIVIDEND_TAX_RATE)

        return {
            "dividend_tax_owed": dividend_tax,
            "taxable_dividends": self._round_currency(taxable_dividends),
            "exemption_used": self._round_currency(exemption_applied),
            "gross_dividends": self._round_currency(dividend_income),
            "tax_rate": float(self.DIVIDEND_TAX_RATE * 100)
        }


# Singleton instance
sa_tax_service = SATaxService()
