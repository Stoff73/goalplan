"""Authentication API endpoints."""

from fastapi import APIRouter
from api.v1.auth import registration, login, refresh, logout, two_factor

router = APIRouter()

# Include sub-routers
router.include_router(registration.router, tags=["authentication"])
router.include_router(login.router, tags=["authentication"])
router.include_router(refresh.router, tags=["authentication"])
router.include_router(logout.router, tags=["authentication"])
router.include_router(two_factor.router, tags=["two-factor-authentication"])
