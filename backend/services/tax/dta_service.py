"""
DTA (Double Tax Agreement) Relief Service

This service provides calculations for UK-SA Double Tax Agreement relief,
including employment income, dividends, interest, capital gains, pensions,
and dual residence tie-breaker rules.

All calculations follow the UK-SA DTA specifications (effective from 2002).
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Optional
from .uk_tax_service import uk_tax_service
from .sa_tax_service import sa_tax_service


class DTAService:
    """
    Service for calculating Double Tax Agreement relief between UK and SA.

    Implements:
    - Employment income relief
    - Dividend relief (15% withholding limit)
    - Interest relief (0% withholding)
    - Capital gains relief
    - Pension relief
    - Tie-breaker rules for dual residents
    """

    # UK-SA DTA withholding rates
    DIVIDEND_WITHHOLDING_RATE = Decimal("0.15")  # 15% max
    INTEREST_WITHHOLDING_RATE = Decimal("0.00")  # 0% (no withholding)

    @staticmethod
    def _round_currency(amount: Decimal) -> Decimal:
        """Round to 2 decimal places."""
        return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def calculate_employment_income_relief(
        self,
        uk_income: Decimal,
        sa_income: Decimal,
        uk_resident: bool,
        sa_resident: bool
    ) -> Dict:
        """
        Calculate DTA relief for employment income.

        Rules:
        - If UK resident earning SA income: SA taxes first, UK gives foreign tax credit
        - If SA resident earning UK income: UK taxes first, SA gives foreign tax credit
        - If dual resident: Apply tie-breaker rules first

        Args:
            uk_income: Employment income from UK sources
            sa_income: Employment income from SA sources
            uk_resident: Whether taxpayer is UK resident
            sa_resident: Whether taxpayer is SA resident

        Returns:
            Dictionary with UK tax, SA tax, relief amount, net tax, and explanation
        """
        uk_income = Decimal(str(uk_income))
        sa_income = Decimal(str(sa_income))

        # Handle non-resident cases
        if not uk_resident and not sa_resident:
            return {
                "uk_tax": Decimal("0.00"),
                "sa_tax": Decimal("0.00"),
                "relief": Decimal("0.00"),
                "net_tax": Decimal("0.00"),
                "explanation": "Not resident in either country - no tax liability"
            }

        # Calculate UK tax on UK income
        uk_tax_on_uk_income = Decimal("0.00")
        if uk_income > 0:
            uk_calc = uk_tax_service.calculate_income_tax(uk_income)
            uk_tax_on_uk_income = uk_calc["tax_owed"]

        # Calculate SA tax on SA income
        sa_tax_on_sa_income = Decimal("0.00")
        if sa_income > 0:
            sa_calc = sa_tax_service.calculate_income_tax(sa_income)
            sa_tax_on_sa_income = sa_calc["tax_owed"]

        # Scenario 1: UK resident only
        if uk_resident and not sa_resident:
            # UK taxes worldwide income
            # SA taxes only SA-source income
            total_uk_income = uk_income + sa_income
            uk_tax_on_total = Decimal("0.00")
            if total_uk_income > 0:
                uk_calc = uk_tax_service.calculate_income_tax(total_uk_income)
                uk_tax_on_total = uk_calc["tax_owed"]

            # Foreign tax credit for SA tax paid
            foreign_tax_credit = min(sa_tax_on_sa_income, uk_tax_on_total - uk_tax_on_uk_income)

            return {
                "uk_tax": self._round_currency(uk_tax_on_total - foreign_tax_credit),
                "sa_tax": self._round_currency(sa_tax_on_sa_income),
                "relief": self._round_currency(foreign_tax_credit),
                "net_tax": self._round_currency(uk_tax_on_total - foreign_tax_credit + sa_tax_on_sa_income),
                "explanation": "UK resident: SA taxes SA income first, UK gives credit for SA tax paid"
            }

        # Scenario 2: SA resident only
        if sa_resident and not uk_resident:
            # SA taxes worldwide income
            # UK taxes only UK-source income
            total_sa_income = uk_income + sa_income
            sa_tax_on_total = Decimal("0.00")
            if total_sa_income > 0:
                sa_calc = sa_tax_service.calculate_income_tax(total_sa_income)
                sa_tax_on_total = sa_calc["tax_owed"]

            # Foreign tax credit for UK tax paid
            foreign_tax_credit = min(uk_tax_on_uk_income, sa_tax_on_total - sa_tax_on_sa_income)

            return {
                "uk_tax": self._round_currency(uk_tax_on_uk_income),
                "sa_tax": self._round_currency(sa_tax_on_total - foreign_tax_credit),
                "relief": self._round_currency(foreign_tax_credit),
                "net_tax": self._round_currency(uk_tax_on_uk_income + sa_tax_on_total - foreign_tax_credit),
                "explanation": "SA resident: UK taxes UK income first, SA gives credit for UK tax paid"
            }

        # Scenario 3: Dual resident (both UK and SA)
        # Calculate total tax in each country
        total_income = uk_income + sa_income
        uk_tax_on_total = Decimal("0.00")
        sa_tax_on_total = Decimal("0.00")

        if total_income > 0:
            uk_calc = uk_tax_service.calculate_income_tax(total_income)
            uk_tax_on_total = uk_calc["tax_owed"]

            sa_calc = sa_tax_service.calculate_income_tax(total_income)
            sa_tax_on_total = sa_calc["tax_owed"]

        # For dual residents, apply tie-breaker to determine which country gives credit
        # Simplified: assume UK gives credit (in practice, tie-breaker rules apply)
        foreign_tax_credit = min(sa_tax_on_total, uk_tax_on_total)

        return {
            "uk_tax": self._round_currency(uk_tax_on_total - foreign_tax_credit),
            "sa_tax": self._round_currency(sa_tax_on_total),
            "relief": self._round_currency(foreign_tax_credit),
            "net_tax": self._round_currency(max(uk_tax_on_total, sa_tax_on_total)),
            "explanation": "Dual resident: Apply tie-breaker rules (simplified - UK gives credit for SA tax)"
        }

    def calculate_dividend_relief(
        self,
        dividend_amount: Decimal,
        source_country: str,
        residence_country: str,
        withholding_rate: Optional[Decimal] = None
    ) -> Dict:
        """
        Calculate DTA relief for dividend income.

        Rules:
        - UK-SA DTA: 15% withholding limit on dividends
        - Source country withholds tax
        - Residence country gives credit for withholding

        Args:
            dividend_amount: Dividend amount
            source_country: Country where dividend sourced ('UK' or 'SA')
            residence_country: Country of residence ('UK' or 'SA')
            withholding_rate: Optional custom withholding rate (default 15%)

        Returns:
            Dictionary with withholding tax, residence tax, foreign tax credit, and net tax
        """
        dividend_amount = Decimal(str(dividend_amount))

        if withholding_rate is None:
            withholding_rate = self.DIVIDEND_WITHHOLDING_RATE
        else:
            withholding_rate = Decimal(str(withholding_rate))

        if source_country not in ["UK", "SA"] or residence_country not in ["UK", "SA"]:
            raise ValueError("Country must be 'UK' or 'SA'")

        # Same country - no DTA relief needed
        if source_country == residence_country:
            if residence_country == "UK":
                uk_calc = uk_tax_service.calculate_dividend_tax(dividend_amount, Decimal("0"))
                residence_tax = uk_calc["dividend_tax_owed"]
            else:
                # SA: 20% dividends tax
                residence_tax = self._round_currency(dividend_amount * Decimal("0.20"))

            return {
                "withholding_tax": Decimal("0.00"),
                "residence_tax": self._round_currency(residence_tax),
                "foreign_tax_credit": Decimal("0.00"),
                "net_tax": self._round_currency(residence_tax),
                "explanation": f"Source and residence both in {residence_country} - no DTA relief needed"
            }

        # Cross-border dividends
        # Source country withholds at DTA rate
        withholding_tax = self._round_currency(dividend_amount * withholding_rate)

        # Residence country calculates tax on gross dividend
        if residence_country == "UK":
            uk_calc = uk_tax_service.calculate_dividend_tax(dividend_amount, Decimal("0"))
            residence_tax_gross = uk_calc["dividend_tax_owed"]
        else:
            # SA: 20% dividends tax
            residence_tax_gross = self._round_currency(dividend_amount * Decimal("0.20"))

        # Foreign tax credit (limited to residence country tax)
        foreign_tax_credit = min(withholding_tax, residence_tax_gross)

        # Net residence tax after credit
        residence_tax_net = max(residence_tax_gross - foreign_tax_credit, Decimal("0"))

        # Total tax paid
        net_tax = withholding_tax + residence_tax_net

        return {
            "withholding_tax": self._round_currency(withholding_tax),
            "residence_tax": self._round_currency(residence_tax_gross),
            "foreign_tax_credit": self._round_currency(foreign_tax_credit),
            "net_tax": self._round_currency(net_tax),
            "explanation": f"{source_country} withholds {float(withholding_rate * 100)}%, {residence_country} gives credit"
        }

    def calculate_interest_relief(
        self,
        interest_amount: Decimal,
        source_country: str,
        residence_country: str
    ) -> Dict:
        """
        Calculate DTA relief for interest income.

        Rules:
        - UK-SA DTA: 0% withholding on interest
        - Taxed only in residence country

        Args:
            interest_amount: Interest amount
            source_country: Country where interest sourced ('UK' or 'SA')
            residence_country: Country of residence ('UK' or 'SA')

        Returns:
            Dictionary with withholding tax (0), residence tax, and net tax
        """
        interest_amount = Decimal(str(interest_amount))

        if source_country not in ["UK", "SA"] or residence_country not in ["UK", "SA"]:
            raise ValueError("Country must be 'UK' or 'SA'")

        # Calculate residence country tax
        if residence_country == "UK":
            # UK: Interest taxed as income at marginal rate (simplified)
            uk_calc = uk_tax_service.calculate_income_tax(interest_amount)
            residence_tax = uk_calc["tax_owed"]
        else:
            # SA: Interest taxed as income
            sa_calc = sa_tax_service.calculate_income_tax(interest_amount)
            residence_tax = sa_calc["tax_owed"]

        return {
            "withholding_tax": Decimal("0.00"),
            "residence_tax": self._round_currency(residence_tax),
            "net_tax": self._round_currency(residence_tax),
            "explanation": f"UK-SA DTA: 0% withholding on interest, taxed only in {residence_country}"
        }

    def calculate_capital_gains_relief(
        self,
        gain_amount: Decimal,
        asset_type: str,
        asset_location: str,
        residence_country: str
    ) -> Dict:
        """
        Calculate DTA relief for capital gains.

        Rules:
        - Immovable property: Taxed where property located
        - Business property: Taxed where PE located
        - Shares/securities: Taxed in residence country (unless >50% immovable property)

        Args:
            gain_amount: Capital gain amount
            asset_type: Asset type ('IMMOVABLE_PROPERTY', 'BUSINESS_PROPERTY', 'SHARES', 'OTHER')
            asset_location: Country where asset located ('UK' or 'SA')
            residence_country: Country of residence ('UK' or 'SA')

        Returns:
            Dictionary with taxing country, tax amount, relief country, and explanation
        """
        gain_amount = Decimal(str(gain_amount))

        if asset_location not in ["UK", "SA"] or residence_country not in ["UK", "SA"]:
            raise ValueError("Country must be 'UK' or 'SA'")

        # Determine taxing rights
        if asset_type == "IMMOVABLE_PROPERTY":
            # Immovable property: taxed in situs country
            taxing_country = asset_location
            explanation = "Immovable property taxed where located"

        elif asset_type == "BUSINESS_PROPERTY":
            # Business property: taxed where PE located (assume same as asset location)
            taxing_country = asset_location
            explanation = "Business property taxed where PE located"

        elif asset_type == "SHARES" and asset_location != residence_country:
            # Shares: generally taxed in residence country
            # Exception: >50% value from immovable property (not implemented here)
            taxing_country = residence_country
            explanation = "Shares taxed in residence country"

        else:
            # Other assets: taxed in residence country
            taxing_country = residence_country
            explanation = "Other assets taxed in residence country"

        # Calculate tax in taxing country
        if taxing_country == "UK":
            uk_calc = uk_tax_service.calculate_cgt(gain_amount, is_higher_rate_taxpayer=False)
            tax_amount = uk_calc["cgt_owed"]
        else:
            sa_calc = sa_tax_service.calculate_cgt(gain_amount)
            tax_amount = sa_calc["cgt_owed"]

        # Relief country (if different from taxing country)
        if taxing_country == residence_country:
            relief_country = "None"
            relief_explanation = "Taxed only in residence country"
        else:
            relief_country = residence_country
            relief_explanation = f"{relief_country} exempts gain (primary taxing rights in {taxing_country})"

        return {
            "taxing_country": taxing_country,
            "tax_amount": self._round_currency(tax_amount),
            "relief_country": relief_country,
            "explanation": f"{explanation}. {relief_explanation}"
        }

    def calculate_pension_relief(
        self,
        pension_amount: Decimal,
        pension_type: str,
        source_country: str,
        residence_country: str
    ) -> Dict:
        """
        Calculate DTA relief for pension income.

        Rules:
        - Private pensions: Taxed in residence country
        - Government pensions: Taxed in source country (paying government)

        Args:
            pension_amount: Pension amount
            pension_type: Pension type ('PRIVATE' or 'GOVERNMENT')
            source_country: Country paying pension ('UK' or 'SA')
            residence_country: Country of residence ('UK' or 'SA')

        Returns:
            Dictionary with taxing country, tax amount, and explanation
        """
        pension_amount = Decimal(str(pension_amount))

        if source_country not in ["UK", "SA"] or residence_country not in ["UK", "SA"]:
            raise ValueError("Country must be 'UK' or 'SA'")

        if pension_type not in ["PRIVATE", "GOVERNMENT"]:
            raise ValueError("Pension type must be 'PRIVATE' or 'GOVERNMENT'")

        # Determine taxing rights
        if pension_type == "PRIVATE":
            # Private pensions: taxed in residence country
            taxing_country = residence_country
            explanation = "Private pension taxed in residence country"

        else:
            # Government pensions: taxed in source country
            taxing_country = source_country
            explanation = "Government pension taxed in source country (paying state)"

        # Calculate tax in taxing country
        if taxing_country == "UK":
            uk_calc = uk_tax_service.calculate_income_tax(pension_amount)
            tax_amount = uk_calc["tax_owed"]
        else:
            sa_calc = sa_tax_service.calculate_income_tax(pension_amount)
            tax_amount = sa_calc["tax_owed"]

        return {
            "taxing_country": taxing_country,
            "tax_amount": self._round_currency(tax_amount),
            "explanation": explanation
        }

    def apply_tie_breaker_rules(
        self,
        has_uk_home: bool,
        has_sa_home: bool,
        uk_vital_interests: bool,
        sa_vital_interests: bool,
        uk_habitual_abode: bool,
        sa_habitual_abode: bool,
        nationality: str
    ) -> Dict:
        """
        Apply DTA tie-breaker rules for dual residents.

        Rules cascade in order:
        1. Permanent home (if only in one country)
        2. Centre of vital interests (family, economic ties)
        3. Habitual abode (where normally lives)
        4. Nationality

        Args:
            has_uk_home: Has permanent home in UK
            has_sa_home: Has permanent home in SA
            uk_vital_interests: Centre of vital interests in UK
            sa_vital_interests: Centre of vital interests in SA
            uk_habitual_abode: Habitual abode in UK
            sa_habitual_abode: Habitual abode in SA
            nationality: Nationality ('UK', 'SA', or 'BOTH')

        Returns:
            Dictionary with sole residence determination, test applied, and explanation
        """
        # Test 1: Permanent home
        if has_uk_home and not has_sa_home:
            return {
                "sole_residence": "UK",
                "test_applied": "Permanent home",
                "explanation": "Permanent home available only in UK"
            }

        if has_sa_home and not has_uk_home:
            return {
                "sole_residence": "SA",
                "test_applied": "Permanent home",
                "explanation": "Permanent home available only in SA"
            }

        # Test 2: Centre of vital interests (if homes in both or neither)
        if uk_vital_interests and not sa_vital_interests:
            return {
                "sole_residence": "UK",
                "test_applied": "Centre of vital interests",
                "explanation": "Closer personal and economic ties to UK"
            }

        if sa_vital_interests and not uk_vital_interests:
            return {
                "sole_residence": "SA",
                "test_applied": "Centre of vital interests",
                "explanation": "Closer personal and economic ties to SA"
            }

        # Test 3: Habitual abode
        if uk_habitual_abode and not sa_habitual_abode:
            return {
                "sole_residence": "UK",
                "test_applied": "Habitual abode",
                "explanation": "Habitually resides in UK"
            }

        if sa_habitual_abode and not uk_habitual_abode:
            return {
                "sole_residence": "SA",
                "test_applied": "Habitual abode",
                "explanation": "Habitually resides in SA"
            }

        # Test 4: Nationality
        if nationality == "UK":
            return {
                "sole_residence": "UK",
                "test_applied": "Nationality",
                "explanation": "UK national"
            }

        if nationality == "SA":
            return {
                "sole_residence": "SA",
                "test_applied": "Nationality",
                "explanation": "SA national"
            }

        # Cannot be determined - requires mutual agreement
        return {
            "sole_residence": "UNDETERMINED",
            "test_applied": "None",
            "explanation": "Cannot be determined by tie-breaker rules. Requires mutual agreement between UK and SA tax authorities."
        }


# Singleton instance
dta_service = DTAService()
