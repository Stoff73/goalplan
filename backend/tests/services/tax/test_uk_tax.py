"""
Comprehensive test suite for UK Tax Service.

Tests all UK tax calculations for 2024/25 tax year:
- Income Tax
- National Insurance
- Capital Gains Tax
- Dividend Tax
"""

import pytest
from decimal import Decimal
from services.tax import uk_tax_service


class TestIncomeTax:
    """Test UK Income Tax calculations."""

    def test_basic_rate_taxpayer_30k(self):
        """Test basic rate taxpayer with £30,000 income."""
        result = uk_tax_service.calculate_income_tax(Decimal("30000"))

        # Personal allowance: £12,570
        # Taxable: £30,000 - £12,570 = £17,430
        # Tax: £17,430 * 20% = £3,486
        assert result["tax_owed"] == Decimal("3486.00")
        assert result["personal_allowance"] == Decimal("12570.00")
        assert result["taxable_income"] == Decimal("17430.00")
        assert len(result["breakdown"]) == 1
        assert result["breakdown"][0]["band"] == "Basic rate"
        assert result["breakdown"][0]["rate"] == 20.0

    def test_higher_rate_taxpayer_70k(self):
        """Test higher rate taxpayer with £70,000 income."""
        result = uk_tax_service.calculate_income_tax(Decimal("70000"))

        # Personal allowance: £12,570
        # Taxable: £70,000 - £12,570 = £57,430
        # Basic rate: £37,700 * 20% = £7,540
        # Higher rate: £19,730 * 40% = £7,892
        # Total: £15,432
        assert result["tax_owed"] == Decimal("15432.00")
        assert result["personal_allowance"] == Decimal("12570.00")
        assert result["taxable_income"] == Decimal("57430.00")
        assert len(result["breakdown"]) == 2
        assert result["breakdown"][0]["band"] == "Basic rate"
        assert result["breakdown"][1]["band"] == "Higher rate"

    def test_additional_rate_taxpayer_150k(self):
        """Test additional rate taxpayer with £150,000 income."""
        result = uk_tax_service.calculate_income_tax(Decimal("150000"))

        # Personal allowance: £0 (fully tapered)
        # Taxable: £150,000
        # Basic rate: £37,700 * 20% = £7,540
        # Higher rate: £74,870 * 40% = £29,948
        # Additional rate: £37,430 * 45% = £16,843.50
        # Total: £54,331.50
        assert result["tax_owed"] == Decimal("54331.50")
        assert result["personal_allowance"] == Decimal("0.00")
        assert result["taxable_income"] == Decimal("150000.00")
        assert len(result["breakdown"]) == 3
        assert result["breakdown"][2]["band"] == "Additional rate"

    def test_personal_allowance_tapering_110k(self):
        """Test personal allowance tapering at £110,000."""
        result = uk_tax_service.calculate_income_tax(Decimal("110000"))

        # Income over £100k: £10,000
        # Taper: £10,000 / 2 = £5,000
        # Personal allowance: £12,570 - £5,000 = £7,570
        # Taxable: £110,000 - £7,570 = £102,430
        assert result["personal_allowance"] == Decimal("7570.00")
        assert result["taxable_income"] == Decimal("102430.00")

    def test_complete_loss_of_personal_allowance_130k(self):
        """Test complete loss of personal allowance at £130,000."""
        result = uk_tax_service.calculate_income_tax(Decimal("130000"))

        # Income over £100k: £30,000
        # Taper: £30,000 / 2 = £15,000 (exceeds personal allowance)
        # Personal allowance: £0
        # Taxable: £130,000
        assert result["personal_allowance"] == Decimal("0.00")
        assert result["taxable_income"] == Decimal("130000.00")

    def test_zero_income(self):
        """Test zero income."""
        result = uk_tax_service.calculate_income_tax(Decimal("0"))

        assert result["tax_owed"] == Decimal("0.00")
        assert result["personal_allowance"] == Decimal("12570.00")
        assert result["taxable_income"] == Decimal("0.00")
        assert result["effective_rate"] == 0.0
        assert len(result["breakdown"]) == 0

    def test_exactly_at_basic_rate_threshold(self):
        """Test income exactly at basic rate upper threshold."""
        # Personal allowance + basic rate band: £12,570 + £37,700 = £50,270
        result = uk_tax_service.calculate_income_tax(Decimal("50270"))

        # Taxable: £50,270 - £12,570 = £37,700
        # All in basic rate: £37,700 * 20% = £7,540
        assert result["tax_owed"] == Decimal("7540.00")
        assert len(result["breakdown"]) == 1
        assert result["breakdown"][0]["band"] == "Basic rate"

    def test_exactly_at_higher_rate_threshold(self):
        """Test income exactly at additional rate threshold (gross income)."""
        result = uk_tax_service.calculate_income_tax(Decimal("125140"))

        # Income over £100k: £25,140
        # Taper: £25,140 / 2 = £12,570 (fully tapers personal allowance)
        # Personal allowance: £0
        # Taxable: £125,140
        # When PA = £0, taxable income £112,570+ goes to additional rate
        # Basic rate (£0-£37,700 taxable): £37,700 at 20% = £7,540
        # Higher rate (£37,701-£112,570 taxable): £74,870 at 40% = £29,948
        # Additional rate (£112,571+ taxable): £12,570 at 45% = £5,656.50
        # Total: £43,144.50
        assert result["tax_owed"] == Decimal("43144.50")
        assert result["personal_allowance"] == Decimal("0.00")
        assert len(result["breakdown"]) == 3

    def test_just_above_personal_allowance(self):
        """Test income just above personal allowance."""
        result = uk_tax_service.calculate_income_tax(Decimal("12571"))

        # Taxable: £1
        # Tax: £1 * 20% = £0.20
        assert result["tax_owed"] == Decimal("0.20")
        assert result["taxable_income"] == Decimal("1.00")

    def test_effective_rate_calculation(self):
        """Test effective rate is calculated correctly."""
        result = uk_tax_service.calculate_income_tax(Decimal("50000"))

        # Tax should be around £7,486
        # Effective rate: (7486/50000) * 100 = 14.97%
        assert result["effective_rate"] == pytest.approx(14.97, abs=0.1)

    def test_negative_income_raises_error(self):
        """Test negative income raises ValueError."""
        with pytest.raises(ValueError, match="Income cannot be negative"):
            uk_tax_service.calculate_income_tax(Decimal("-1000"))

    def test_unsupported_tax_year_raises_error(self):
        """Test unsupported tax year raises ValueError."""
        with pytest.raises(ValueError, match="Tax year 2023/24 not supported"):
            uk_tax_service.calculate_income_tax(Decimal("50000"), tax_year="2023/24")


