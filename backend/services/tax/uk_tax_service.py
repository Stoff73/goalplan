"""
UK Tax Calculation Service

This service provides comprehensive UK tax calculations for the 2024/25 tax year,
including Income Tax, National Insurance, Capital Gains Tax, and Dividend Tax.

All calculations follow HMRC specifications and use high-precision decimal arithmetic
to ensure accuracy in financial calculations.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Literal
from datetime import datetime


class UKTaxService:
    """
    Service for calculating UK taxes for the 2024/25 tax year.

    Supports:
    - Income Tax (England/Wales/NI and Scottish rates)
    - National Insurance (Class 1, 2, and 4)
    - Capital Gains Tax
    - Dividend Tax
    """

    # 2024/25 Tax Year Constants
    PERSONAL_ALLOWANCE = Decimal("12570.00")
    PERSONAL_ALLOWANCE_TAPER_THRESHOLD = Decimal("100000.00")

    # Income Tax Bands (England/Wales/NI)
    BASIC_RATE_UPPER = Decimal("50270.00")
    HIGHER_RATE_UPPER = Decimal("125140.00")

    BASIC_RATE = Decimal("0.20")
    HIGHER_RATE = Decimal("0.40")
    ADDITIONAL_RATE = Decimal("0.45")

    # National Insurance
    NI_PRIMARY_THRESHOLD = Decimal("12570.00")
    NI_UPPER_EARNINGS_LIMIT = Decimal("50270.00")
    NI_CLASS_1_RATE = Decimal("0.12")
    NI_CLASS_1_ADDITIONAL_RATE = Decimal("0.02")

    NI_CLASS_2_THRESHOLD = Decimal("6725.00")
    NI_CLASS_2_WEEKLY_RATE = Decimal("3.45")

    NI_CLASS_4_LOWER = Decimal("12570.00")
    NI_CLASS_4_UPPER = Decimal("50270.00")
    NI_CLASS_4_RATE = Decimal("0.09")
    NI_CLASS_4_ADDITIONAL_RATE = Decimal("0.02")

    # Capital Gains Tax
    CGT_ANNUAL_EXEMPTION = Decimal("3000.00")
    CGT_BASIC_RATE_OTHER = Decimal("0.10")
    CGT_HIGHER_RATE_OTHER = Decimal("0.20")
    CGT_BASIC_RATE_PROPERTY = Decimal("0.18")
    CGT_HIGHER_RATE_PROPERTY = Decimal("0.24")

    # Dividend Tax
    DIVIDEND_ALLOWANCE = Decimal("500.00")
    DIVIDEND_BASIC_RATE = Decimal("0.0875")
    DIVIDEND_HIGHER_RATE = Decimal("0.3375")
    DIVIDEND_ADDITIONAL_RATE = Decimal("0.3935")

    @staticmethod
    def _round_currency(amount: Decimal) -> Decimal:
        """Round to 2 decimal places using banker's rounding."""
        return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @staticmethod
    def _round_percentage(rate: Decimal) -> Decimal:
        """Round percentage to 2 decimal places."""
        return rate.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def calculate_income_tax(
        self,
        income: Decimal,
        tax_year: str = "2024/25",
        is_scottish_resident: bool = False
    ) -> Dict:
        """
        Calculate UK Income Tax for a given income.

        Args:
            income: Gross income amount
            tax_year: Tax year (currently only 2024/25 supported)
            is_scottish_resident: Whether taxpayer is Scottish resident

        Returns:
            Dictionary containing:
            - tax_owed: Total tax payable
            - effective_rate: Effective tax rate as percentage
            - breakdown: List of tax by band
            - personal_allowance: Personal allowance used
            - taxable_income: Income after personal allowance
        """
        if tax_year != "2024/25":
            raise ValueError(f"Tax year {tax_year} not supported. Only 2024/25 available.")

        # Convert to Decimal first
        income = Decimal(str(income))

        if income < 0:
            raise ValueError("Income cannot be negative")

        # Calculate personal allowance with tapering
        personal_allowance = self.PERSONAL_ALLOWANCE

        if income > self.PERSONAL_ALLOWANCE_TAPER_THRESHOLD:
            # £1 reduction for every £2 over £100,000
            taper_amount = (income - self.PERSONAL_ALLOWANCE_TAPER_THRESHOLD) / 2
            personal_allowance = max(personal_allowance - taper_amount, Decimal("0"))

        # Calculate taxable income
        taxable_income = max(income - personal_allowance, Decimal("0"))

        # Tax bands (Scotland has different rates - not implemented in this version)
        if is_scottish_resident:
            raise NotImplementedError("Scottish tax rates not yet implemented")

        # Calculate tax by band
        # Tax bands apply to TAXABLE income (after personal allowance deducted)
        # Basic rate: £0 - £37,700 of taxable income (20%)
        # Higher rate: £37,701 - £112,570 of taxable income (40%)
        # Additional rate: £112,571+ of taxable income (45%)

        breakdown = []
        total_tax = Decimal("0")
        remaining_income = taxable_income

        # Basic rate band size (after personal allowance)
        basic_rate_band_size = self.BASIC_RATE_UPPER - self.PERSONAL_ALLOWANCE  # £37,700

        # Higher rate band threshold (where additional rate starts, after PA)
        additional_rate_start = self.HIGHER_RATE_UPPER - self.PERSONAL_ALLOWANCE  # £112,570

        # Basic rate band (20% on first £37,700 of taxable income)
        if remaining_income > 0:
            taxable_at_basic = min(remaining_income, basic_rate_band_size)
            tax_at_basic = self._round_currency(taxable_at_basic * self.BASIC_RATE)

            breakdown.append({
                "band": "Basic rate",
                "amount": self._round_currency(taxable_at_basic),
                "rate": float(self.BASIC_RATE * 100),
                "tax": tax_at_basic
            })

            total_tax += tax_at_basic
            remaining_income -= taxable_at_basic

        # Higher rate band (40% on £37,701 - £112,570 of taxable income)
        higher_rate_band_size = additional_rate_start - basic_rate_band_size  # £74,870
        if remaining_income > 0:
            taxable_at_higher = min(remaining_income, higher_rate_band_size)
            tax_at_higher = self._round_currency(taxable_at_higher * self.HIGHER_RATE)

            breakdown.append({
                "band": "Higher rate",
                "amount": self._round_currency(taxable_at_higher),
                "rate": float(self.HIGHER_RATE * 100),
                "tax": tax_at_higher
            })

            total_tax += tax_at_higher
            remaining_income -= taxable_at_higher

        # Additional rate band (45% on £112,571+ of taxable income)
        if remaining_income > 0:
            tax_at_additional = self._round_currency(remaining_income * self.ADDITIONAL_RATE)

            breakdown.append({
                "band": "Additional rate",
                "amount": self._round_currency(remaining_income),
                "rate": float(self.ADDITIONAL_RATE * 100),
                "tax": tax_at_additional
            })

            total_tax += tax_at_additional

        # Calculate effective rate
        effective_rate = Decimal("0")
        if income > 0:
            effective_rate = self._round_percentage((total_tax / income) * 100)

        return {
            "tax_owed": self._round_currency(total_tax),
            "effective_rate": float(effective_rate),
            "breakdown": breakdown,
            "personal_allowance": self._round_currency(personal_allowance),
            "taxable_income": self._round_currency(taxable_income),
            "gross_income": self._round_currency(income)
        }

    def calculate_national_insurance(
        self,
        employment_income: Decimal,
        is_self_employed: bool = False,
        profits: Decimal = Decimal("0")
    ) -> Dict:
        """
        Calculate National Insurance contributions.

        Args:
            employment_income: Employment income for Class 1 NI
            is_self_employed: Whether self-employed (for Class 2 & 4)
            profits: Self-employment profits for Class 4 NI

        Returns:
            Dictionary containing:
            - ni_owed: Total NI payable
            - class_1: Class 1 NI (employees)
            - class_2: Class 2 NI (self-employed)
            - class_4: Class 4 NI (self-employed)
            - breakdown: Detailed breakdown
        """
        # Convert to Decimal first
        employment_income = Decimal(str(employment_income))
        profits = Decimal(str(profits))

        if employment_income < 0 or profits < 0:
            raise ValueError("Income and profits cannot be negative")

        class_1_ni = Decimal("0")
        class_2_ni = Decimal("0")
        class_4_ni = Decimal("0")
        breakdown = []

        # Class 1 NI (Employees)
        if employment_income > 0:
            if employment_income > self.NI_PRIMARY_THRESHOLD:
                # 12% on £12,570 - £50,270
                band_1_income = min(
                    employment_income - self.NI_PRIMARY_THRESHOLD,
                    self.NI_UPPER_EARNINGS_LIMIT - self.NI_PRIMARY_THRESHOLD
                )
                class_1_band_1 = self._round_currency(band_1_income * self.NI_CLASS_1_RATE)
                class_1_ni += class_1_band_1

                breakdown.append({
                    "type": "Class 1",
                    "band": "Primary (12%)",
                    "amount": self._round_currency(band_1_income),
                    "rate": float(self.NI_CLASS_1_RATE * 100),
                    "ni": class_1_band_1
                })

                # 2% on income above £50,270
                if employment_income > self.NI_UPPER_EARNINGS_LIMIT:
                    band_2_income = employment_income - self.NI_UPPER_EARNINGS_LIMIT
                    class_1_band_2 = self._round_currency(band_2_income * self.NI_CLASS_1_ADDITIONAL_RATE)
                    class_1_ni += class_1_band_2

                    breakdown.append({
                        "type": "Class 1",
                        "band": "Additional (2%)",
                        "amount": self._round_currency(band_2_income),
                        "rate": float(self.NI_CLASS_1_ADDITIONAL_RATE * 100),
                        "ni": class_1_band_2
                    })

        # Class 2 & 4 NI (Self-Employed)
        if is_self_employed:
            # Class 2: £3.45/week if profits > £6,725
            if profits > self.NI_CLASS_2_THRESHOLD:
                class_2_ni = self._round_currency(self.NI_CLASS_2_WEEKLY_RATE * 52)

                breakdown.append({
                    "type": "Class 2",
                    "band": "Weekly (£3.45)",
                    "amount": self._round_currency(profits),
                    "rate": "Flat",
                    "ni": class_2_ni
                })

            # Class 4: 9% on £12,570 - £50,270, 2% above
            if profits > self.NI_CLASS_4_LOWER:
                # 9% band
                band_1_profits = min(
                    profits - self.NI_CLASS_4_LOWER,
                    self.NI_CLASS_4_UPPER - self.NI_CLASS_4_LOWER
                )
                class_4_band_1 = self._round_currency(band_1_profits * self.NI_CLASS_4_RATE)
                class_4_ni += class_4_band_1

                breakdown.append({
                    "type": "Class 4",
                    "band": "Main (9%)",
                    "amount": self._round_currency(band_1_profits),
                    "rate": float(self.NI_CLASS_4_RATE * 100),
                    "ni": class_4_band_1
                })

                # 2% band
                if profits > self.NI_CLASS_4_UPPER:
                    band_2_profits = profits - self.NI_CLASS_4_UPPER
                    class_4_band_2 = self._round_currency(band_2_profits * self.NI_CLASS_4_ADDITIONAL_RATE)
                    class_4_ni += class_4_band_2

                    breakdown.append({
                        "type": "Class 4",
                        "band": "Additional (2%)",
                        "amount": self._round_currency(band_2_profits),
                        "rate": float(self.NI_CLASS_4_ADDITIONAL_RATE * 100),
                        "ni": class_4_band_2
                    })

        total_ni = class_1_ni + class_2_ni + class_4_ni

        return {
            "ni_owed": self._round_currency(total_ni),
            "class_1": self._round_currency(class_1_ni),
            "class_2": self._round_currency(class_2_ni),
            "class_4": self._round_currency(class_4_ni),
            "breakdown": breakdown
        }

    def calculate_cgt(
        self,
        total_gains: Decimal,
        annual_exempt_amount_used: Decimal = Decimal("0"),
        is_higher_rate_taxpayer: bool = False,
        is_property: bool = False
    ) -> Dict:
        """
        Calculate Capital Gains Tax.

        Args:
            total_gains: Total capital gains for the year
            annual_exempt_amount_used: Amount of annual exemption already used
            is_higher_rate_taxpayer: Whether taxpayer pays higher/additional rate income tax
            is_property: Whether gains are from residential property

        Returns:
            Dictionary containing:
            - cgt_owed: Total CGT payable
            - taxable_gain: Gain after exemption
            - exempt_amount: Exemption used
            - rate_applied: Tax rate applied (%)
        """
        # Convert to Decimal first
        total_gains = Decimal(str(total_gains))
        annual_exempt_amount_used = Decimal(str(annual_exempt_amount_used))

        if total_gains < 0:
            raise ValueError("Total gains cannot be negative")

        if annual_exempt_amount_used < 0:
            raise ValueError("Annual exempt amount used cannot be negative")

        # Calculate remaining annual exemption
        remaining_exemption = max(
            self.CGT_ANNUAL_EXEMPTION - annual_exempt_amount_used,
            Decimal("0")
        )

        # Apply exemption to gains
        exempt_amount = min(total_gains, remaining_exemption)
        taxable_gain = max(total_gains - exempt_amount, Decimal("0"))

        # Determine rate based on property type and taxpayer band
        if is_property:
            rate = self.CGT_HIGHER_RATE_PROPERTY if is_higher_rate_taxpayer else self.CGT_BASIC_RATE_PROPERTY
        else:
            rate = self.CGT_HIGHER_RATE_OTHER if is_higher_rate_taxpayer else self.CGT_BASIC_RATE_OTHER

        # Calculate CGT
        cgt_owed = self._round_currency(taxable_gain * rate)

        return {
            "cgt_owed": cgt_owed,
            "taxable_gain": self._round_currency(taxable_gain),
            "exempt_amount": self._round_currency(exempt_amount),
            "rate_applied": float(rate * 100),
            "total_gains": self._round_currency(total_gains)
        }

    def calculate_dividend_tax(
        self,
        dividend_income: Decimal,
        other_income: Decimal = Decimal("0")
    ) -> Dict:
        """
        Calculate Dividend Tax.

        Dividends are taxed after other income, so we need to know total other income
        to determine which tax band the dividends fall into.

        Args:
            dividend_income: Total dividend income
            other_income: Other taxable income (employment, rental, etc.)

        Returns:
            Dictionary containing:
            - dividend_tax_owed: Total dividend tax payable
            - taxable_dividends: Dividends after allowance
            - allowance_used: Dividend allowance used
            - breakdown: Tax breakdown by band
        """
        # Convert to Decimal first
        dividend_income = Decimal(str(dividend_income))
        other_income = Decimal(str(other_income))

        if dividend_income < 0 or other_income < 0:
            raise ValueError("Income amounts cannot be negative")

        # Apply dividend allowance
        allowance_used = min(dividend_income, self.DIVIDEND_ALLOWANCE)
        taxable_dividends = max(dividend_income - allowance_used, Decimal("0"))

        if taxable_dividends == 0:
            return {
                "dividend_tax_owed": Decimal("0.00"),
                "taxable_dividends": Decimal("0.00"),
                "allowance_used": self._round_currency(allowance_used),
                "breakdown": []
            }

        # Calculate personal allowance (considering tapering)
        personal_allowance = self.PERSONAL_ALLOWANCE
        if other_income > self.PERSONAL_ALLOWANCE_TAPER_THRESHOLD:
            taper_amount = (other_income - self.PERSONAL_ALLOWANCE_TAPER_THRESHOLD) / 2
            personal_allowance = max(personal_allowance - taper_amount, Decimal("0"))

        # Calculate taxable other income
        taxable_other_income = max(other_income - personal_allowance, Decimal("0"))

        # Total taxable income including dividends (before allowance)
        total_income_position = taxable_other_income + taxable_dividends

        # Tax band thresholds after personal allowance
        basic_rate_band_size = self.BASIC_RATE_UPPER - self.PERSONAL_ALLOWANCE  # £37,700
        higher_rate_threshold = basic_rate_band_size  # £37,700
        additional_rate_threshold = self.HIGHER_RATE_UPPER - self.PERSONAL_ALLOWANCE  # £112,570

        # Determine how dividends fall into tax bands
        dividends_at_basic = Decimal("0")
        dividends_at_higher = Decimal("0")
        dividends_at_additional = Decimal("0")

        # Start of dividend income in tax bands
        dividend_start = taxable_other_income
        dividend_end = total_income_position

        # Calculate dividends in basic rate band
        if dividend_start < higher_rate_threshold:
            dividends_at_basic = min(
                taxable_dividends,
                higher_rate_threshold - dividend_start
            )

        # Calculate dividends in higher rate band
        if dividend_end > higher_rate_threshold:
            higher_band_start = max(dividend_start, higher_rate_threshold)
            higher_band_end = min(dividend_end, additional_rate_threshold)
            if higher_band_end > higher_band_start:
                dividends_at_higher = higher_band_end - higher_band_start

        # Calculate dividends in additional rate band
        if dividend_end > additional_rate_threshold:
            additional_band_start = max(dividend_start, additional_rate_threshold)
            dividends_at_additional = dividend_end - additional_band_start

        # Calculate tax
        breakdown = []
        total_tax = Decimal("0")

        if dividends_at_basic > 0:
            tax_at_basic = self._round_currency(dividends_at_basic * self.DIVIDEND_BASIC_RATE)
            total_tax += tax_at_basic

            breakdown.append({
                "band": "Basic rate",
                "amount": self._round_currency(dividends_at_basic),
                "rate": float(self.DIVIDEND_BASIC_RATE * 100),
                "tax": tax_at_basic
            })

        if dividends_at_higher > 0:
            tax_at_higher = self._round_currency(dividends_at_higher * self.DIVIDEND_HIGHER_RATE)
            total_tax += tax_at_higher

            breakdown.append({
                "band": "Higher rate",
                "amount": self._round_currency(dividends_at_higher),
                "rate": float(self.DIVIDEND_HIGHER_RATE * 100),
                "tax": tax_at_higher
            })

        if dividends_at_additional > 0:
            tax_at_additional = self._round_currency(dividends_at_additional * self.DIVIDEND_ADDITIONAL_RATE)
            total_tax += tax_at_additional

            breakdown.append({
                "band": "Additional rate",
                "amount": self._round_currency(dividends_at_additional),
                "rate": float(self.DIVIDEND_ADDITIONAL_RATE * 100),
                "tax": tax_at_additional
            })

        return {
            "dividend_tax_owed": self._round_currency(total_tax),
            "taxable_dividends": self._round_currency(taxable_dividends),
            "allowance_used": self._round_currency(allowance_used),
            "breakdown": breakdown
        }


# Singleton instance
uk_tax_service = UKTaxService()
