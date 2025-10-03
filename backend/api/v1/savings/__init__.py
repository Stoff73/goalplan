"""
Savings module API router.

This module aggregates all savings-related endpoint routers:
- accounts: CRUD and balance management
- allowances: ISA/TFSA tracking
- emergency_fund: Emergency fund assessment
"""

from fastapi import APIRouter

from api.v1.savings.accounts import router as accounts_router
from api.v1.savings.allowances import router as allowances_router

router = APIRouter()

# Register sub-routers
router.include_router(accounts_router, prefix="", tags=["Savings Accounts"])
router.include_router(allowances_router, prefix="", tags=["Savings Allowances"])
