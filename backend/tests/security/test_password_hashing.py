"""
Tests for password hashing utilities.

This module tests the Argon2-based password hashing functionality.

Test Coverage:
- Password hashing produces unique hashes (salt)
- Password verification with correct password
- Password verification with wrong password
- Hash irreversibility
- Performance requirements (<500ms)
- Edge cases (empty passwords, invalid inputs, etc.)
"""

import time
import pytest

from utils.password import hash_password, verify_password, needs_rehash


class TestPasswordHashing:
    """Tests for password hashing functionality."""

    def test_hash_password_produces_different_hashes(self):
        """Test that hashing the same password twice produces different hashes due to salt."""
        # Arrange
        password = "MySecurePassword123!"

        # Act
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Assert - Different hashes due to different salts
        assert hash1 != hash2
        assert isinstance(hash1, str)
        assert isinstance(hash2, str)
        assert hash1.startswith("$argon2")
        assert hash2.startswith("$argon2")

    def test_verify_password_with_correct_password_returns_true(self):
        """Test that password verification returns True for correct password."""
        # Arrange
        password = "CorrectPassword123!"
        password_hash = hash_password(password)

        # Act
        result = verify_password(password, password_hash)

        # Assert
        assert result is True

    def test_verify_password_with_wrong_password_returns_false(self):
        """Test that password verification returns False for wrong password."""
        # Arrange
        correct_password = "CorrectPassword123!"
        wrong_password = "WrongPassword456!"
        password_hash = hash_password(correct_password)

        # Act
        result = verify_password(wrong_password, password_hash)

        # Assert
        assert result is False

    def test_password_hash_is_not_reversible(self):
        """Test that password cannot be derived from hash."""
        # Arrange
        password = "SecretPassword789!"
        password_hash = hash_password(password)

        # Assert - Hash should not contain the original password
        assert password not in password_hash
        assert len(password_hash) > len(password)

        # Should be impossible to reverse engineer original password
        # (We can't programmatically test this, but we verify hash format)
        assert password_hash.startswith("$argon2id$")  # Argon2id variant

    def test_hash_password_performance_under_500ms(self):
        """Test that password hashing completes in under 500ms."""
        # Arrange
        password = "PerformanceTest123!"
        max_time_ms = 500

        # Act
        start_time = time.perf_counter()
        hash_password(password)
        end_time = time.perf_counter()

        # Calculate duration in milliseconds
        duration_ms = (end_time - start_time) * 1000

        # Assert - Should complete in under 500ms
        assert duration_ms < max_time_ms, f"Hashing took {duration_ms:.2f}ms (max: {max_time_ms}ms)"

    def test_verify_password_performance_under_500ms(self):
        """Test that password verification completes in under 500ms."""
        # Arrange
        password = "VerifyPerformanceTest123!"
        password_hash = hash_password(password)
        max_time_ms = 500

        # Act
        start_time = time.perf_counter()
        verify_password(password, password_hash)
        end_time = time.perf_counter()

        # Calculate duration in milliseconds
        duration_ms = (end_time - start_time) * 1000

        # Assert - Should complete in under 500ms
        assert duration_ms < max_time_ms, f"Verification took {duration_ms:.2f}ms (max: {max_time_ms}ms)"

    def test_hash_empty_password_raises_error(self):
        """Test that hashing empty password raises ValueError."""
        # Arrange
        empty_password = ""

        # Act & Assert
        with pytest.raises(ValueError, match="Password cannot be empty"):
            hash_password(empty_password)

    def test_hash_non_string_password_raises_error(self):
        """Test that hashing non-string password raises TypeError."""
        # Arrange
        invalid_password = 12345  # Not a string

        # Act & Assert
        with pytest.raises(TypeError, match="Password must be a string"):
            hash_password(invalid_password)  # type: ignore

    def test_verify_with_empty_password_raises_error(self):
        """Test that verifying empty password raises ValueError."""
        # Arrange
        password_hash = hash_password("ValidPassword123!")

        # Act & Assert
        with pytest.raises(ValueError, match="Password cannot be empty"):
            verify_password("", password_hash)

    def test_verify_with_empty_hash_raises_error(self):
        """Test that verifying with empty hash raises ValueError."""
        # Arrange
        password = "ValidPassword123!"

        # Act & Assert
        with pytest.raises(ValueError, match="Password hash cannot be empty"):
            verify_password(password, "")

    def test_verify_with_non_string_password_raises_error(self):
        """Test that verifying non-string password raises TypeError."""
        # Arrange
        password_hash = hash_password("ValidPassword123!")

        # Act & Assert
        with pytest.raises(TypeError, match="Password must be a string"):
            verify_password(12345, password_hash)  # type: ignore

    def test_verify_with_non_string_hash_raises_error(self):
        """Test that verifying with non-string hash raises TypeError."""
        # Act & Assert
        with pytest.raises(TypeError, match="Password hash must be a string"):
            verify_password("ValidPassword123!", 12345)  # type: ignore

    def test_verify_with_invalid_hash_format_returns_false(self):
        """Test that verification returns False for invalid hash format."""
        # Arrange
        password = "ValidPassword123!"
        invalid_hash = "not-a-valid-argon2-hash"

        # Act
        result = verify_password(password, invalid_hash)

        # Assert - Should return False, not raise exception
        assert result is False

    def test_verify_with_corrupted_hash_returns_false(self):
        """Test that verification returns False for corrupted hash."""
        # Arrange
        password = "ValidPassword123!"
        password_hash = hash_password(password)
        # Corrupt the hash by modifying some characters
        corrupted_hash = password_hash[:-10] + "corrupted!"

        # Act
        result = verify_password(password, corrupted_hash)

        # Assert - Should return False, not raise exception
        assert result is False

    def test_hash_contains_argon2_parameters(self):
        """Test that hash contains Argon2 algorithm identifier and parameters."""
        # Arrange
        password = "ParametersTest123!"

        # Act
        password_hash = hash_password(password)

        # Assert - Hash should contain Argon2id identifier and parameters
        assert password_hash.startswith("$argon2id$")
        assert "m=" in password_hash  # Memory cost parameter
        assert "t=" in password_hash  # Time cost parameter
        assert "p=" in password_hash  # Parallelism parameter

    def test_different_passwords_produce_different_hashes(self):
        """Test that different passwords produce different hashes."""
        # Arrange
        password1 = "FirstPassword123!"
        password2 = "SecondPassword456!"

        # Act
        hash1 = hash_password(password1)
        hash2 = hash_password(password2)

        # Assert
        assert hash1 != hash2

    def test_similar_passwords_produce_different_hashes(self):
        """Test that very similar passwords produce completely different hashes."""
        # Arrange - Only differ by one character
        password1 = "SimilarPassword123!"
        password2 = "SimilarPassword124!"

        # Act
        hash1 = hash_password(password1)
        hash2 = hash_password(password2)

        # Assert - Hashes should be completely different (avalanche effect)
        assert hash1 != hash2

    def test_case_sensitive_password_verification(self):
        """Test that password verification is case-sensitive."""
        # Arrange
        password = "CaseSensitive123!"
        password_hash = hash_password(password)

        # Act
        result_correct = verify_password("CaseSensitive123!", password_hash)
        result_wrong_case = verify_password("casesensitive123!", password_hash)

        # Assert
        assert result_correct is True
        assert result_wrong_case is False

    def test_unicode_password_support(self):
        """Test that Unicode characters in passwords are supported."""
        # Arrange
        unicode_password = "P@ssw0rd密码🔒!"

        # Act
        password_hash = hash_password(unicode_password)
        result = verify_password(unicode_password, password_hash)

        # Assert
        assert result is True

    def test_needs_rehash_for_current_hash(self):
        """Test needs_rehash returns False for hash with current parameters."""
        # Arrange
        password = "CurrentParams123!"
        password_hash = hash_password(password)

        # Act
        result = needs_rehash(password_hash)

        # Assert - Should not need rehash with current parameters
        assert result is False

    def test_needs_rehash_for_empty_hash(self):
        """Test needs_rehash returns True for empty hash."""
        # Act
        result = needs_rehash("")

        # Assert
        assert result is True

    def test_needs_rehash_for_invalid_hash(self):
        """Test needs_rehash returns True for invalid hash."""
        # Act
        result = needs_rehash("invalid-hash-format")

        # Assert
        assert result is True
