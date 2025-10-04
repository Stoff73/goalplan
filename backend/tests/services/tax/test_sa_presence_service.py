"""
Tests for SA Physical Presence Test Service

Tests all SA presence test calculations including:
- Ordinarily resident test
- Physical presence test (91 days current + 5 year average)
- Edge cases and boundary conditions
"""

import pytest
from services.tax.sa_presence_service import sa_presence_service


class TestOrdinarilyResident:
    """Test ordinarily resident determination."""

    def test_ordinarily_resident_automatic(self):
        """Ordinarily resident (traditional home in SA) - automatically resident."""
        result = sa_presence_service.calculate_sa_residence(
            days_current_year=0,
            days_prior_years=[0, 0, 0, 0, 0],
            ordinarily_resident=True
        )

        assert result["resident"] is True
        assert result["test_passed"] == "Ordinarily resident"
        assert "traditional home" in result["explanation"]


class TestPhysicalPresenceTest:
    """Test physical presence test."""

    def test_meets_all_requirements(self):
        """Meets all physical presence requirements."""
        result = sa_presence_service.calculate_sa_residence(
            days_current_year=120,
            days_prior_years=[200, 200, 190, 180, 145],  # Total = 915, all >91
            ordinarily_resident=False
        )

        assert result["resident"] is True  # All requirements met
        assert result["test_passed"] == "Physical presence"
        assert "120 days in current year" in result["explanation"]

    def test_current_year_91_days_exact_fails(self):
        """Exactly 91 days (not >91) - fails."""
        result = sa_presence_service.calculate_sa_residence(
            days_current_year=91,
            days_prior_years=[100, 100, 100, 100, 100],
            ordinarily_resident=False
        )

        assert result["resident"] is False
        assert "Not present for more than 91 days" in result["explanation"]

    def test_current_year_92_days_passes(self):
        """92 days (>91) passes current year test, but fails total requirement."""
        result = sa_presence_service.calculate_sa_residence(
            days_current_year=92,
            days_prior_years=[92, 92, 92, 92, 92],
            ordinarily_resident=False
        )

        # Total = 460 which is < 915, so should fail
        assert result["resident"] is False

    def test_one_prior_year_fails_91_days(self):
        """One prior year has only 91 days (not >91) - fails."""
        result = sa_presence_service.calculate_sa_residence(
            days_current_year=120,
            days_prior_years=[100, 91, 100, 100, 100],  # Year 2 fails
            ordinarily_resident=False
        )

        assert result["resident"] is False
        assert "of prior 5 years" in result["explanation"]

    def test_total_914_days_fails(self):
        """Total 914 days in prior 5 years (<915) - fails."""
        result = sa_presence_service.calculate_sa_residence(
            days_current_year=120,
            days_prior_years=[183, 183, 183, 183, 182],  # Total 914
            ordinarily_resident=False
        )

        assert result["resident"] is False
        assert "<915" in result["explanation"]

    def test_total_915_days_passes(self):
        """Total exactly 915 days in prior 5 years - passes (>=915)."""
        result = sa_presence_service.calculate_sa_residence(
            days_current_year=92,
            days_prior_years=[183, 183, 183, 183, 183],  # Total 915
            ordinarily_resident=False
        )

        # >=915 is the requirement, so 915 should pass
        assert result["resident"] is True

    def test_insufficient_prior_year_data(self):
        """Insufficient prior year data - pads with zeros."""
        result = sa_presence_service.calculate_sa_residence(
            days_current_year=120,
            days_prior_years=[100, 100],  # Only 2 years provided
            ordinarily_resident=False
        )

        assert result["resident"] is False  # Will fail because missing years = 0 days


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_zero_days_everywhere(self):
        """Zero days in all years - not resident."""
        result = sa_presence_service.calculate_sa_residence(
            days_current_year=0,
            days_prior_years=[0, 0, 0, 0, 0],
            ordinarily_resident=False
        )

        assert result["resident"] is False

    def test_366_days_current_year_leap_year(self):
        """366 days in current year (leap year)."""
        result = sa_presence_service.calculate_sa_residence(
            days_current_year=366,
            days_prior_years=[366, 366, 365, 365, 365],
            ordinarily_resident=False
        )

        assert result["resident"] is True
        assert result["days_breakdown"]["total_prior_5_years"] == 1827

    def test_exactly_threshold_values(self):
        """Test with exactly threshold values."""
        result = sa_presence_service.calculate_sa_residence(
            days_current_year=92,  # Minimum >91
            days_prior_years=[92, 92, 92, 92, 92],  # Each year minimum, total 460 (<915)
            ordinarily_resident=False
        )

        assert result["resident"] is False  # Total only 460, need >=915

    def test_minimum_passing_values(self):
        """Minimum values to pass all tests."""
        result = sa_presence_service.calculate_sa_residence(
            days_current_year=92,
            days_prior_years=[183, 183, 183, 183, 184],  # Total 916 (>=915)
            ordinarily_resident=False
        )

        assert result["resident"] is True

    def test_average_days_calculation(self):
        """Verify average days calculation in breakdown."""
        result = sa_presence_service.calculate_sa_residence(
            days_current_year=200,
            days_prior_years=[200, 200, 200, 200, 200],
            ordinarily_resident=False
        )

        assert result["resident"] is True
        assert result["days_breakdown"]["average_days_per_year"] == 200.0
        assert result["days_breakdown"]["total_6_years"] == 1200
