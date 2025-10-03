"""
Tests for TOTP service.

Tests cover:
- Secret generation
- TOTP verification
- Time window tolerance
- Backup code generation
- Backup code validation
- QR code generation
"""

import pytest
import time
import pyotp

from services.totp import TOTPService


class TestTOTPService:
    """Test suite for TOTP service."""

    def test_generate_secret(self):
        """Test secret generation produces valid base32 string."""
        secret = TOTPService.generate_secret()

        # Check length (32 bytes base32 encoded = ~52 chars)
        assert len(secret) >= 26
        assert len(secret) <= 52

        # Check it's valid base32 (alphanumeric, uppercase)
        assert secret.isalnum()
        assert secret.isupper()

    def test_generate_secret_uniqueness(self):
        """Test that generated secrets are unique."""
        secret1 = TOTPService.generate_secret()
        secret2 = TOTPService.generate_secret()

        assert secret1 != secret2

    def test_verify_totp_valid_code(self):
        """Test TOTP verification with valid code."""
        secret = TOTPService.generate_secret()
        totp = TOTPService.generate_totp(secret)

        # Generate current code
        code = totp.now()

        # Verify it
        assert TOTPService.verify_totp(secret, code) is True

    def test_verify_totp_invalid_code(self):
        """Test TOTP verification with invalid code."""
        secret = TOTPService.generate_secret()

        # Use wrong code
        assert TOTPService.verify_totp(secret, "000000") is False

    def test_verify_totp_wrong_length(self):
        """Test TOTP verification rejects codes with wrong length."""
        secret = TOTPService.generate_secret()

        # Test various invalid lengths
        assert TOTPService.verify_totp(secret, "123") is False
        assert TOTPService.verify_totp(secret, "1234567") is False
        assert TOTPService.verify_totp(secret, "") is False

    def test_verify_totp_time_window_tolerance(self):
        """Test TOTP verification accepts codes from adjacent time windows."""
        import datetime
        secret = TOTPService.generate_secret()
        totp = TOTPService.generate_totp(secret)

        # Get code from previous time window (30 seconds ago)
        past_time = datetime.datetime.now() - datetime.timedelta(seconds=30)
        past_code = totp.at(past_time)

        # Should still be valid due to time window tolerance
        assert TOTPService.verify_totp(secret, past_code) is True

    def test_verify_totp_future_window(self):
        """Test TOTP verification accepts codes from next time window."""
        import datetime
        secret = TOTPService.generate_secret()
        totp = TOTPService.generate_totp(secret)

        # Get code from next time window (30 seconds ahead)
        future_time = datetime.datetime.now() + datetime.timedelta(seconds=30)
        future_code = totp.at(future_time)

        # Should still be valid due to time window tolerance
        assert TOTPService.verify_totp(secret, future_code) is True

    def test_verify_totp_too_old(self):
        """Test TOTP verification rejects very old codes."""
        import datetime
        secret = TOTPService.generate_secret()
        totp = TOTPService.generate_totp(secret)

        # Get code from 2 time windows ago (60 seconds ago)
        old_time = datetime.datetime.now() - datetime.timedelta(seconds=60)
        old_code = totp.at(old_time)

        # Should be invalid (outside tolerance window)
        assert TOTPService.verify_totp(secret, old_code) is False

    def test_generate_backup_codes(self):
        """Test backup code generation."""
        codes = TOTPService.generate_backup_codes()

        # Should generate 10 codes
        assert len(codes) == 10

        # Each code should be 8 digits
        for code in codes:
            assert len(code) == 8
            assert code.isdigit()

    def test_generate_backup_codes_uniqueness(self):
        """Test that backup codes are unique."""
        codes = TOTPService.generate_backup_codes()

        # All codes should be unique
        assert len(codes) == len(set(codes))

    def test_hash_backup_code(self):
        """Test backup code hashing."""
        code = "12345678"
        hashed = TOTPService.hash_backup_code(code)

        # Hash should be different from original
        assert hashed != code

        # Hash should be reasonably long (Argon2 hashes are >50 chars)
        assert len(hashed) > 50

    def test_verify_backup_code_valid(self):
        """Test backup code verification with correct code."""
        code = "12345678"
        hashed = TOTPService.hash_backup_code(code)

        # Should verify successfully
        assert TOTPService.verify_backup_code(code, hashed) is True

    def test_verify_backup_code_invalid(self):
        """Test backup code verification with wrong code."""
        code = "12345678"
        hashed = TOTPService.hash_backup_code(code)

        # Should fail verification
        assert TOTPService.verify_backup_code("87654321", hashed) is False

    def test_verify_backup_code_wrong_length(self):
        """Test backup code verification rejects wrong length codes."""
        code = "12345678"
        hashed = TOTPService.hash_backup_code(code)

        # Should reject codes with wrong length
        assert TOTPService.verify_backup_code("123", hashed) is False
        assert TOTPService.verify_backup_code("123456789", hashed) is False

    def test_validate_backup_codes_valid(self):
        """Test validating a backup code against stored codes."""
        codes = TOTPService.generate_backup_codes()
        hashed_codes = [TOTPService.hash_backup_code(code) for code in codes]

        # Validate first code
        is_valid, matched_hash = TOTPService.validate_backup_codes(codes[0], hashed_codes)

        assert is_valid is True
        assert matched_hash is not None
        assert matched_hash in hashed_codes

    def test_validate_backup_codes_invalid(self):
        """Test validating invalid backup code."""
        codes = TOTPService.generate_backup_codes()
        hashed_codes = [TOTPService.hash_backup_code(code) for code in codes]

        # Try invalid code
        is_valid, matched_hash = TOTPService.validate_backup_codes("00000000", hashed_codes)

        assert is_valid is False
        assert matched_hash is None

    def test_is_backup_code_format_valid(self):
        """Test backup code format validation."""
        # Valid format (8 digits)
        assert TOTPService.is_backup_code_format("12345678") is True

    def test_is_backup_code_format_invalid(self):
        """Test backup code format validation rejects invalid formats."""
        # Invalid formats
        assert TOTPService.is_backup_code_format("123456") is False  # Too short (TOTP)
        assert TOTPService.is_backup_code_format("123456789") is False  # Too long
        assert TOTPService.is_backup_code_format("1234abcd") is False  # Non-digits
        assert TOTPService.is_backup_code_format("") is False  # Empty

    def test_get_provisioning_uri(self):
        """Test provisioning URI generation."""
        secret = "JBSWY3DPEHPK3PXP"
        email = "user@example.com"

        uri = TOTPService.get_provisioning_uri(secret, email)

        # Check URI format
        assert uri.startswith("otpauth://totp/")
        assert "GoalPlan" in uri
        # Email may be URL-encoded
        assert "user" in uri and "example.com" in uri
        assert f"secret={secret}" in uri

    def test_generate_qr_code(self):
        """Test QR code generation."""
        secret = "JBSWY3DPEHPK3PXP"
        email = "user@example.com"

        qr_code = TOTPService.generate_qr_code(secret, email)

        # Check it's a base64 data URI
        assert qr_code.startswith("data:image/png;base64,")

        # Check it contains base64 data
        assert len(qr_code) > 100  # QR codes are large

    def test_totp_configuration(self):
        """Test TOTP configuration matches specifications."""
        assert TOTPService.TOTP_ISSUER == "GoalPlan"
        assert TOTPService.TOTP_DIGITS == 6
        assert TOTPService.TOTP_INTERVAL == 30
        assert TOTPService.TOTP_ALGORITHM == "sha1"
        assert TOTPService.TOTP_VALID_WINDOW == 1

    def test_backup_code_configuration(self):
        """Test backup code configuration."""
        assert TOTPService.BACKUP_CODE_COUNT == 10
        assert TOTPService.BACKUP_CODE_LENGTH == 8

    def test_generate_totp_instance(self):
        """Test TOTP instance generation."""
        secret = "JBSWY3DPEHPK3PXP"
        totp = TOTPService.generate_totp(secret)

        # Check TOTP instance configuration
        assert isinstance(totp, pyotp.TOTP)
        assert totp.digits == 6
        assert totp.interval == 30

    def test_verify_totp_with_none(self):
        """Test TOTP verification handles None gracefully."""
        secret = TOTPService.generate_secret()

        assert TOTPService.verify_totp(secret, None) is False
