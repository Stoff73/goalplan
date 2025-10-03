"""
JWT token generation and verification using RS256 asymmetric signing.

This module provides secure JWT token management using RSA-2048 asymmetric
key pairs. Access tokens expire in 15 minutes, refresh tokens in 7 days.

Security:
- RS256 algorithm (asymmetric signing)
- Private key for signing, public key for verification
- Unique token IDs (jti) for revocation support
- Cryptographically secure token generation
- Expiration validation
- Signature verification

Token Claims:
- sub: User ID (UUID as string)
- jti: Token ID (UUID for revocation)
- exp: Expiration timestamp
- iat: Issued at timestamp
- type: "access" or "refresh"
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, Literal, Optional
from uuid import UUID, uuid4

from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError, JWTClaimsError

from config import settings


def generate_access_token(user_id: UUID) -> str:
    """
    Generate a JWT access token for authentication.

    Access tokens are short-lived (15 minutes) and used for API requests.

    Args:
        user_id: The user's UUID

    Returns:
        str: Encoded JWT access token

    Raises:
        ValueError: If user_id is invalid
        RuntimeError: If key loading or signing fails

    Example:
        >>> from uuid import uuid4
        >>> user_id = uuid4()
        >>> token = generate_access_token(user_id)
        >>> print(token)
        eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
    """
    if not isinstance(user_id, UUID):
        raise ValueError("user_id must be a UUID")

    return _generate_token(
        user_id=user_id,
        token_type="access",
        expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def generate_refresh_token(user_id: UUID) -> str:
    """
    Generate a JWT refresh token for obtaining new access tokens.

    Refresh tokens are long-lived (7 days) and used to obtain new access tokens
    without re-authentication.

    Args:
        user_id: The user's UUID

    Returns:
        str: Encoded JWT refresh token

    Raises:
        ValueError: If user_id is invalid
        RuntimeError: If key loading or signing fails

    Example:
        >>> from uuid import uuid4
        >>> user_id = uuid4()
        >>> token = generate_refresh_token(user_id)
    """
    if not isinstance(user_id, UUID):
        raise ValueError("user_id must be a UUID")

    return _generate_token(
        user_id=user_id,
        token_type="refresh",
        expires_delta=timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
    )


def verify_token(token: str, token_type: Optional[Literal["access", "refresh"]] = None) -> Dict:
    """
    Verify and decode a JWT token.

    Verifies signature, expiration, and optionally validates token type.

    Args:
        token: The JWT token to verify
        token_type: Optional token type to validate ("access" or "refresh")

    Returns:
        dict: Decoded token payload with claims

    Raises:
        ValueError: If token is invalid, expired, or wrong type
        RuntimeError: If public key loading fails

    Example:
        >>> token = generate_access_token(user_id)
        >>> payload = verify_token(token, token_type="access")
        >>> print(payload["sub"])  # User ID
    """
    if not token:
        raise ValueError("Token cannot be empty")

    try:
        # Load public key for verification
        public_key = settings.get_jwt_public_key()

        # Decode and verify token
        payload = jwt.decode(
            token,
            public_key,
            algorithms=[settings.JWT_ALGORITHM],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_iat": True,
            },
        )

        # Validate token type if specified
        if token_type is not None:
            token_type_claim = payload.get("type")
            if token_type_claim != token_type:
                raise ValueError(
                    f"Invalid token type. Expected '{token_type}', got '{token_type_claim}'"
                )

        return payload

    except ValueError:
        # Re-raise ValueError as is (includes token type validation errors)
        raise

    except ExpiredSignatureError:
        raise ValueError("Token has expired")

    except JWTClaimsError as e:
        raise ValueError(f"Invalid token claims: {str(e)}")

    except JWTError as e:
        raise ValueError(f"Invalid token: {str(e)}")

    except Exception as e:
        raise RuntimeError(f"Token verification failed: {str(e)}")


def decode_token(token: str) -> Dict:
    """
    Decode a JWT token without verification.

    WARNING: This does not verify the signature. Use verify_token() for
    secure token validation. This is useful for inspecting expired tokens
    or debugging.

    Args:
        token: The JWT token to decode

    Returns:
        dict: Decoded token payload (unverified)

    Raises:
        ValueError: If token is malformed

    Example:
        >>> token = generate_access_token(user_id)
        >>> payload = decode_token(token)
        >>> print(payload["jti"])  # Token ID
    """
    if not token:
        raise ValueError("Token cannot be empty")

    try:
        # Decode without verification - need to provide a key but verification is disabled
        # Using empty string as key since we're not verifying
        payload = jwt.decode(
            token,
            key="",  # Key not used when verify_signature=False
            options={
                "verify_signature": False,
                "verify_exp": False,
                "verify_iat": False,
                "verify_aud": False,
            },
        )
        return payload

    except JWTError as e:
        raise ValueError(f"Malformed token: {str(e)}")


def get_token_jti(token: str) -> str:
    """
    Extract the JWT ID (jti) from a token without verification.

    Useful for token revocation systems.

    Args:
        token: The JWT token

    Returns:
        str: The token's jti claim

    Raises:
        ValueError: If token is malformed or missing jti

    Example:
        >>> token = generate_access_token(user_id)
        >>> jti = get_token_jti(token)
        >>> # Store jti in revocation list
    """
    payload = decode_token(token)
    jti = payload.get("jti")

    if not jti:
        raise ValueError("Token missing jti claim")

    return jti


def _generate_token(
    user_id: UUID, token_type: Literal["access", "refresh"], expires_delta: timedelta
) -> str:
    """
    Internal function to generate JWT tokens.

    Args:
        user_id: The user's UUID
        token_type: Type of token ("access" or "refresh")
        expires_delta: Time until expiration

    Returns:
        str: Encoded JWT token

    Raises:
        RuntimeError: If private key loading or signing fails
    """
    now = datetime.now(timezone.utc)
    expires_at = now + expires_delta

    # Build token claims
    claims = {
        "sub": str(user_id),  # Subject (user ID)
        "jti": str(uuid4()),  # JWT ID (unique token identifier)
        "exp": expires_at,  # Expiration time
        "iat": now,  # Issued at time
        "type": token_type,  # Token type (access or refresh)
    }

    try:
        # Load private key for signing
        private_key = settings.get_jwt_private_key()

        # Encode and sign token
        token = jwt.encode(claims, private_key, algorithm=settings.JWT_ALGORITHM)

        return token

    except Exception as e:
        raise RuntimeError(f"Failed to generate token: {str(e)}")
