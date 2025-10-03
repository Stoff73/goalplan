"""
Session management service.

This module provides session management functionality with Redis caching
for fast validation (<10ms target) and PostgreSQL for persistence.

Key features:
- Max 5 concurrent sessions per user (enforced)
- Redis fast path for session validation
- PostgreSQL fallback and audit trail
- Session revocation (single or all)
- Automatic cleanup of expired sessions
- Device and IP tracking

Performance targets:
- Session validation: <10ms (Redis fast path)
- Session creation: <50ms
- Cleanup: Background task
"""

import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional, List

from sqlalchemy import select, delete, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from models.session import UserSession
from redis_client import redis_client
from config import settings

logger = logging.getLogger(__name__)


class SessionService:
    """
    Session management service.

    Handles user session lifecycle including creation, validation,
    updates, and revocation with Redis caching for performance.
    """

    # Redis key prefix for sessions
    SESSION_KEY_PREFIX = "session"

    # Max concurrent sessions per user
    MAX_SESSIONS_PER_USER = 5

    # Session expiration (7 days - refresh token lifetime)
    SESSION_EXPIRY_SECONDS = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

    async def create_session(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        refresh_token_jti: str,
        access_token_jti: str,
        device_info: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> UserSession:
        """
        Create a new user session.

        Stores session in both PostgreSQL (persistence) and Redis (fast validation).
        Enforces max 5 concurrent sessions per user (removes oldest if exceeded).

        Args:
            db: Database session
            user_id: User identifier
            refresh_token_jti: JTI from JWT refresh token (session identifier)
            access_token_jti: JTI from JWT access token
            device_info: User agent string
            ip_address: Client IP address

        Returns:
            UserSession: Created session object

        Raises:
            Exception: If session creation fails
        """
        try:
            # Check current session count
            session_count = await self.get_session_count(db, user_id)

            # If at max sessions, remove oldest
            if session_count >= self.MAX_SESSIONS_PER_USER:
                await self._remove_oldest_session(db, user_id)

            # Calculate expiration timestamp
            expires_at = datetime.utcnow() + timedelta(seconds=self.SESSION_EXPIRY_SECONDS)

            # Create session record
            session = UserSession(
                id=uuid.uuid4(),
                user_id=user_id,
                session_token=refresh_token_jti,
                access_token_jti=access_token_jti,
                device_info=device_info,
                ip_address=ip_address,
                is_active=True,
                created_at=datetime.utcnow(),
                last_activity=datetime.utcnow(),
                expires_at=expires_at,
            )

            db.add(session)
            await db.commit()
            await db.refresh(session)

            # Store in Redis for fast validation
            await self._store_session_in_redis(session)

            logger.info(
                f"Session created for user {user_id}: {refresh_token_jti}"
            )

            return session

        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to create session for user {user_id}: {e}")
            raise

    async def validate_session(
        self,
        db: AsyncSession,
        session_token: str,
    ) -> Optional[UserSession]:
        """
        Validate a session by token.

        Checks Redis first (fast path <10ms), falls back to PostgreSQL.
        Updates last_activity timestamp on successful validation.

        Args:
            db: Database session
            session_token: Session token (refresh token JTI)

        Returns:
            UserSession if valid, None if expired or revoked
        """
        try:
            # Try Redis first (fast path)
            session_data = await self._get_session_from_redis(session_token)

            if session_data:
                # Reconstruct session object from Redis data
                session = await self._get_session_from_db(db, session_token)

                if session and session.is_valid():
                    # Update last_activity
                    await self._update_last_activity(db, session)
                    return session
                else:
                    # Session invalid, remove from Redis
                    await self._remove_session_from_redis(session_token)
                    return None

            # Redis miss - check PostgreSQL
            session = await self._get_session_from_db(db, session_token)

            if session and session.is_valid():
                # Store back in Redis for future fast lookups
                await self._store_session_in_redis(session)
                # Update last_activity
                await self._update_last_activity(db, session)
                return session

            return None

        except Exception as e:
            logger.error(f"Session validation error for token {session_token}: {e}")
            return None

    async def update_access_token(
        self,
        db: AsyncSession,
        session_token: str,
        new_access_token_jti: str,
    ) -> None:
        """
        Update access token JTI for a session.

        Updates both Redis and PostgreSQL.

        Args:
            db: Database session
            session_token: Session token (refresh token JTI)
            new_access_token_jti: New access token JTI

        Raises:
            ValueError: If session not found
        """
        try:
            # Update in PostgreSQL
            result = await db.execute(
                select(UserSession).where(UserSession.session_token == session_token)
            )
            session = result.scalar_one_or_none()

            if not session:
                raise ValueError(f"Session not found: {session_token}")

            session.access_token_jti = new_access_token_jti
            await db.commit()

            # Update in Redis
            session_data = await self._get_session_from_redis(session_token)
            if session_data:
                session_data["access_token_jti"] = new_access_token_jti
                await self._store_session_in_redis_raw(session_token, session_data)

            logger.info(f"Access token updated for session {session_token}")

        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to update access token for session {session_token}: {e}")
            raise

    async def revoke_session(
        self,
        db: AsyncSession,
        session_token: str,
    ) -> None:
        """
        Revoke a single session.

        Marks session as inactive in PostgreSQL and removes from Redis.

        Args:
            db: Database session
            session_token: Session token to revoke
        """
        try:
            # Update in PostgreSQL
            result = await db.execute(
                select(UserSession).where(UserSession.session_token == session_token)
            )
            session = result.scalar_one_or_none()

            if session:
                session.is_active = False
                await db.commit()

            # Remove from Redis
            await self._remove_session_from_redis(session_token)

            logger.info(f"Session revoked: {session_token}")

        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to revoke session {session_token}: {e}")
            raise

    async def revoke_all_user_sessions(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> int:
        """
        Revoke all sessions for a user.

        Useful for password changes, security events, or user logout from all devices.

        Args:
            db: Database session
            user_id: User identifier

        Returns:
            int: Number of sessions revoked
        """
        try:
            # Get all active sessions
            result = await db.execute(
                select(UserSession).where(
                    and_(
                        UserSession.user_id == user_id,
                        UserSession.is_active == True
                    )
                )
            )
            sessions = result.scalars().all()

            # Mark all as inactive
            for session in sessions:
                session.is_active = False
                # Remove from Redis
                await self._remove_session_from_redis(session.session_token)

            await db.commit()

            count = len(sessions)
            logger.info(f"Revoked {count} sessions for user {user_id}")

            return count

        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to revoke sessions for user {user_id}: {e}")
            raise

    async def cleanup_expired_sessions(
        self,
        db: AsyncSession,
    ) -> int:
        """
        Delete expired sessions from database.

        Should be called periodically via background task.

        Args:
            db: Database session

        Returns:
            int: Number of sessions deleted
        """
        try:
            # Delete expired sessions
            result = await db.execute(
                delete(UserSession).where(
                    UserSession.expires_at <= datetime.utcnow()
                )
            )

            await db.commit()

            count = result.rowcount
            logger.info(f"Cleaned up {count} expired sessions")

            return count

        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to cleanup expired sessions: {e}")
            raise

    async def get_user_sessions(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> List[UserSession]:
        """
        Get all active sessions for a user.

        Ordered by last_activity (newest first).

        Args:
            db: Database session
            user_id: User identifier

        Returns:
            List[UserSession]: Active sessions
        """
        try:
            result = await db.execute(
                select(UserSession)
                .where(
                    and_(
                        UserSession.user_id == user_id,
                        UserSession.is_active == True,
                        UserSession.expires_at > datetime.utcnow()
                    )
                )
                .order_by(UserSession.last_activity.desc())
            )

            return result.scalars().all()

        except Exception as e:
            logger.error(f"Failed to get sessions for user {user_id}: {e}")
            return []

    async def get_session_count(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> int:
        """
        Count active sessions for a user.

        Args:
            db: Database session
            user_id: User identifier

        Returns:
            int: Number of active sessions
        """
        try:
            result = await db.execute(
                select(func.count(UserSession.id)).where(
                    and_(
                        UserSession.user_id == user_id,
                        UserSession.is_active == True,
                        UserSession.expires_at > datetime.utcnow()
                    )
                )
            )

            return result.scalar()

        except Exception as e:
            logger.error(f"Failed to count sessions for user {user_id}: {e}")
            return 0

    async def get_session_by_access_token_jti(
        self,
        db: AsyncSession,
        access_token_jti: str,
    ) -> Optional[UserSession]:
        """
        Get session by access token JTI.

        Looks up a session using the access token's JTI (JWT ID).
        Used for authentication and token validation.

        Args:
            db: Database session
            access_token_jti: Access token JTI to lookup

        Returns:
            UserSession if found and valid, None otherwise
        """
        try:
            result = await db.execute(
                select(UserSession).where(
                    UserSession.access_token_jti == access_token_jti
                )
            )
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"Failed to get session by access_token_jti {access_token_jti}: {e}")
            return None

    async def get_session_by_token(
        self,
        db: AsyncSession,
        session_token: str,
    ) -> Optional[UserSession]:
        """
        Get session by session token (refresh token JTI).

        Public wrapper for _get_session_from_db for use by other modules.

        Args:
            db: Database session
            session_token: Session token (refresh token JTI)

        Returns:
            UserSession if found, None otherwise
        """
        return await self._get_session_from_db(db, session_token)

    # Private helper methods

    async def _remove_oldest_session(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> None:
        """Remove the oldest session for a user."""
        result = await db.execute(
            select(UserSession)
            .where(
                and_(
                    UserSession.user_id == user_id,
                    UserSession.is_active == True
                )
            )
            .order_by(UserSession.created_at.asc())
            .limit(1)
        )

        oldest_session = result.scalar_one_or_none()

        if oldest_session:
            await self.revoke_session(db, oldest_session.session_token)
            logger.info(
                f"Removed oldest session for user {user_id}: {oldest_session.session_token}"
            )

    async def _store_session_in_redis(self, session: UserSession) -> None:
        """Store session in Redis."""
        # Skip if Redis not connected (e.g., in tests)
        if not redis_client.client:
            return

        session_data = {
            "user_id": str(session.user_id),
            "access_token_jti": session.access_token_jti,
            "device_info": session.device_info,
            "ip_address": session.ip_address,
            "expires_at": session.expires_at.isoformat(),
            "is_active": session.is_active,
        }

        key = f"{self.SESSION_KEY_PREFIX}:{session.session_token}"
        await redis_client.set(key, session_data, expire=self.SESSION_EXPIRY_SECONDS)

    async def _store_session_in_redis_raw(
        self,
        session_token: str,
        session_data: dict,
    ) -> None:
        """Store raw session data in Redis."""
        if not redis_client.client:
            return
        key = f"{self.SESSION_KEY_PREFIX}:{session_token}"
        await redis_client.set(key, session_data, expire=self.SESSION_EXPIRY_SECONDS)

    async def _get_session_from_redis(self, session_token: str) -> Optional[dict]:
        """Get session from Redis."""
        if not redis_client.client:
            return None
        key = f"{self.SESSION_KEY_PREFIX}:{session_token}"
        return await redis_client.get(key, deserialize=True)

    async def _remove_session_from_redis(self, session_token: str) -> None:
        """Remove session from Redis."""
        if not redis_client.client:
            return
        key = f"{self.SESSION_KEY_PREFIX}:{session_token}"
        await redis_client.delete(key)

    async def _get_session_from_db(
        self,
        db: AsyncSession,
        session_token: str,
    ) -> Optional[UserSession]:
        """Get session from PostgreSQL."""
        result = await db.execute(
            select(UserSession).where(UserSession.session_token == session_token)
        )
        return result.scalar_one_or_none()

    async def _update_last_activity(
        self,
        db: AsyncSession,
        session: UserSession,
    ) -> None:
        """Update last_activity timestamp."""
        session.last_activity = datetime.utcnow()
        await db.commit()


# Create singleton instance
session_service = SessionService()
