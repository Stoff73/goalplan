"""
UK Statutory Residence Test (SRT) calculator service.

This module implements the complete UK SRT as per HMRC rules.

Reference: TaxResidency.md - UK SRT complete section

The SRT has three parts:
1. Automatic Overseas Test - definitely NOT UK resident
2. Automatic UK Test - definitely UK resident
3. Sufficient Ties Test - depends on days and ties

Performance target: < 500ms
"""

from typing import Dict, List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.tax_status import UKSRTData
from schemas.tax_status import SRTCalculatorRequest, SRTCalculatorResponse


class SRTCalculatorService:
    """
    UK Statutory Residence Test calculator.

    Implements HMRC's three-part residency test:
    1. Automatic Overseas Test (< 16 days or < 46 days if non-resident previous 3 years)
    2. Automatic UK Test (≥ 183 days or only home in UK)
    3. Sufficient Ties Test (depends on days and number of ties)
    """

    def __init__(self, db: AsyncSession):
        """Initialize SRT calculator service."""
        self.db = db

    async def calculate_residency(
        self,
        request: SRTCalculatorRequest,
        user_id: UUID = None,
        save_result: bool = False
    ) -> SRTCalculatorResponse:
        """
        Calculate UK tax residency using SRT.

        Args:
            request: SRT calculator request with days and ties
            user_id: Optional user ID to save result
            save_result: Whether to save result to database

        Returns:
            SRTCalculatorResponse: Residency determination and explanation
        """
        days_in_uk = request.daysInUk
        was_resident_previous_year = request.wasUkResidentPreviousYear

        # Step 1: Automatic Overseas Test
        automatic_overseas_result = self._check_automatic_overseas_test(
            days_in_uk, was_resident_previous_year
        )

        if automatic_overseas_result['result']:
            response = SRTCalculatorResponse(
                taxResident=False,
                testResult='automatic_overseas',
                tieCount=self._count_ties(request),
                daysInUk=days_in_uk,
                explanation=automatic_overseas_result['explanation']
            )

            if save_result and user_id:
                await self._save_srt_result(user_id, request, response)

            return response

        # Step 2: Automatic UK Test
        if days_in_uk >= 183:
            response = SRTCalculatorResponse(
                taxResident=True,
                testResult='automatic_uk',
                tieCount=self._count_ties(request),
                daysInUk=days_in_uk,
                explanation=f'Automatic UK resident: {days_in_uk} days in UK (≥ 183 days)'
            )

            if save_result and user_id:
                await self._save_srt_result(user_id, request, response)

            return response

        # Step 3: Sufficient Ties Test
        tie_count = self._count_ties(request)
        required_ties = self._get_required_ties(days_in_uk, was_resident_previous_year)

        tax_resident = tie_count >= required_ties

        status_type = 'leaver' if was_resident_previous_year else 'arriver'

        if tax_resident:
            explanation = (
                f'UK resident (sufficient ties): {tie_count} ties, '
                f'{required_ties} needed for {days_in_uk} days ({status_type})'
            )
        else:
            explanation = (
                f'Not UK resident: {tie_count} ties, '
                f'{required_ties} needed for {days_in_uk} days ({status_type})'
            )

        response = SRTCalculatorResponse(
            taxResident=tax_resident,
            testResult='sufficient_ties',
            tieCount=tie_count,
            daysInUk=days_in_uk,
            explanation=explanation
        )

        if save_result and user_id:
            await self._save_srt_result(user_id, request, response)

        return response

    def _check_automatic_overseas_test(
        self,
        days_in_uk: int,
        was_resident_previous_year: bool
    ) -> Dict[str, any]:
        """
        Check automatic overseas test.

        Rules:
        - If UK resident in previous year (leaver): < 16 days = automatic non-resident
        - If NOT UK resident in previous 3 years (arriver): < 46 days = automatic non-resident

        Args:
            days_in_uk: Number of days in UK
            was_resident_previous_year: Whether UK resident in previous year

        Returns:
            Dict with 'result' (bool) and 'explanation' (str)
        """
        if was_resident_previous_year:
            # Leaver threshold
            if days_in_uk < 16:
                return {
                    'result': True,
                    'explanation': f'Automatic non-resident (leaver): {days_in_uk} days in UK (< 16 days)'
                }
        else:
            # Arriver threshold
            if days_in_uk < 46:
                return {
                    'result': True,
                    'explanation': f'Automatic non-resident (arriver): {days_in_uk} days in UK (< 46 days)'
                }

        return {'result': False, 'explanation': ''}

    def _count_ties(self, request: SRTCalculatorRequest) -> int:
        """
        Count number of UK ties.

        Five UK ties:
        1. Family tie: Spouse/civil partner or minor children resident in UK
        2. Accommodation tie: Available UK accommodation used during year
        3. Work tie: 40+ days doing >3 hours work in UK
        4. 90-day tie: 90+ days in UK in either of previous 2 tax years
        5. Country tie: More days in UK than any other single country (leavers only)

        Args:
            request: SRT calculator request

        Returns:
            Number of ties (0-5)
        """
        tie_count = 0

        if request.familyTie:
            tie_count += 1
        if request.accommodationTie:
            tie_count += 1
        if request.workTie:
            tie_count += 1
        if request.ninetyDayTie:
            tie_count += 1
        if request.countryTie and request.wasUkResidentPreviousYear:
            # Country tie only counts for leavers
            tie_count += 1

        return tie_count

    def _get_required_ties(
        self,
        days_in_uk: int,
        was_resident_previous_year: bool
    ) -> int:
        """
        Get required number of ties for residency based on days in UK.

        Leavers (UK resident in previous year):
        - 16-45 days: 4 ties needed
        - 46-90 days: 3 ties needed
        - 91-120 days: 2 ties needed
        - 121-182 days: 1 tie needed

        Arrivers (NOT UK resident in previous 3 years):
        - 46-90 days: 4 ties needed (all ties)
        - 91-120 days: 3 ties needed
        - 121-182 days: 2 ties needed

        Args:
            days_in_uk: Number of days in UK
            was_resident_previous_year: Whether UK resident in previous year

        Returns:
            Number of ties required for residency
        """
        if was_resident_previous_year:
            # Leaver thresholds
            if days_in_uk < 46:
                return 4
            elif days_in_uk < 91:
                return 3
            elif days_in_uk < 121:
                return 2
            else:
                return 1
        else:
            # Arriver thresholds
            if days_in_uk < 91:
                return 4
            elif days_in_uk < 121:
                return 3
            else:
                return 2

    async def _save_srt_result(
        self,
        user_id: UUID,
        request: SRTCalculatorRequest,
        response: SRTCalculatorResponse
    ) -> UKSRTData:
        """
        Save SRT calculation result to database.

        Args:
            user_id: User ID
            request: SRT calculator request
            response: SRT calculator response

        Returns:
            UKSRTData: Saved SRT record
        """
        # Check if record already exists for this user and tax year
        existing_query = select(UKSRTData).where(
            UKSRTData.user_id == user_id,
            UKSRTData.tax_year == request.taxYear
        )
        result = await self.db.execute(existing_query)
        existing_record = result.scalar_one_or_none()

        if existing_record:
            # Update existing record
            existing_record.days_in_uk = request.daysInUk
            existing_record.family_tie = request.familyTie
            existing_record.accommodation_tie = request.accommodationTie
            existing_record.work_tie = request.workTie
            existing_record.ninety_day_tie = request.ninetyDayTie
            existing_record.country_tie = request.countryTie
            existing_record.tax_resident = response.taxResident
            existing_record.test_result = response.testResult

            await self.db.commit()
            await self.db.refresh(existing_record)
            return existing_record
        else:
            # Create new record
            srt_record = UKSRTData(
                user_id=user_id,
                tax_year=request.taxYear,
                days_in_uk=request.daysInUk,
                family_tie=request.familyTie,
                accommodation_tie=request.accommodationTie,
                work_tie=request.workTie,
                ninety_day_tie=request.ninetyDayTie,
                country_tie=request.countryTie,
                tax_resident=response.taxResident,
                test_result=response.testResult
            )

            self.db.add(srt_record)
            await self.db.commit()
            await self.db.refresh(srt_record)
            return srt_record

    async def get_srt_history(
        self,
        user_id: UUID,
        limit: int = 10
    ) -> List[UKSRTData]:
        """
        Get SRT calculation history for user.

        Args:
            user_id: User ID
            limit: Maximum number of records to return

        Returns:
            List of UKSRTData records ordered by tax_year DESC
        """
        query = select(UKSRTData).where(
            UKSRTData.user_id == user_id
        ).order_by(UKSRTData.tax_year.desc()).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()
