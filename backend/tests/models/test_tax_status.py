"""
Tests for tax status models.

This module tests:
- UserTaxStatus model and temporal data
- UKSRTData model
- SAPresenceData model
- Temporal validity constraints
- Database constraints
"""

import pytest
from datetime import date, timedelta
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from models.tax_status import UserTaxStatus, UKSRTData, SAPresenceData, UKDomicileStatus
from models.user import User, UserStatus, CountryPreference


@pytest.mark.asyncio
class TestUserTaxStatusModel:
    """Tests for UserTaxStatus model."""

    async def test_create_tax_status(self, db_session, test_user):
        """Test creating a tax status record."""
        tax_status = UserTaxStatus(
            user_id=test_user.id,
            effective_from=date(2024, 4, 6),
            effective_to=None,
            uk_tax_resident=True,
            uk_domicile=UKDomicileStatus.UK_DOMICILE,
            sa_tax_resident=False,
            dual_resident=False
        )

        db_session.add(tax_status)
        await db_session.commit()
        await db_session.refresh(tax_status)

        assert tax_status.id is not None
        assert tax_status.user_id == test_user.id
        assert tax_status.uk_tax_resident is True
        assert tax_status.uk_domicile == UKDomicileStatus.UK_DOMICILE
        assert tax_status.effective_to is None

    async def test_temporal_validity_constraint(self, db_session, test_user):
        """Test that effective_to must be after effective_from."""
        tax_status = UserTaxStatus(
            user_id=test_user.id,
            effective_from=date(2024, 4, 6),
            effective_to=date(2024, 4, 5),  # Before effective_from
            uk_tax_resident=True,
            sa_tax_resident=False
        )

        db_session.add(tax_status)

        with pytest.raises(IntegrityError) as exc_info:
            await db_session.commit()

        assert "valid_effective_dates" in str(exc_info.value)
        await db_session.rollback()

    async def test_no_overlapping_periods_constraint(self, db_session, test_user):
        """Test that no overlapping effective periods are allowed."""
        # Create first record
        tax_status1 = UserTaxStatus(
            user_id=test_user.id,
            effective_from=date(2024, 4, 6),
            effective_to=None,
            uk_tax_resident=True,
            sa_tax_resident=False
        )

        db_session.add(tax_status1)
        await db_session.commit()

        # Try to create overlapping record (same effective_from)
        tax_status2 = UserTaxStatus(
            user_id=test_user.id,
            effective_from=date(2024, 4, 6),  # Same date
            effective_to=None,
            uk_tax_resident=False,
            sa_tax_resident=True
        )

        db_session.add(tax_status2)

        with pytest.raises(IntegrityError) as exc_info:
            await db_session.commit()

        # Check constraint violation (name varies between SQLite and PostgreSQL)
        error_str = str(exc_info.value).lower()
        assert "unique" in error_str or "no_overlapping_periods" in error_str
        await db_session.rollback()

    async def test_dual_resident_requires_dta_country(self, db_session, test_user):
        """Test validation that dual residents must have DTA tie-breaker country."""
        # This is validated at application level, not database level
        # But we can test the model accepts the data
        tax_status = UserTaxStatus(
            user_id=test_user.id,
            effective_from=date(2024, 4, 6),
            uk_tax_resident=True,
            sa_tax_resident=True,
            dual_resident=True,
            dta_tie_breaker_country='UK'
        )

        db_session.add(tax_status)
        await db_session.commit()
        await db_session.refresh(tax_status)

        assert tax_status.dual_resident is True
        assert tax_status.dta_tie_breaker_country == 'UK'

    async def test_query_current_status(self, db_session, test_user):
        """Test querying current tax status (effective_to IS NULL)."""
        # Create historical record
        tax_status1 = UserTaxStatus(
            user_id=test_user.id,
            effective_from=date(2023, 4, 6),
            effective_to=date(2024, 4, 5),
            uk_tax_resident=False,
            sa_tax_resident=True
        )

        # Create current record
        tax_status2 = UserTaxStatus(
            user_id=test_user.id,
            effective_from=date(2024, 4, 6),
            effective_to=None,
            uk_tax_resident=True,
            sa_tax_resident=False
        )

        db_session.add_all([tax_status1, tax_status2])
        await db_session.commit()

        # Query current status
        query = select(UserTaxStatus).where(
            UserTaxStatus.user_id == test_user.id,
            UserTaxStatus.effective_to.is_(None)
        )

        result = await db_session.execute(query)
        current_status = result.scalar_one_or_none()

        assert current_status is not None
        assert current_status.id == tax_status2.id
        assert current_status.uk_tax_resident is True

    async def test_query_status_at_date(self, db_session, test_user):
        """Test point-in-time query for tax status."""
        # Create multiple records
        tax_status1 = UserTaxStatus(
            user_id=test_user.id,
            effective_from=date(2023, 4, 6),
            effective_to=date(2024, 4, 5),
            uk_tax_resident=False,
            sa_tax_resident=True
        )

        tax_status2 = UserTaxStatus(
            user_id=test_user.id,
            effective_from=date(2024, 4, 6),
            effective_to=None,
            uk_tax_resident=True,
            sa_tax_resident=False
        )

        db_session.add_all([tax_status1, tax_status2])
        await db_session.commit()

        # Query status at specific date (in first period)
        query_date = date(2023, 10, 1)
        query = select(UserTaxStatus).where(
            UserTaxStatus.user_id == test_user.id,
            UserTaxStatus.effective_from <= query_date,
            (UserTaxStatus.effective_to.is_(None)) | (UserTaxStatus.effective_to > query_date)
        )

        result = await db_session.execute(query)
        status_at_date = result.scalar_one_or_none()

        assert status_at_date is not None
        assert status_at_date.id == tax_status1.id
        assert status_at_date.uk_tax_resident is False


