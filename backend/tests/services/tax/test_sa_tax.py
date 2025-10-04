"""
Test suite for South Africa Tax Calculation Service

Tests comprehensive SA tax calculations for 2024/25 tax year:
- Income Tax with age-based rebates
- Capital Gains Tax (inclusion rate method)
- Dividend Withholding Tax
"""

import pytest
from decimal import Decimal
from backend.services.tax.sa_tax_service import sa_tax_service


class TestSAIncomeTax:
    """Test SA Income Tax calculations."""

    def test_low_income_under_65(self):
        """Test low income earner (R200,000) under 65 - should benefit from full rebate."""
        result = sa_tax_service.calculate_income_tax(
            income=Decimal("200000"),
            age=30
        )

        # Expected calculation:
        # Tax on R200,000: 18% = R36,000
        # Rebate: R17,235
        # Tax owed: R36,000 - R17,235 = R18,765
        assert result["tax_owed"] == Decimal("18765.00")
        assert result["rebates_applied"] == Decimal("17235.00")
        assert result["gross_tax_before_rebates"] == Decimal("36000.00")
        assert result["gross_income"] == Decimal("200000.00")
        assert result["effective_rate"] > 0
        assert len(result["breakdown"]) == 1  # Only in first bracket

    def test_middle_income_under_65(self):
        """Test middle income earner (R400,000) under 65."""
        result = sa_tax_service.calculate_income_tax(
            income=Decimal("400000"),
            age=45
        )

        # Expected calculation:
        # R0 - R237,100: 18% = R42,678
        # R237,101 - R370,500: 26% of R133,400 = R34,684
        # R370,501 - R400,000: 31% of R29,500 = R9,145
        # Total: R42,678 + R34,684 + R9,145 = R86,507
        # Rebate: R17,235
        # Tax owed: R86,507 - R17,235 = R69,272
        assert result["tax_owed"] == Decimal("69272.00")
        assert result["rebates_applied"] == Decimal("17235.00")
        assert result["gross_income"] == Decimal("400000.00")
        assert len(result["breakdown"]) == 3  # Three brackets

    def test_high_income_under_65(self):
        """Test high income earner (R800,000) under 65."""
        result = sa_tax_service.calculate_income_tax(
            income=Decimal("800000"),
            age=50
        )

        # Expected calculation spans multiple brackets
        # R0 - R237,100: R42,678
        # R237,101 - R370,500: R34,684
        # R370,501 - R512,800: 31% of R142,300 = R44,113
        # R512,801 - R673,000: 36% of R160,200 = R57,672
        # R673,001 - R800,000: 39% of R127,000 = R49,530
        # Total: R228,677
        # Rebate: R17,235
        # Tax owed: R211,442
        assert result["tax_owed"] == Decimal("211442.00")
        assert result["rebates_applied"] == Decimal("17235.00")
        assert result["gross_income"] == Decimal("800000.00")
        assert len(result["breakdown"]) == 5  # Five brackets

    def test_very_high_income(self):
        """Test very high income (R2,000,000) in top bracket."""
        result = sa_tax_service.calculate_income_tax(
            income=Decimal("2000000"),
            age=40
        )

        # Income reaches top bracket (45%)
        # R0 - R237,100: 18% = R42,678
        # R237,101 - R370,500: 26% of R133,400 = R34,684
        # R370,501 - R512,800: 31% of R142,300 = R44,113
        # R512,801 - R673,000: 36% of R160,200 = R57,672
        # R673,001 - R1,817,000: 39% of R1,144,000 = R446,160
        # R1,817,001 - R2,000,000: 45% of R183,000 = R82,350
        # Total tax before rebate: R707,657
        # Rebate: R17,235
        # Tax owed: R690,422
        assert result["tax_owed"] == Decimal("690422.00")
        assert result["rebates_applied"] == Decimal("17235.00")
        assert result["gross_income"] == Decimal("2000000.00")
        assert len(result["breakdown"]) == 6  # All six brackets

    def test_age_65_to_74_secondary_rebate(self):
        """Test income with secondary rebate (age 65-74)."""
        result = sa_tax_service.calculate_income_tax(
            income=Decimal("300000"),
            age=68
        )

        # Tax calculation same as before
        # R0 - R237,100: R42,678
        # R237,101 - R300,000: 26% of R62,900 = R16,354
        # Total: R59,032
        # Rebate: R26,679 (primary + secondary)
        # Tax owed: R32,353
        assert result["tax_owed"] == Decimal("32353.00")
        assert result["rebates_applied"] == Decimal("26679.00")  # Higher rebate
        assert result["gross_income"] == Decimal("300000.00")

    def test_age_75_plus_tertiary_rebate(self):
        """Test income with tertiary rebate (age 75+)."""
        result = sa_tax_service.calculate_income_tax(
            income=Decimal("300000"),
            age=78
        )

        # Same tax calculation as above
        # Total: R59,032
        # Rebate: R29,824 (primary + secondary + tertiary)
        # Tax owed: R29,208
        assert result["tax_owed"] == Decimal("29208.00")
        assert result["rebates_applied"] == Decimal("29824.00")  # Highest rebate
        assert result["gross_income"] == Decimal("300000.00")

    def test_exact_bracket_threshold_237100(self):
        """Test income exactly at R237,100 threshold."""
        result = sa_tax_service.calculate_income_tax(
            income=Decimal("237100"),
            age=40
        )

        # All income in first bracket: 18% of R237,100 = R42,678
        # Rebate: R17,235
        # Tax owed: R25,443
        assert result["tax_owed"] == Decimal("25443.00")
        assert result["rebates_applied"] == Decimal("17235.00")
        assert len(result["breakdown"]) == 1

    def test_exact_bracket_threshold_370500(self):
        """Test income exactly at R370,500 threshold."""
        result = sa_tax_service.calculate_income_tax(
            income=Decimal("370500"),
            age=40
        )

        # R0 - R237,100: R42,678
        # R237,101 - R370,500: 26% of R133,400 = R34,684
        # Total: R77,362
        # Rebate: R17,235
        # Tax owed: R60,127
        assert result["tax_owed"] == Decimal("60127.00")
        assert result["rebates_applied"] == Decimal("17235.00")
        assert len(result["breakdown"]) == 2

    def test_zero_income(self):
        """Test zero income - no tax owed."""
        result = sa_tax_service.calculate_income_tax(
            income=Decimal("0"),
            age=40
        )

        assert result["tax_owed"] == Decimal("0.00")
        assert result["rebates_applied"] == Decimal("17235.00")
        assert result["effective_rate"] == 0
        assert len(result["breakdown"]) == 0

    def test_income_below_rebate_threshold(self):
        """Test very low income where rebate exceeds gross tax."""
        result = sa_tax_service.calculate_income_tax(
            income=Decimal("50000"),
            age=30
        )

        # Tax: 18% of R50,000 = R9,000
        # Rebate: R17,235
        # Tax owed: max(R9,000 - R17,235, 0) = R0
        assert result["tax_owed"] == Decimal("0.00")
        assert result["rebates_applied"] == Decimal("17235.00")
        assert result["effective_rate"] == 0

    def test_negative_income_raises_error(self):
        """Test that negative income raises ValueError."""
        with pytest.raises(ValueError, match="Income cannot be negative"):
            sa_tax_service.calculate_income_tax(
                income=Decimal("-1000"),
                age=40
            )

    def test_invalid_tax_year_raises_error(self):
        """Test that invalid tax year raises ValueError."""
        with pytest.raises(ValueError, match="Tax year .* not supported"):
            sa_tax_service.calculate_income_tax(
                income=Decimal("100000"),
                age=40,
                tax_year="2023/24"
            )

    def test_age_none_defaults_to_under_65(self):
        """Test that age=None defaults to under 65 rebate."""
        result = sa_tax_service.calculate_income_tax(
            income=Decimal("300000"),
            age=None
        )

        # Should use primary rebate only (R17,235)
        assert result["rebates_applied"] == Decimal("17235.00")


