"""
UK Statutory Residence Test (SRT) Service

This service implements the UK Statutory Residence Test to determine
UK tax residence status based on days in UK, ties, and automatic tests.

All calculations follow HMRC's SRT specifications.
"""

from decimal import Decimal
from typing import Dict, List, Optional


class UKSRTService:
    """
    Service for calculating UK tax residence using the Statutory Residence Test.

    Implements:
    - Automatic Overseas Test (definitely NOT resident)
    - Automatic UK Test (definitely resident)
    - Sufficient Ties Test (depends on days and ties)
    - UK ties calculation (5 ties)
    """

    def automatic_overseas_test(
        self,
        days_in_uk: int,
        uk_resident_prior_3_years: bool,
        full_time_work_abroad: bool = False,
        uk_days_while_working_abroad: int = 0
    ) -> Dict:
        """
        Apply UK SRT Automatic Overseas Test.

        If any test passes, individual is automatically NOT UK resident.

        Tests:
        1. <16 days in UK
        2. <46 days in UK (if not UK resident in all 3 prior years)
        3. Full-time work abroad (<91 UK days, no >30 consecutive UK days)

        Args:
            days_in_uk: Days present in UK during tax year
            uk_resident_prior_3_years: UK resident in any of prior 3 years
            full_time_work_abroad: Working full-time abroad (>=35hrs/week)
            uk_days_while_working_abroad: UK days while working abroad

        Returns:
            Dictionary with passes status, test passed, and explanation
        """
        # Test 1: Fewer than 16 days in UK
        if days_in_uk < 16:
            return {
                "passes": True,
                "test_passed": "Test 1: <16 days",
                "explanation": f"Present in UK for {days_in_uk} days (fewer than 16) - automatically not UK resident"
            }

        # Test 2: Not UK resident in prior 3 years AND <46 days
        if not uk_resident_prior_3_years and days_in_uk < 46:
            return {
                "passes": True,
                "test_passed": "Test 2: Not resident prior 3 years + <46 days",
                "explanation": f"Not UK resident in prior 3 years and present {days_in_uk} days (fewer than 46) - automatically not UK resident"
            }

        # Test 3: Full-time work abroad
        if full_time_work_abroad:
            if days_in_uk < 91 and uk_days_while_working_abroad <= 30:
                return {
                    "passes": True,
                    "test_passed": "Test 3: Full-time work abroad",
                    "explanation": f"Full-time work abroad with {days_in_uk} UK days (<91) and {uk_days_while_working_abroad} working days in UK (<=30) - automatically not UK resident"
                }

        return {
            "passes": False,
            "test_passed": None,
            "explanation": "No automatic overseas test met"
        }

    def automatic_uk_test(
        self,
        days_in_uk: int,
        has_uk_home: bool = False,
        days_at_uk_home: int = 0,
        full_time_work_uk: bool = False
    ) -> Dict:
        """
        Apply UK SRT Automatic UK Test.

        If any test passes, individual is automatically UK resident.

        Tests:
        1. >=183 days in UK
        2. UK home for >=91 days AND present >=30 days
        3. Full-time work in UK (>=35hrs/week for 365 days)

        Args:
            days_in_uk: Days present in UK during tax year
            has_uk_home: Has UK home available for >=91 days
            days_at_uk_home: Days present at UK home
            full_time_work_uk: Full-time work in UK

        Returns:
            Dictionary with passes status, test passed, and explanation
        """
        # Test 1: 183 days or more in UK
        if days_in_uk >= 183:
            return {
                "passes": True,
                "test_passed": "Test 1: >=183 days",
                "explanation": f"Present in UK for {days_in_uk} days (183 or more) - automatically UK resident"
            }

        # Test 2: Only home in UK
        if has_uk_home and days_at_uk_home >= 30:
            return {
                "passes": True,
                "test_passed": "Test 2: UK home >=91 days + present >=30 days",
                "explanation": f"UK home available and present {days_at_uk_home} days (>=30) - automatically UK resident"
            }

        # Test 3: Full-time work in UK
        if full_time_work_uk:
            return {
                "passes": True,
                "test_passed": "Test 3: Full-time work in UK",
                "explanation": "Full-time work in UK (>=35hrs/week for 365 days) - automatically UK resident"
            }

        return {
            "passes": False,
            "test_passed": None,
            "explanation": "No automatic UK test met"
        }

    def calculate_uk_ties(
        self,
        has_family: bool,
        has_accommodation: bool,
        accommodation_days: int,
        work_days: int,
        prior_year_days: List[int],
        is_leaver: bool,
        days_in_other_countries: Optional[Dict[str, int]] = None
    ) -> Dict:
        """
        Calculate UK ties for Sufficient Ties Test.

        Five UK ties:
        1. Family tie: Spouse/partner or minor children UK resident
        2. Accommodation tie: Available accommodation in UK (used during year)
        3. Work tie: >=40 days doing >3 hours work in UK
        4. 90-day tie: >=90 days in UK in either of prior 2 years
        5. Country tie (leavers only): More days in UK than any other country

        Args:
            has_family: Has UK resident spouse/partner or minor children
            has_accommodation: Has UK accommodation available
            accommodation_days: Days spent at UK accommodation
            work_days: Days working >=3 hours in UK
            prior_year_days: Days in UK in prior 2 years [year-1, year-2]
            is_leaver: UK resident in 1+ of prior 3 years
            days_in_other_countries: Dict of country -> days (for country tie)

        Returns:
            Dictionary with tie count, ties list, and details
        """
        ties_count = 0
        ties = []

        # Tie 1: Family
        if has_family:
            ties_count += 1
            ties.append("Family tie")

        # Tie 2: Accommodation
        if has_accommodation and accommodation_days >= 1:
            ties_count += 1
            ties.append("Accommodation tie")

        # Tie 3: Work
        if work_days >= 40:
            ties_count += 1
            ties.append("Work tie")

        # Tie 4: 90-day
        if len(prior_year_days) >= 2:
            if prior_year_days[0] >= 90 or prior_year_days[1] >= 90:
                ties_count += 1
                ties.append("90-day tie")

        # Tie 5: Country tie (leavers only)
        country_tie_applicable = is_leaver
        if country_tie_applicable:
            if days_in_other_countries:
                max_other_country_days = max(days_in_other_countries.values()) if days_in_other_countries else 0
                # Note: We need UK days to compare, but this is called before we know final result
                # For now, mark as "conditional" - caller must verify
                country_tie_details = {
                    "applicable": True,
                    "max_other_country_days": max_other_country_days,
                    "note": "Country tie met if UK days > max other country days"
                }
            else:
                country_tie_details = {
                    "applicable": True,
                    "note": "Need days in other countries to determine"
                }
        else:
            country_tie_details = {
                "applicable": False,
                "note": "Not a leaver (not UK resident in prior 3 years)"
            }

        return {
            "tie_count": ties_count,
            "ties": ties,
            "details": {
                "family_tie": "Family tie" in ties,
                "accommodation_tie": "Accommodation tie" in ties,
                "work_tie": "Work tie" in ties,
                "ninety_day_tie": "90-day tie" in ties,
                "country_tie": country_tie_details
            }
        }

    def sufficient_ties_test(
        self,
        days_in_uk: int,
        ties: int,
        is_leaver: bool
    ) -> Dict:
        """
        Apply UK SRT Sufficient Ties Test.

        Different thresholds for "arrivers" (not UK resident in prior 3 years)
        vs "leavers" (UK resident in 1+ of prior 3 years).

        Arrivers:
        - <46 days: Always not resident
        - 46-90 days: Resident if 4+ ties
        - 91-120 days: Resident if 3+ ties
        - 121+ days: Resident if 2+ ties

        Leavers:
        - <16 days: Always not resident
        - 16-45 days: Resident if 4+ ties
        - 46-90 days: Resident if 3+ ties
        - 91-120 days: Resident if 2+ ties
        - 121+ days: Resident if 1+ tie

        Args:
            days_in_uk: Days present in UK
            ties: Number of UK ties
            is_leaver: Whether individual is a "leaver"

        Returns:
            Dictionary with resident status, threshold, and explanation
        """
        if is_leaver:
            # Leaver thresholds
            if days_in_uk < 16:
                resident = False
                threshold = "N/A (<16 days)"
            elif 16 <= days_in_uk <= 45:
                resident = ties >= 4
                threshold = "4 ties"
            elif 46 <= days_in_uk <= 90:
                resident = ties >= 3
                threshold = "3 ties"
            elif 91 <= days_in_uk <= 120:
                resident = ties >= 2
                threshold = "2 ties"
            else:  # 121+ days
                resident = ties >= 1
                threshold = "1 tie"

            status = "Leaver"
        else:
            # Arriver thresholds
            if days_in_uk < 46:
                resident = False
                threshold = "N/A (<46 days)"
            elif 46 <= days_in_uk <= 90:
                resident = ties >= 4
                threshold = "4 ties"
            elif 91 <= days_in_uk <= 120:
                resident = ties >= 3
                threshold = "3 ties"
            else:  # 121+ days
                resident = ties >= 2
                threshold = "2 ties"

            status = "Arriver"

        explanation = (
            f"{status}: {days_in_uk} days in UK, {ties} ties. "
            f"Threshold: {threshold}. "
            f"Result: {'UK resident' if resident else 'Not UK resident'}"
        )

        return {
            "resident": resident,
            "threshold": threshold,
            "explanation": explanation,
            "status": status
        }

    def calculate_uk_residence(
        self,
        days_in_uk: int,
        ties: Dict,
        prior_residence: List[bool],
        work_status: Dict
    ) -> Dict:
        """
        Complete UK residence determination using SRT.

        Runs all three tests in order:
        1. Automatic Overseas Test (if passes: not resident, done)
        2. Automatic UK Test (if passes: resident, done)
        3. Sufficient Ties Test (determines based on days + ties)

        Args:
            days_in_uk: Days present in UK during tax year
            ties: Dictionary with tie information (from calculate_uk_ties)
            prior_residence: List of UK residence status for prior 3 years [year-1, year-2, year-3]
            work_status: Dictionary with work information

        Returns:
            Dictionary with resident status, determination method, and explanation
        """
        # Determine if leaver (UK resident in any of prior 3 years)
        is_leaver = any(prior_residence) if prior_residence else False

        # Step 1: Automatic Overseas Test
        automatic_overseas = self.automatic_overseas_test(
            days_in_uk=days_in_uk,
            uk_resident_prior_3_years=is_leaver,
            full_time_work_abroad=work_status.get("full_time_work_abroad", False),
            uk_days_while_working_abroad=work_status.get("uk_days_while_working_abroad", 0)
        )

        if automatic_overseas["passes"]:
            return {
                "resident": False,
                "determination_method": "Automatic Overseas Test",
                "test_passed": automatic_overseas["test_passed"],
                "days_in_uk": days_in_uk,
                "ties_count": ties.get("tie_count", 0),
                "explanation": automatic_overseas["explanation"]
            }

        # Step 2: Automatic UK Test
        automatic_uk = self.automatic_uk_test(
            days_in_uk=days_in_uk,
            has_uk_home=work_status.get("has_uk_home", False),
            days_at_uk_home=work_status.get("days_at_uk_home", 0),
            full_time_work_uk=work_status.get("full_time_work_uk", False)
        )

        if automatic_uk["passes"]:
            return {
                "resident": True,
                "determination_method": "Automatic UK Test",
                "test_passed": automatic_uk["test_passed"],
                "days_in_uk": days_in_uk,
                "ties_count": ties.get("tie_count", 0),
                "explanation": automatic_uk["explanation"]
            }

        # Step 3: Sufficient Ties Test
        tie_count = ties.get("tie_count", 0)

        # Handle country tie if applicable
        if ties.get("details", {}).get("country_tie", {}).get("applicable", False):
            days_in_other_countries = work_status.get("days_in_other_countries", {})
            if days_in_other_countries:
                max_other_country_days = max(days_in_other_countries.values())
                if days_in_uk > max_other_country_days:
                    tie_count += 1

        sufficient_ties = self.sufficient_ties_test(
            days_in_uk=days_in_uk,
            ties=tie_count,
            is_leaver=is_leaver
        )

        return {
            "resident": sufficient_ties["resident"],
            "determination_method": "Sufficient Ties Test",
            "days_in_uk": days_in_uk,
            "ties_count": tie_count,
            "ties_detail": ties.get("ties", []),
            "threshold": sufficient_ties["threshold"],
            "status": sufficient_ties["status"],
            "explanation": sufficient_ties["explanation"]
        }


# Singleton instance
uk_srt_service = UKSRTService()
