"""
TOTP (Time-based One-Time Password) service for two-factor authentication.

This module implements TOTP functionality using pyotp for secure 2FA:
- Secret generation (32-byte base32)
- QR code generation for authenticator apps
- TOTP code verification with time window tolerance
- Backup code generation and validation

Specification:
- Algorithm: SHA1 (Google Authenticator standard)
- Time window: 30 seconds
- Code length: 6 digits
- Time tolerance: ±1 window (90 seconds total: previous, current, next)
"""

import base64
import secrets
import io
from typing import List, Optional, Tuple

import pyotp
import qrcode
from qrcode.image.pil import PilImage


class TOTPService:
    """
    Service for TOTP operations.

    Handles all TOTP-related operations including secret generation,
    QR code generation, code verification, and backup codes.
    """

    # TOTP Configuration
    TOTP_ISSUER = "GoalPlan"
    TOTP_DIGITS = 6
    TOTP_INTERVAL = 30  # seconds
    TOTP_ALGORITHM = "sha1"  # Google Authenticator standard

    # Time window tolerance: ±1 window = 90 seconds total
    # Accepts codes from: previous (t-30s), current (t), next (t+30s)
    TOTP_VALID_WINDOW = 1

    # Backup codes configuration
    BACKUP_CODE_COUNT = 10
    BACKUP_CODE_LENGTH = 8  # 8 digits

    @staticmethod
    def generate_secret() -> str:
        """
        Generate a random TOTP secret.

        Returns:
            str: Base32-encoded secret (32 bytes)

        Example:
            >>> secret = TOTPService.generate_secret()
            >>> len(secret)
            32
        """
        # Generate 32 random bytes and encode as base32
        random_bytes = secrets.token_bytes(32)
        secret = base64.b32encode(random_bytes).decode('utf-8')

        # Remove padding for cleaner secret
        return secret.rstrip('=')

    @staticmethod
    def generate_totp(secret: str) -> pyotp.TOTP:
        """
        Create TOTP instance from secret.

        Args:
            secret: Base32-encoded TOTP secret

        Returns:
            pyotp.TOTP: TOTP instance for generating/verifying codes
        """
        import hashlib
        return pyotp.TOTP(
            secret,
            digits=TOTPService.TOTP_DIGITS,
            interval=TOTPService.TOTP_INTERVAL,
            digest=hashlib.sha1  # Pass the hash function, not string
        )

    @staticmethod
    def get_provisioning_uri(secret: str, email: str) -> str:
        """
        Generate provisioning URI for QR code.

        The URI format is: otpauth://totp/ISSUER:EMAIL?secret=SECRET&issuer=ISSUER

        Args:
            secret: Base32-encoded TOTP secret
            email: User email address

        Returns:
            str: Provisioning URI for authenticator apps

        Example:
            >>> uri = TOTPService.get_provisioning_uri("SECRET123", "user@example.com")
            >>> "otpauth://totp/GoalPlan:user@example.com" in uri
            True
        """
        totp = TOTPService.generate_totp(secret)
        return totp.provisioning_uri(
            name=email,
            issuer_name=TOTPService.TOTP_ISSUER
        )

    @staticmethod
    def generate_qr_code(secret: str, email: str) -> str:
        """
        Generate QR code image for TOTP setup.

        Args:
            secret: Base32-encoded TOTP secret
            email: User email address

        Returns:
            str: Base64-encoded PNG image of QR code

        Example:
            >>> qr_base64 = TOTPService.generate_qr_code("SECRET123", "user@example.com")
            >>> qr_base64.startswith("data:image/png;base64,")
            True
        """
        # Get provisioning URI
        uri = TOTPService.get_provisioning_uri(secret, email)

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(uri)
        qr.make(fit=True)

        # Create image
        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

        # Return as data URI
        return f"data:image/png;base64,{img_base64}"

    @staticmethod
    def verify_totp(secret: str, code: str) -> bool:
        """
        Verify TOTP code with time window tolerance.

        Accepts codes from previous, current, and next time windows
        (90 seconds total tolerance).

        Args:
            secret: Base32-encoded TOTP secret
            code: 6-digit TOTP code from user

        Returns:
            bool: True if code is valid, False otherwise

        Example:
            >>> secret = TOTPService.generate_secret()
            >>> totp = TOTPService.generate_totp(secret)
            >>> code = totp.now()
            >>> TOTPService.verify_totp(secret, code)
            True
        """
        if not code or len(code) != TOTPService.TOTP_DIGITS:
            return False

        try:
            totp = TOTPService.generate_totp(secret)
            # Verify with time window tolerance (±1 window = 90 seconds)
            return totp.verify(code, valid_window=TOTPService.TOTP_VALID_WINDOW)
        except Exception:
            return False

    @staticmethod
    def generate_backup_codes() -> List[str]:
        """
        Generate backup codes for account recovery.

        Generates 10 random 8-digit backup codes for use when
        TOTP is unavailable.

        Returns:
            List[str]: List of 10 backup codes (8 digits each)

        Example:
            >>> codes = TOTPService.generate_backup_codes()
            >>> len(codes)
            10
            >>> all(len(code) == 8 and code.isdigit() for code in codes)
            True
        """
        backup_codes = []
        for _ in range(TOTPService.BACKUP_CODE_COUNT):
            # Generate random 8-digit code
            code = ''.join(str(secrets.randbelow(10)) for _ in range(TOTPService.BACKUP_CODE_LENGTH))
            backup_codes.append(code)

        return backup_codes

    @staticmethod
    def hash_backup_code(code: str) -> str:
        """
        Hash a backup code for secure storage.

        Uses Argon2 for hashing (consistent with password hashing).

        Args:
            code: Backup code to hash

        Returns:
            str: Hashed backup code

        Example:
            >>> hashed = TOTPService.hash_backup_code("12345678")
            >>> len(hashed) > 50
            True
        """
        from argon2 import PasswordHasher

        ph = PasswordHasher()
        return ph.hash(code)

    @staticmethod
    def verify_backup_code(code: str, hashed_code: str) -> bool:
        """
        Verify a backup code against its hash.

        Args:
            code: Backup code from user
            hashed_code: Stored hashed backup code

        Returns:
            bool: True if code matches hash, False otherwise

        Example:
            >>> code = "12345678"
            >>> hashed = TOTPService.hash_backup_code(code)
            >>> TOTPService.verify_backup_code(code, hashed)
            True
            >>> TOTPService.verify_backup_code("87654321", hashed)
            False
        """
        from argon2 import PasswordHasher
        from argon2.exceptions import VerifyMismatchError, InvalidHashError

        if not code or len(code) != TOTPService.BACKUP_CODE_LENGTH:
            return False

        try:
            ph = PasswordHasher()
            ph.verify(hashed_code, code)
            return True
        except (VerifyMismatchError, InvalidHashError):
            return False

    @staticmethod
    def validate_backup_codes(
        code: str,
        stored_codes: List[str]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a backup code and return the matching hashed code.

        Args:
            code: Backup code from user
            stored_codes: List of hashed backup codes

        Returns:
            Tuple[bool, Optional[str]]: (is_valid, matching_hash)
                - is_valid: True if code matches any stored code
                - matching_hash: The hashed code that matched (for removal)

        Example:
            >>> codes = TOTPService.generate_backup_codes()
            >>> hashed_codes = [TOTPService.hash_backup_code(c) for c in codes]
            >>> is_valid, matched = TOTPService.validate_backup_codes(codes[0], hashed_codes)
            >>> is_valid
            True
            >>> matched is not None
            True
        """
        for hashed_code in stored_codes:
            if TOTPService.verify_backup_code(code, hashed_code):
                return True, hashed_code

        return False, None

    @staticmethod
    def is_backup_code_format(code: str) -> bool:
        """
        Check if a code looks like a backup code (8 digits).

        Args:
            code: Code to check

        Returns:
            bool: True if code matches backup code format

        Example:
            >>> TOTPService.is_backup_code_format("12345678")
            True
            >>> TOTPService.is_backup_code_format("123456")
            False
        """
        return bool(code and len(code) == TOTPService.BACKUP_CODE_LENGTH and code.isdigit())
