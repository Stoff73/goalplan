"""
Tests for email change endpoints.

Test coverage:
- POST /api/v1/user/change-email - Request email change
- POST /api/v1/user/verify-email-change - Verify with token
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User, UserStatus, CountryPreference
from models.profile import EmailChangeToken
from utils.password import hash_password
from utils.jwt import generate_access_token


@pytest.mark.asyncio
async def test_change_email_success(client: AsyncClient, db_session: AsyncSession):
    """Test successful email change request."""
    # Create test user
    password = "TestPassword123!"
    user = User(
        email="old@example.com",
        password_hash=hash_password(password),
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

    # Email change request
    change_data = {
        "newEmail": "new@example.com",
        "password": password,
    }

    # Make request
    response = await client.post(
        "/api/v1/user/change-email",
        headers={"Authorization": f"Bearer {access_token}"},
        json=change_data,
    )

    # Assertions
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert "verification" in data["message"].lower()

    # Verify email change token was created
    result = await db_session.execute(
        select(EmailChangeToken).where(EmailChangeToken.user_id == user.id)
    )
    token = result.scalar_one_or_none()

    assert token is not None
    assert token.new_email == "new@example.com"
    assert token.old_email == "old@example.com"
    assert token.used is False


@pytest.mark.asyncio
async def test_change_email_wrong_password(client: AsyncClient, db_session: AsyncSession):
    """Test email change with wrong password."""
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

    access_token = generate_access_token(user.id)

    change_data = {
        "newEmail": "new@example.com",
        "password": "WrongPassword123!",
    }

    response = await client.post(
        "/api/v1/user/change-email",
        headers={"Authorization": f"Bearer {access_token}"},
        json=change_data,
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_change_email_already_in_use(client: AsyncClient, db_session: AsyncSession):
    """Test email change to an email already in use."""
    password = "TestPassword123!"

    # Create first user
    user1 = User(
        email="existing@example.com",
        password_hash=hash_password(password),
        first_name="Existing",
        last_name="User",
        country_preference=CountryPreference.UK,
        status=UserStatus.ACTIVE,
        email_verified=True,
        terms_accepted_at=datetime.utcnow(),
    )

    # Create second user
    user2 = User(
        email="test@example.com",
        password_hash=hash_password(password),
        first_name="Test",
        last_name="User",
        country_preference=CountryPreference.UK,
        status=UserStatus.ACTIVE,
        email_verified=True,
        terms_accepted_at=datetime.utcnow(),
    )

    db_session.add(user1)
    db_session.add(user2)
    await db_session.commit()
    await db_session.refresh(user2)

    access_token = generate_access_token(user2.id)

    # Try to change to existing email
    change_data = {
        "newEmail": "existing@example.com",
        "password": password,
    }

    response = await client.post(
        "/api/v1/user/change-email",
        headers={"Authorization": f"Bearer {access_token}"},
        json=change_data,
    )

    # Should return 409 Conflict
    assert response.status_code == 409
    assert "already in use" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_verify_email_change_success(client: AsyncClient, db_session: AsyncSession):
    """Test successful email change verification."""
    # Create user
    user = User(
        email="old@example.com",
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

    # Create email change token
    token_str = str(uuid4())
    token = EmailChangeToken(
        id=uuid4(),
        user_id=user.id,
        new_email="new@example.com",
        old_email="old@example.com",
        token=token_str,
        expires_at=datetime.utcnow() + timedelta(hours=24),
        used=False,
    )

    db_session.add(token)
    await db_session.commit()

    # Verify email change
    verify_data = {"token": token_str}

    response = await client.post(
        "/api/v1/user/verify-email-change",
        json=verify_data,
    )

    # Assertions
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert data["email"] == "new@example.com"

    # Verify email was updated in database
    await db_session.refresh(user)
    assert user.email == "new@example.com"

    # Verify token was marked as used
    await db_session.refresh(token)
    assert token.used is True


@pytest.mark.asyncio
async def test_verify_email_change_invalid_token(client: AsyncClient):
    """Test email verification with invalid token."""
    verify_data = {"token": "invalid_token"}

    response = await client.post(
        "/api/v1/user/verify-email-change",
        json=verify_data,
    )

    assert response.status_code == 400
    assert "invalid" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_verify_email_change_expired_token(client: AsyncClient, db_session: AsyncSession):
    """Test email verification with expired token."""
    # Create user
    user = User(
        email="old@example.com",
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

    # Create expired token
    token_str = str(uuid4())
    token = EmailChangeToken(
        id=uuid4(),
        user_id=user.id,
        new_email="new@example.com",
        old_email="old@example.com",
        token=token_str,
        expires_at=datetime.utcnow() - timedelta(hours=1),  # Expired
        used=False,
    )

    db_session.add(token)
    await db_session.commit()

    # Try to verify
    verify_data = {"token": token_str}

    response = await client.post(
        "/api/v1/user/verify-email-change",
        json=verify_data,
    )

    assert response.status_code == 400
    assert "expired" in response.json()["detail"].lower()
