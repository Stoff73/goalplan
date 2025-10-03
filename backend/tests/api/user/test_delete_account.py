"""
Tests for POST /api/v1/user/delete-account endpoint.

Test coverage:
- Successful account deletion (soft delete)
- Wrong password
- Account already deleted
- Data export generation
- Session invalidation
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User, UserStatus, CountryPreference
from models.session import UserSession
from utils.password import hash_password
from utils.jwt import generate_access_token


@pytest.mark.asyncio
async def test_delete_account_success(client: AsyncClient, db_session: AsyncSession):
    """Test successful account deletion."""
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

    # Delete account request
    delete_data = {
        "password": password,
        "exportData": False,
    }

    # Make request
    response = await client.post(
        "/api/v1/user/delete-account",
        headers={"Authorization": f"Bearer {access_token}"},
        json=delete_data,
    )

    # Assertions
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert "deleted" in data["message"].lower()
    assert data["deletionDate"] is not None
    assert data["exportUrl"] is None

    # Verify user status changed to DELETED
    await db_session.refresh(user)
    assert user.status == UserStatus.DELETED
    assert user.deleted_at is not None

    # Verify deleted_at is approximately now
    assert (datetime.utcnow() - user.deleted_at).total_seconds() < 60

    # Verify deletion_date is 30 days in the future
    deletion_date_from_response = datetime.fromisoformat(
        data["deletionDate"].replace("Z", "+00:00")
    )
    expected_deletion = user.deleted_at + timedelta(days=30)
    time_diff = abs((deletion_date_from_response - expected_deletion).total_seconds())
    assert time_diff < 60  # Within 1 minute


@pytest.mark.asyncio
async def test_delete_account_wrong_password(client: AsyncClient, db_session: AsyncSession):
    """Test account deletion with wrong password."""
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

    # Wrong password
    delete_data = {
        "password": "WrongPassword123!",
        "exportData": False,
    }

    response = await client.post(
        "/api/v1/user/delete-account",
        headers={"Authorization": f"Bearer {access_token}"},
        json=delete_data,
    )

    # Should return 401 Unauthorized
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()

    # Verify account was NOT deleted
    await db_session.refresh(user)
    assert user.status == UserStatus.ACTIVE
    assert user.deleted_at is None


@pytest.mark.asyncio
async def test_delete_account_already_deleted(client: AsyncClient, db_session: AsyncSession):
    """Test deleting an already deleted account."""
    password = "TestPassword123!"
    user = User(
        email="test@example.com",
        password_hash=hash_password(password),
        first_name="John",
        last_name="Doe",
        country_preference=CountryPreference.UK,
        status=UserStatus.DELETED,  # Already deleted
        email_verified=True,
        terms_accepted_at=datetime.utcnow(),
        deleted_at=datetime.utcnow(),
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    access_token = generate_access_token(user.id)

    delete_data = {
        "password": password,
        "exportData": False,
    }

    response = await client.post(
        "/api/v1/user/delete-account",
        headers={"Authorization": f"Bearer {access_token}"},
        json=delete_data,
    )

    # Should return 400 Bad Request (but first 403 because user not ACTIVE)
    # Actually will return 403 from the get_current_active_user dependency
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_account_with_data_export(
    client: AsyncClient, db_session: AsyncSession
):
    """Test account deletion with data export."""
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

    access_token = generate_access_token(user.id)

    # Request data export
    delete_data = {
        "password": password,
        "exportData": True,
    }

    response = await client.post(
        "/api/v1/user/delete-account",
        headers={"Authorization": f"Bearer {access_token}"},
        json=delete_data,
    )

    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    # Export URL should be provided
    assert data["exportUrl"] is not None
    assert len(data["exportUrl"]) > 0


@pytest.mark.asyncio
async def test_delete_account_sessions_invalidated(
    client: AsyncClient, db_session: AsyncSession
):
    """Test that account deletion invalidates all sessions."""
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

    # Create multiple sessions
    for i in range(3):
        session = UserSession(
            id=uuid4(),
            user_id=user.id,
            session_token=f"session_token_{i}",
            access_token_jti=f"access_jti_{i}",
            is_active=True,
            expires_at=datetime.utcnow() + timedelta(days=7),
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

    access_token = generate_access_token(user.id)

    # Delete account
    delete_data = {
        "password": password,
        "exportData": False,
    }

    response = await client.post(
        "/api/v1/user/delete-account",
        headers={"Authorization": f"Bearer {access_token}"},
        json=delete_data,
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
async def test_delete_account_unauthenticated(client: AsyncClient):
    """Test account deletion without authentication."""
    delete_data = {
        "password": "TestPassword123!",
        "exportData": False,
    }

    response = await client.post(
        "/api/v1/user/delete-account",
        json=delete_data,
    )

    assert response.status_code == 401
