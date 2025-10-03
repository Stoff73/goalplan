"""
Comprehensive test suite for JWT token service.

Tests cover:
- Access token generation
- Refresh token generation
- Token claim validation
- Signature verification
- Expiration detection
- Token decoding
- Invalid signature rejection
- Malformed token rejection
- Token type validation
"""

import time
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import pytest
from jose import jwt

from config import settings
from utils.jwt import (
    decode_token,
    generate_access_token,
    generate_refresh_token,
    get_token_jti,
    verify_token,
)


class TestAccessTokenGeneration:
    """Tests for access token generation."""

    def test_generate_access_token_success(self):
        """Test successful access token generation."""
        user_id = uuid4()

        token = generate_access_token(user_id)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_access_token_contains_correct_claims(self):
        """Test access token contains all required claims."""
        user_id = uuid4()

        token = generate_access_token(user_id)
        payload = decode_token(token)

        # Check all required claims exist
        assert "sub" in payload
        assert "jti" in payload
        assert "exp" in payload
        assert "iat" in payload
        assert "type" in payload

        # Validate claim values
        assert payload["sub"] == str(user_id)
        assert payload["type"] == "access"

        # Validate UUIDs are valid
        assert UUID(payload["sub"]) == user_id
        assert UUID(payload["jti"])  # Should not raise

    def test_access_token_expiration_time(self):
        """Test access token expires in 15 minutes."""
        user_id = uuid4()

        token = generate_access_token(user_id)
        payload = decode_token(token)

        # Get issued at and expiration timestamps
        iat = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)

        # Calculate difference
        time_diff = exp - iat

        # Should be 15 minutes (within 1 second tolerance)
        expected_delta = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        assert abs(time_diff - expected_delta) < timedelta(seconds=1)

    def test_access_token_unique_jti(self):
        """Test each access token has unique JWT ID."""
        user_id = uuid4()

        token1 = generate_access_token(user_id)
        token2 = generate_access_token(user_id)

        payload1 = decode_token(token1)
        payload2 = decode_token(token2)

        # JTI should be different
        assert payload1["jti"] != payload2["jti"]

    def test_generate_access_token_invalid_user_id(self):
        """Test access token generation with invalid user_id."""
        with pytest.raises(ValueError, match="user_id must be a UUID"):
            generate_access_token("not-a-uuid")

        with pytest.raises(ValueError, match="user_id must be a UUID"):
            generate_access_token(123)

        with pytest.raises(ValueError, match="user_id must be a UUID"):
            generate_access_token(None)


class TestRefreshTokenGeneration:
    """Tests for refresh token generation."""

    def test_generate_refresh_token_success(self):
        """Test successful refresh token generation."""
        user_id = uuid4()

        token = generate_refresh_token(user_id)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_refresh_token_contains_correct_claims(self):
        """Test refresh token contains all required claims."""
        user_id = uuid4()

        token = generate_refresh_token(user_id)
        payload = decode_token(token)

        # Check all required claims exist
        assert "sub" in payload
        assert "jti" in payload
        assert "exp" in payload
        assert "iat" in payload
        assert "type" in payload

        # Validate claim values
        assert payload["sub"] == str(user_id)
        assert payload["type"] == "refresh"

        # Validate UUIDs are valid
        assert UUID(payload["sub"]) == user_id
        assert UUID(payload["jti"])  # Should not raise

    def test_refresh_token_expiration_time(self):
        """Test refresh token expires in 7 days."""
        user_id = uuid4()

        token = generate_refresh_token(user_id)
        payload = decode_token(token)

        # Get issued at and expiration timestamps
        iat = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)

        # Calculate difference
        time_diff = exp - iat

        # Should be 7 days (within 1 second tolerance)
        expected_delta = timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        assert abs(time_diff - expected_delta) < timedelta(seconds=1)

    def test_refresh_token_unique_jti(self):
        """Test each refresh token has unique JWT ID."""
        user_id = uuid4()

        token1 = generate_refresh_token(user_id)
        token2 = generate_refresh_token(user_id)

        payload1 = decode_token(token1)
        payload2 = decode_token(token2)

        # JTI should be different
        assert payload1["jti"] != payload2["jti"]

    def test_generate_refresh_token_invalid_user_id(self):
        """Test refresh token generation with invalid user_id."""
        with pytest.raises(ValueError, match="user_id must be a UUID"):
            generate_refresh_token("not-a-uuid")


