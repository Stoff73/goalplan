"""
Tests for disable 2FA endpoint.

Tests cover:
- 2FA disabled with correct credentials
- Cannot disable without password
- Cannot disable without valid TOTP
- 2FA state updated correctly
- Secret and backup codes removed
"""

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from models import User2FA
from services.totp import TOTPService


@pytest.mark.asyncio
class TestDisable2FA:
    """Test suite for disable 2FA endpoint."""

    async def test_disable_2fa_with_totp_success(
        self, async_client: AsyncClient, authenticated_headers, db_session, test_user
    ):
        """Test successfully disabling 2FA with TOTP code."""
        # Enable 2FA
        secret = TOTPService.generate_secret()
        user_2fa = User2FA(
            user_id=test_user.id,
            secret=secret,
            enabled=True,
            backup_codes=[],
        )
        db_session.add(user_2fa)
        await db_session.commit()

        # Generate valid TOTP code
        totp = TOTPService.generate_totp(secret)
        code = totp.now()

        # Disable 2FA
        response = await async_client.post(
            "/api/v1/auth/2fa/disable",
            headers=authenticated_headers,
            json={
                "password": "SecurePass123!",
                "totp_code": code,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "disabled" in data["message"].lower()

    async def test_disable_2fa_with_backup_code_success(
        self, async_client: AsyncClient, authenticated_headers, db_session, test_user
    ):
        """Test successfully disabling 2FA with backup code."""
        # Enable 2FA with backup codes
        secret = TOTPService.generate_secret()
        backup_codes_plain = TOTPService.generate_backup_codes()
        backup_codes_hashed = [
            TOTPService.hash_backup_code(code) for code in backup_codes_plain
        ]

        user_2fa = User2FA(
            user_id=test_user.id,
            secret=secret,
            enabled=True,
            backup_codes=backup_codes_hashed,
        )
        db_session.add(user_2fa)
        await db_session.commit()

        # Disable 2FA with backup code
        response = await async_client.post(
            "/api/v1/auth/2fa/disable",
            headers=authenticated_headers,
            json={
                "password": "SecurePass123!",
                "totp_code": backup_codes_plain[0],
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    async def test_disable_2fa_removes_record(
        self, async_client: AsyncClient, authenticated_headers, db_session, test_user
    ):
        """Test that disabling 2FA removes the record from database."""
        # Enable 2FA
        secret = TOTPService.generate_secret()
        user_2fa = User2FA(
            user_id=test_user.id,
            secret=secret,
            enabled=True,
            backup_codes=[],
        )
        db_session.add(user_2fa)
        await db_session.commit()

        # Generate valid TOTP code
        totp = TOTPService.generate_totp(secret)
        code = totp.now()

        # Disable 2FA
        await async_client.post(
            "/api/v1/auth/2fa/disable",
            headers=authenticated_headers,
            json={
                "password": "SecurePass123!",
                "totp_code": code,
            },
        )

        # Check database - record should be deleted
        result = await db_session.execute(
            select(User2FA).where(User2FA.user_id == test_user.id)
        )
        user_2fa = result.scalar_one_or_none()

        assert user_2fa is None

    async def test_disable_2fa_requires_password(
        self, async_client: AsyncClient, authenticated_headers, db_session, test_user
    ):
        """Test that password is required to disable 2FA."""
        # Enable 2FA
        secret = TOTPService.generate_secret()
        user_2fa = User2FA(
            user_id=test_user.id,
            secret=secret,
            enabled=True,
            backup_codes=[],
        )
        db_session.add(user_2fa)
        await db_session.commit()

        # Generate valid TOTP code
        totp = TOTPService.generate_totp(secret)
        code = totp.now()

        # Try to disable without password
        response = await async_client.post(
            "/api/v1/auth/2fa/disable",
            headers=authenticated_headers,
            json={
                "totp_code": code,
            },
        )

        # Should fail validation
        assert response.status_code == 422  # Validation error

    async def test_disable_2fa_wrong_password(
        self, async_client: AsyncClient, authenticated_headers, db_session, test_user
    ):
        """Test that wrong password fails to disable 2FA."""
        # Enable 2FA
        secret = TOTPService.generate_secret()
        user_2fa = User2FA(
            user_id=test_user.id,
            secret=secret,
            enabled=True,
            backup_codes=[],
        )
        db_session.add(user_2fa)
        await db_session.commit()

        # Generate valid TOTP code
        totp = TOTPService.generate_totp(secret)
        code = totp.now()

        # Try to disable with wrong password
        response = await async_client.post(
            "/api/v1/auth/2fa/disable",
            headers=authenticated_headers,
            json={
                "password": "WrongPassword123!",
                "totp_code": code,
            },
        )

        assert response.status_code == 401
        data = response.json()
        assert "password" in data["detail"].lower()

    async def test_disable_2fa_requires_totp_code(
        self, async_client: AsyncClient, authenticated_headers, db_session, test_user
    ):
        """Test that TOTP/backup code is required to disable 2FA."""
        # Enable 2FA
        secret = TOTPService.generate_secret()
        user_2fa = User2FA(
            user_id=test_user.id,
            secret=secret,
            enabled=True,
            backup_codes=[],
        )
        db_session.add(user_2fa)
        await db_session.commit()

        # Try to disable without TOTP code
        response = await async_client.post(
            "/api/v1/auth/2fa/disable",
            headers=authenticated_headers,
            json={
                "password": "SecurePass123!",
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert "required" in data["detail"].lower()

    async def test_disable_2fa_invalid_totp_code(
        self, async_client: AsyncClient, authenticated_headers, db_session, test_user
    ):
        """Test that invalid TOTP code fails to disable 2FA."""
        # Enable 2FA
        secret = TOTPService.generate_secret()
        user_2fa = User2FA(
            user_id=test_user.id,
            secret=secret,
            enabled=True,
            backup_codes=[],
        )
        db_session.add(user_2fa)
        await db_session.commit()

        # Try to disable with invalid code
        response = await async_client.post(
            "/api/v1/auth/2fa/disable",
            headers=authenticated_headers,
            json={
                "password": "SecurePass123!",
                "totp_code": "000000",
            },
        )

        assert response.status_code == 401
        data = response.json()
        assert "invalid" in data["detail"].lower() or "expired" in data["detail"].lower()

    async def test_disable_2fa_not_enabled(
        self, async_client: AsyncClient, authenticated_headers
    ):
        """Test that disabling 2FA fails when not enabled."""
        response = await async_client.post(
            "/api/v1/auth/2fa/disable",
            headers=authenticated_headers,
            json={
                "password": "SecurePass123!",
                "totp_code": "123456",
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert "not enabled" in data["detail"].lower()

    async def test_disable_2fa_requires_authentication(
        self, async_client: AsyncClient
    ):
        """Test that disable endpoint requires authentication."""
        response = await async_client.post(
            "/api/v1/auth/2fa/disable",
            json={
                "password": "SecurePass123!",
                "totp_code": "123456",
            },
        )

        assert response.status_code == 401
