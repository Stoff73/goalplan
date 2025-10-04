"""
GoalPlan API - Main application entry point.

This module initializes the FastAPI application with all necessary middleware,
error handlers, and routes.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging
import time
from typing import AsyncGenerator

from config import settings
from database import engine, Base
from redis_client import redis_client

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.

    Handles startup and shutdown events for the application.
    """
    # Startup
    logger.info("Starting GoalPlan API...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")

    # Initialize Redis connection
    try:
        await redis_client.connect()
        logger.info("Redis connection established")
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}")

    # Create database tables (for development only)
    # In production, use Alembic migrations
    if settings.is_development():
        logger.info("Development mode: Database tables will be created via migrations")

    yield

    # Shutdown
    logger.info("Shutting down GoalPlan API...")

    # Close Redis connection
    try:
        await redis_client.disconnect()
        logger.info("Redis connection closed")
    except Exception as e:
        logger.warning(f"Error closing Redis connection: {e}")


# Initialize FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Dual-country financial planning platform for UK and South Africa",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS if settings.ALLOWED_HOSTS != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"{request.method} {request.url.path} - Status: {response.status_code}")
    return response


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    # Convert errors to JSON-serializable format
    errors = []
    for error in exc.errors():
        error_dict = {
            "loc": error.get("loc", []),
            "msg": error.get("msg", ""),
            "type": error.get("type", ""),
        }
        # Convert ctx values to strings if present
        if "ctx" in error:
            error_dict["ctx"] = {k: str(v) for k, v in error["ctx"].items()}
        errors.append(error_dict)

    logger.error(f"Validation error: {errors}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": errors,
            "message": "Validation error",
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)

    if settings.DEBUG:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "Internal server error",
                "detail": str(exc),
                "type": type(exc).__name__,
            },
        )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "Internal server error"},
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Returns the API status and basic system information.
    This endpoint is used by monitoring systems and load balancers.

    Returns:
        dict: Health status information
    """
    redis_status = "connected" if await redis_client.check_connection() else "disconnected"

    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "redis": redis_status,
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint.

    Returns basic API information.
    """
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs" if settings.DEBUG else "Documentation disabled in production",
    }


# API v1 routes
from api.v1.auth import router as auth_router
from api.v1.user import router as user_router
from api.v1.dashboard import router as dashboard_router
from api.v1.savings import router as savings_router
from api.v1.protection import router as protection_router
from api.v1.investments import router as investments_router
from api.v1.tax import router as tax_router
from api.v1.tax.dta import router as dta_router
from api.v1.tax.residency import router as residency_router
from api.v1.recommendations import router as recommendations_router
from api.v1.retirement.uk_pensions import router as retirement_router
from api.v1.retirement.sa_funds import router as sa_funds_router
from api.v1.iht.estate import router as iht_router
from api.v1.goals import router as goals_router
from api.v1.scenarios.scenarios import router as scenarios_router
from api.v1.ai.advisory import router as ai_router
from api.v1.personalization import router as personalization_router

app.include_router(auth_router, prefix=f"{settings.API_V1_PREFIX}/auth")
app.include_router(user_router, prefix=f"{settings.API_V1_PREFIX}/user")
app.include_router(dashboard_router, prefix=settings.API_V1_PREFIX)
app.include_router(savings_router, prefix=f"{settings.API_V1_PREFIX}/savings")
app.include_router(protection_router, prefix=settings.API_V1_PREFIX)
app.include_router(investments_router, prefix=f"{settings.API_V1_PREFIX}/investments")
app.include_router(tax_router, prefix=f"{settings.API_V1_PREFIX}/tax")
app.include_router(dta_router, prefix=f"{settings.API_V1_PREFIX}/tax/dta", tags=["DTA Relief"])
app.include_router(residency_router, prefix=f"{settings.API_V1_PREFIX}/tax/residency", tags=["Tax Residency"])
app.include_router(recommendations_router, prefix=f"{settings.API_V1_PREFIX}/recommendations", tags=["recommendations"])
app.include_router(retirement_router, prefix=settings.API_V1_PREFIX, tags=["retirement"])
app.include_router(sa_funds_router, prefix=f"{settings.API_V1_PREFIX}/retirement", tags=["sa-retirement"])
app.include_router(iht_router, prefix=f"{settings.API_V1_PREFIX}/iht", tags=["IHT Planning"])
app.include_router(goals_router, prefix=f"{settings.API_V1_PREFIX}/goals", tags=["Goals"])
app.include_router(scenarios_router, prefix=settings.API_V1_PREFIX)
app.include_router(ai_router, prefix=f"{settings.API_V1_PREFIX}/ai", tags=["AI Advisory"])
app.include_router(personalization_router, prefix=f"{settings.API_V1_PREFIX}/personalization")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info",
    )
