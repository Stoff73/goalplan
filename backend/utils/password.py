"""
Password hashing and verification utilities using Argon2.

This module provides secure password hashing using Argon2id, which is
recommended for password hashing due to its resistance to side-channel
attacks and GPU cracking attempts.

Security:
- Uses Argon2id variant (hybrid of Argon2i and Argon2d)
- Configurable time cost, memory cost, and parallelism
- Automatic salt generation
- Constant-time password verification

Performance:
- Target: <500ms per hash operation
- Parameters tuned for security/performance balance
"""

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError


# Initialize Argon2 password hasher with recommended parameters
# These parameters are tuned for a balance between security and performance
_password_hasher = PasswordHasher(
    time_cost=2,        # Number of iterations (2 is OWASP recommended minimum)
    memory_cost=65536,  # Memory cost in KiB (64 MB) - resistant to GPU attacks
    parallelism=4,      # Number of parallel threads
    hash_len=32,        # Length of hash in bytes (32 bytes = 256 bits)
    salt_len=16,        # Length of salt in bytes (16 bytes = 128 bits)
    encoding='utf-8',   # Encoding for password string
)


def hash_password(password: str) -> str:
    """
    Hash a password using Argon2id.

    Args:
        password: The plain-text password to hash

    Returns:
        str: The hashed password with embedded salt and parameters

    Raises:
        TypeError: If password is not a string
        ValueError: If password is empty

    Example:
        >>> hashed = hash_password("my_secure_password_123")
        >>> print(hashed)
        $argon2id$v=19$m=65536,t=2,p=4$...

    Security Notes:
        - Never log or store the plain password
        - Hash contains: algorithm, version, parameters, salt, and hash
        - Each hash is unique due to random salt generation
        - Safe to store hash in database
    """
    if not isinstance(password, str):
        raise TypeError("Password must be a string")

    if not password:
        raise ValueError("Password cannot be empty")

    # Hash the password - this includes automatic salt generation
    hashed = _password_hasher.hash(password)

    return hashed


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a password against its hash.

    This function performs constant-time comparison to prevent timing attacks.

    Args:
        password: The plain-text password to verify
        password_hash: The hashed password to verify against

    Returns:
        bool: True if password matches, False otherwise

    Raises:
        TypeError: If password or password_hash is not a string
        ValueError: If password or password_hash is empty

    Example:
        >>> hashed = hash_password("my_password")
        >>> verify_password("my_password", hashed)
        True
        >>> verify_password("wrong_password", hashed)
        False

    Security Notes:
        - Uses constant-time comparison to prevent timing attacks
        - Returns False for any error (invalid hash, wrong password, etc.)
        - Never reveals why verification failed (security through obscurity)
    """
    if not isinstance(password, str):
        raise TypeError("Password must be a string")

    if not isinstance(password_hash, str):
        raise TypeError("Password hash must be a string")

    if not password:
        raise ValueError("Password cannot be empty")

    if not password_hash:
        raise ValueError("Password hash cannot be empty")

    try:
        # Verify the password - returns None on success, raises on failure
        _password_hasher.verify(password_hash, password)
        return True

    except VerifyMismatchError:
        # Password doesn't match - this is the expected error for wrong password
        return False

    except (VerificationError, InvalidHashError):
        # Hash is invalid or corrupted - treat as verification failure
        return False

    except Exception:
        # Any other unexpected error - fail closed (return False)
        return False


def needs_rehash(password_hash: str) -> bool:
    """
    Check if a password hash needs to be rehashed.

    This is useful when parameters change (e.g., increasing time_cost for
    better security). Allows gradual migration of existing password hashes.

    Args:
        password_hash: The password hash to check

    Returns:
        bool: True if hash needs rehashing with current parameters

    Example:
        >>> old_hash = hash_password("password")
        >>> # Later, after changing parameters...
        >>> if needs_rehash(old_hash):
        >>>     new_hash = hash_password(password)  # Rehash with new params

    Usage Pattern:
        On successful login:
        1. Verify password with verify_password()
        2. If verification succeeds, check needs_rehash()
        3. If rehash needed, hash password again and update database
    """
    if not password_hash:
        return True

    try:
        return _password_hasher.check_needs_rehash(password_hash)
    except Exception:
        # If check fails, assume rehash is needed
        return True
