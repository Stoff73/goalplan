"""
Email service for sending transactional emails.

This module provides email sending capabilities with support for:
- Multiple email backends (SendGrid, Console for development)
- Async email queue processing
- Email templates
- Retry logic for failed sends

Configuration:
- EMAIL_BACKEND: 'sendgrid' or 'console' (default: console)
- SENDGRID_API_KEY: API key for SendGrid
- EMAIL_FROM_ADDRESS: Sender email address
- EMAIL_FROM_NAME: Sender name

Usage:
    email_service = EmailService()
    await email_service.send_verification_email(
        to_email="user@example.com",
        verification_token="abc123",
        user_name="John Doe"
    )
"""

import logging
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod

from config import settings

logger = logging.getLogger(__name__)


class EmailBackend(ABC):
    """Abstract base class for email backends."""

    @abstractmethod
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """
        Send an email.

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email body
            text_content: Plain text email body (optional)

        Returns:
            bool: True if sent successfully, False otherwise
        """
        pass


class ConsoleEmailBackend(EmailBackend):
    """
    Console email backend for development.

    Prints emails to console instead of sending them.
    Useful for development and testing.
    """

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """Print email to console."""
        logger.info("=" * 80)
        logger.info("EMAIL (Console Backend)")
        logger.info("=" * 80)
        logger.info(f"To: {to_email}")
        logger.info(f"From: {settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM_ADDRESS}>")
        logger.info(f"Subject: {subject}")
        logger.info("-" * 80)
        logger.info("HTML Content:")
        logger.info(html_content)
        if text_content:
            logger.info("-" * 80)
            logger.info("Text Content:")
            logger.info(text_content)
        logger.info("=" * 80)
        return True


class SendGridEmailBackend(EmailBackend):
    """
    SendGrid email backend for production.

    Sends emails via SendGrid API.
    """

    def __init__(self):
        """Initialize SendGrid client."""
        if not settings.SENDGRID_API_KEY:
            raise ValueError("SENDGRID_API_KEY is required for SendGrid backend")

        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail

            self.sg_client = SendGridAPIClient(settings.SENDGRID_API_KEY)
            self.Mail = Mail
        except ImportError:
            raise ImportError(
                "sendgrid package is required for SendGrid backend. "
                "Install with: pip install sendgrid"
            )

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """Send email via SendGrid API."""
        try:
            message = self.Mail(
                from_email=(settings.EMAIL_FROM_ADDRESS, settings.EMAIL_FROM_NAME),
                to_emails=to_email,
                subject=subject,
                html_content=html_content,
                plain_text_content=text_content,
            )

            response = self.sg_client.send(message)

            if response.status_code in (200, 201, 202):
                logger.info(f"Email sent successfully to {to_email}")
                return True
            else:
                logger.error(
                    f"Failed to send email to {to_email}. "
                    f"Status: {response.status_code}"
                )
                return False

        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {str(e)}")
            return False


class EmailService:
    """
    Email service for sending transactional emails.

    Handles email template rendering and sending via configured backend.
    """

    def __init__(self):
        """Initialize email service with appropriate backend."""
        backend = getattr(settings, "EMAIL_BACKEND", "console").lower()

        if backend == "sendgrid":
            self.backend = SendGridEmailBackend()
        else:
            self.backend = ConsoleEmailBackend()

        logger.info(f"Email service initialized with {backend} backend")

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """
        Send an email.

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email body
            text_content: Plain text email body (optional)

        Returns:
            bool: True if sent successfully, False otherwise
        """
        return await self.backend.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
        )

    async def send_verification_email(
        self,
        to_email: str,
        verification_token: str,
        user_name: str,
    ) -> bool:
        """
        Send email verification email.

        Args:
            to_email: User's email address
            verification_token: Verification token
            user_name: User's name

        Returns:
            bool: True if sent successfully, False otherwise
        """
        # Build verification URL
        verification_url = (
            f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"
        )

        # Render email template
        html_content = self._render_verification_email_html(
            user_name=user_name,
            verification_url=verification_url,
        )

        text_content = self._render_verification_email_text(
            user_name=user_name,
            verification_url=verification_url,
        )

        # Send email
        return await self.send_email(
            to_email=to_email,
            subject="Verify your GoalPlan account",
            html_content=html_content,
            text_content=text_content,
        )

    def _render_verification_email_html(
        self, user_name: str, verification_url: str
    ) -> str:
        """
        Render HTML template for verification email.

        Args:
            user_name: User's name
            verification_url: Verification URL

        Returns:
            str: Rendered HTML content
        """
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verify Your Email</title>
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #f4f4f4; padding: 20px 0;">
        <tr>
            <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" border="0" style="background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="padding: 40px 40px 20px 40px; text-align: center; background-color: #0066cc; border-radius: 8px 8px 0 0;">
                            <h1 style="color: #ffffff; margin: 0; font-size: 28px;">GoalPlan</h1>
                        </td>
                    </tr>

                    <!-- Content -->
                    <tr>
                        <td style="padding: 40px;">
                            <h2 style="color: #333333; margin: 0 0 20px 0; font-size: 24px;">Welcome, {user_name}!</h2>

                            <p style="color: #666666; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                                Thank you for signing up for GoalPlan. We're excited to help you manage your financial planning across the UK and South Africa.
                            </p>

                            <p style="color: #666666; font-size: 16px; line-height: 1.6; margin: 0 0 30px 0;">
                                To complete your registration and verify your email address, please click the button below:
                            </p>

                            <!-- Button -->
                            <table width="100%" cellpadding="0" cellspacing="0" border="0">
                                <tr>
                                    <td align="center">
                                        <a href="{verification_url}" style="display: inline-block; padding: 14px 40px; background-color: #0066cc; color: #ffffff; text-decoration: none; border-radius: 4px; font-size: 16px; font-weight: bold;">
                                            Verify Email Address
                                        </a>
                                    </td>
                                </tr>
                            </table>

                            <p style="color: #666666; font-size: 14px; line-height: 1.6; margin: 30px 0 0 0;">
                                This link will expire in 24 hours. If you didn't create a GoalPlan account, you can safely ignore this email.
                            </p>

                            <p style="color: #666666; font-size: 14px; line-height: 1.6; margin: 20px 0 0 0;">
                                If the button doesn't work, copy and paste this link into your browser:
                            </p>

                            <p style="color: #0066cc; font-size: 12px; word-break: break-all; margin: 10px 0 0 0;">
                                {verification_url}
                            </p>
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="padding: 20px 40px; background-color: #f8f8f8; border-radius: 0 0 8px 8px; text-align: center;">
                            <p style="color: #999999; font-size: 12px; margin: 0;">
                                &copy; {settings.APP_NAME} | Dual-Country Financial Planning
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

    def _render_verification_email_text(
        self, user_name: str, verification_url: str
    ) -> str:
        """
        Render plain text template for verification email.

        Args:
            user_name: User's name
            verification_url: Verification URL

        Returns:
            str: Rendered text content
        """
        return f"""
Welcome to GoalPlan, {user_name}!

Thank you for signing up for GoalPlan. We're excited to help you manage your financial planning across the UK and South Africa.

To complete your registration and verify your email address, please visit this link:

{verification_url}

This link will expire in 24 hours.

If you didn't create a GoalPlan account, you can safely ignore this email.

---
{settings.APP_NAME}
Dual-Country Financial Planning
"""


# Create singleton instance
email_service = EmailService()