class TestNationalInsurance:
    """Test UK National Insurance calculations."""

    def test_class_1_employee_30k(self):
        """Test Class 1 NI for employee earning £30,000."""
        result = uk_tax_service.calculate_national_insurance(Decimal("30000"))

        # £12,570 - £30,000 at 12%: £17,430 * 12% = £2,091.60
        assert result["class_1"] == Decimal("2091.60")
        assert result["class_2"] == Decimal("0.00")
        assert result["class_4"] == Decimal("0.00")
        assert result["ni_owed"] == Decimal("2091.60")

    def test_class_1_employee_60k(self):
        """Test Class 1 NI for employee earning £60,000."""
        result = uk_tax_service.calculate_national_insurance(Decimal("60000"))

        # £12,570 - £50,270 at 12%: £37,700 * 12% = £4,524
        # £50,270 - £60,000 at 2%: £9,730 * 2% = £194.60
        # Total: £4,718.60
        assert result["class_1"] == Decimal("4718.60")
        assert result["ni_owed"] == Decimal("4718.60")

    def test_class_1_below_threshold(self):
        """Test Class 1 NI below primary threshold."""
        result = uk_tax_service.calculate_national_insurance(Decimal("10000"))

        assert result["class_1"] == Decimal("0.00")
        assert result["ni_owed"] == Decimal("0.00")

    def test_self_employed_20k(self):
        """Test self-employed NI with £20,000 profits."""
        result = uk_tax_service.calculate_national_insurance(
            Decimal("0"),
            is_self_employed=True,
            profits=Decimal("20000")
        )

        # Class 2: £3.45 * 52 = £179.40
        # Class 4: (£20,000 - £12,570) * 9% = £7,430 * 9% = £668.70
        # Total: £848.10
        assert result["class_2"] == Decimal("179.40")
        assert result["class_4"] == Decimal("668.70")
        assert result["ni_owed"] == Decimal("848.10")

    def test_self_employed_60k(self):
        """Test self-employed NI with £60,000 profits."""
        result = uk_tax_service.calculate_national_insurance(
            Decimal("0"),
            is_self_employed=True,
            profits=Decimal("60000")
        )

        # Class 2: £3.45 * 52 = £179.40
        # Class 4 main: £37,700 * 9% = £3,393
        # Class 4 additional: £9,730 * 2% = £194.60
        # Total: £3,767
        assert result["class_2"] == Decimal("179.40")
        assert result["class_4"] == Decimal("3587.60")
        assert result["ni_owed"] == Decimal("3767.00")

    def test_self_employed_below_class_2_threshold(self):
        """Test self-employed below Class 2 threshold."""
        result = uk_tax_service.calculate_national_insurance(
            Decimal("0"),
            is_self_employed=True,
            profits=Decimal("5000")
        )

        # Below £6,725 threshold - no Class 2
        assert result["class_2"] == Decimal("0.00")
        assert result["class_4"] == Decimal("0.00")
        assert result["ni_owed"] == Decimal("0.00")

    def test_combined_employee_and_self_employed(self):
        """Test combined employee and self-employed income."""
        result = uk_tax_service.calculate_national_insurance(
            Decimal("30000"),
            is_self_employed=True,
            profits=Decimal("20000")
        )

        # Class 1: £17,430 * 12% = £2,091.60
        # Class 2: £179.40
        # Class 4: £7,430 * 9% = £668.70
        assert result["class_1"] == Decimal("2091.60")
        assert result["class_2"] == Decimal("179.40")
        assert result["class_4"] == Decimal("668.70")
        assert result["ni_owed"] == Decimal("2939.70")

    def test_exactly_at_upper_earnings_limit(self):
        """Test NI at exactly upper earnings limit."""
        result = uk_tax_service.calculate_national_insurance(Decimal("50270"))

        # All at 12%: £37,700 * 12% = £4,524
        assert result["class_1"] == Decimal("4524.00")

    def test_negative_income_raises_error(self):
        """Test negative income raises ValueError."""
        with pytest.raises(ValueError, match="cannot be negative"):
            uk_tax_service.calculate_national_insurance(Decimal("-1000"))


