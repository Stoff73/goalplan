"""
User profile management API endpoints.

This module provides REST API endpoints for user profile operations.
"""

from fastapi import APIRouter

from .profile import router as profile_router
from .password import router as password_router
from .email import router as email_router
from .account import router as account_router
from .tax_status import router as tax_status_router
from .income import router as income_router

# Create main user router
router = APIRouter()

# Include sub-routers
router.include_router(profile_router, tags=["User Profile"])
router.include_router(password_router, tags=["User Profile"])
router.include_router(email_router, tags=["User Profile"])
router.include_router(account_router, tags=["User Profile"])
router.include_router(tax_status_router, tags=["Tax Status"])
router.include_router(income_router, tags=["Income"])

__all__ = ["router"]
