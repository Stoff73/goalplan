"""
Emergency Fund Assessment Service Demonstration

This script demonstrates the Emergency Fund Assessment Service with example scenarios.
Run this to see how the service evaluates different emergency fund situations.

Usage:
    python3 demo_emergency_fund_assessment.py
"""

from decimal import Decimal
from services.emergency_fund_assessment import EmergencyFundAssessmentService


def print_assessment(title: str, assessment: dict) -> None:
    """Pretty print an assessment result."""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}\n")

    symbol = "£" if assessment["base_currency"] == "GBP" else "R"

    print(f"Current Emergency Fund:    {symbol}{assessment['current_emergency_fund']:,.2f}")
    print(f"Recommended (6 months):    {symbol}{assessment['recommended_emergency_fund']:,.2f}")
    print(f"Months Covered:            {assessment['months_covered']:.1f} months")
    print(f"Ratio (current/recommended): {assessment['ratio']:.2%}")
    print(f"\nStatus: {assessment['status']}")
    print(f"\n{assessment['status_message']}")

    print(f"\nRecommendations:")
    for i, rec in enumerate(assessment['recommendations'], 1):
        print(f"  {i}. {rec}")

    print(f"\n{'=' * 80}\n")


def demo_standalone():
    """Demonstrate service without database (calculation methods only)."""
    print("\n" + "=" * 80)
    print("  EMERGENCY FUND ASSESSMENT SERVICE - STANDALONE DEMONSTRATION")
    print("=" * 80)

    # Create service instance (will work without db for calculation methods)
    service = EmergencyFundAssessmentService(db=None)

    # Example 1: Adequate Emergency Fund
    print("\n\nExample 1: ADEQUATE Emergency Fund")
    print("-" * 80)
    monthly_expenses = Decimal('2000.00')
    print(f"Monthly Expenses: £{monthly_expenses:,.2f}")

    recommended = service.calculate_recommended_emergency_fund(monthly_expenses)
    print(f"Recommended Emergency Fund (6 months): £{recommended:,.2f}")

    # Simulate adequate fund
    current = Decimal('15000.00')
    ratio = current / recommended
    months_covered = current / monthly_expenses
    status = service._determine_status(current, recommended)

    print(f"\nSimulated Current Fund: £{current:,.2f}")
    print(f"Months Covered: {months_covered:.1f}")
    print(f"Ratio: {ratio:.2%}")
    print(f"Status: {status}")

    # Example 2: Insufficient Emergency Fund
    print("\n\nExample 2: INSUFFICIENT Emergency Fund")
    print("-" * 80)
    monthly_expenses = Decimal('3000.00')
    print(f"Monthly Expenses: £{monthly_expenses:,.2f}")

    recommended = service.calculate_recommended_emergency_fund(monthly_expenses)
    print(f"Recommended Emergency Fund (6 months): £{recommended:,.2f}")

    # Simulate insufficient fund
    current = Decimal('12000.00')
    ratio = current / recommended
    months_covered = current / monthly_expenses
    status = service._determine_status(current, recommended)
    shortfall = recommended - current

    print(f"\nSimulated Current Fund: £{current:,.2f}")
    print(f"Months Covered: {months_covered:.1f}")
    print(f"Ratio: {ratio:.2%}")
    print(f"Status: {status}")
    print(f"Shortfall: £{shortfall:,.2f}")

    # Example 3: No Emergency Fund
    print("\n\nExample 3: NO Emergency Fund")
    print("-" * 80)
    monthly_expenses = Decimal('2500.00')
    print(f"Monthly Expenses: £{monthly_expenses:,.2f}")

    recommended = service.calculate_recommended_emergency_fund(monthly_expenses)
    print(f"Recommended Emergency Fund (6 months): £{recommended:,.2f}")

    # Simulate no fund
    current = Decimal('0.00')
    status = service._determine_status(current, recommended)

    print(f"\nSimulated Current Fund: £{current:,.2f}")
    print(f"Months Covered: 0.0")
    print(f"Ratio: 0.00%")
    print(f"Status: {status}")

    # Example 4: Recommendations
    print("\n\nExample 4: Recommendation Generation")
    print("-" * 80)

    print("\nADEQUATE Recommendations:")
    recs = service.generate_recommendations(
        status="ADEQUATE",
        current=Decimal('15000.00'),
        recommended=Decimal('12000.00'),
        shortfall=Decimal('0.00'),
        base_currency="GBP"
    )
    for i, rec in enumerate(recs, 1):
        print(f"  {i}. {rec}")

    print("\nINSUFFICIENT Recommendations:")
    recs = service.generate_recommendations(
        status="INSUFFICIENT",
        current=Decimal('8000.00'),
        recommended=Decimal('12000.00'),
        shortfall=Decimal('4000.00'),
        base_currency="GBP"
    )
    for i, rec in enumerate(recs, 1):
        print(f"  {i}. {rec}")

    print("\nNONE Recommendations:")
    recs = service.generate_recommendations(
        status="NONE",
        current=Decimal('0.00'),
        recommended=Decimal('12000.00'),
        shortfall=Decimal('12000.00'),
        base_currency="GBP"
    )
    for i, rec in enumerate(recs, 1):
        print(f"  {i}. {rec}")

    # Example 5: Multi-Currency (South Africa)
    print("\n\nExample 5: Multi-Currency (South African Rand)")
    print("-" * 80)
    monthly_expenses = Decimal('30000.00')
    print(f"Monthly Expenses: R{monthly_expenses:,.2f}")

    recommended = service.calculate_recommended_emergency_fund(monthly_expenses)
    print(f"Recommended Emergency Fund (6 months): R{recommended:,.2f}")

    # Simulate insufficient fund
    current = Decimal('150000.00')
    ratio = current / recommended
    months_covered = current / monthly_expenses
    status = service._determine_status(current, recommended)
    shortfall = recommended - current

    print(f"\nSimulated Current Fund: R{current:,.2f}")
    print(f"Months Covered: {months_covered:.1f}")
    print(f"Ratio: {ratio:.2%}")
    print(f"Status: {status}")
    print(f"Shortfall: R{shortfall:,.2f}")

    # Example 6: High Net Worth Individual
    print("\n\nExample 6: High Net Worth Individual")
    print("-" * 80)
    monthly_expenses = Decimal('25000.00')
    print(f"Monthly Expenses: £{monthly_expenses:,.2f}")

    recommended = service.calculate_recommended_emergency_fund(monthly_expenses)
    print(f"Recommended Emergency Fund (6 months): £{recommended:,.2f}")

    # Simulate well-stocked fund
    current = Decimal('200000.00')
    ratio = current / recommended
    months_covered = current / monthly_expenses
    status = service._determine_status(current, recommended)

    print(f"\nSimulated Current Fund: £{current:,.2f}")
    print(f"Months Covered: {months_covered:.1f}")
    print(f"Ratio: {ratio:.2%}")
    print(f"Status: {status}")

    print("\n" + "=" * 80)
    print("  END OF DEMONSTRATION")
    print("=" * 80 + "\n")


