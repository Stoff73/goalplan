"""
Tests for GET /api/v1/user/profile endpoint.

Test coverage:
- Successful profile retrieval
- Unauthenticated access (401)
- Profile data structure validation
- Password hash exclusion from response
"""

import pytest
from datetime import datetime, date
from uuid import UUID

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User, UserStatus, CountryPreference
from utils.password import hash_password
from utils.jwt import generate_access_token


@pytest.mark.asyncio
async def test_get_profile_success(client: AsyncClient, db_session: AsyncSession):
    """Test successful profile retrieval."""
    # Create test user with profile data
    user = User(
        email="test@example.com",
        password_hash=hash_password("TestPassword123!"),
        first_name="John",
        last_name="Doe",
        country_preference=CountryPreference.BOTH,
        status=UserStatus.ACTIVE,
        email_verified=True,
        terms_accepted_at=datetime.utcnow(),
        phone="+447911123456",
        date_of_birth=date(1990, 1, 1),
        address={
            "line1": "123 Test Street",
            "line2": "Apt 4",
            "city": "London",
            "postcode": "SW1A 1AA",
            "country": "UK",
        },
        timezone="Europe/London",
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create access token
    access_token = generate_access_token(user.id)

    # Make request
    response = await client.get(
        "/api/v1/user/profile",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    # Assertions
    assert response.status_code == 200

    data = response.json()

    # Verify profile data
    assert data["id"] == str(user.id)
    assert data["email"] == "test@example.com"
    assert data["firstName"] == "John"
    assert data["lastName"] == "Doe"
    assert data["phone"] == "+447911123456"
    assert data["dateOfBirth"] == "1990-01-01"
    assert data["address"]["line1"] == "123 Test Street"
    assert data["address"]["city"] == "London"
    assert data["timezone"] == "Europe/London"
    assert data["status"] == "ACTIVE"
    assert data["emailVerified"] is True
    assert data["countryPreference"] == "BOTH"

    # Verify password hash is NOT in response
    assert "password_hash" not in data
    assert "passwordHash" not in data


@pytest.mark.asyncio
async def test_get_profile_unauthenticated(client: AsyncClient):
    """Test profile retrieval without authentication returns 401."""
    response = await client.get("/api/v1/user/profile")

    assert response.status_code == 401
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_get_profile_invalid_token(client: AsyncClient):
    """Test profile retrieval with invalid token returns 401."""
    response = await client.get(
        "/api/v1/user/profile",
        headers={"Authorization": "Bearer invalid_token_here"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_profile_minimal_data(client: AsyncClient, db_session: AsyncSession):
    """Test profile retrieval with minimal user data (no optional fields)."""
    # Create user with only required fields
    user = User(
        email="minimal@example.com",
        password_hash=hash_password("TestPassword123!"),
        first_name="Jane",
        last_name="Smith",
        country_preference=CountryPreference.UK,
        status=UserStatus.ACTIVE,
        email_verified=True,
        terms_accepted_at=datetime.utcnow(),
        # No phone, date_of_birth, or address
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create access token
    access_token = generate_access_token(user.id)

    # Make request
    response = await client.get(
        "/api/v1/user/profile",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    # Assertions
    assert response.status_code == 200

    data = response.json()

    assert data["email"] == "minimal@example.com"
    assert data["firstName"] == "Jane"
    assert data["lastName"] == "Smith"
    assert data["phone"] is None
    assert data["dateOfBirth"] is None
    assert data["address"] is None
    assert data["timezone"] == "Europe/London"  # Default


@pytest.mark.asyncio
async def test_get_profile_suspended_user(client: AsyncClient, db_session: AsyncSession):
    """Test profile retrieval for suspended user returns 403."""
    # Create suspended user
    user = User(
        email="suspended@example.com",
        password_hash=hash_password("TestPassword123!"),
        first_name="Suspended",
        last_name="User",
        country_preference=CountryPreference.UK,
        status=UserStatus.SUSPENDED,
        email_verified=True,
        terms_accepted_at=datetime.utcnow(),
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create access token
    access_token = generate_access_token(user.id)

    # Make request
    response = await client.get(
        "/api/v1/user/profile",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    # Should return 403 Forbidden (user not ACTIVE)
    assert response.status_code == 403