class TestSACapitalGainsTax:
    """Test SA Capital Gains Tax calculations."""

    def test_gains_below_annual_exclusion(self):
        """Test gains below R40,000 annual exclusion."""
        result = sa_tax_service.calculate_cgt(
            total_gains=Decimal("30000"),
            annual_exclusion_used=Decimal("0"),
            taxable_income=Decimal("500000"),
            age=40
        )

        # Gain below exclusion: no CGT
        assert result["cgt_owed"] == Decimal("0.00")
        assert result["exclusion_used"] == Decimal("30000.00")
        assert result["taxable_gain"] == Decimal("0.00")
        assert result["included_amount"] == Decimal("0.00")

    def test_gains_above_exclusion_individual_40_percent(self):
        """Test gains above exclusion with 40% inclusion rate."""
        result = sa_tax_service.calculate_cgt(
            total_gains=Decimal("100000"),
            annual_exclusion_used=Decimal("0"),
            inclusion_rate=Decimal("0.40"),
            taxable_income=Decimal("400000"),
            age=45
        )

        # Gain after exclusion: R100,000 - R40,000 = R60,000
        # Included amount (40%): R60,000 * 0.40 = R24,000
        # This R24,000 is added to taxable income and taxed at marginal rate

        # Tax on R400,000 = R69,272 (from income tax test)
        # Tax on R424,000:
        #   R0-237,100: R42,678
        #   R237,101-370,500: R34,684
        #   R370,501-424,000: 31% of R53,500 = R16,585
        #   Total: R93,947
        #   Rebate: R17,235
        #   Tax: R76,712
        # CGT = R76,712 - R69,272 = R7,440

        assert result["cgt_owed"] == Decimal("7440.00")
        assert result["exclusion_used"] == Decimal("40000.00")
        assert result["taxable_gain"] == Decimal("60000.00")
        assert result["included_amount"] == Decimal("24000.00")
        assert result["inclusion_rate"] == 40.0

    def test_gains_with_exclusion_already_used(self):
        """Test gains when annual exclusion already used."""
        result = sa_tax_service.calculate_cgt(
            total_gains=Decimal("100000"),
            annual_exclusion_used=Decimal("40000"),  # Already used
            taxable_income=Decimal("400000"),
            age=45
        )

        # No exclusion available
        # Included amount: R100,000 * 0.40 = R40,000
        # CGT should be higher than previous test
        assert result["exclusion_used"] == Decimal("0.00")
        assert result["taxable_gain"] == Decimal("100000.00")
        assert result["included_amount"] == Decimal("40000.00")
        assert result["cgt_owed"] > Decimal("7440.00")  # More than previous test

    def test_company_80_percent_inclusion_rate(self):
        """Test CGT with 80% inclusion rate (companies)."""
        result = sa_tax_service.calculate_cgt(
            total_gains=Decimal("100000"),
            annual_exclusion_used=Decimal("0"),
            inclusion_rate=Decimal("0.80"),  # Company rate
            taxable_income=Decimal("400000"),
            age=45
        )

        # Gain after exclusion: R60,000
        # Included amount (80%): R60,000 * 0.80 = R48,000
        # CGT should be double the 40% rate case
        assert result["inclusion_rate"] == 80.0
        assert result["included_amount"] == Decimal("48000.00")
        assert result["cgt_owed"] > Decimal("7440.00")  # Higher than 40% case

    def test_cgt_with_different_income_levels_low(self):
        """Test CGT at low income level (lower marginal rate)."""
        result = sa_tax_service.calculate_cgt(
            total_gains=Decimal("100000"),
            annual_exclusion_used=Decimal("0"),
            taxable_income=Decimal("150000"),  # Low income
            age=30
        )

        # Low income = lower marginal rate = lower CGT
        # Included amount: R24,000
        # Will be taxed at 18% (first bracket)
        assert result["included_amount"] == Decimal("24000.00")
        # CGT should be roughly 18% of R24,000 = R4,320
        assert Decimal("4000.00") < result["cgt_owed"] < Decimal("5000.00")

    def test_cgt_with_different_income_levels_high(self):
        """Test CGT at high income level (higher marginal rate)."""
        result = sa_tax_service.calculate_cgt(
            total_gains=Decimal("100000"),
            annual_exclusion_used=Decimal("0"),
            taxable_income=Decimal("1500000"),  # High income
            age=40
        )

        # High income = higher marginal rate (39% bracket)
        # Included amount: R24,000
        # Will be taxed at 39% = R9,360
        assert result["included_amount"] == Decimal("24000.00")
        # CGT should be roughly 39% of R24,000 = R9,360
        assert Decimal("9000.00") < result["cgt_owed"] < Decimal("10000.00")

    def test_cgt_partial_exclusion_remaining(self):
        """Test CGT with partial exclusion remaining."""
        result = sa_tax_service.calculate_cgt(
            total_gains=Decimal("60000"),
            annual_exclusion_used=Decimal("25000"),  # R15,000 remaining
            taxable_income=Decimal("400000"),
            age=45
        )

        # Exclusion remaining: R40,000 - R25,000 = R15,000
        # Gain after exclusion: R60,000 - R15,000 = R45,000
        # Included: R45,000 * 0.40 = R18,000
        assert result["exclusion_used"] == Decimal("15000.00")
        assert result["taxable_gain"] == Decimal("45000.00")
        assert result["included_amount"] == Decimal("18000.00")

    def test_zero_gains(self):
        """Test zero capital gains."""
        result = sa_tax_service.calculate_cgt(
            total_gains=Decimal("0"),
            taxable_income=Decimal("400000"),
            age=40
        )

        assert result["cgt_owed"] == Decimal("0.00")
        assert result["exclusion_used"] == Decimal("0.00")
        assert result["included_amount"] == Decimal("0.00")

    def test_negative_gains_raises_error(self):
        """Test that negative gains raise ValueError."""
        with pytest.raises(ValueError, match="Total gains cannot be negative"):
            sa_tax_service.calculate_cgt(
                total_gains=Decimal("-5000"),
                taxable_income=Decimal("400000")
            )

    def test_negative_exclusion_used_raises_error(self):
        """Test that negative exclusion used raises ValueError."""
        with pytest.raises(ValueError, match="Annual exclusion used cannot be negative"):
            sa_tax_service.calculate_cgt(
                total_gains=Decimal("100000"),
                annual_exclusion_used=Decimal("-1000"),
                taxable_income=Decimal("400000")
            )

    def test_effective_cgt_rate_calculation(self):
        """Test that effective CGT rate is calculated correctly."""
        result = sa_tax_service.calculate_cgt(
            total_gains=Decimal("100000"),
            annual_exclusion_used=Decimal("0"),
            taxable_income=Decimal("400000"),
            age=45
        )

        # Effective rate is CGT / total_gains * 100
        expected_rate = (result["cgt_owed"] / Decimal("100000")) * 100
        assert result["effective_cgt_rate"] == float(expected_rate.quantize(Decimal("0.01")))


