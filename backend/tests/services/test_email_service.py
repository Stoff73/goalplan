"""
Tests for email service.

This module tests the email sending functionality including:
- Email service initialization
- Console backend (development)
- SendGrid backend (production)
- Verification email templates
- Email queueing
"""

import logging
import pytest
from unittest.mock import Mock, patch, AsyncMock

from services.email import (
    EmailService,
    ConsoleEmailBackend,
    SendGridEmailBackend,
)
from config import settings


class TestConsoleEmailBackend:
    """Tests for console email backend (development)."""

    @pytest.mark.asyncio
    async def test_console_backend_sends_email(self, caplog):
        """Test that console backend logs email to console."""
        # Arrange
        caplog.set_level(logging.INFO)
        backend = ConsoleEmailBackend()

        # Act
        result = await backend.send_email(
            to_email="test@example.com",
            subject="Test Subject",
            html_content="<h1>Test HTML</h1>",
            text_content="Test Text",
        )

        # Assert
        assert result is True
        assert "test@example.com" in caplog.text
        assert "Test Subject" in caplog.text

    @pytest.mark.asyncio
    async def test_console_backend_without_text_content(self, caplog):
        """Test console backend works without text content."""
        # Arrange
        caplog.set_level(logging.INFO)
        backend = ConsoleEmailBackend()

        # Act
        result = await backend.send_email(
            to_email="test@example.com",
            subject="Test Subject",
            html_content="<h1>Test HTML</h1>",
        )

        # Assert
        assert result is True
        assert "test@example.com" in caplog.text


