"""
Tests for encryption utilities.

This module tests:
- Value encryption/decryption
- Account number encryption/decryption
- Error handling
- Key generation
"""

import pytest
import os
from cryptography.fernet import Fernet

from utils.encryption import (
    encrypt_value,
    decrypt_value,
    encrypt_account_number,
    decrypt_account_number,
    generate_encryption_key
)


class TestEncryption:
    """Test encryption utilities."""

    def test_encrypt_decrypt_value(self):
        """Test basic encryption and decryption."""
        original_value = "sensitive_data_12345"

        # Encrypt
        encrypted = encrypt_value(original_value)

        # Verify encrypted value is different
        assert encrypted != original_value
        assert len(encrypted) > len(original_value)

        # Decrypt
        decrypted = decrypt_value(encrypted)

        # Verify decryption returns original value
        assert decrypted == original_value

    def test_encrypt_decrypt_account_number(self):
        """Test account number encryption/decryption."""
        account_number = "GB29NWBK60161331926819"

        # Encrypt
        encrypted = encrypt_account_number(account_number)

        # Verify encrypted value is different
        assert encrypted != account_number

        # Decrypt
        decrypted = decrypt_account_number(encrypted)

        # Verify decryption returns original value
        assert decrypted == account_number

    def test_encrypt_different_values_produce_different_ciphertexts(self):
        """Test that different values produce different ciphertexts."""
        value1 = "account123"
        value2 = "account456"

        encrypted1 = encrypt_value(value1)
        encrypted2 = encrypt_value(value2)

        assert encrypted1 != encrypted2

    def test_encrypt_same_value_twice_produces_different_ciphertexts(self):
        """Test that same value encrypted twice produces different ciphertexts (due to timestamp)."""
        value = "test_value"

        encrypted1 = encrypt_value(value)
        encrypted2 = encrypt_value(value)

        # Different ciphertexts (Fernet includes timestamp)
        assert encrypted1 != encrypted2

        # But both decrypt to same value
        assert decrypt_value(encrypted1) == value
        assert decrypt_value(encrypted2) == value

    def test_encrypt_empty_string_raises_error(self):
        """Test that encrypting empty string raises ValueError."""
        with pytest.raises(ValueError, match="Value cannot be empty"):
            encrypt_value("")

    def test_encrypt_non_string_raises_error(self):
        """Test that encrypting non-string raises TypeError."""
        with pytest.raises(TypeError, match="Value must be a string"):
            encrypt_value(12345)

        with pytest.raises(TypeError, match="Value must be a string"):
            encrypt_value(None)

    def test_decrypt_empty_string_raises_error(self):
        """Test that decrypting empty string raises ValueError."""
        with pytest.raises(ValueError, match="Encrypted value cannot be empty"):
            decrypt_value("")

    def test_decrypt_non_string_raises_error(self):
        """Test that decrypting non-string raises TypeError."""
        with pytest.raises(TypeError, match="Encrypted value must be a string"):
            decrypt_value(12345)

        with pytest.raises(TypeError, match="Encrypted value must be a string"):
            decrypt_value(None)

    def test_decrypt_invalid_value_raises_error(self):
        """Test that decrypting invalid value raises ValueError."""
        with pytest.raises(ValueError, match="Invalid encrypted value"):
            decrypt_value("invalid_encrypted_value")

    def test_decrypt_tampered_value_raises_error(self):
        """Test that decrypting tampered value raises ValueError."""
        original_value = "test_value"
        encrypted = encrypt_value(original_value)

        # Tamper with encrypted value (change last character)
        tampered = encrypted[:-1] + "X"

        with pytest.raises(ValueError, match="Invalid encrypted value"):
            decrypt_value(tampered)

    def test_encrypt_unicode_characters(self):
        """Test encryption with unicode characters."""
        unicode_value = "测试数据 £€¥"

        encrypted = encrypt_value(unicode_value)
        decrypted = decrypt_value(encrypted)

        assert decrypted == unicode_value

    def test_encrypt_special_characters(self):
        """Test encryption with special characters."""
        special_value = "!@#$%^&*()_+-=[]{}|;:',.<>?/~`"

        encrypted = encrypt_value(special_value)
        decrypted = decrypt_value(encrypted)

        assert decrypted == special_value

    def test_encrypt_long_value(self):
        """Test encryption with long value."""
        long_value = "A" * 10000  # 10,000 characters

        encrypted = encrypt_value(long_value)
        decrypted = decrypt_value(encrypted)

        assert decrypted == long_value

    def test_generate_encryption_key(self):
        """Test encryption key generation."""
        key1 = generate_encryption_key()
        key2 = generate_encryption_key()

        # Keys should be different
        assert key1 != key2

        # Keys should be valid base64-encoded strings
        assert isinstance(key1, str)
        assert isinstance(key2, str)
        assert len(key1) > 0
        assert len(key2) > 0

        # Keys should be usable with Fernet
        fernet1 = Fernet(key1.encode())
        fernet2 = Fernet(key2.encode())

        # Test encryption with generated keys
        test_value = "test"
        encrypted1 = fernet1.encrypt(test_value.encode()).decode()
        encrypted2 = fernet2.encrypt(test_value.encode()).decode()

        # Verify decryption works
        assert fernet1.decrypt(encrypted1.encode()).decode() == test_value
        assert fernet2.decrypt(encrypted2.encode()).decode() == test_value

        # Verify keys are independent (can't decrypt with wrong key)
        with pytest.raises(Exception):
            fernet1.decrypt(encrypted2.encode())

    def test_account_number_patterns(self):
        """Test encryption with various account number patterns."""
        account_numbers = [
            "12345678",  # Simple numeric
            "GB29NWBK60161331926819",  # IBAN
            "1234-5678-9012-3456",  # Formatted
            "****5678",  # Masked
            "ZA123456789012",  # SA format
        ]

        for account_number in account_numbers:
            encrypted = encrypt_account_number(account_number)
            decrypted = decrypt_account_number(encrypted)
            assert decrypted == account_number

    def test_encryption_with_missing_key_in_testing_mode(self):
        """Test that encryption works in testing mode even without ENCRYPTION_KEY set."""
        # This test verifies that _get_fernet() generates a key when TESTING=true
        # The conftest.py should set TESTING=true for all tests
        value = "test_value"

        # Should work without error
        encrypted = encrypt_value(value)
        decrypted = decrypt_value(encrypted)

        assert decrypted == value
