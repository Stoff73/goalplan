"""
Tests for UK SRT calculator service.

This module tests the complete UK Statutory Residence Test implementation.
"""

import pytest
from datetime import date

from services.srt_calculator import SRTCalculatorService
from schemas.tax_status import SRTCalculatorRequest


@pytest.mark.asyncio
class TestSRTCalculator:
    """Tests for SRT calculator service."""

    async def test_automatic_overseas_leaver_under_16_days(self, db_session):
        """Test automatic overseas test for leaver with < 16 days."""
        service = SRTCalculatorService(db_session)

        request = SRTCalculatorRequest(
            taxYear='2023/24',
            daysInUk=15,
            familyTie=True,
            accommodationTie=True,
            workTie=True,
            ninetyDayTie=True,
            countryTie=True,
            wasUkResidentPreviousYear=True  # Leaver
        )

        result = await service.calculate_residency(request)

        assert result.taxResident is False
        assert result.testResult == 'automatic_overseas'
        assert 'leaver' in result.explanation.lower()
        assert result.daysInUk == 15

    async def test_automatic_overseas_arriver_under_46_days(self, db_session):
        """Test automatic overseas test for arriver with < 46 days."""
        service = SRTCalculatorService(db_session)

        request = SRTCalculatorRequest(
            taxYear='2023/24',
            daysInUk=45,
            familyTie=False,
            accommodationTie=False,
            workTie=False,
            ninetyDayTie=False,
            countryTie=False,
            wasUkResidentPreviousYear=False  # Arriver
        )

        result = await service.calculate_residency(request)

        assert result.taxResident is False
        assert result.testResult == 'automatic_overseas'
        assert 'arriver' in result.explanation.lower()

    async def test_automatic_uk_183_days(self, db_session):
        """Test automatic UK test with 183+ days."""
        service = SRTCalculatorService(db_session)

        request = SRTCalculatorRequest(
            taxYear='2023/24',
            daysInUk=200,
            familyTie=False,
            accommodationTie=False,
            workTie=False,
            ninetyDayTie=False,
            countryTie=False,
            wasUkResidentPreviousYear=False
        )

        result = await service.calculate_residency(request)

        assert result.taxResident is True
        assert result.testResult == 'automatic_uk'
        assert '183' in result.explanation

    async def test_sufficient_ties_leaver_resident(self, db_session):
        """Test sufficient ties for leaver - resident case."""
        service = SRTCalculatorService(db_session)

        # Leaver with 150 days needs 1 tie
        request = SRTCalculatorRequest(
            taxYear='2023/24',
            daysInUk=150,
            familyTie=True,
            accommodationTie=False,
            workTie=False,
            ninetyDayTie=False,
            countryTie=False,
            wasUkResidentPreviousYear=True  # Leaver
        )

        result = await service.calculate_residency(request)

        assert result.taxResident is True
        assert result.testResult == 'sufficient_ties'
        assert result.tieCount == 1
        assert 'leaver' in result.explanation.lower()

    async def test_sufficient_ties_leaver_non_resident(self, db_session):
        """Test sufficient ties for leaver - non-resident case."""
        service = SRTCalculatorService(db_session)

        # Leaver with 150 days but no ties
        request = SRTCalculatorRequest(
            taxYear='2023/24',
            daysInUk=150,
            familyTie=False,
            accommodationTie=False,
            workTie=False,
            ninetyDayTie=False,
            countryTie=False,
            wasUkResidentPreviousYear=True  # Leaver
        )

        result = await service.calculate_residency(request)

        assert result.taxResident is False
        assert result.testResult == 'sufficient_ties'
        assert result.tieCount == 0

    async def test_sufficient_ties_arriver_needs_4_ties(self, db_session):
        """Test sufficient ties for arriver (46-90 days needs 4 ties)."""
        service = SRTCalculatorService(db_session)

        # Arriver with 80 days needs 4 ties (all ties)
        request = SRTCalculatorRequest(
            taxYear='2023/24',
            daysInUk=80,
            familyTie=True,
            accommodationTie=True,
            workTie=True,
            ninetyDayTie=True,
            countryTie=False,  # Country tie doesn't count for arrivers
            wasUkResidentPreviousYear=False  # Arriver
        )

        result = await service.calculate_residency(request)

        assert result.taxResident is True
        assert result.testResult == 'sufficient_ties'
        assert result.tieCount == 4
        assert 'arriver' in result.explanation.lower()

    async def test_country_tie_only_for_leavers(self, db_session):
        """Test that country tie only counts for leavers."""
        service = SRTCalculatorService(db_session)

        # Arriver with country tie
        request = SRTCalculatorRequest(
            taxYear='2023/24',
            daysInUk=100,
            familyTie=False,
            accommodationTie=False,
            workTie=False,
            ninetyDayTie=False,
            countryTie=True,
            wasUkResidentPreviousYear=False  # Arriver
        )

        result_arriver = await service.calculate_residency(request)
        assert result_arriver.tieCount == 0  # Country tie doesn't count

        # Leaver with country tie
        request.wasUkResidentPreviousYear = True
        result_leaver = await service.calculate_residency(request)
        assert result_leaver.tieCount == 1  # Country tie counts

    async def test_edge_case_exactly_16_days_leaver(self, db_session):
        """Test edge case: exactly 16 days for leaver."""
        service = SRTCalculatorService(db_session)

        request = SRTCalculatorRequest(
            taxYear='2023/24',
            daysInUk=16,
            familyTie=False,
            accommodationTie=False,
            workTie=False,
            ninetyDayTie=False,
            countryTie=False,
            wasUkResidentPreviousYear=True
        )

        result = await service.calculate_residency(request)

        # 16 days doesn't meet automatic overseas (< 16 required)
        # So goes to sufficient ties test
        assert result.testResult == 'sufficient_ties'

    async def test_edge_case_exactly_183_days(self, db_session):
        """Test edge case: exactly 183 days."""
        service = SRTCalculatorService(db_session)

        request = SRTCalculatorRequest(
            taxYear='2023/24',
            daysInUk=183,
            familyTie=False,
            accommodationTie=False,
            workTie=False,
            ninetyDayTie=False,
            countryTie=False,
            wasUkResidentPreviousYear=False
        )

        result = await service.calculate_residency(request)

        assert result.taxResident is True
        assert result.testResult == 'automatic_uk'

    async def test_save_srt_result(self, db_session, test_user):
        """Test saving SRT result to database."""
        service = SRTCalculatorService(db_session)

        request = SRTCalculatorRequest(
            taxYear='2023/24',
            daysInUk=150,
            familyTie=True,
            accommodationTie=True,
            workTie=False,
            ninetyDayTie=True,
            countryTie=False,
            wasUkResidentPreviousYear=True
        )

        result = await service.calculate_residency(
            request,
            user_id=test_user.id,
            save_result=True
        )

        # Verify result saved
        history = await service.get_srt_history(test_user.id)
        assert len(history) == 1
        assert history[0].tax_year == '2023/24'
        assert history[0].days_in_uk == 150
        assert history[0].tax_resident is True
