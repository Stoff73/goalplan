"""
Savings allowances API endpoints.

This module provides endpoints for:
- ISA allowance tracking (UK tax-advantaged)
- TFSA allowance tracking (SA tax-advantaged)
- Emergency fund assessment

Business logic:
- UK ISA: £20,000 annual allowance (2024/25)
- SA TFSA: R36,000 annual + R500,000 lifetime (2024/25)
- Emergency fund: 6 months of expenses recommended
- Real-time allowance calculations
- Approaching limit warnings (80%, 95%)
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict
from uuid import UUID
from decimal import Decimal
import logging

from database import get_db
from middleware.auth import get_current_user
from services.isa_tfsa_tracking import (
    ISATrackingService,
    TFSATrackingService,
    get_current_uk_tax_year,
    get_current_sa_tax_year
)
from services.emergency_fund_assessment import EmergencyFundAssessmentService

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# ISA ALLOWANCE ENDPOINTS
# ============================================================================

@router.get("/isa-allowance")
async def get_isa_allowance(
    current_user_id: str = Depends(get_current_user),
    tax_year: Optional[str] = Query(None, description="UK tax year (e.g., '2024/25')"),
    db: AsyncSession = Depends(get_db)
) -> Dict:
    """
    Get ISA allowance for current or specified tax year.

    Calculates:
    - Total ISA allowance (£20,000 for 2024/25)
    - Used allowance
    - Remaining allowance
    - Percentage used
    - List of contributions

    Args:
        current_user_id: Authenticated user ID
        tax_year: Optional tax year (defaults to current UK tax year)
        db: Database session

    Returns:
        Dict with ISA allowance details:
        {
            "tax_year": "2024/25",
            "total_allowance": 20000.00,
            "used": 15000.00,
            "remaining": 5000.00,
            "percentage_used": 75.0,
            "contributions": [...]
        }

    Example:
        GET /api/v1/savings/isa-allowance
        GET /api/v1/savings/isa-allowance?tax_year=2023/24
    """
    try:
        isa_service = ISATrackingService(db)

        if tax_year is None:
            tax_year = get_current_uk_tax_year()

        allowance = await isa_service.get_isa_allowance(
            user_id=UUID(current_user_id),
            tax_year=tax_year
        )

        logger.info(
            f"Retrieved ISA allowance for user {current_user_id} "
            f"(tax year {tax_year}): £{allowance['used']} used"
        )

        return allowance

    except Exception as e:
        logger.error(f"Failed to retrieve ISA allowance: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve ISA allowance"
        )


# ============================================================================
# TFSA ALLOWANCE ENDPOINTS
# ============================================================================

@router.get("/tfsa-allowance")
async def get_tfsa_allowance(
    current_user_id: str = Depends(get_current_user),
    tax_year: Optional[str] = Query(None, description="SA tax year (e.g., '2024/25')"),
    db: AsyncSession = Depends(get_db)
) -> Dict:
    """
    Get TFSA allowance for current or specified tax year.

    Calculates:
    - Annual allowance (R36,000 for 2024/25)
    - Annual used and remaining
    - Lifetime allowance (R500,000)
    - Lifetime used and remaining
    - Percentage used (both annual and lifetime)
    - List of contributions

    Args:
        current_user_id: Authenticated user ID
        tax_year: Optional tax year (defaults to current SA tax year)
        db: Database session

    Returns:
        Dict with TFSA allowance details:
        {
            "tax_year": "2024/25",
            "annual_allowance": 36000.00,
            "annual_used": 30000.00,
            "annual_remaining": 6000.00,
            "annual_percentage_used": 83.33,
            "lifetime_allowance": 500000.00,
            "lifetime_used": 150000.00,
            "lifetime_remaining": 350000.00,
            "lifetime_percentage_used": 30.0,
            "contributions": [...]
        }

    Example:
        GET /api/v1/savings/tfsa-allowance
        GET /api/v1/savings/tfsa-allowance?tax_year=2023/24
    """
    try:
        tfsa_service = TFSATrackingService(db)

        if tax_year is None:
            tax_year = get_current_sa_tax_year()

        allowance = await tfsa_service.get_tfsa_allowance(
            user_id=UUID(current_user_id),
            tax_year=tax_year
        )

        logger.info(
            f"Retrieved TFSA allowance for user {current_user_id} "
            f"(tax year {tax_year}): R{allowance['annual_used']} annual, "
            f"R{allowance['lifetime_used']} lifetime"
        )

        return allowance

    except Exception as e:
        logger.error(f"Failed to retrieve TFSA allowance: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve TFSA allowance"
        )


# ============================================================================
# EMERGENCY FUND ASSESSMENT
# ============================================================================

@router.get("/emergency-fund-assessment")
async def get_emergency_fund_assessment(
    current_user_id: str = Depends(get_current_user),
    monthly_expenses: Decimal = Query(..., description="Monthly expenses amount", gt=0),
    base_currency: str = Query("GBP", description="Currency for assessment (GBP or ZAR)"),
    db: AsyncSession = Depends(get_db)
) -> Dict:
    """
    Assess emergency fund adequacy.

    Compares current emergency fund (accounts marked as EMERGENCY_FUND)
    against recommended 6 months of expenses.

    Business logic:
    - Recommended: 6 months of expenses
    - Status: ADEQUATE (>= 6 months), INSUFFICIENT (> 0 but < 6), NONE (0)
    - Includes personalized recommendations

    Args:
        current_user_id: Authenticated user ID
        monthly_expenses: Monthly expenses amount (required)
        base_currency: Currency for calculation (GBP or ZAR)
        db: Database session

    Returns:
        Dict with emergency fund assessment:
        {
            "current_emergency_fund": 30000.00,
            "recommended_emergency_fund": 36000.00,
            "months_covered": 5.0,
            "ratio": 0.83,
            "status": "INSUFFICIENT",
            "status_message": "Your emergency fund is insufficient...",
            "recommendations": ["..."],
            "base_currency": "GBP"
        }

    Raises:
        400: Invalid monthly_expenses (must be > 0)
        400: Invalid base_currency (must be GBP or ZAR)

    Example:
        GET /api/v1/savings/emergency-fund-assessment?monthly_expenses=2000
        GET /api/v1/savings/emergency-fund-assessment?monthly_expenses=30000&base_currency=ZAR
    """
    try:
        # Validate base currency
        if base_currency not in ["GBP", "ZAR"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Base currency must be 'GBP' or 'ZAR'"
            )

        # Initialize emergency fund service
        emergency_fund_service = EmergencyFundAssessmentService(db)

        # Perform assessment
        assessment = await emergency_fund_service.assess_emergency_fund(
            user_id=UUID(current_user_id),
            monthly_expenses=monthly_expenses,
            base_currency=base_currency
        )

        logger.info(
            f"Emergency fund assessment for user {current_user_id}: "
            f"Status={assessment['status']}, "
            f"Months covered={assessment['months_covered']:.1f}"
        )

        return assessment

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to assess emergency fund: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to assess emergency fund"
        )
