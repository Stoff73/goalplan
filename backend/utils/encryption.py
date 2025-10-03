"""
Encryption utilities for sensitive data using Fernet symmetric encryption.

This module provides encryption/decryption for sensitive PII fields like
account numbers, ensuring data protection at rest.

Security:
- Uses Fernet (AES-128 in CBC mode with HMAC for authentication)
- Keys stored in environment variables
- Automatic key generation for development
- Constant-time decryption to prevent timing attacks

Performance:
- Symmetric encryption is fast (<1ms per operation)
- Keys are cached in memory
- Suitable for encrypting individual fields
"""

import os
import base64
from typing import Optional
from cryptography.fernet import Fernet, InvalidToken


# Global Fernet instance (initialized once)
_fernet: Optional[Fernet] = None


def _get_fernet() -> Fernet:
    """
    Get or initialize the Fernet encryption instance.

    Returns:
        Fernet: Initialized Fernet instance

    Raises:
        ValueError: If ENCRYPTION_KEY is not set and not in testing mode
    """
    global _fernet

    if _fernet is not None:
        return _fernet

    # Get encryption key from environment
    encryption_key = os.getenv('ENCRYPTION_KEY')

    # In testing mode, generate a temporary key
    if not encryption_key:
        if os.getenv('TESTING') == 'true':
            encryption_key = Fernet.generate_key().decode()
        else:
            raise ValueError(
                "ENCRYPTION_KEY environment variable not set. "
                "Generate one using: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
            )

    # Ensure key is bytes
    if isinstance(encryption_key, str):
        encryption_key = encryption_key.encode()

    _fernet = Fernet(encryption_key)
    return _fernet


def encrypt_value(value: str) -> str:
    """
    Encrypt a string value using Fernet symmetric encryption.

    Args:
        value: Plain text value to encrypt

    Returns:
        str: Base64-encoded encrypted value

    Raises:
        TypeError: If value is not a string
        ValueError: If value is empty

    Example:
        >>> encrypted = encrypt_value("1234567890")
        >>> print(encrypted)
        gAAAAABh... (base64-encoded ciphertext)

    Security Notes:
        - Each encryption produces different output (includes timestamp)
        - Safe to store encrypted value in database
        - Includes authentication to prevent tampering
    """
    if not isinstance(value, str):
        raise TypeError("Value must be a string")

    if not value:
        raise ValueError("Value cannot be empty")

    fernet = _get_fernet()

    # Encrypt the value (returns bytes)
    encrypted_bytes = fernet.encrypt(value.encode())

    # Return as string for database storage
    return encrypted_bytes.decode()


def decrypt_value(encrypted_value: str) -> str:
    """
    Decrypt a Fernet-encrypted value.

    Args:
        encrypted_value: Base64-encoded encrypted value

    Returns:
        str: Decrypted plain text value

    Raises:
        TypeError: If encrypted_value is not a string
        ValueError: If encrypted_value is empty or invalid

    Example:
        >>> decrypted = decrypt_value(encrypted)
        >>> print(decrypted)
        1234567890

    Security Notes:
        - Verifies authentication tag before decrypting
        - Prevents tampering with encrypted data
        - Raises exception if data has been modified
    """
    if not isinstance(encrypted_value, str):
        raise TypeError("Encrypted value must be a string")

    if not encrypted_value:
        raise ValueError("Encrypted value cannot be empty")

    fernet = _get_fernet()

    try:
        # Decrypt the value (returns bytes)
        decrypted_bytes = fernet.decrypt(encrypted_value.encode())

        # Return as string
        return decrypted_bytes.decode()

    except InvalidToken:
        raise ValueError("Invalid encrypted value - data may be corrupted or tampered with")

    except Exception as e:
        raise ValueError(f"Decryption failed: {str(e)}")


def encrypt_account_number(account_number: str) -> str:
    """
    Encrypt a bank account number.

    Convenience wrapper around encrypt_value for account numbers.

    Args:
        account_number: Plain text account number

    Returns:
        str: Encrypted account number (base64-encoded)

    Example:
        >>> encrypted = encrypt_account_number("GB29NWBK60161331926819")
        >>> # Store encrypted value in database
    """
    return encrypt_value(account_number)


def decrypt_account_number(encrypted_account_number: str) -> str:
    """
    Decrypt a bank account number.

    Convenience wrapper around decrypt_value for account numbers.

    Args:
        encrypted_account_number: Encrypted account number

    Returns:
        str: Plain text account number

    Example:
        >>> decrypted = decrypt_account_number(encrypted)
        >>> print(decrypted)
        GB29NWBK60161331926819
    """
    return decrypt_value(encrypted_account_number)


def generate_encryption_key() -> str:
    """
    Generate a new Fernet encryption key.

    Returns:
        str: Base64-encoded encryption key

    Example:
        >>> key = generate_encryption_key()
        >>> print(f"Export this to your environment: ENCRYPTION_KEY={key}")

    Usage:
        1. Generate key: python -c 'from utils.encryption import generate_encryption_key; print(generate_encryption_key())'
        2. Add to .env: ENCRYPTION_KEY=<generated_key>
        3. Never commit the key to version control
    """
    return Fernet.generate_key().decode()