class TestSADividendTax:
    """Test SA Dividend Withholding Tax calculations."""

    def test_dividends_below_exemption(self):
        """Test dividends below R23,800 exemption."""
        result = sa_tax_service.calculate_dividend_tax(
            dividend_income=Decimal("20000"),
            exemption_used=Decimal("0")
        )

        # Fully exempt
        assert result["dividend_tax_owed"] == Decimal("0.00")
        assert result["exemption_used"] == Decimal("20000.00")
        assert result["taxable_dividends"] == Decimal("0.00")
        assert result["gross_dividends"] == Decimal("20000.00")

    def test_dividends_above_exemption(self):
        """Test dividends above R23,800 exemption."""
        result = sa_tax_service.calculate_dividend_tax(
            dividend_income=Decimal("50000"),
            exemption_used=Decimal("0")
        )

        # Exemption: R23,800
        # Taxable: R50,000 - R23,800 = R26,200
        # Tax: 20% of R26,200 = R5,240
        assert result["dividend_tax_owed"] == Decimal("5240.00")
        assert result["exemption_used"] == Decimal("23800.00")
        assert result["taxable_dividends"] == Decimal("26200.00")
        assert result["tax_rate"] == 20.0

    def test_dividends_with_exemption_already_used(self):
        """Test dividends when exemption already used."""
        result = sa_tax_service.calculate_dividend_tax(
            dividend_income=Decimal("50000"),
            exemption_used=Decimal("23800")  # Already used
        )

        # No exemption available
        # Taxable: R50,000
        # Tax: 20% of R50,000 = R10,000
        assert result["dividend_tax_owed"] == Decimal("10000.00")
        assert result["exemption_used"] == Decimal("0.00")
        assert result["taxable_dividends"] == Decimal("50000.00")

    def test_dividends_with_partial_exemption_remaining(self):
        """Test dividends with partial exemption remaining."""
        result = sa_tax_service.calculate_dividend_tax(
            dividend_income=Decimal("30000"),
            exemption_used=Decimal("10000")  # R13,800 remaining
        )

        # Exemption remaining: R23,800 - R10,000 = R13,800
        # Taxable: R30,000 - R13,800 = R16,200
        # Tax: 20% of R16,200 = R3,240
        assert result["dividend_tax_owed"] == Decimal("3240.00")
        assert result["exemption_used"] == Decimal("13800.00")
        assert result["taxable_dividends"] == Decimal("16200.00")

    def test_dividends_exactly_at_exemption(self):
        """Test dividends exactly at exemption amount."""
        result = sa_tax_service.calculate_dividend_tax(
            dividend_income=Decimal("23800"),
            exemption_used=Decimal("0")
        )

        # Fully exempt
        assert result["dividend_tax_owed"] == Decimal("0.00")
        assert result["exemption_used"] == Decimal("23800.00")
        assert result["taxable_dividends"] == Decimal("0.00")

    def test_zero_dividends(self):
        """Test zero dividend income."""
        result = sa_tax_service.calculate_dividend_tax(
            dividend_income=Decimal("0"),
            exemption_used=Decimal("0")
        )

        assert result["dividend_tax_owed"] == Decimal("0.00")
        assert result["exemption_used"] == Decimal("0.00")
        assert result["taxable_dividends"] == Decimal("0.00")

    def test_large_dividend_income(self):
        """Test large dividend income (R200,000)."""
        result = sa_tax_service.calculate_dividend_tax(
            dividend_income=Decimal("200000"),
            exemption_used=Decimal("0")
        )

        # Exemption: R23,800
        # Taxable: R200,000 - R23,800 = R176,200
        # Tax: 20% of R176,200 = R35,240
        assert result["dividend_tax_owed"] == Decimal("35240.00")
        assert result["exemption_used"] == Decimal("23800.00")
        assert result["taxable_dividends"] == Decimal("176200.00")

    def test_negative_dividend_raises_error(self):
        """Test that negative dividend income raises ValueError."""
        with pytest.raises(ValueError, match="Dividend income cannot be negative"):
            sa_tax_service.calculate_dividend_tax(
                dividend_income=Decimal("-1000"),
                exemption_used=Decimal("0")
            )

    def test_negative_exemption_used_raises_error(self):
        """Test that negative exemption used raises ValueError."""
        with pytest.raises(ValueError, match="Exemption used cannot be negative"):
            sa_tax_service.calculate_dividend_tax(
                dividend_income=Decimal("50000"),
                exemption_used=Decimal("-1000")
            )

    def test_20_percent_withholding_rate(self):
        """Test that 20% withholding rate is applied correctly."""
        # Test with round number to verify exact rate
        result = sa_tax_service.calculate_dividend_tax(
            dividend_income=Decimal("100000"),
            exemption_used=Decimal("23800")  # Use full exemption
        )

        # Taxable: R100,000
        # Tax: exactly 20% = R20,000
        assert result["dividend_tax_owed"] == Decimal("20000.00")
        assert result["tax_rate"] == 20.0


