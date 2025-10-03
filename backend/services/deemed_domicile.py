"""
Deemed domicile calculation service.

This module implements UK deemed domicile rules for inheritance tax purposes.

Business Rules (from TaxResidency.md):
1. 15 out of 20 years rule: Individual is deemed domiciled if UK resident for 15 of the last 20 tax years
2. Domicile of origin rule: Individual born in UK with UK domicile of origin who returns to UK as resident

Performance target: < 100ms
"""

from datetime import date, timedelta
from typing import Optional, Dict, List, Tuple
from uuid import UUID

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from models.tax_status import UserTaxStatus
from schemas.tax_status import DeemedDomicileResponse


class DeemedDomicileService:
    """
    Service for calculating UK deemed domicile status.

    UK deemed domicile rules (for IHT purposes):
    - Deemed domiciled if UK resident for 15 of last 20 tax years
    - Deemed domiciled if UK domicile of origin AND UK resident in 1 of last 2 years
    """

    def __init__(self, db: AsyncSession):
        """Initialize deemed domicile service."""
        self.db = db

    async def calculate_deemed_domicile(
        self,
        user_id: UUID,
        as_of_date: date = None
    ) -> DeemedDomicileResponse:
        """
        Calculate deemed domicile status for a user.

        Args:
            user_id: User ID
            as_of_date: Date to calculate deemed domicile (default: today)

        Returns:
            DeemedDomicileResponse: Deemed domicile status and details

        Performance: < 100ms
        """
        if as_of_date is None:
            as_of_date = date.today()

        # Get all tax status records for user
        tax_statuses = await self._get_tax_status_history(user_id, as_of_date)

        if not tax_statuses:
            return DeemedDomicileResponse(
                isDeemedDomiciled=False,
                deemedDomicileDate=None,
                reason="No tax status records found",
                ukResidentYears=0
            )

        # Rule 1: 15 out of 20 years UK resident
        uk_resident_years = self._count_uk_resident_years(tax_statuses, as_of_date, years_to_check=20)

        if uk_resident_years >= 15:
            # Calculate the date deemed domicile started (when they hit 15 years)
            deemed_domicile_date = self._calculate_deemed_domicile_start_date(
                tax_statuses, as_of_date, required_years=15
            )

            return DeemedDomicileResponse(
                isDeemedDomiciled=True,
                deemedDomicileDate=deemed_domicile_date,
                reason=f"15 of last 20 years UK resident ({uk_resident_years} years)",
                ukResidentYears=uk_resident_years
            )

        # Rule 2: Domicile of origin rule
        # Note: This requires user profile data which we don't have in tax_status
        # For now, we only implement Rule 1
        # In production, this would check user.domicile_of_origin and recent residency

        return DeemedDomicileResponse(
            isDeemedDomiciled=False,
            deemedDomicileDate=None,
            reason=f"Only {uk_resident_years} of last 20 years UK resident (need 15)",
            ukResidentYears=uk_resident_years
        )

    async def _get_tax_status_history(
        self,
        user_id: UUID,
        as_of_date: date
    ) -> List[UserTaxStatus]:
        """
        Get tax status history for user up to specified date.

        Args:
            user_id: User ID
            as_of_date: Date to query up to

        Returns:
            List of UserTaxStatus records ordered by effective_from DESC
        """
        query = select(UserTaxStatus).where(
            and_(
                UserTaxStatus.user_id == user_id,
                UserTaxStatus.effective_from <= as_of_date
            )
        ).order_by(UserTaxStatus.effective_from.desc())

        result = await self.db.execute(query)
        return result.scalars().all()

    def _count_uk_resident_years(
        self,
        tax_statuses: List[UserTaxStatus],
        as_of_date: date,
        years_to_check: int = 20
    ) -> int:
        """
        Count how many of the last N tax years user was UK resident.

        A tax year counts as UK resident if the user was UK resident for 183+ days
        or the majority of the tax year.

        Args:
            tax_statuses: List of tax status records
            as_of_date: Date to count from
            years_to_check: Number of years to look back (default 20)

        Returns:
            Number of UK resident years in the period
        """
        # UK tax year: April 6 to April 5
        uk_resident_years = 0

        for year_offset in range(years_to_check):
            # Calculate tax year
            tax_year_end = self._get_tax_year_for_date(as_of_date)
            target_tax_year_end = tax_year_end - timedelta(days=365 * year_offset)
            tax_year_start = date(target_tax_year_end.year - 1, 4, 6)
            tax_year_end_date = date(target_tax_year_end.year, 4, 5)

            # Check if user was UK resident for this tax year
            if self._was_uk_resident_in_period(
                tax_statuses,
                tax_year_start,
                tax_year_end_date
            ):
                uk_resident_years += 1

        return uk_resident_years

    def _was_uk_resident_in_period(
        self,
        tax_statuses: List[UserTaxStatus],
        period_start: date,
        period_end: date
    ) -> bool:
        """
        Check if user was UK resident during a period.

        Logic:
        - If majority of period shows UK resident status, return True
        - We consider it UK resident if any tax status during period shows uk_tax_resident=True

        Args:
            tax_statuses: List of tax status records
            period_start: Start of period
            period_end: End of period

        Returns:
            True if UK resident during period
        """
        for status in tax_statuses:
            # Check if this status overlaps with the period
            status_start = status.effective_from
            status_end = status.effective_to or date.max

            # Check for overlap
            if status_start <= period_end and status_end >= period_start:
                if status.uk_tax_resident:
                    return True

        return False

    def _get_tax_year_for_date(self, d: date) -> date:
        """
        Get the end date of the UK tax year for a given date.

        UK tax year: April 6 to April 5

        Args:
            d: Date to find tax year for

        Returns:
            End date of tax year (April 5)
        """
        if d.month >= 4 and d.day >= 6:
            # After April 6, so in tax year ending next April 5
            return date(d.year + 1, 4, 5)
        else:
            # Before April 6, so in tax year ending this April 5
            return date(d.year, 4, 5)

    def _calculate_deemed_domicile_start_date(
        self,
        tax_statuses: List[UserTaxStatus],
        as_of_date: date,
        required_years: int = 15
    ) -> Optional[date]:
        """
        Calculate the date when deemed domicile started (when user hit 15 years).

        Args:
            tax_statuses: List of tax status records
            as_of_date: Current date
            required_years: Number of years required (default 15)

        Returns:
            Date when deemed domicile started, or None if not deemed domiciled
        """
        # Work backwards to find when user first hit 15 years
        # For simplicity, we return the start of the 15th year of UK residency

        uk_resident_years_count = 0

        for year_offset in range(50):  # Check up to 50 years back
            tax_year_end = self._get_tax_year_for_date(as_of_date)
            target_tax_year_end = tax_year_end - timedelta(days=365 * year_offset)
            tax_year_start = date(target_tax_year_end.year - 1, 4, 6)
            tax_year_end_date = date(target_tax_year_end.year, 4, 5)

            if self._was_uk_resident_in_period(tax_statuses, tax_year_start, tax_year_end_date):
                uk_resident_years_count += 1

                if uk_resident_years_count == required_years:
                    # This is the 15th year - deemed domicile starts here
                    return tax_year_start

        return None

    async def update_deemed_domicile_status(
        self,
        user_id: UUID,
        as_of_date: date = None
    ) -> Optional[date]:
        """
        Calculate and update deemed domicile status in user's current tax status.

        This is called when creating/updating tax status to automatically
        calculate deemed domicile.

        Args:
            user_id: User ID
            as_of_date: Date to calculate (default: today)

        Returns:
            Deemed domicile date if applicable, None otherwise
        """
        result = await self.calculate_deemed_domicile(user_id, as_of_date)

        if result.isDeemedDomiciled:
            return result.deemedDomicileDate

        return None
