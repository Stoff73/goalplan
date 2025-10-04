"""
Protection module API endpoints.

This package provides API endpoints for the protection module:
- Life assurance policy management
- Coverage needs analysis
- Premium reminders
"""

from fastapi import APIRouter
from api.v1.protection import life_assurance, coverage

# Create protection router
router = APIRouter(prefix="/protection", tags=["Protection"])

# Include sub-routers
router.include_router(life_assurance.router)
router.include_router(coverage.router)

__all__ = ["router"]
