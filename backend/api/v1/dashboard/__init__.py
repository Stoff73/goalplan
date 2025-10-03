"""
Dashboard API Router.

This module provides endpoints for dashboard data aggregation including:
- Net worth summary with breakdowns
- Historical trend data
- Change calculations

All endpoints require authentication.
"""

from fastapi import APIRouter

from .net_worth import router as net_worth_router

# Create main dashboard router
router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

# Include sub-routers
router.include_router(net_worth_router)
