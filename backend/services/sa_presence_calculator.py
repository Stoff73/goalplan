"""
SA Physical Presence Test calculator service.

This module implements the SA tax residency test based on physical presence.

Reference: TaxResidency.md - SA Physical Presence Test section

Business Rules:
- Resident if: 91+ days in current year AND 91+ days average over 5 years (current + 4 previous)
- Ordinarily resident if: Resident for 3+ consecutive years

Performance target: < 500ms
"""

from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.tax_status import SAPresenceData
from schemas.tax_status import SAPresenceTestRequest, SAPresenceTestResponse


class SAPresenceCalculatorService:
    """
    SA Physical Presence Test calculator.

    Implements SARS physical presence test:
    1. Must be present 91+ days in current tax year, AND
    2. Must have average of 91+ days over current + 4 previous tax years
    3. Ordinarily resident if resident for 3+ consecutive years
    """

    def __init__(self, db: AsyncSession):
        """Initialize SA presence calculator service."""
        self.db = db

    async def calculate_residency(
        self,
        request: SAPresenceTestRequest,
        user_id: UUID = None,
        save_result: bool = False
    ) -> SAPresenceTestResponse:
        """
        Calculate SA tax residency using physical presence test.

        Args:
            request: SA presence test request with days data
            user_id: Optional user ID to save result
            save_result: Whether to save result to database

        Returns:
            SAPresenceTestResponse: Residency determination and explanation
        """
        days_in_sa = request.daysInSa

        # Test 1: Current year test (91+ days)
        if days_in_sa < 91:
            response = SAPresenceTestResponse(
                taxResident=False,
                ordinarilyResident=False,
                testResult='non_resident',
                fiveYearAverage=None,
                explanation=f'Non-resident: {days_in_sa} days in current year (< 91 days required)'
            )

            if save_result and user_id:
                await self._save_presence_result(user_id, request, response)

            return response

        # Test 2: 5-year average test (if all previous years data provided)
        previous_years = [
            request.yearMinus1Days,
            request.yearMinus2Days,
            request.yearMinus3Days,
            request.yearMinus4Days
        ]

        if all(days is not None for days in previous_years):
            # Calculate 5-year average (current + 4 previous)
            total_days = days_in_sa + sum(previous_years)
            five_year_average = round(total_days / 5, 2)

            if five_year_average < 91:
                response = SAPresenceTestResponse(
                    taxResident=False,
                    ordinarilyResident=False,
                    testResult='non_resident',
                    fiveYearAverage=five_year_average,
                    explanation=(
                        f'Non-resident: {five_year_average} days average over 5 years '
                        f'(< 91 days required, despite {days_in_sa} days current year)'
                    )
                )

                if save_result and user_id:
                    await self._save_presence_result(user_id, request, response)

                return response

            # Both tests passed - user is resident
            # Check ordinarily resident status (if we have 3+ years data)
            ordinarily_resident = await self._check_ordinarily_resident(
                user_id, request.taxYear
            ) if user_id else False

            response = SAPresenceTestResponse(
                taxResident=True,
                ordinarilyResident=ordinarily_resident,
                testResult='5_year_average',
                fiveYearAverage=five_year_average,
                explanation=(
                    f'Resident: {days_in_sa} days current year (≥ 91) AND '
                    f'{five_year_average} days average over 5 years (≥ 91)'
                )
            )

            if save_result and user_id:
                await self._save_presence_result(user_id, request, response)

            return response
        else:
            # Insufficient historical data - can only confirm current year
            response = SAPresenceTestResponse(
                taxResident=True,
                ordinarilyResident=False,
                testResult='91_day_current',
                fiveYearAverage=None,
                explanation=(
                    f'Resident (current year only): {days_in_sa} days (≥ 91). '
                    f'5-year average test requires historical data'
                )
            )

            if save_result and user_id:
                await self._save_presence_result(user_id, request, response)

            return response

    async def _check_ordinarily_resident(
        self,
        user_id: UUID,
        current_tax_year: str
    ) -> bool:
        """
        Check if user is ordinarily resident (resident for 3+ consecutive years).

        Args:
            user_id: User ID
            current_tax_year: Current tax year

        Returns:
            True if ordinarily resident (3+ consecutive years)
        """
        # Get last 3 years of presence data
        query = select(SAPresenceData).where(
            SAPresenceData.user_id == user_id
        ).order_by(SAPresenceData.tax_year.desc()).limit(3)

        result = await self.db.execute(query)
        records = result.scalars().all()

        if len(records) < 3:
            return False

        # Check if all 3 records show tax_resident=True
        consecutive_resident_years = sum(
            1 for record in records if record.tax_resident
        )

        return consecutive_resident_years >= 3

    async def _save_presence_result(
        self,
        user_id: UUID,
        request: SAPresenceTestRequest,
        response: SAPresenceTestResponse
    ) -> SAPresenceData:
        """
        Save SA presence test result to database.

        Args:
            user_id: User ID
            request: SA presence test request
            response: SA presence test response

        Returns:
            SAPresenceData: Saved presence record
        """
        # Check if record already exists for this user and tax year
        existing_query = select(SAPresenceData).where(
            SAPresenceData.user_id == user_id,
            SAPresenceData.tax_year == request.taxYear
        )
        result = await self.db.execute(existing_query)
        existing_record = result.scalar_one_or_none()

        if existing_record:
            # Update existing record
            existing_record.days_in_sa = request.daysInSa
            existing_record.year_minus_1_days = request.yearMinus1Days
            existing_record.year_minus_2_days = request.yearMinus2Days
            existing_record.year_minus_3_days = request.yearMinus3Days
            existing_record.year_minus_4_days = request.yearMinus4Days
            existing_record.tax_resident = response.taxResident
            existing_record.ordinarily_resident = response.ordinarilyResident
            existing_record.test_result = response.testResult
            existing_record.five_year_average = response.fiveYearAverage

            await self.db.commit()
            await self.db.refresh(existing_record)
            return existing_record
        else:
            # Create new record
            presence_record = SAPresenceData(
                user_id=user_id,
                tax_year=request.taxYear,
                days_in_sa=request.daysInSa,
                year_minus_1_days=request.yearMinus1Days,
                year_minus_2_days=request.yearMinus2Days,
                year_minus_3_days=request.yearMinus3Days,
                year_minus_4_days=request.yearMinus4Days,
                tax_resident=response.taxResident,
                ordinarily_resident=response.ordinarilyResident,
                test_result=response.testResult,
                five_year_average=response.fiveYearAverage
            )

            self.db.add(presence_record)
            await self.db.commit()
            await self.db.refresh(presence_record)
            return presence_record

    async def get_presence_history(
        self,
        user_id: UUID,
        limit: int = 10
    ) -> List[SAPresenceData]:
        """
        Get SA presence test history for user.

        Args:
            user_id: User ID
            limit: Maximum number of records to return

        Returns:
            List of SAPresenceData records ordered by tax_year DESC
        """
        query = select(SAPresenceData).where(
            SAPresenceData.user_id == user_id
        ).order_by(SAPresenceData.tax_year.desc()).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()
