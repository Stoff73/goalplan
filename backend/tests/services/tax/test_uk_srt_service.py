"""
Tests for UK Statutory Residence Test Service

Tests all UK SRT calculations including:
- Automatic Overseas Test
- Automatic UK Test
- UK ties calculation
- Sufficient Ties Test
- Complete residence determination
"""

import pytest
from services.tax.uk_srt_service import uk_srt_service


class TestAutomaticOverseasTest:
    """Test UK SRT Automatic Overseas Test."""

    def test_fewer_than_16_days(self):
        """<16 days in UK - automatically not resident."""
        result = uk_srt_service.automatic_overseas_test(
            days_in_uk=15,
            uk_resident_prior_3_years=False
        )

        assert result["passes"] is True
        assert result["test_passed"] == "Test 1: <16 days"

    def test_16_days_fails_test_1(self):
        """16 days doesn't pass test 1."""
        result = uk_srt_service.automatic_overseas_test(
            days_in_uk=16,
            uk_resident_prior_3_years=False
        )

        # Should move to test 2 or fail
        assert result["test_passed"] is None or "Test 2" in str(result.get("test_passed", ""))

    def test_not_resident_prior_3_years_under_46_days(self):
        """Not UK resident prior 3 years + <46 days."""
        result = uk_srt_service.automatic_overseas_test(
            days_in_uk=45,
            uk_resident_prior_3_years=False
        )

        assert result["passes"] is True
        assert "Test 2" in result["test_passed"]

    def test_was_resident_prior_3_years_45_days(self):
        """Was UK resident prior 3 years - 45 days doesn't pass test 2."""
        result = uk_srt_service.automatic_overseas_test(
            days_in_uk=45,
            uk_resident_prior_3_years=True
        )

        assert result["passes"] is False

    def test_full_time_work_abroad(self):
        """Full-time work abroad with <91 UK days and <=30 working days."""
        result = uk_srt_service.automatic_overseas_test(
            days_in_uk=90,
            uk_resident_prior_3_years=False,
            full_time_work_abroad=True,
            uk_days_while_working_abroad=30
        )

        assert result["passes"] is True
        assert "Test 3" in result["test_passed"]

    def test_full_time_work_abroad_too_many_working_days(self):
        """Full-time work abroad but >30 working days in UK."""
        result = uk_srt_service.automatic_overseas_test(
            days_in_uk=90,
            uk_resident_prior_3_years=False,
            full_time_work_abroad=True,
            uk_days_while_working_abroad=31
        )

        assert result["passes"] is False


class TestAutomaticUKTest:
    """Test UK SRT Automatic UK Test."""

    def test_183_days_or_more(self):
        """>=183 days in UK - automatically resident."""
        result = uk_srt_service.automatic_uk_test(
            days_in_uk=183
        )

        assert result["passes"] is True
        assert "Test 1" in result["test_passed"]

    def test_182_days_fails_test_1(self):
        """182 days doesn't pass test 1."""
        result = uk_srt_service.automatic_uk_test(
            days_in_uk=182
        )

        assert result["passes"] is False or "Test 2" in str(result.get("test_passed", ""))

    def test_uk_home_30_days(self):
        """UK home available >=91 days and present >=30 days."""
        result = uk_srt_service.automatic_uk_test(
            days_in_uk=100,
            has_uk_home=True,
            days_at_uk_home=30
        )

        assert result["passes"] is True
        assert "Test 2" in result["test_passed"]

    def test_uk_home_29_days_fails(self):
        """UK home but only 29 days present."""
        result = uk_srt_service.automatic_uk_test(
            days_in_uk=100,
            has_uk_home=True,
            days_at_uk_home=29
        )

        assert result["passes"] is False

    def test_full_time_work_uk(self):
        """Full-time work in UK."""
        result = uk_srt_service.automatic_uk_test(
            days_in_uk=150,
            full_time_work_uk=True
        )

        assert result["passes"] is True
        assert "Test 3" in result["test_passed"]


class TestCalculateUKTies:
    """Test UK ties calculation."""

    def test_all_ties_arriver(self):
        """Arriver with all applicable ties (no country tie)."""
        result = uk_srt_service.calculate_uk_ties(
            has_family=True,
            has_accommodation=True,
            accommodation_days=10,
            work_days=40,
            prior_year_days=[100, 95],
            is_leaver=False,
            days_in_other_countries=None
        )

        assert result["tie_count"] == 4
        assert "Family tie" in result["ties"]
        assert "Accommodation tie" in result["ties"]
        assert "Work tie" in result["ties"]
        assert "90-day tie" in result["ties"]
        assert result["details"]["country_tie"]["applicable"] is False

    def test_leaver_with_country_tie(self):
        """Leaver with country tie applicable."""
        result = uk_srt_service.calculate_uk_ties(
            has_family=False,
            has_accommodation=False,
            accommodation_days=0,
            work_days=0,
            prior_year_days=[50, 40],
            is_leaver=True,
            days_in_other_countries={"SA": 100, "US": 50}
        )

        assert result["tie_count"] == 0
        assert result["details"]["country_tie"]["applicable"] is True

    def test_no_ties(self):
        """No ties met."""
        result = uk_srt_service.calculate_uk_ties(
            has_family=False,
            has_accommodation=False,
            accommodation_days=0,
            work_days=0,
            prior_year_days=[50, 40],
            is_leaver=False,
            days_in_other_countries=None
        )

        assert result["tie_count"] == 0
        assert len(result["ties"]) == 0

    def test_accommodation_tie_needs_days(self):
        """Accommodation available but not used - no tie."""
        result = uk_srt_service.calculate_uk_ties(
            has_family=False,
            has_accommodation=True,
            accommodation_days=0,
            work_days=0,
            prior_year_days=[0, 0],
            is_leaver=False
        )

        assert "Accommodation tie" not in result["ties"]

    def test_work_tie_needs_40_days(self):
        """39 days work doesn't meet tie."""
        result = uk_srt_service.calculate_uk_ties(
            has_family=False,
            has_accommodation=False,
            accommodation_days=0,
            work_days=39,
            prior_year_days=[0, 0],
            is_leaver=False
        )

        assert "Work tie" not in result["ties"]