class TestTokenVerification:
    """Tests for token signature verification."""

    def test_verify_access_token_success(self):
        """Test successful access token verification."""
        user_id = uuid4()
        token = generate_access_token(user_id)

        payload = verify_token(token, token_type="access")

        assert payload is not None
        assert payload["sub"] == str(user_id)
        assert payload["type"] == "access"

    def test_verify_refresh_token_success(self):
        """Test successful refresh token verification."""
        user_id = uuid4()
        token = generate_refresh_token(user_id)

        payload = verify_token(token, token_type="refresh")

        assert payload is not None
        assert payload["sub"] == str(user_id)
        assert payload["type"] == "refresh"

    def test_verify_token_without_type_check(self):
        """Test token verification without type validation."""
        user_id = uuid4()
        access_token = generate_access_token(user_id)
        refresh_token = generate_refresh_token(user_id)

        # Should verify both without type check
        payload1 = verify_token(access_token)
        payload2 = verify_token(refresh_token)

        assert payload1["type"] == "access"
        assert payload2["type"] == "refresh"

    def test_verify_token_wrong_type(self):
        """Test token verification fails with wrong type."""
        user_id = uuid4()
        access_token = generate_access_token(user_id)

        # Try to verify access token as refresh token
        with pytest.raises(ValueError, match="Invalid token type.*Expected 'refresh'"):
            verify_token(access_token, token_type="refresh")

    def test_verify_expired_token(self):
        """Test expired token detection."""
        user_id = uuid4()

        # Manually create expired token
        now = datetime.now(timezone.utc)
        past_time = now - timedelta(minutes=20)  # 20 minutes ago

        claims = {
            "sub": str(user_id),
            "jti": str(uuid4()),
            "exp": past_time,  # Already expired
            "iat": past_time - timedelta(minutes=15),
            "type": "access",
        }

        private_key = settings.get_jwt_private_key()
        expired_token = jwt.encode(claims, private_key, algorithm=settings.JWT_ALGORITHM)

        # Should raise expired error
        with pytest.raises(ValueError, match="Token has expired"):
            verify_token(expired_token)

    def test_verify_token_invalid_signature(self):
        """Test invalid signature rejection."""
        user_id = uuid4()
        token = generate_access_token(user_id)

        # Tamper with token by changing last character
        tampered_token = token[:-5] + "XXXXX"

        with pytest.raises(ValueError, match="Invalid token"):
            verify_token(tampered_token)

    def test_verify_token_empty(self):
        """Test empty token rejection."""
        with pytest.raises(ValueError, match="Token cannot be empty"):
            verify_token("")

        with pytest.raises(ValueError, match="Token cannot be empty"):
            verify_token(None)

    def test_verify_token_malformed(self):
        """Test malformed token rejection."""
        malformed_tokens = [
            "not.a.token",
            "invalid_token",
            "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9",  # Only header
            "a.b",  # Too short
        ]

        for malformed_token in malformed_tokens:
            with pytest.raises(ValueError, match="Invalid token"):
                verify_token(malformed_token)

    def test_verify_token_signed_with_wrong_key(self):
        """Test token signed with different key is rejected."""
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.backends import default_backend

        # Generate different key pair
        different_private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=default_backend()
        )
        different_private_pem = different_private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode()

        # Create token with different key
        user_id = uuid4()
        now = datetime.now(timezone.utc)
        claims = {
            "sub": str(user_id),
            "jti": str(uuid4()),
            "exp": now + timedelta(minutes=15),
            "iat": now,
            "type": "access",
        }

        wrong_key_token = jwt.encode(claims, different_private_pem, algorithm="RS256")

        # Should fail verification with our public key
        with pytest.raises(ValueError, match="Invalid token"):
            verify_token(wrong_key_token)


class TestTokenDecoding:
    """Tests for token payload decoding."""

    def test_decode_token_success(self):
        """Test successful token decoding."""
        user_id = uuid4()
        token = generate_access_token(user_id)

        payload = decode_token(token)

        assert payload is not None
        assert payload["sub"] == str(user_id)
        assert payload["type"] == "access"

    def test_decode_expired_token(self):
        """Test decoding expired token (should succeed without verification)."""
        user_id = uuid4()

        # Create expired token
        now = datetime.now(timezone.utc)
        past_time = now - timedelta(minutes=20)

        claims = {
            "sub": str(user_id),
            "jti": str(uuid4()),
            "exp": past_time,
            "iat": past_time - timedelta(minutes=15),
            "type": "access",
        }

        private_key = settings.get_jwt_private_key()
        expired_token = jwt.encode(claims, private_key, algorithm=settings.JWT_ALGORITHM)

        # Should decode successfully (no verification)
        payload = decode_token(expired_token)
        assert payload["sub"] == str(user_id)

    def test_decode_token_empty(self):
        """Test decoding empty token."""
        with pytest.raises(ValueError, match="Token cannot be empty"):
            decode_token("")

    def test_decode_token_malformed(self):
        """Test decoding malformed token."""
        with pytest.raises(ValueError, match="Malformed token"):
            decode_token("not.a.valid.token")

    def test_get_token_jti_success(self):
        """Test extracting JTI from token."""
        user_id = uuid4()
        token = generate_access_token(user_id)

        jti = get_token_jti(token)

        assert jti is not None
        assert UUID(jti)  # Should be valid UUID

    def test_get_token_jti_from_refresh_token(self):
        """Test extracting JTI from refresh token."""
        user_id = uuid4()
        token = generate_refresh_token(user_id)

        jti = get_token_jti(token)

        assert jti is not None
        assert UUID(jti)  # Should be valid UUID

    def test_get_token_jti_invalid_token(self):
        """Test JTI extraction from invalid token."""
        with pytest.raises(ValueError, match="Malformed token"):
            get_token_jti("invalid_token")