class TestCapitalGainsTax:
    """Test UK Capital Gains Tax calculations."""

    def test_gains_below_annual_exemption(self):
        """Test gains below annual exempt amount."""
        result = uk_tax_service.calculate_cgt(Decimal("2000"))

        assert result["cgt_owed"] == Decimal("0.00")
        assert result["exempt_amount"] == Decimal("2000.00")
        assert result["taxable_gain"] == Decimal("0.00")

    def test_basic_rate_taxpayer_other_assets(self):
        """Test basic rate taxpayer with other assets."""
        result = uk_tax_service.calculate_cgt(
            Decimal("10000"),
            is_higher_rate_taxpayer=False,
            is_property=False
        )

        # Taxable: £10,000 - £3,000 = £7,000
        # Tax: £7,000 * 10% = £700
        assert result["cgt_owed"] == Decimal("700.00")
        assert result["taxable_gain"] == Decimal("7000.00")
        assert result["rate_applied"] == 10.0

    def test_higher_rate_taxpayer_other_assets(self):
        """Test higher rate taxpayer with other assets."""
        result = uk_tax_service.calculate_cgt(
            Decimal("10000"),
            is_higher_rate_taxpayer=True,
            is_property=False
        )

        # Taxable: £10,000 - £3,000 = £7,000
        # Tax: £7,000 * 20% = £1,400
        assert result["cgt_owed"] == Decimal("1400.00")
        assert result["rate_applied"] == 20.0

    def test_basic_rate_residential_property(self):
        """Test basic rate taxpayer with residential property."""
        result = uk_tax_service.calculate_cgt(
            Decimal("50000"),
            is_higher_rate_taxpayer=False,
            is_property=True
        )

        # Taxable: £50,000 - £3,000 = £47,000
        # Tax: £47,000 * 18% = £8,460
        assert result["cgt_owed"] == Decimal("8460.00")
        assert result["rate_applied"] == 18.0

    def test_higher_rate_residential_property(self):
        """Test higher rate taxpayer with residential property."""
        result = uk_tax_service.calculate_cgt(
            Decimal("100000"),
            is_higher_rate_taxpayer=True,
            is_property=True
        )

        # Taxable: £100,000 - £3,000 = £97,000
        # Tax: £97,000 * 24% = £23,280
        assert result["cgt_owed"] == Decimal("23280.00")
        assert result["rate_applied"] == 24.0

    def test_annual_exempt_amount_already_used(self):
        """Test with annual exempt amount already used."""
        result = uk_tax_service.calculate_cgt(
            Decimal("10000"),
            annual_exempt_amount_used=Decimal("3000"),
            is_higher_rate_taxpayer=False
        )

        # No exemption left
        # Tax: £10,000 * 10% = £1,000
        assert result["cgt_owed"] == Decimal("1000.00")
        assert result["exempt_amount"] == Decimal("0.00")
        assert result["taxable_gain"] == Decimal("10000.00")

    def test_partial_annual_exemption_used(self):
        """Test with partial annual exemption used."""
        result = uk_tax_service.calculate_cgt(
            Decimal("5000"),
            annual_exempt_amount_used=Decimal("1500"),
            is_higher_rate_taxpayer=False
        )

        # Remaining exemption: £3,000 - £1,500 = £1,500
        # Taxable: £5,000 - £1,500 = £3,500
        # Tax: £3,500 * 10% = £350
        assert result["cgt_owed"] == Decimal("350.00")
        assert result["exempt_amount"] == Decimal("1500.00")
        assert result["taxable_gain"] == Decimal("3500.00")

    def test_exactly_at_annual_exemption(self):
        """Test gains exactly equal to annual exemption."""
        result = uk_tax_service.calculate_cgt(Decimal("3000"))

        assert result["cgt_owed"] == Decimal("0.00")
        assert result["exempt_amount"] == Decimal("3000.00")
        assert result["taxable_gain"] == Decimal("0.00")

    def test_zero_gains(self):
        """Test zero capital gains."""
        result = uk_tax_service.calculate_cgt(Decimal("0"))

        assert result["cgt_owed"] == Decimal("0.00")
        assert result["exempt_amount"] == Decimal("0.00")

    def test_negative_gains_raises_error(self):
        """Test negative gains raises ValueError."""
        with pytest.raises(ValueError, match="cannot be negative"):
            uk_tax_service.calculate_cgt(Decimal("-1000"))


