"""
Personalization API module.
"""

from fastapi import APIRouter
from .preferences import router as preferences_router

router = APIRouter()
router.include_router(preferences_router, tags=["Personalization"])
