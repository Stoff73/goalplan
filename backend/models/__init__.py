"""
Database models for GoalPlan application.

This package contains all SQLAlchemy ORM models organized by domain.
"""

from .user import User, EmailVerificationToken, UserStatus
from .session import UserSession, LoginAttempt
from .two_factor import User2FA
from .tax_status import UserTaxStatus, UKSRTData, SAPresenceData, UKDomicileStatus
from .income import UserIncome, IncomeTaxWithholding, ExchangeRate
from .profile import UserProfileHistory, EmailChangeToken
from .net_worth_snapshot import NetWorthSnapshot
from .savings_account import SavingsAccount, AccountBalanceHistory

__all__ = [
    "User",
    "EmailVerificationToken",
    "UserStatus",
    "UserSession",
    "LoginAttempt",
    "User2FA",
    "UserTaxStatus",
    "UKSRTData",
    "SAPresenceData",
    "UKDomicileStatus",
    "UserIncome",
    "IncomeTaxWithholding",
    "ExchangeRate",
    "UserProfileHistory",
    "EmailChangeToken",
    "NetWorthSnapshot",
    "SavingsAccount",
    "AccountBalanceHistory",
]
