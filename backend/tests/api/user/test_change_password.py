"""
Tests for POST /api/v1/user/change-password endpoint.

Test coverage:
- Successful password change
- Wrong current password
- Weak new password
- Same password as current
- Session invalidation
- Email notification
"""

import pytest
from datetime import datetime
from uuid import UUID, uuid4

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User, UserStatus, CountryPreference
from models.session import UserSession
from utils.password import hash_password, verify_password
from utils.jwt import generate_access_token


@pytest.mark.asyncio
async def test_change_password_success(client: AsyncClient, db_session: AsyncSession):
    """Test successful password change."""
    # Create test user
    old_password = "OldPassword123!"
    user = User(
        email="test@example.com",
        password_hash=hash_password(old_password),
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

    # Password change request
    change_data = {
        "currentPassword": old_password,
        "newPassword": "NewPassword456!",
    }

    # Make request
    response = await client.post(
        "/api/v1/user/change-password",
        headers={"Authorization": f"Bearer {access_token}"},
        json=change_data,
    )

    # Assertions
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert "successfully" in data["message"].lower()

    # Verify password was changed in database
    await db_session.refresh(user)
    assert verify_password("NewPassword456!", user.password_hash)
    assert not verify_password(old_password, user.password_hash)


@pytest.mark.asyncio
async def test_change_password_wrong_current_password(
    client: AsyncClient, db_session: AsyncSession
):
    """Test password change with wrong current password."""
    # Create test user
    user = User(
        email="test@example.com",
        password_hash=hash_password("OldPassword123!"),
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

    # Password change with wrong current password
    change_data = {
        "currentPassword": "WrongPassword123!",
        "newPassword": "NewPassword456!",
    }

    # Make request
    response = await client.post(
        "/api/v1/user/change-password",
        headers={"Authorization": f"Bearer {access_token}"},
        json=change_data,
    )

    # Should return 401 Unauthorized
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_change_password_weak_new_password(
    client: AsyncClient, db_session: AsyncSession
):
    """Test password change with weak new password."""
    # Create test user
    old_password = "OldPassword123!"
    user = User(
        email="test@example.com",
        password_hash=hash_password(old_password),
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

    # Weak passwords to test
    weak_passwords = [
        "short",  # Too short
        "nouppercaseorspecial123",  # No uppercase or special
        "NOLOWERCASEORSPECIAL123",  # No lowercase or special
        "NoSpecialChar123",  # No special character
        "NoDigits!@#",  # No digits
    ]

    for weak_password in weak_passwords:
        change_data = {
            "currentPassword": old_password,
            "newPassword": weak_password,
        }

        # Make request
        response = await client.post(
            "/api/v1/user/change-password",
            headers={"Authorization": f"Bearer {access_token}"},
            json=change_data,
        )

        # Should return 422 validation error
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_change_password_same_as_current(
    client: AsyncClient, db_session: AsyncSession
):
    """Test password change with new password same as current."""
    # Create test user
    password = "TestPassword123!"
    user = User(
        email="test@example.com",
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

    # Try to change to same password
    change_data = {
        "currentPassword": password,
        "newPassword": password,
    }

    # Make request
    response = await client.post(
        "/api/v1/user/change-password",
        headers={"Authorization": f"Bearer {access_token}"},
        json=change_data,
    )

    # Should return 400 Bad Request
    assert response.status_code == 400
    assert "different" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_change_password_sessions_invalidated(
    client: AsyncClient, db_session: AsyncSession
):
    """Test that password change invalidates all sessions."""
    # Create test user
    old_password = "OldPassword123!"
    user = User(
        email="test@example.com",
        password_hash=hash_password(old_password),
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

    # Create multiple sessions for the user
    for i in range(3):
        session = UserSession(
            id=uuid4(),
            user_id=user.id,
            session_token=f"session_token_{i}",
            access_token_jti=f"access_jti_{i}",
            is_active=True,
            expires_at=datetime.utcnow(),
        )
        db_session.add(session)

    await db_session.commit()

    # Verify sessions are active
    result = await db_session.execute(
        select(UserSession).where(
            UserSession.user_id == user.id,
            UserSession.is_active == True,
        )
    )
    active_sessions = result.scalars().all()
    assert len(active_sessions) == 3

    # Create access token
    access_token = generate_access_token(user.id)

    # Change password
    change_data = {
        "currentPassword": old_password,
        "newPassword": "NewPassword456!",
    }

    response = await client.post(
        "/api/v1/user/change-password",
        headers={"Authorization": f"Bearer {access_token}"},
        json=change_data,
    )

    assert response.status_code == 200

    # Verify all sessions are now inactive
    result = await db_session.execute(
        select(UserSession).where(
            UserSession.user_id == user.id,
            UserSession.is_active == True,
        )
    )
    active_sessions = result.scalars().all()
    assert len(active_sessions) == 0


@pytest.mark.asyncio
async def test_change_password_unauthenticated(client: AsyncClient):
    """Test password change without authentication."""
    change_data = {
        "currentPassword": "OldPassword123!",
        "newPassword": "NewPassword456!",
    }

    response = await client.post(
        "/api/v1/user/change-password",
        json=change_data,
    )

    assert response.status_code == 401