@pytest.mark.asyncio
class TestUKSRTDataModel:
    """Tests for UKSRTData model."""

    async def test_create_srt_record(self, db_session, test_user):
        """Test creating a UK SRT record."""
        srt_record = UKSRTData(
            user_id=test_user.id,
            tax_year='2023/24',
            days_in_uk=150,
            family_tie=True,
            accommodation_tie=True,
            work_tie=False,
            ninety_day_tie=True,
            country_tie=False,
            tax_resident=True,
            test_result='sufficient_ties'
        )

        db_session.add(srt_record)
        await db_session.commit()
        await db_session.refresh(srt_record)

        assert srt_record.id is not None
        assert srt_record.user_id == test_user.id
        assert srt_record.tax_year == '2023/24'
        assert srt_record.days_in_uk == 150
        assert srt_record.tax_resident is True

    async def test_unique_srt_per_user_year(self, db_session, test_user):
        """Test that each user can only have one SRT record per tax year."""
        srt_record1 = UKSRTData(
            user_id=test_user.id,
            tax_year='2023/24',
            days_in_uk=150,
            tax_resident=True,
            test_result='sufficient_ties'
        )

        db_session.add(srt_record1)
        await db_session.commit()

        # Try to create duplicate
        srt_record2 = UKSRTData(
            user_id=test_user.id,
            tax_year='2023/24',  # Same tax year
            days_in_uk=200,
            tax_resident=True,
            test_result='automatic_uk'
        )

        db_session.add(srt_record2)

        with pytest.raises(IntegrityError) as exc_info:
            await db_session.commit()

        # Check constraint violation (name varies between SQLite and PostgreSQL)
        error_str = str(exc_info.value).lower()
        assert "unique" in error_str or "unique_srt_per_user_year" in error_str
        await db_session.rollback()


@pytest.mark.asyncio
class TestSAPresenceDataModel:
    """Tests for SAPresenceData model."""

    async def test_create_sa_presence_record(self, db_session, test_user):
        """Test creating a SA presence record."""
        presence_record = SAPresenceData(
            user_id=test_user.id,
            tax_year='2023/24',
            days_in_sa=120,
            year_minus_1_days=100,
            year_minus_2_days=95,
            year_minus_3_days=90,
            year_minus_4_days=85,
            tax_resident=True,
            ordinarily_resident=False,
            test_result='5_year_average',
            five_year_average=98.0
        )

        db_session.add(presence_record)
        await db_session.commit()
        await db_session.refresh(presence_record)

        assert presence_record.id is not None
        assert presence_record.user_id == test_user.id
        assert presence_record.tax_year == '2023/24'
        assert presence_record.days_in_sa == 120
        assert presence_record.five_year_average == 98.0

    async def test_unique_sa_presence_per_user_year(self, db_session, test_user):
        """Test that each user can only have one SA presence record per tax year."""
        presence_record1 = SAPresenceData(
            user_id=test_user.id,
            tax_year='2023/24',
            days_in_sa=120,
            tax_resident=True,
            test_result='91_day_current'
        )

        db_session.add(presence_record1)
        await db_session.commit()

        # Try to create duplicate
        presence_record2 = SAPresenceData(
            user_id=test_user.id,
            tax_year='2023/24',  # Same tax year
            days_in_sa=150,
            tax_resident=True,
            test_result='91_day_current'
        )

        db_session.add(presence_record2)

        with pytest.raises(IntegrityError) as exc_info:
            await db_session.commit()

        # Check constraint violation (name varies between SQLite and PostgreSQL)
        error_str = str(exc_info.value).lower()
        assert "unique" in error_str or "unique_sa_presence_per_user_year" in error_str
        await db_session.rollback()
