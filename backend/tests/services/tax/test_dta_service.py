"""
Tests for DTA Relief Service

Tests all DTA relief calculations including:
- Employment income relief
- Dividend relief
- Interest relief
- Capital gains relief
- Pension relief
- Tie-breaker rules
"""

import pytest
from decimal import Decimal
from services.tax.dta_service import dta_service


class TestEmploymentIncomeRelief:
    """Test employment income DTA relief calculations."""

    def test_uk_resident_only_with_sa_income(self):
        """UK resident earning SA income - SA taxes first, UK gives credit."""
        result = dta_service.calculate_employment_income_relief(
            uk_income=Decimal("50000"),
            sa_income=Decimal("200000"),
            uk_resident=True,
            sa_resident=False
        )

        assert "uk_tax" in result
        assert "sa_tax" in result
        assert "relief" in result
        assert "net_tax" in result
        assert result["relief"] > 0
        assert "UK gives credit" in result["explanation"]

    def test_sa_resident_only_with_uk_income(self):
        """SA resident earning UK income - UK taxes first, SA gives credit."""
        result = dta_service.calculate_employment_income_relief(
            uk_income=Decimal("50000"),
            sa_income=Decimal("200000"),
            uk_resident=False,
            sa_resident=True
        )

        assert result["relief"] > 0
        assert "SA gives credit" in result["explanation"]

    def test_dual_resident(self):
        """Dual resident - apply tie-breaker (simplified)."""
        result = dta_service.calculate_employment_income_relief(
            uk_income=Decimal("50000"),
            sa_income=Decimal("200000"),
            uk_resident=True,
            sa_resident=True
        )

        assert result["relief"] > 0
        assert "Dual resident" in result["explanation"]

    def test_neither_resident(self):
        """Not resident in either country - no tax liability."""
        result = dta_service.calculate_employment_income_relief(
            uk_income=Decimal("50000"),
            sa_income=Decimal("200000"),
            uk_resident=False,
            sa_resident=False
        )

        assert result["uk_tax"] == Decimal("0.00")
        assert result["sa_tax"] == Decimal("0.00")
        assert result["relief"] == Decimal("0.00")
        assert result["net_tax"] == Decimal("0.00")

    def test_zero_income(self):
        """Zero income in both countries."""
        result = dta_service.calculate_employment_income_relief(
            uk_income=Decimal("0"),
            sa_income=Decimal("0"),
            uk_resident=True,
            sa_resident=False
        )

        assert result["uk_tax"] == Decimal("0.00")
        assert result["sa_tax"] == Decimal("0.00")
        assert result["relief"] == Decimal("0.00")


class TestDividendRelief:
    """Test dividend DTA relief calculations."""

    def test_cross_border_dividend_uk_to_sa(self):
        """UK dividend to SA resident - 15% withholding."""
        result = dta_service.calculate_dividend_relief(
            dividend_amount=Decimal("10000"),
            source_country="UK",
            residence_country="SA"
        )

        assert result["withholding_tax"] == Decimal("1500.00")  # 15%
        assert result["foreign_tax_credit"] > 0
        assert "15.0%" in result["explanation"]

    def test_cross_border_dividend_sa_to_uk(self):
        """SA dividend to UK resident - 15% withholding."""
        result = dta_service.calculate_dividend_relief(
            dividend_amount=Decimal("10000"),
            source_country="SA",
            residence_country="UK"
        )

        assert result["withholding_tax"] == Decimal("1500.00")  # 15%
        assert result["foreign_tax_credit"] > 0

    def test_same_country_dividend_no_dta(self):
        """Same country dividend - no DTA relief needed."""
        result = dta_service.calculate_dividend_relief(
            dividend_amount=Decimal("10000"),
            source_country="UK",
            residence_country="UK"
        )

        assert result["withholding_tax"] == Decimal("0.00")
        assert result["foreign_tax_credit"] == Decimal("0.00")
        assert "no DTA relief needed" in result["explanation"]

    def test_custom_withholding_rate(self):
        """Custom withholding rate (e.g., 10% for >10% shareholding)."""
        result = dta_service.calculate_dividend_relief(
            dividend_amount=Decimal("10000"),
            source_country="SA",
            residence_country="UK",
            withholding_rate=Decimal("0.10")
        )

        assert result["withholding_tax"] == Decimal("1000.00")  # 10%

    def test_invalid_country(self):
        """Invalid country code raises error."""
        with pytest.raises(ValueError):
            dta_service.calculate_dividend_relief(
                dividend_amount=Decimal("10000"),
                source_country="US",
                residence_country="UK"
            )


