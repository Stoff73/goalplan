"""
Tests for PATCH /api/v1/user/profile endpoint.

Test coverage:
- Successful profile updates (full and partial)
- Individual field updates
- Invalid data validation
- Audit trail creation
- Unauthenticated access
"""

import pytest
from datetime import datetime, date
from uuid import UUID

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User, UserStatus, CountryPreference
from models.profile import UserProfileHistory
from utils.password import hash_password
from utils.jwt import generate_access_token


@pytest.mark.asyncio
async def test_update_profile_full(client: AsyncClient, db_session: AsyncSession):
    """Test full profile update with all fields."""
    # Create test user
    user = User(
        email="test@example.com",
        password_hash=hash_password("TestPassword123!"),
        first_name="John",
        last_name="Doe",
        country_preference=CountryPreference.UK,
        status=UserStatus.ACTIVE,
        email_verified=True,
        terms_accepted_at=datetime.utcnow(),
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create access token
    access_token = generate_access_token(user.id)

    # Update data
    update_data = {
        "firstName": "Jane",
        "lastName": "Smith",
        "phone": "+447911123456",
        "dateOfBirth": "1990-01-01",
        "address": {
            "line1": "123 Test St",
            "line2": "Apt 4",
            "city": "London",
            "postcode": "SW1A 1AA",
            "country": "UK",
        },
        "timezone": "Europe/London",
    }

    # Make request
    response = await client.patch(
        "/api/v1/user/profile",
        headers={"Authorization": f"Bearer {access_token}"},
        json=update_data,
    )

    # Assertions
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Profile updated successfully"

    # Verify updated fields
    user_data = data["user"]
    assert user_data["firstName"] == "Jane"
    assert user_data["lastName"] == "Smith"
    assert user_data["phone"] == "+447911123456"
    assert user_data["dateOfBirth"] == "1990-01-01"
    assert user_data["address"]["city"] == "London"
    assert user_data["timezone"] == "Europe/London"

    # Verify audit trail created
    result = await db_session.execute(
        select(UserProfileHistory).where(UserProfileHistory.user_id == user.id)
    )
    history_entries = result.scalars().all()

    # Should have 6 history entries (one for each field changed)
    assert len(history_entries) >= 6


@pytest.mark.asyncio
async def test_update_profile_partial(client: AsyncClient, db_session: AsyncSession):
    """Test partial profile update (PATCH semantics)."""
    # Create test user with existing data
    user = User(
        email="test@example.com",
        password_hash=hash_password("TestPassword123!"),
        first_name="John",
        last_name="Doe",
        country_preference=CountryPreference.UK,
        status=UserStatus.ACTIVE,
        email_verified=True,
        terms_accepted_at=datetime.utcnow(),
        phone="+447911111111",
        timezone="Europe/London",
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create access token
    access_token = generate_access_token(user.id)

    # Update only phone
    update_data = {"phone": "+447922222222"}

    # Make request
    response = await client.patch(
        "/api/v1/user/profile",
        headers={"Authorization": f"Bearer {access_token}"},
        json=update_data,
    )

    # Assertions
    assert response.status_code == 200

    data = response.json()
    user_data = data["user"]

    # Phone updated
    assert user_data["phone"] == "+447922222222"

    # Other fields unchanged
    assert user_data["firstName"] == "John"
    assert user_data["lastName"] == "Doe"
    assert user_data["timezone"] == "Europe/London"


@pytest.mark.asyncio
async def test_update_profile_invalid_phone(client: AsyncClient, db_session: AsyncSession):
    """Test profile update with invalid phone number."""
    # Create test user
    user = User(
        email="test@example.com",
        password_hash=hash_password("TestPassword123!"),
        first_name="John",
        last_name="Doe",
        country_preference=CountryPreference.UK,
        status=UserStatus.ACTIVE,
        email_verified=True,
        terms_accepted_at=datetime.utcnow(),
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create access token
    access_token = generate_access_token(user.id)

    # Invalid phone number (no country code, letters)
    update_data = {"phone": "123abc"}

    # Make request
    response = await client.patch(
        "/api/v1/user/profile",
        headers={"Authorization": f"Bearer {access_token}"},
        json=update_data,
    )

    # Should return 422 validation error
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_profile_invalid_date_of_birth(client: AsyncClient, db_session: AsyncSession):
    """Test profile update with invalid date of birth (under 18)."""
    # Create test user
    user = User(
        email="test@example.com",
        password_hash=hash_password("TestPassword123!"),
        first_name="John",
        last_name="Doe",
        country_preference=CountryPreference.UK,
        status=UserStatus.ACTIVE,
        email_verified=True,
        terms_accepted_at=datetime.utcnow(),
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create access token
    access_token = generate_access_token(user.id)

    # Date of birth less than 18 years ago
    update_data = {"dateOfBirth": "2020-01-01"}

    # Make request
    response = await client.patch(
        "/api/v1/user/profile",
        headers={"Authorization": f"Bearer {access_token}"},
        json=update_data,
    )

    # Should return 422 validation error
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_profile_invalid_timezone(client: AsyncClient, db_session: AsyncSession):
    """Test profile update with invalid timezone."""
    # Create test user
    user = User(
        email="test@example.com",
        password_hash=hash_password("TestPassword123!"),
        first_name="John",
        last_name="Doe",
        country_preference=CountryPreference.UK,
        status=UserStatus.ACTIVE,
        email_verified=True,
        terms_accepted_at=datetime.utcnow(),
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create access token
    access_token = generate_access_token(user.id)

    # Invalid timezone
    update_data = {"timezone": "Invalid/Timezone"}

    # Make request
    response = await client.patch(
        "/api/v1/user/profile",
        headers={"Authorization": f"Bearer {access_token}"},
        json=update_data,
    )

    # Should return 422 validation error
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_profile_no_changes(client: AsyncClient, db_session: AsyncSession):
    """Test profile update with no changes."""
    # Create test user
    user = User(
        email="test@example.com",
        password_hash=hash_password("TestPassword123!"),
        first_name="John",
        last_name="Doe",
        country_preference=CountryPreference.UK,
        status=UserStatus.ACTIVE,
        email_verified=True,
        terms_accepted_at=datetime.utcnow(),
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create access token
    access_token = generate_access_token(user.id)

    # Empty update
    update_data = {}

    # Make request
    response = await client.patch(
        "/api/v1/user/profile",
        headers={"Authorization": f"Bearer {access_token}"},
        json=update_data,
    )

    # Should succeed but indicate no changes
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "No changes were made"


@pytest.mark.asyncio
async def test_update_profile_unauthenticated(client: AsyncClient):
    """Test profile update without authentication."""
    update_data = {"firstName": "Jane"}

    response = await client.patch(
        "/api/v1/user/profile",
        json=update_data,
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_profile_audit_trail(client: AsyncClient, db_session: AsyncSession):
    """Test that profile updates create audit trail entries."""
    # Create test user
    user = User(
        email="test@example.com",
        password_hash=hash_password("TestPassword123!"),
        first_name="John",
        last_name="Doe",
        country_preference=CountryPreference.UK,
        status=UserStatus.ACTIVE,
        email_verified=True,
        terms_accepted_at=datetime.utcnow(),
        phone="+447911111111",
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create access token
    access_token = generate_access_token(user.id)

    # Update phone
    update_data = {"phone": "+447922222222"}

    # Make request
    response = await client.patch(
        "/api/v1/user/profile",
        headers={"Authorization": f"Bearer {access_token}"},
        json=update_data,
    )

    assert response.status_code == 200

    # Verify audit trail entry created
    result = await db_session.execute(
        select(UserProfileHistory).where(
            UserProfileHistory.user_id == user.id,
            UserProfileHistory.field_name == "phone",
        )
    )
    history_entry = result.scalar_one_or_none()

    assert history_entry is not None
    assert history_entry.old_value == "+447911111111"
    assert history_entry.new_value == "+447922222222"
    assert history_entry.field_name == "phone"
    assert history_entry.changed_by == user.id


@pytest.mark.asyncio
async def test_update_profile_address(client: AsyncClient, db_session: AsyncSession):
    """Test updating address field."""
    # Create test user
    user = User(
        email="test@example.com",
        password_hash=hash_password("TestPassword123!"),
        first_name="John",
        last_name="Doe",
        country_preference=CountryPreference.UK,
        status=UserStatus.ACTIVE,
        email_verified=True,
        terms_accepted_at=datetime.utcnow(),
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create access token
    access_token = generate_access_token(user.id)

    # Update with valid address
    update_data = {
        "address": {
            "line1": "10 Downing Street",
            "city": "London",
            "postcode": "SW1A 2AA",
            "country": "UK",
        }
    }

    # Make request
    response = await client.patch(
        "/api/v1/user/profile",
        headers={"Authorization": f"Bearer {access_token}"},
        json=update_data,
    )

    assert response.status_code == 200

    data = response.json()
    assert data["user"]["address"]["line1"] == "10 Downing Street"
    assert data["user"]["address"]["city"] == "London"
    assert data["user"]["address"]["postcode"] == "SW1A 2AA"