class TestDividendTax:
    """Test UK Dividend Tax calculations."""

    def test_dividends_below_allowance(self):
        """Test dividends below allowance."""
        result = uk_tax_service.calculate_dividend_tax(Decimal("400"))

        assert result["dividend_tax_owed"] == Decimal("0.00")
        assert result["allowance_used"] == Decimal("400.00")
        assert result["taxable_dividends"] == Decimal("0.00")

    def test_basic_rate_with_dividends(self):
        """Test basic rate taxpayer with dividends."""
        # Other income: £30,000
        # Dividends: £5,000
        result = uk_tax_service.calculate_dividend_tax(
            Decimal("5000"),
            other_income=Decimal("30000")
        )

        # Taxable dividends: £5,000 - £500 = £4,500
        # Other income uses personal allowance + some basic rate band
        # Dividends fall in basic rate: £4,500 * 8.75% = £393.75
        assert result["dividend_tax_owed"] == Decimal("393.75")
        assert result["taxable_dividends"] == Decimal("4500.00")
        assert result["allowance_used"] == Decimal("500.00")

    def test_higher_rate_with_dividends(self):
        """Test higher rate taxpayer with dividends."""
        # Other income: £60,000
        # Dividends: £10,000
        result = uk_tax_service.calculate_dividend_tax(
            Decimal("10000"),
            other_income=Decimal("60000")
        )

        # Taxable dividends: £10,000 - £500 = £9,500
        # Other income already in higher rate band
        # All dividends at higher rate: £9,500 * 33.75% = £3,206.25
        assert result["dividend_tax_owed"] == Decimal("3206.25")
        assert len(result["breakdown"]) == 1
        assert result["breakdown"][0]["rate"] == 33.75

    def test_dividends_pushing_into_higher_band(self):
        """Test dividends pushing taxpayer into higher band."""
        # Other income: £45,000 (basic rate, close to threshold)
        # Dividends: £10,000
        result = uk_tax_service.calculate_dividend_tax(
            Decimal("10000"),
            other_income=Decimal("45000")
        )

        # Personal allowance: £12,570
        # Taxable other income: £45,000 - £12,570 = £32,430
        # Basic rate band remaining: £37,700 - £32,430 = £5,270
        # Taxable dividends: £10,000 - £500 = £9,500
        # At basic rate: £5,270 * 8.75% = £461.125 → £461.13
        # At higher rate: £4,230 * 33.75% = £1,427.625 → £1,427.63
        # Total: £1,888.76 (rounding applied to each band)
        assert result["dividend_tax_owed"] == Decimal("1888.76")
        assert len(result["breakdown"]) == 2

    def test_dividends_at_additional_rate(self):
        """Test dividends at additional rate."""
        # Other income: £130,000 (additional rate)
        # Dividends: £20,000
        result = uk_tax_service.calculate_dividend_tax(
            Decimal("20000"),
            other_income=Decimal("130000")
        )

        # Taxable dividends: £20,000 - £500 = £19,500
        # All at additional rate: £19,500 * 39.35% = £7,673.25
        assert result["dividend_tax_owed"] == Decimal("7673.25")
        assert len(result["breakdown"]) == 1
        assert result["breakdown"][0]["rate"] == 39.35

    def test_exactly_at_dividend_allowance(self):
        """Test dividends exactly at allowance."""
        result = uk_tax_service.calculate_dividend_tax(Decimal("500"))

        assert result["dividend_tax_owed"] == Decimal("0.00")
        assert result["allowance_used"] == Decimal("500.00")
        assert result["taxable_dividends"] == Decimal("0.00")

    def test_zero_dividends(self):
        """Test zero dividends."""
        result = uk_tax_service.calculate_dividend_tax(Decimal("0"))

        assert result["dividend_tax_owed"] == Decimal("0.00")
        assert result["allowance_used"] == Decimal("0.00")

    def test_no_other_income(self):
        """Test dividends with no other income."""
        result = uk_tax_service.calculate_dividend_tax(
            Decimal("40000"),
            other_income=Decimal("0")
        )

        # Taxable dividends: £40,000 - £500 = £39,500
        # Personal allowance: £12,570 leaves £37,700 in basic rate band
        # At basic rate: £37,700 * 8.75% = £3,298.75
        # At higher rate: £1,800 * 33.75% = £607.50
        # Total: £3,906.25
        assert result["dividend_tax_owed"] == Decimal("3906.25")

    def test_with_tapered_personal_allowance(self):
        """Test dividends when personal allowance is tapered."""
        # Other income: £110,000 (triggers tapering)
        # Dividends: £5,000
        result = uk_tax_service.calculate_dividend_tax(
            Decimal("5000"),
            other_income=Decimal("110000")
        )

        # Personal allowance tapered: £12,570 - (£10,000/2) = £7,570
        # Taxable other: £110,000 - £7,570 = £102,430
        # Already well into higher rate
        # Taxable dividends: £5,000 - £500 = £4,500
        # All at higher rate: £4,500 * 33.75% = £1,518.75
        assert result["dividend_tax_owed"] == Decimal("1518.75")

    def test_negative_income_raises_error(self):
        """Test negative income raises ValueError."""
        with pytest.raises(ValueError, match="cannot be negative"):
            uk_tax_service.calculate_dividend_tax(Decimal("-1000"))


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_very_high_income(self):
        """Test very high income (£1 million)."""
        result = uk_tax_service.calculate_income_tax(Decimal("1000000"))

        # Should handle large numbers correctly
        assert result["tax_owed"] > Decimal("400000")
        assert result["personal_allowance"] == Decimal("0.00")

    def test_decimal_precision(self):
        """Test decimal precision is maintained."""
        result = uk_tax_service.calculate_income_tax(Decimal("50000.55"))

        # Should round to 2 decimal places
        assert isinstance(result["tax_owed"], Decimal)
        assert str(result["tax_owed"]).count(".") == 1

    def test_income_at_taper_start(self):
        """Test income exactly at taper threshold."""
        result = uk_tax_service.calculate_income_tax(Decimal("100000"))

        # Should have full personal allowance
        assert result["personal_allowance"] == Decimal("12570.00")

    def test_income_just_above_taper_start(self):
        """Test income just above taper threshold."""
        result = uk_tax_service.calculate_income_tax(Decimal("100001"))

        # Should have £0.50 reduction in personal allowance
        assert result["personal_allowance"] == Decimal("12569.50")

    def test_all_calculations_with_string_input(self):
        """Test that string inputs are converted correctly."""
        income_result = uk_tax_service.calculate_income_tax("50000")
        ni_result = uk_tax_service.calculate_national_insurance("50000")
        cgt_result = uk_tax_service.calculate_cgt("10000")
        div_result = uk_tax_service.calculate_dividend_tax("5000")

        assert isinstance(income_result["tax_owed"], Decimal)
        assert isinstance(ni_result["ni_owed"], Decimal)
        assert isinstance(cgt_result["cgt_owed"], Decimal)
        assert isinstance(div_result["dividend_tax_owed"], Decimal)