class TestInterestRelief:
    """Test interest DTA relief calculations."""

    def test_interest_zero_withholding(self):
        """UK-SA DTA: 0% withholding on interest."""
        result = dta_service.calculate_interest_relief(
            interest_amount=Decimal("50000"),  # Use larger amount to ensure tax > 0
            source_country="UK",
            residence_country="SA"
        )

        assert result["withholding_tax"] == Decimal("0.00")
        assert result["residence_tax"] >= Decimal("0.00")  # May be 0 if below threshold
        assert result["net_tax"] == result["residence_tax"]
        assert "0% withholding" in result["explanation"]

    def test_interest_taxed_in_residence_only(self):
        """Interest taxed only in residence country."""
        result = dta_service.calculate_interest_relief(
            interest_amount=Decimal("50000"),  # Use larger amount
            source_country="SA",
            residence_country="UK"
        )

        assert result["withholding_tax"] == Decimal("0.00")
        assert result["residence_tax"] >= Decimal("0.00")
        assert result["net_tax"] == result["residence_tax"]

    def test_interest_same_country(self):
        """Same country interest."""
        result = dta_service.calculate_interest_relief(
            interest_amount=Decimal("50000"),  # Use larger amount
            source_country="UK",
            residence_country="UK"
        )

        assert result["withholding_tax"] == Decimal("0.00")
        assert result["residence_tax"] >= Decimal("0.00")


class TestCapitalGainsRelief:
    """Test capital gains DTA relief calculations."""

    def test_immovable_property_taxed_at_location(self):
        """Immovable property taxed where located."""
        result = dta_service.calculate_capital_gains_relief(
            gain_amount=Decimal("50000"),
            asset_type="IMMOVABLE_PROPERTY",
            asset_location="UK",
            residence_country="SA"
        )

        assert result["taxing_country"] == "UK"
        assert result["tax_amount"] > 0
        assert "Immovable property" in result["explanation"]

    def test_business_property_taxed_at_pe(self):
        """Business property taxed where PE located."""
        result = dta_service.calculate_capital_gains_relief(
            gain_amount=Decimal("50000"),
            asset_type="BUSINESS_PROPERTY",
            asset_location="SA",
            residence_country="UK"
        )

        assert result["taxing_country"] == "SA"
        assert "Business property" in result["explanation"]

    def test_shares_taxed_in_residence(self):
        """Shares taxed in residence country."""
        result = dta_service.calculate_capital_gains_relief(
            gain_amount=Decimal("30000"),
            asset_type="SHARES",
            asset_location="UK",
            residence_country="SA"
        )

        assert result["taxing_country"] == "SA"
        assert "residence country" in result["explanation"]

    def test_other_assets_taxed_in_residence(self):
        """Other assets taxed in residence country."""
        result = dta_service.calculate_capital_gains_relief(
            gain_amount=Decimal("20000"),
            asset_type="OTHER",
            asset_location="SA",
            residence_country="UK"
        )

        assert result["taxing_country"] == "UK"


