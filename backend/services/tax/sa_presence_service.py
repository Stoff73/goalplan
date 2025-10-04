"""
SA Physical Presence Test Service

This service implements the South African physical presence test to determine
SA tax residence status based on days spent in SA.

All calculations follow SARS specifications.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List


class SAPresenceService:
    """
    Service for calculating SA tax residence using the physical presence test.

    Implements:
    - Physical presence test (91 days current year + average over 5 years)
    - Ordinarily resident test (traditional home in SA)
    """

    @staticmethod
    def _round_decimal(value: float, decimals: int = 2) -> Decimal:
        """Round to specified decimal places."""
        quantizer = Decimal(10) ** -decimals
        return Decimal(str(value)).quantize(quantizer, rounding=ROUND_HALF_UP)

    def calculate_sa_residence(
        self,
        days_current_year: int,
        days_prior_years: List[int],
        ordinarily_resident: bool = False
    ) -> Dict:
        """
        Calculate SA tax residence using physical presence test.

        Rules:
        - Ordinarily resident test: If traditional home in SA, automatically resident
        - Physical presence test:
          1. >=91 days in current year, AND
          2. >=91 days in each of prior 5 years, AND
          3. >=915 days total in prior 5 years

        Args:
            days_current_year: Days in SA in current tax year
            days_prior_years: Days in SA in prior 5 years [year-1, year-2, ..., year-5]
            ordinarily_resident: Has traditional home in SA

        Returns:
            Dictionary with resident status, test passed, days breakdown, and explanation
        """
        # Ordinarily resident test
        if ordinarily_resident:
            return {
                "resident": True,
                "test_passed": "Ordinarily resident",
                "days_current_year": days_current_year,
                "days_breakdown": None,
                "explanation": "Ordinarily resident (traditional home in SA) - automatically SA resident"
            }

        # Physical presence test requires prior 5 years of data
        if len(days_prior_years) < 5:
            # Pad with zeros if insufficient data
            days_prior_years = days_prior_years + [0] * (5 - len(days_prior_years))

        # Test 1: Current year requirement (>91 days)
        if days_current_year <= 91:
            return {
                "resident": False,
                "test_passed": None,
                "days_current_year": days_current_year,
                "days_breakdown": {
                    "current_year": days_current_year,
                    "prior_years": days_prior_years,
                    "requirement": "Must be present >91 days in current year"
                },
                "explanation": f"Not present for more than 91 days in current year ({days_current_year} days) - not SA resident"
            }

        # Test 2: Prior 5 years - each year must have >91 days
        years_meeting_requirement = sum(1 for days in days_prior_years if days > 91)
        if years_meeting_requirement < 5:
            return {
                "resident": False,
                "test_passed": None,
                "days_current_year": days_current_year,
                "days_breakdown": {
                    "current_year": days_current_year,
                    "prior_years": days_prior_years,
                    "years_meeting_requirement": years_meeting_requirement,
                    "requirement": "Must be present >91 days in each of prior 5 years"
                },
                "explanation": f"Only {years_meeting_requirement} of prior 5 years meet >91 days requirement - not SA resident"
            }

        # Test 3: Total days in prior 5 years (>=915 days)
        total_prior_5_years = sum(days_prior_years)
        if total_prior_5_years < 915:
            return {
                "resident": False,
                "test_passed": None,
                "days_current_year": days_current_year,
                "days_breakdown": {
                    "current_year": days_current_year,
                    "prior_years": days_prior_years,
                    "total_prior_5_years": total_prior_5_years,
                    "requirement": "Must have >=915 days total in prior 5 years"
                },
                "explanation": f"Total of {total_prior_5_years} days in prior 5 years (<915) - not SA resident"
            }

        # All tests passed - SA resident
        total_6_years = days_current_year + total_prior_5_years
        average_days = self._round_decimal(total_6_years / 6, 1)

        return {
            "resident": True,
            "test_passed": "Physical presence",
            "days_current_year": days_current_year,
            "days_breakdown": {
                "current_year": days_current_year,
                "prior_years": days_prior_years,
                "total_prior_5_years": total_prior_5_years,
                "total_6_years": total_6_years,
                "average_days_per_year": float(average_days)
            },
            "explanation": (
                f"Physical presence test met: {days_current_year} days in current year, "
                f"all prior 5 years >91 days, total {total_prior_5_years} days in prior 5 years (>=915), "
                f"average {average_days} days per year - SA resident"
            )
        }


# Singleton instance
sa_presence_service = SAPresenceService()
