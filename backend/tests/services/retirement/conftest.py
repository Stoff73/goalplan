"""
Pytest fixtures for retirement service tests.

Provides common test fixtures for all retirement service tests.
"""

import pytest
import uuid
from datetime import datetime

from models.user import User, UserStatus, CountryPreference


@pytest.fixture
async def test_user(db_session):
    """
    Create a test user for retirement service tests.

    Returns a User with all required fields populated.
    """
    user = User(
        id=uuid.uuid4(),
        email="retirement_test@example.com",
        password_hash="hashed_password",
        first_name="Test",
        last_name="User",
        country_preference=CountryPreference.UK,
        status=UserStatus.ACTIVE,
        email_verified=True,
        terms_accepted_at=datetime.utcnow(),
        marketing_consent=False
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user
