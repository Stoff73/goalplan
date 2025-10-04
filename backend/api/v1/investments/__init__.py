"""
Investment module API router.

This module aggregates all investment-related endpoint routers:
- accounts: Investment account CRUD
- holdings: Holdings management, price updates, selling, dividends
- portfolio: Portfolio analysis, allocation, performance, tax calculations

All endpoints require authentication.
Rate limiting applied to mutation endpoints.
"""

from fastapi import APIRouter

from api.v1.investments.accounts import router as accounts_router
from api.v1.investments.holdings import router as holdings_router
from api.v1.investments.portfolio import router as portfolio_router

router = APIRouter()

# Register sub-routers
router.include_router(accounts_router, prefix="", tags=["Investment Accounts"])
router.include_router(holdings_router, prefix="", tags=["Investment Holdings"])
router.include_router(portfolio_router, prefix="", tags=["Portfolio Analysis"])