class TestTokenTypeValidation:
    """Tests for token type validation."""

    def test_access_token_type_claim(self):
        """Test access token has correct type claim."""
        user_id = uuid4()
        token = generate_access_token(user_id)

        payload = decode_token(token)

        assert payload["type"] == "access"

    def test_refresh_token_type_claim(self):
        """Test refresh token has correct type claim."""
        user_id = uuid4()
        token = generate_refresh_token(user_id)

        payload = decode_token(token)

        assert payload["type"] == "refresh"

    def test_verify_enforces_token_type(self):
        """Test verify_token enforces token type when specified."""
        user_id = uuid4()
        access_token = generate_access_token(user_id)
        refresh_token = generate_refresh_token(user_id)

        # Correct type should succeed
        verify_token(access_token, token_type="access")
        verify_token(refresh_token, token_type="refresh")

        # Wrong type should fail
        with pytest.raises(ValueError, match="Invalid token type"):
            verify_token(access_token, token_type="refresh")

        with pytest.raises(ValueError, match="Invalid token type"):
            verify_token(refresh_token, token_type="access")


class TestRS256SigningVerification:
    """Tests specifically for RS256 asymmetric signing."""

    def test_token_signed_with_rs256(self):
        """Test tokens are signed with RS256 algorithm."""
        user_id = uuid4()
        token = generate_access_token(user_id)

        # Decode header to check algorithm
        header = jwt.get_unverified_header(token)

        assert header["alg"] == "RS256"
        assert header["typ"] == "JWT"

    def test_private_key_for_signing(self):
        """Test tokens are signed with private key."""
        user_id = uuid4()
        token = generate_access_token(user_id)

        # Should be able to verify with public key
        public_key = settings.get_jwt_public_key()
        payload = jwt.decode(token, public_key, algorithms=["RS256"])

        assert payload["sub"] == str(user_id)

    def test_public_key_cannot_sign(self):
        """Test public key cannot be used for signing."""
        from jose.exceptions import JWTError

        user_id = uuid4()
        now = datetime.now(timezone.utc)

        claims = {
            "sub": str(user_id),
            "jti": str(uuid4()),
            "exp": now + timedelta(minutes=15),
            "iat": now,
            "type": "access",
        }

        # Try to sign with public key (should fail)
        public_key = settings.get_jwt_public_key()

        with pytest.raises(Exception):  # Will raise cryptography error
            jwt.encode(claims, public_key, algorithm="RS256")


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_token_iat_is_current_time(self):
        """Test issued at timestamp is close to current time."""
        user_id = uuid4()
        before_generation = datetime.now(timezone.utc)

        token = generate_access_token(user_id)

        after_generation = datetime.now(timezone.utc)
        payload = decode_token(token)

        iat = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)

        # IAT should be between before and after (within 1 second tolerance)
        assert before_generation - timedelta(seconds=1) <= iat <= after_generation + timedelta(
            seconds=1
        )

    def test_multiple_tokens_same_user(self):
        """Test generating multiple tokens for same user."""
        user_id = uuid4()

        tokens = [generate_access_token(user_id) for _ in range(5)]

        # All should be valid
        for token in tokens:
            payload = verify_token(token, token_type="access")
            assert payload["sub"] == str(user_id)

        # All should have unique JTIs
        jtis = [decode_token(token)["jti"] for token in tokens]
        assert len(set(jtis)) == 5

    def test_tokens_for_different_users(self):
        """Test generating tokens for different users."""
        user_ids = [uuid4() for _ in range(3)]
        tokens = [generate_access_token(uid) for uid in user_ids]

        # Each token should have correct user ID
        for token, user_id in zip(tokens, user_ids):
            payload = verify_token(token, token_type="access")
            assert payload["sub"] == str(user_id)