class TestSufficientTiesTest:
    """Test UK SRT Sufficient Ties Test."""

    def test_arriver_46_days_4_ties_resident(self):
        """Arriver: 46-90 days needs 4 ties."""
        result = uk_srt_service.sufficient_ties_test(
            days_in_uk=60,
            ties=4,
            is_leaver=False
        )

        assert result["resident"] is True
        assert result["threshold"] == "4 ties"

    def test_arriver_60_days_3_ties_not_resident(self):
        """Arriver: 60 days with only 3 ties - not resident."""
        result = uk_srt_service.sufficient_ties_test(
            days_in_uk=60,
            ties=3,
            is_leaver=False
        )

        assert result["resident"] is False

    def test_arriver_91_120_days_3_ties_resident(self):
        """Arriver: 91-120 days needs 3 ties."""
        result = uk_srt_service.sufficient_ties_test(
            days_in_uk=100,
            ties=3,
            is_leaver=False
        )

        assert result["resident"] is True
        assert result["threshold"] == "3 ties"

    def test_arriver_121_days_2_ties_resident(self):
        """Arriver: 121+ days needs 2 ties."""
        result = uk_srt_service.sufficient_ties_test(
            days_in_uk=150,
            ties=2,
            is_leaver=False
        )

        assert result["resident"] is True
        assert result["threshold"] == "2 ties"

    def test_leaver_16_45_days_4_ties_resident(self):
        """Leaver: 16-45 days needs 4 ties."""
        result = uk_srt_service.sufficient_ties_test(
            days_in_uk=30,
            ties=4,
            is_leaver=True
        )

        assert result["resident"] is True
        assert result["threshold"] == "4 ties"

    def test_leaver_46_90_days_3_ties_resident(self):
        """Leaver: 46-90 days needs 3 ties."""
        result = uk_srt_service.sufficient_ties_test(
            days_in_uk=60,
            ties=3,
            is_leaver=True
        )

        assert result["resident"] is True
        assert result["threshold"] == "3 ties"

    def test_leaver_91_120_days_2_ties_resident(self):
        """Leaver: 91-120 days needs 2 ties."""
        result = uk_srt_service.sufficient_ties_test(
            days_in_uk=100,
            ties=2,
            is_leaver=True
        )

        assert result["resident"] is True

    def test_leaver_121_days_1_tie_resident(self):
        """Leaver: 121+ days needs 1 tie."""
        result = uk_srt_service.sufficient_ties_test(
            days_in_uk=150,
            ties=1,
            is_leaver=True
        )

        assert result["resident"] is True
        assert result["threshold"] == "1 tie"


class TestCalculateUKResidence:
    """Test complete UK residence determination."""

    def test_automatic_overseas_wins(self):
        """Automatic overseas test passes - immediately not resident."""
        ties = {"tie_count": 4, "ties": [], "details": {}}
        result = uk_srt_service.calculate_uk_residence(
            days_in_uk=10,
            ties=ties,
            prior_residence=[False, False, False],
            work_status={}
        )

        assert result["resident"] is False
        assert result["determination_method"] == "Automatic Overseas Test"

    def test_automatic_uk_wins(self):
        """Automatic UK test passes - immediately resident."""
        ties = {"tie_count": 0, "ties": [], "details": {}}
        result = uk_srt_service.calculate_uk_residence(
            days_in_uk=183,
            ties=ties,
            prior_residence=[False, False, False],
            work_status={}
        )

        assert result["resident"] is True
        assert result["determination_method"] == "Automatic UK Test"

    def test_sufficient_ties_used(self):
        """Neither automatic test passes - use sufficient ties."""
        ties = {"tie_count": 3, "ties": ["Family tie", "Work tie", "90-day tie"], "details": {}}
        result = uk_srt_service.calculate_uk_residence(
            days_in_uk=100,
            ties=ties,
            prior_residence=[False, False, False],
            work_status={}
        )

        assert result["determination_method"] == "Sufficient Ties Test"
        assert result["resident"] is True  # Arriver, 100 days, 3 ties

    def test_leaver_with_ties(self):
        """Leaver with sufficient ties."""
        ties = {"tie_count": 2, "ties": ["Family tie", "Work tie"], "details": {}}
        result = uk_srt_service.calculate_uk_residence(
            days_in_uk=100,
            ties=ties,
            prior_residence=[True, True, False],  # Was UK resident
            work_status={}
        )

        assert result["resident"] is True  # Leaver, 100 days, 2 ties = resident
        assert result["determination_method"] == "Sufficient Ties Test"