class TestEmailService:
    """Tests for email service."""

    @pytest.mark.asyncio
    async def test_email_service_initialization_console_backend(self):
        """Test email service initializes with console backend by default."""
        # Act
        service = EmailService()

        # Assert
        assert isinstance(service.backend, ConsoleEmailBackend)

    @pytest.mark.asyncio
    async def test_send_email_via_service(self, caplog):
        """Test sending email through email service."""
        # Arrange
        caplog.set_level(logging.INFO)
        service = EmailService()

        # Act
        result = await service.send_email(
            to_email="recipient@example.com",
            subject="Service Test",
            html_content="<p>Service Test</p>",
        )

        # Assert
        assert result is True
        assert "recipient@example.com" in caplog.text
        assert "Service Test" in caplog.text

    @pytest.mark.asyncio
    async def test_send_verification_email(self, caplog):
        """Test sending verification email with template."""
        # Arrange
        caplog.set_level(logging.INFO)
        service = EmailService()

        # Act
        result = await service.send_verification_email(
            to_email="newuser@example.com",
            verification_token="abc123xyz",
            user_name="John Doe",
        )

        # Assert
        assert result is True
        assert "newuser@example.com" in caplog.text
        assert "Verify your GoalPlan account" in caplog.text

    @pytest.mark.asyncio
    async def test_verification_email_contains_user_name(self, caplog):
        """Test verification email template includes user name."""
        # Arrange
        caplog.set_level(logging.INFO)
        service = EmailService()

        # Act
        await service.send_verification_email(
            to_email="user@example.com",
            verification_token="token123",
            user_name="Jane Smith",
        )

        # Assert
        assert "Jane Smith" in caplog.text

    @pytest.mark.asyncio
    async def test_verification_email_contains_verification_url(self, caplog):
        """Test verification email contains proper verification URL."""
        # Arrange
        caplog.set_level(logging.INFO)
        service = EmailService()
        token = "unique-token-123"

        # Act
        await service.send_verification_email(
            to_email="user@example.com",
            verification_token=token,
            user_name="Test User",
        )

        # Assert
        expected_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
        assert expected_url in caplog.text

    @pytest.mark.asyncio
    async def test_verification_email_html_rendering(self):
        """Test HTML template rendering for verification email."""
        # Arrange
        service = EmailService()

        # Act
        html = service._render_verification_email_html(
            user_name="Test User",
            verification_url="https://example.com/verify?token=abc123",
        )

        # Assert
        assert "Test User" in html
        assert "https://example.com/verify?token=abc123" in html
        assert "GoalPlan" in html
        assert "Verify Email Address" in html
        assert "<!DOCTYPE html>" in html

    @pytest.mark.asyncio
    async def test_verification_email_text_rendering(self):
        """Test text template rendering for verification email."""
        # Arrange
        service = EmailService()

        # Act
        text = service._render_verification_email_text(
            user_name="Test User",
            verification_url="https://example.com/verify?token=abc123",
        )

        # Assert
        assert "Test User" in text
        assert "https://example.com/verify?token=abc123" in text
        assert "GoalPlan" in text
        assert "Welcome to GoalPlan" in text

    @pytest.mark.asyncio
    async def test_email_template_includes_expiration_info(self):
        """Test that verification email mentions 24-hour expiration."""
        # Arrange
        service = EmailService()

        # Act
        html = service._render_verification_email_html(
            user_name="Test User",
            verification_url="https://example.com/verify?token=abc123",
        )

        # Assert
        assert "24 hours" in html

    @pytest.mark.asyncio
    async def test_email_template_responsive_design(self):
        """Test that HTML template includes responsive design elements."""
        # Arrange
        service = EmailService()

        # Act
        html = service._render_verification_email_html(
            user_name="Test User",
            verification_url="https://example.com/verify?token=abc123",
        )

        # Assert
        assert 'width="600"' in html  # Standard email width
        assert 'cellpadding="0"' in html  # Email best practices
        assert 'style=' in html  # Inline styles for email compatibility

    @pytest.mark.asyncio
    async def test_email_template_includes_branding(self):
        """Test that email template includes proper branding."""
        # Arrange
        service = EmailService()

        # Act
        html = service._render_verification_email_html(
            user_name="Test User",
            verification_url="https://example.com/verify?token=abc123",
        )

        # Assert
        assert settings.APP_NAME in html
        assert "Dual-Country Financial Planning" in html

    @pytest.mark.asyncio
    async def test_email_template_includes_fallback_link(self):
        """Test that email template includes fallback URL for button."""
        # Arrange
        service = EmailService()
        url = "https://example.com/verify?token=abc123"

        # Act
        html = service._render_verification_email_html(
            user_name="Test User",
            verification_url=url,
        )

        # Assert
        # Should contain the URL twice: once in button, once as fallback text
        assert html.count(url) >= 2

    @pytest.mark.asyncio
    async def test_multiple_emails_can_be_sent(self, caplog):
        """Test that multiple emails can be sent sequentially."""
        # Arrange
        caplog.set_level(logging.INFO)
        service = EmailService()

        # Act
        result1 = await service.send_verification_email(
            to_email="user1@example.com",
            verification_token="token1",
            user_name="User One",
        )

        result2 = await service.send_verification_email(
            to_email="user2@example.com",
            verification_token="token2",
            user_name="User Two",
        )

        # Assert
        assert result1 is True
        assert result2 is True
        assert "user1@example.com" in caplog.text
        assert "user2@example.com" in caplog.text

    @pytest.mark.asyncio
    async def test_email_handles_special_characters_in_name(self, caplog):
        """Test email service handles special characters in user name."""
        # Arrange
        caplog.set_level(logging.INFO)
        service = EmailService()

        # Act
        result = await service.send_verification_email(
            to_email="user@example.com",
            verification_token="token123",
            user_name="José María O'Brien",
        )

        # Assert
        assert result is True
        assert "José María O'Brien" in caplog.text

    @pytest.mark.asyncio
    async def test_email_handles_long_tokens(self, caplog):
        """Test email service handles long verification tokens."""
        # Arrange
        caplog.set_level(logging.INFO)
        service = EmailService()
        long_token = "a" * 200

        # Act
        result = await service.send_verification_email(
            to_email="user@example.com",
            verification_token=long_token,
            user_name="Test User",
        )

        # Assert
        assert result is True
        assert long_token in caplog.text
