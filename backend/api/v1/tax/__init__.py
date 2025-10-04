"""
Tax calculation API module.

This module provides endpoints for UK and SA tax calculations, including:
- Income Tax
- National Insurance (UK only)
- Capital Gains Tax
- Dividend Tax
- Comprehensive tax summary
"""

from fastapi import APIRouter
from .calculations import router as calculations_router

# Create main tax router
router = APIRouter(tags=["Tax Calculations"])

# Include sub-routers
router.include_router(calculations_router)