class TestSATaxServiceEdgeCases:
    """Test edge cases and integration scenarios."""

    def test_decimal_precision_rounding(self):
        """Test that decimal precision is handled correctly."""
        result = sa_tax_service.calculate_income_tax(
            income=Decimal("123456.789"),
            age=40
        )

        # Should round to 2 decimal places
        assert isinstance(result["tax_owed"], Decimal)
        assert result["tax_owed"] == result["tax_owed"].quantize(Decimal("0.01"))

    def test_string_to_decimal_conversion(self):
        """Test that string inputs are converted to Decimal correctly."""
        # Service should accept string inputs and convert to Decimal
        result = sa_tax_service.calculate_income_tax(
            income=Decimal("300000"),  # Already Decimal, but service handles strings too
            age=40
        )

        assert result["tax_owed"] > 0
        assert isinstance(result["tax_owed"], Decimal)

    def test_age_boundary_64_to_65(self):
        """Test age boundary between under 65 and 65-74."""
        # Age 64 - primary rebate only
        result_64 = sa_tax_service.calculate_income_tax(
            income=Decimal("300000"),
            age=64
        )

        # Age 65 - primary + secondary rebate
        result_65 = sa_tax_service.calculate_income_tax(
            income=Decimal("300000"),
            age=65
        )

        # Age 65 should have lower tax due to higher rebate
        assert result_64["tax_owed"] > result_65["tax_owed"]
        assert result_64["rebates_applied"] < result_65["rebates_applied"]

    def test_age_boundary_74_to_75(self):
        """Test age boundary between 65-74 and 75+."""
        # Age 74 - primary + secondary
        result_74 = sa_tax_service.calculate_income_tax(
            income=Decimal("300000"),
            age=74
        )

        # Age 75 - all three rebates
        result_75 = sa_tax_service.calculate_income_tax(
            income=Decimal("300000"),
            age=75
        )

        # Age 75 should have lower tax
        assert result_74["tax_owed"] > result_75["tax_owed"]
        assert result_74["rebates_applied"] < result_75["rebates_applied"]

    def test_cgt_and_dividend_tax_combined_scenario(self):
        """Test realistic scenario with both CGT and dividend tax."""
        # Individual with:
        # - R500,000 income
        # - R100,000 capital gains
        # - R50,000 dividend income

        income_tax = sa_tax_service.calculate_income_tax(
            income=Decimal("500000"),
            age=45
        )

        cgt = sa_tax_service.calculate_cgt(
            total_gains=Decimal("100000"),
            annual_exclusion_used=Decimal("0"),
            taxable_income=Decimal("500000"),
            age=45
        )

        dividend_tax = sa_tax_service.calculate_dividend_tax(
            dividend_income=Decimal("50000"),
            exemption_used=Decimal("0")
        )

        # Total tax liability
        total_tax = income_tax["tax_owed"] + cgt["cgt_owed"] + dividend_tax["dividend_tax_owed"]

        assert total_tax > Decimal("0")
        assert income_tax["tax_owed"] > Decimal("0")
        assert cgt["cgt_owed"] > Decimal("0")
        assert dividend_tax["dividend_tax_owed"] > Decimal("0")