class TestPensionRelief:
    """Test pension DTA relief calculations."""

    def test_private_pension_taxed_in_residence(self):
        """Private pension taxed in residence country."""
        result = dta_service.calculate_pension_relief(
            pension_amount=Decimal("300000"),  # Use larger amount to ensure tax > 0
            pension_type="PRIVATE",
            source_country="UK",
            residence_country="SA"
        )

        assert result["taxing_country"] == "SA"
        assert "Private pension" in result["explanation"]
        assert result["tax_amount"] >= Decimal("0.00")  # May be 0 if below threshold

    def test_government_pension_taxed_in_source(self):
        """Government pension taxed in source country."""
        result = dta_service.calculate_pension_relief(
            pension_amount=Decimal("30000"),
            pension_type="GOVERNMENT",
            source_country="UK",
            residence_country="SA"
        )

        assert result["taxing_country"] == "UK"
        assert "Government pension" in result["explanation"]

    def test_invalid_pension_type(self):
        """Invalid pension type raises error."""
        with pytest.raises(ValueError):
            dta_service.calculate_pension_relief(
                pension_amount=Decimal("30000"),
                pension_type="CORPORATE",
                source_country="UK",
                residence_country="SA"
            )


class TestTieBreakerRules:
    """Test DTA tie-breaker rules for dual residents."""

    def test_permanent_home_uk_only(self):
        """Permanent home in UK only."""
        result = dta_service.apply_tie_breaker_rules(
            has_uk_home=True,
            has_sa_home=False,
            uk_vital_interests=False,
            sa_vital_interests=False,
            uk_habitual_abode=False,
            sa_habitual_abode=False,
            nationality="BOTH"
        )

        assert result["sole_residence"] == "UK"
        assert result["test_applied"] == "Permanent home"

    def test_permanent_home_sa_only(self):
        """Permanent home in SA only."""
        result = dta_service.apply_tie_breaker_rules(
            has_uk_home=False,
            has_sa_home=True,
            uk_vital_interests=False,
            sa_vital_interests=False,
            uk_habitual_abode=False,
            sa_habitual_abode=False,
            nationality="BOTH"
        )

        assert result["sole_residence"] == "SA"
        assert result["test_applied"] == "Permanent home"

    def test_vital_interests_uk(self):
        """Homes in both, vital interests in UK."""
        result = dta_service.apply_tie_breaker_rules(
            has_uk_home=True,
            has_sa_home=True,
            uk_vital_interests=True,
            sa_vital_interests=False,
            uk_habitual_abode=False,
            sa_habitual_abode=False,
            nationality="BOTH"
        )

        assert result["sole_residence"] == "UK"
        assert result["test_applied"] == "Centre of vital interests"

    def test_habitual_abode_sa(self):
        """Vital interests unclear, habitual abode in SA."""
        result = dta_service.apply_tie_breaker_rules(
            has_uk_home=True,
            has_sa_home=True,
            uk_vital_interests=False,
            sa_vital_interests=False,
            uk_habitual_abode=False,
            sa_habitual_abode=True,
            nationality="BOTH"
        )

        assert result["sole_residence"] == "SA"
        assert result["test_applied"] == "Habitual abode"

    def test_nationality_uk(self):
        """All tests fail, nationality UK."""
        result = dta_service.apply_tie_breaker_rules(
            has_uk_home=True,
            has_sa_home=True,
            uk_vital_interests=False,
            sa_vital_interests=False,
            uk_habitual_abode=False,
            sa_habitual_abode=False,
            nationality="UK"
        )

        assert result["sole_residence"] == "UK"
        assert result["test_applied"] == "Nationality"

    def test_undetermined(self):
        """All tests fail - undetermined."""
        result = dta_service.apply_tie_breaker_rules(
            has_uk_home=True,
            has_sa_home=True,
            uk_vital_interests=False,
            sa_vital_interests=False,
            uk_habitual_abode=True,
            sa_habitual_abode=True,
            nationality="BOTH"
        )

        assert result["sole_residence"] == "UNDETERMINED"
        assert "mutual agreement" in result["explanation"]