def demo_integration():
    """Show how to integrate the service with an API endpoint."""
    print("\n" + "=" * 80)
    print("  API INTEGRATION EXAMPLE")
    print("=" * 80)

    print("""
# Example FastAPI Endpoint Integration

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from decimal import Decimal

from database import get_db
from services.emergency_fund_assessment import EmergencyFundAssessmentService
from middleware.auth import get_current_user
from models.user import User

router = APIRouter(prefix="/api/v1/savings", tags=["savings"])


@router.get("/emergency-fund-assessment")
async def assess_emergency_fund(
    monthly_expenses: float,
    base_currency: str = "GBP",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    \"\"\"
    Assess user's emergency fund adequacy.

    Args:
        monthly_expenses: User's monthly expenses
        base_currency: Currency for assessment (GBP, ZAR, USD, EUR)

    Returns:
        Emergency fund assessment with status and recommendations
    \"\"\"
    # Validate currency
    if base_currency not in ["GBP", "ZAR", "USD", "EUR"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid currency. Must be GBP, ZAR, USD, or EUR"
        )

    # Validate monthly expenses
    if monthly_expenses < 0:
        raise HTTPException(
            status_code=400,
            detail="Monthly expenses cannot be negative"
        )

    # Create service
    service = EmergencyFundAssessmentService(db)

    # Perform assessment
    assessment = await service.assess_emergency_fund(
        user_id=current_user.id,
        monthly_expenses=Decimal(str(monthly_expenses)),
        base_currency=base_currency
    )

    return assessment


# Example Response (INSUFFICIENT status):
{
    "current_emergency_fund": 8000.00,
    "recommended_emergency_fund": 12000.00,
    "months_covered": 4.0,
    "ratio": 0.67,
    "status": "INSUFFICIENT",
    "status_message": "Your emergency fund is insufficient. You have 4.0 months covered but need £4,000.00 more to reach 6 months.",
    "recommendations": [
        "You have 4.0 months covered. Aim to reach 6 months (£4,000.00 more needed).",
        "Consider setting up automatic transfers to build your fund faster.",
        "Keep your emergency fund in instant-access accounts."
    ],
    "base_currency": "GBP"
}
""")

    print("=" * 80 + "\n")


if __name__ == "__main__":
    print("\n")
    print("*" * 80)
    print("*" + " " * 78 + "*")
    print("*" + "  EMERGENCY FUND ASSESSMENT SERVICE - DEMONSTRATION".center(78) + "*")
    print("*" + " " * 78 + "*")
    print("*" * 80)

    demo_standalone()
    demo_integration()

    print("\nDemonstration complete! The service is ready for integration.\n")
