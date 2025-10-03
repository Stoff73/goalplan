"""
Tests for Savings Interest Tax Treatment Service.

Tests UK and SA savings interest tax calculations including:
- UK Personal Savings Allowance (PSA)
- UK starting rate for savings
- SA interest exemptions (age-based)
- ISA and TFSA exclusions
- Edge cases and validation
"""

import pytest
from decimal import Decimal

from services.savings_tax_treatment import SavingsTaxTreatmentService


class TestUKPSACalculation:
    """Test UK Personal Savings Allowance calculation."""

    def test_basic_rate_psa(self):
        """Basic rate taxpayers get £1,000 PSA."""
        psa = SavingsTaxTreatmentService.calculate_uk_psa('BASIC')
        assert psa == Decimal('1000.00')

    def test_higher_rate_psa(self):
        """Higher rate taxpayers get £500 PSA."""
        psa = SavingsTaxTreatmentService.calculate_uk_psa('HIGHER')
        assert psa == Decimal('500.00')

    def test_additional_rate_psa(self):
        """Additional rate taxpayers get £0 PSA."""
        psa = SavingsTaxTreatmentService.calculate_uk_psa('ADDITIONAL')
        assert psa == Decimal('0.00')

    def test_case_insensitive_tax_band(self):
        """Tax band should be case insensitive."""
        psa1 = SavingsTaxTreatmentService.calculate_uk_psa('basic')
        psa2 = SavingsTaxTreatmentService.calculate_uk_psa('BASIC')
        assert psa1 == psa2 == Decimal('1000.00')

    def test_invalid_tax_band(self):
        """Invalid tax band should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid tax band"):
            SavingsTaxTreatmentService.calculate_uk_psa('INVALID')


class TestUKStartingRateAllowance:
    """Test UK starting rate for savings allowance calculation."""

    def test_zero_income_gets_full_allowance(self):
        """Zero income gets full £5,000 allowance."""
        allowance = SavingsTaxTreatmentService.calculate_uk_starting_rate_allowance(
            Decimal('0.00')
        )
        assert allowance == Decimal('5000.00')

    def test_low_income_gets_full_allowance(self):
        """Income below £12,570 gets full £5,000 allowance."""
        allowance = SavingsTaxTreatmentService.calculate_uk_starting_rate_allowance(
            Decimal('10000.00')
        )
        assert allowance == Decimal('5000.00')

    def test_income_at_personal_allowance_gets_full_allowance(self):
        """Income at personal allowance (£12,570) gets full £5,000 allowance."""
        allowance = SavingsTaxTreatmentService.calculate_uk_starting_rate_allowance(
            Decimal('12570.00')
        )
        assert allowance == Decimal('5000.00')

    def test_income_reduces_allowance(self):
        """Income over £12,570 reduces allowance £1 for £1."""
        # £15,000 income = £2,430 over personal allowance
        # Allowance = min(5000, 17570 - 15000) = min(5000, 2570) = £2,570
        allowance = SavingsTaxTreatmentService.calculate_uk_starting_rate_allowance(
            Decimal('15000.00')
        )
        assert allowance == Decimal('2570.00')

    def test_income_at_threshold_gets_zero_allowance(self):
        """Income at £17,570 gets zero allowance."""
        allowance = SavingsTaxTreatmentService.calculate_uk_starting_rate_allowance(
            Decimal('17570.00')
        )
        assert allowance == Decimal('0.00')

    def test_income_above_threshold_gets_zero_allowance(self):
        """Income above £17,570 gets zero allowance."""
        allowance = SavingsTaxTreatmentService.calculate_uk_starting_rate_allowance(
            Decimal('20000.00')
        )
        assert allowance == Decimal('0.00')

    def test_negative_income_raises_error(self):
        """Negative income should raise ValueError."""
        with pytest.raises(ValueError, match="cannot be negative"):
            SavingsTaxTreatmentService.calculate_uk_starting_rate_allowance(
                Decimal('-1000.00')
            )


class TestUKSavingsTaxCalculation:
    """Test UK savings interest tax calculation."""

    def test_basic_rate_with_interest_below_psa(self):
        """Basic rate taxpayer with interest below PSA pays no tax."""
        result = SavingsTaxTreatmentService.calculate_uk_savings_tax(
            total_interest=Decimal('800.00'),
            isa_interest=Decimal('0.00'),
            tax_band='BASIC',
            non_savings_income=Decimal('20000.00')
        )

        assert result['total_interest'] == Decimal('800.00')
        assert result['isa_interest_tax_free'] == Decimal('0.00')
        assert result['starting_rate_allowance'] == Decimal('0.00')  # Income too high
        assert result['starting_rate_used'] == Decimal('0.00')
        assert result['psa_allowance'] == Decimal('1000.00')
        assert result['psa_used'] == Decimal('800.00')
        assert result['taxable_interest'] == Decimal('0.00')
        assert result['tax_rate'] == Decimal('0.20')
        assert result['tax_due'] == Decimal('0.00')
        assert result['tax_free_interest'] == Decimal('800.00')

    def test_basic_rate_with_interest_above_psa(self):
        """Basic rate taxpayer with £2,000 interest pays tax on £1,000."""
        result = SavingsTaxTreatmentService.calculate_uk_savings_tax(
            total_interest=Decimal('2000.00'),
            isa_interest=Decimal('0.00'),
            tax_band='BASIC',
            non_savings_income=Decimal('20000.00')
        )

        assert result['total_interest'] == Decimal('2000.00')
        assert result['psa_allowance'] == Decimal('1000.00')
        assert result['psa_used'] == Decimal('1000.00')
        assert result['taxable_interest'] == Decimal('1000.00')
        assert result['tax_rate'] == Decimal('0.20')
        assert result['tax_due'] == Decimal('200.00')  # £1,000 × 20%
        assert result['tax_free_interest'] == Decimal('1000.00')

    def test_higher_rate_with_interest_above_psa(self):
        """Higher rate taxpayer with £1,000 interest pays tax on £500."""
        result = SavingsTaxTreatmentService.calculate_uk_savings_tax(
            total_interest=Decimal('1000.00'),
            isa_interest=Decimal('0.00'),
            tax_band='HIGHER',
            non_savings_income=Decimal('60000.00')
        )

        assert result['total_interest'] == Decimal('1000.00')
        assert result['psa_allowance'] == Decimal('500.00')
        assert result['psa_used'] == Decimal('500.00')
        assert result['taxable_interest'] == Decimal('500.00')
        assert result['tax_rate'] == Decimal('0.40')
        assert result['tax_due'] == Decimal('200.00')  # £500 × 40%
        assert result['tax_free_interest'] == Decimal('500.00')

    def test_additional_rate_all_interest_taxable(self):
        """Additional rate taxpayer has no PSA, all interest taxable."""
        result = SavingsTaxTreatmentService.calculate_uk_savings_tax(
            total_interest=Decimal('5000.00'),
            isa_interest=Decimal('0.00'),
            tax_band='ADDITIONAL',
            non_savings_income=Decimal('200000.00')
        )

        assert result['psa_allowance'] == Decimal('0.00')
        assert result['psa_used'] == Decimal('0.00')
        assert result['taxable_interest'] == Decimal('5000.00')
        assert result['tax_rate'] == Decimal('0.45')
        assert result['tax_due'] == Decimal('2250.00')  # £5,000 × 45%
        assert result['tax_free_interest'] == Decimal('0.00')

    def test_low_income_with_starting_rate_allowance(self):
        """Low income (£10,000) gets starting rate allowance."""
        result = SavingsTaxTreatmentService.calculate_uk_savings_tax(
            total_interest=Decimal('3000.00'),
            isa_interest=Decimal('0.00'),
            tax_band='BASIC',
            non_savings_income=Decimal('10000.00')
        )

        # Income £10,000 < £17,570, so starting rate allowance = £5,000
        assert result['starting_rate_allowance'] == Decimal('5000.00')
        assert result['starting_rate_used'] == Decimal('3000.00')  # Use all £3,000
        assert result['psa_allowance'] == Decimal('1000.00')
        assert result['psa_used'] == Decimal('0.00')  # No interest left after starting rate
        assert result['taxable_interest'] == Decimal('0.00')
        assert result['tax_due'] == Decimal('0.00')
        assert result['tax_free_interest'] == Decimal('3000.00')

    def test_partial_starting_rate_then_psa(self):
        """Income £15,000 gets partial starting rate, then uses PSA."""
        result = SavingsTaxTreatmentService.calculate_uk_savings_tax(
            total_interest=Decimal('4000.00'),
            isa_interest=Decimal('0.00'),
            tax_band='BASIC',
            non_savings_income=Decimal('15000.00')
        )

        # Starting rate allowance = min(5000, 17570 - 15000) = £2,570
        assert result['starting_rate_allowance'] == Decimal('2570.00')
        assert result['starting_rate_used'] == Decimal('2570.00')
        # Remaining interest = £4,000 - £2,570 = £1,430
        # PSA covers £1,000, leaving £430 taxable
        assert result['psa_allowance'] == Decimal('1000.00')
        assert result['psa_used'] == Decimal('1000.00')
        assert result['taxable_interest'] == Decimal('430.00')
        assert result['tax_due'] == Decimal('86.00')  # £430 × 20%
        assert result['tax_free_interest'] == Decimal('3570.00')  # £2,570 + £1,000

    def test_isa_interest_excluded(self):
        """ISA interest is completely tax-free and excluded."""
        result = SavingsTaxTreatmentService.calculate_uk_savings_tax(
            total_interest=Decimal('3000.00'),
            isa_interest=Decimal('500.00'),
            tax_band='BASIC',
            non_savings_income=Decimal('20000.00')
        )

        assert result['total_interest'] == Decimal('3000.00')
        assert result['isa_interest_tax_free'] == Decimal('500.00')
        # Only £2,500 non-ISA interest subject to PSA/tax
        assert result['psa_used'] == Decimal('1000.00')
        assert result['taxable_interest'] == Decimal('1500.00')  # £2,500 - £1,000 PSA
        assert result['tax_due'] == Decimal('300.00')  # £1,500 × 20%
        assert result['tax_free_interest'] == Decimal('1500.00')  # £500 ISA + £1,000 PSA

    def test_all_isa_interest_no_tax(self):
        """All interest from ISA means no tax at all."""
        result = SavingsTaxTreatmentService.calculate_uk_savings_tax(
            total_interest=Decimal('5000.00'),
            isa_interest=Decimal('5000.00'),
            tax_band='ADDITIONAL',
            non_savings_income=Decimal('200000.00')
        )

        assert result['isa_interest_tax_free'] == Decimal('5000.00')
        assert result['taxable_interest'] == Decimal('0.00')
        assert result['tax_due'] == Decimal('0.00')
        assert result['tax_free_interest'] == Decimal('5000.00')

    def test_zero_interest(self):
        """Zero interest should return all zeros."""
        result = SavingsTaxTreatmentService.calculate_uk_savings_tax(
            total_interest=Decimal('0.00'),
            isa_interest=Decimal('0.00'),
            tax_band='BASIC',
            non_savings_income=Decimal('20000.00')
        )

        assert result['total_interest'] == Decimal('0.00')
        assert result['taxable_interest'] == Decimal('0.00')
        assert result['tax_due'] == Decimal('0.00')
        assert result['tax_free_interest'] == Decimal('0.00')

    def test_negative_total_interest_raises_error(self):
        """Negative total interest should raise ValueError."""
        with pytest.raises(ValueError, match="Total interest cannot be negative"):
            SavingsTaxTreatmentService.calculate_uk_savings_tax(
                total_interest=Decimal('-100.00'),
                isa_interest=Decimal('0.00'),
                tax_band='BASIC',
                non_savings_income=Decimal('20000.00')
            )

    def test_isa_exceeds_total_raises_error(self):
        """ISA interest exceeding total interest should raise ValueError."""
        with pytest.raises(ValueError, match="ISA interest cannot exceed total interest"):
            SavingsTaxTreatmentService.calculate_uk_savings_tax(
                total_interest=Decimal('1000.00'),
                isa_interest=Decimal('1500.00'),
                tax_band='BASIC',
                non_savings_income=Decimal('20000.00')
            )


class TestSAInterestExemption:
    """Test SA interest exemption calculation."""

    def test_under_65_exemption(self):
        """Under 65 gets R23,800 exemption."""
        exemption = SavingsTaxTreatmentService.calculate_sa_interest_exemption(60)
        assert exemption == Decimal('23800.00')

    def test_exactly_65_exemption(self):
        """Exactly 65 gets R34,500 exemption."""
        exemption = SavingsTaxTreatmentService.calculate_sa_interest_exemption(65)
        assert exemption == Decimal('34500.00')

    def test_over_65_exemption(self):
        """Over 65 gets R34,500 exemption."""
        exemption = SavingsTaxTreatmentService.calculate_sa_interest_exemption(70)
        assert exemption == Decimal('34500.00')

    def test_age_boundary_64(self):
        """Age 64 gets R23,800 exemption."""
        exemption = SavingsTaxTreatmentService.calculate_sa_interest_exemption(64)
        assert exemption == Decimal('23800.00')

    def test_negative_age_raises_error(self):
        """Negative age should raise ValueError."""
        with pytest.raises(ValueError, match="Age cannot be negative"):
            SavingsTaxTreatmentService.calculate_sa_interest_exemption(-1)


class TestSASavingsTaxCalculation:
    """Test SA savings interest tax calculation."""

    def test_interest_below_exemption_under_65(self):
        """Interest below exemption (under 65) pays no tax."""
        result = SavingsTaxTreatmentService.calculate_sa_savings_tax(
            total_interest=Decimal('20000.00'),
            tfsa_interest=Decimal('0.00'),
            age=60,
            marginal_rate=Decimal('0.31')
        )

        assert result['total_interest'] == Decimal('20000.00')
        assert result['tfsa_interest_tax_free'] == Decimal('0.00')
        assert result['interest_exemption'] == Decimal('23800.00')
        assert result['exemption_used'] == Decimal('20000.00')
        assert result['taxable_interest'] == Decimal('0.00')
        assert result['marginal_rate'] == Decimal('0.31')
        assert result['tax_due'] == Decimal('0.00')
        assert result['tax_free_interest'] == Decimal('20000.00')

    def test_interest_above_exemption_under_65(self):
        """Interest above exemption (under 65) pays tax on excess."""
        result = SavingsTaxTreatmentService.calculate_sa_savings_tax(
            total_interest=Decimal('30000.00'),
            tfsa_interest=Decimal('0.00'),
            age=60,
            marginal_rate=Decimal('0.31')
        )

        assert result['interest_exemption'] == Decimal('23800.00')
        assert result['exemption_used'] == Decimal('23800.00')
        assert result['taxable_interest'] == Decimal('6200.00')  # R30,000 - R23,800
        assert result['tax_due'] == Decimal('1922.00')  # R6,200 × 31%
        assert result['tax_free_interest'] == Decimal('23800.00')

    def test_interest_below_exemption_over_65(self):
        """Interest below exemption (over 65) pays no tax."""
        result = SavingsTaxTreatmentService.calculate_sa_savings_tax(
            total_interest=Decimal('30000.00'),
            tfsa_interest=Decimal('0.00'),
            age=70,
            marginal_rate=Decimal('0.31')
        )

        assert result['interest_exemption'] == Decimal('34500.00')
        assert result['exemption_used'] == Decimal('30000.00')
        assert result['taxable_interest'] == Decimal('0.00')
        assert result['tax_due'] == Decimal('0.00')
        assert result['tax_free_interest'] == Decimal('30000.00')

    def test_interest_above_exemption_over_65(self):
        """Interest above exemption (over 65) pays tax on excess."""
        result = SavingsTaxTreatmentService.calculate_sa_savings_tax(
            total_interest=Decimal('40000.00'),
            tfsa_interest=Decimal('0.00'),
            age=70,
            marginal_rate=Decimal('0.31')
        )

        assert result['interest_exemption'] == Decimal('34500.00')
        assert result['exemption_used'] == Decimal('34500.00')
        assert result['taxable_interest'] == Decimal('5500.00')  # R40,000 - R34,500
        assert result['tax_due'] == Decimal('1705.00')  # R5,500 × 31%
        assert result['tax_free_interest'] == Decimal('34500.00')

    def test_tfsa_interest_excluded(self):
        """TFSA interest is completely tax-free and excluded."""
        result = SavingsTaxTreatmentService.calculate_sa_savings_tax(
            total_interest=Decimal('30000.00'),
            tfsa_interest=Decimal('10000.00'),
            age=60,
            marginal_rate=Decimal('0.31')
        )

        assert result['total_interest'] == Decimal('30000.00')
        assert result['tfsa_interest_tax_free'] == Decimal('10000.00')
        # Only R20,000 non-TFSA interest subject to exemption
        assert result['exemption_used'] == Decimal('20000.00')
        assert result['taxable_interest'] == Decimal('0.00')
        assert result['tax_due'] == Decimal('0.00')
        assert result['tax_free_interest'] == Decimal('30000.00')  # R10k TFSA + R20k exempt

    def test_different_marginal_rates(self):
        """Test various SA marginal tax rates."""
        test_cases = [
            (Decimal('0.18'), Decimal('558.00')),   # 18%
            (Decimal('0.26'), Decimal('806.00')),   # 26%
            (Decimal('0.31'), Decimal('961.00')),   # 31%
            (Decimal('0.36'), Decimal('1116.00')),  # 36%
            (Decimal('0.39'), Decimal('1209.00')),  # 39%
            (Decimal('0.41'), Decimal('1271.00')),  # 41%
            (Decimal('0.45'), Decimal('1395.00')),  # 45%
        ]

        for rate, expected_tax in test_cases:
            result = SavingsTaxTreatmentService.calculate_sa_savings_tax(
                total_interest=Decimal('26900.00'),  # R3,100 over exemption (R23,800)
                tfsa_interest=Decimal('0.00'),
                age=60,
                marginal_rate=rate
            )
            assert result['taxable_interest'] == Decimal('3100.00')
            assert result['tax_due'] == expected_tax

    def test_zero_interest(self):
        """Zero interest should return all zeros."""
        result = SavingsTaxTreatmentService.calculate_sa_savings_tax(
            total_interest=Decimal('0.00'),
            tfsa_interest=Decimal('0.00'),
            age=60,
            marginal_rate=Decimal('0.31')
        )

        assert result['total_interest'] == Decimal('0.00')
        assert result['taxable_interest'] == Decimal('0.00')
        assert result['tax_due'] == Decimal('0.00')
        assert result['tax_free_interest'] == Decimal('0.00')

    def test_all_tfsa_interest_no_tax(self):
        """All interest from TFSA means no tax at all."""
        result = SavingsTaxTreatmentService.calculate_sa_savings_tax(
            total_interest=Decimal('50000.00'),
            tfsa_interest=Decimal('50000.00'),
            age=60,
            marginal_rate=Decimal('0.45')
        )

        assert result['tfsa_interest_tax_free'] == Decimal('50000.00')
        assert result['taxable_interest'] == Decimal('0.00')
        assert result['tax_due'] == Decimal('0.00')
        assert result['tax_free_interest'] == Decimal('50000.00')

    def test_negative_total_interest_raises_error(self):
        """Negative total interest should raise ValueError."""
        with pytest.raises(ValueError, match="Total interest cannot be negative"):
            SavingsTaxTreatmentService.calculate_sa_savings_tax(
                total_interest=Decimal('-100.00'),
                tfsa_interest=Decimal('0.00'),
                age=60,
                marginal_rate=Decimal('0.31')
            )

    def test_tfsa_exceeds_total_raises_error(self):
        """TFSA interest exceeding total interest should raise ValueError."""
        with pytest.raises(ValueError, match="TFSA interest cannot exceed total interest"):
            SavingsTaxTreatmentService.calculate_sa_savings_tax(
                total_interest=Decimal('10000.00'),
                tfsa_interest=Decimal('15000.00'),
                age=60,
                marginal_rate=Decimal('0.31')
            )

    def test_invalid_marginal_rate_raises_error(self):
        """Marginal rate outside 0-1 range should raise ValueError."""
        with pytest.raises(ValueError, match="Marginal rate must be between 0 and 1"):
            SavingsTaxTreatmentService.calculate_sa_savings_tax(
                total_interest=Decimal('10000.00'),
                tfsa_interest=Decimal('0.00'),
                age=60,
                marginal_rate=Decimal('1.5')  # 150% is invalid
            )

        with pytest.raises(ValueError, match="Marginal rate must be between 0 and 1"):
            SavingsTaxTreatmentService.calculate_sa_savings_tax(
                total_interest=Decimal('10000.00'),
                tfsa_interest=Decimal('0.00'),
                age=60,
                marginal_rate=Decimal('-0.1')  # Negative is invalid
            )


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_very_high_uk_interest(self):
        """Test with very high interest amounts."""
        result = SavingsTaxTreatmentService.calculate_uk_savings_tax(
            total_interest=Decimal('100000.00'),
            isa_interest=Decimal('0.00'),
            tax_band='ADDITIONAL',
            non_savings_income=Decimal('500000.00')
        )

        # Additional rate: no PSA, all taxable at 45%
        assert result['taxable_interest'] == Decimal('100000.00')
        assert result['tax_due'] == Decimal('45000.00')

    def test_very_high_sa_interest(self):
        """Test with very high interest amounts."""
        result = SavingsTaxTreatmentService.calculate_sa_savings_tax(
            total_interest=Decimal('100000.00'),
            tfsa_interest=Decimal('0.00'),
            age=60,
            marginal_rate=Decimal('0.45')
        )

        # R100,000 - R23,800 exemption = R76,200 taxable
        assert result['taxable_interest'] == Decimal('76200.00')
        assert result['tax_due'] == Decimal('34290.00')  # R76,200 × 45%

    def test_decimal_precision_uk(self):
        """Test decimal precision in UK calculations."""
        result = SavingsTaxTreatmentService.calculate_uk_savings_tax(
            total_interest=Decimal('1234.56'),
            isa_interest=Decimal('0.00'),
            tax_band='BASIC',
            non_savings_income=Decimal('20000.00')
        )

        # £1,234.56 - £1,000 PSA = £234.56 taxable
        # £234.56 × 20% = £46.91
        assert result['taxable_interest'] == Decimal('234.56')
        assert result['tax_due'] == Decimal('46.91')

    def test_decimal_precision_sa(self):
        """Test decimal precision in SA calculations."""
        result = SavingsTaxTreatmentService.calculate_sa_savings_tax(
            total_interest=Decimal('25999.99'),
            tfsa_interest=Decimal('0.00'),
            age=60,
            marginal_rate=Decimal('0.31')
        )

        # R25,999.99 - R23,800 = R2,199.99 taxable
        # R2,199.99 × 31% = R682.00 (rounded)
        assert result['taxable_interest'] == Decimal('2199.99')
        assert result['tax_due'] == Decimal('682.00')
