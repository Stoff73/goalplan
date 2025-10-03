"""
ISA/TFSA Allowance Tracking Service.

This module provides services for tracking ISA (UK) and TFSA (South Africa)
contribution allowances, including:
- Annual allowance tracking
- Lifetime allowance tracking (TFSA only)
- Tax year calculations for UK (April 6 - April 5) and SA (March 1 - Feb 28/29)
- Contribution recording and validation
- Approaching limit warnings (80%, 95%)

Constants:
- UK ISA: £20,000 annual allowance (2024/25)
- SA TFSA: R36,000 annual + R500,000 lifetime allowance (2024/25)

Business Rules:
- UK tax year: April 6 - April 5
- SA tax year: March 1 - February 28/29
- TFSA growth counts toward annual limit
- Unused allowance does NOT carry forward
"""

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from calendar import isleap

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.savings_account import ISAContribution, TFSAContribution, TFSAContributionType


# ===== CONFIGURATION =====

# ISA Allowances (UK)
ISA_ANNUAL_ALLOWANCE = Decimal('20000.00')  # GBP for 2024/25

# TFSA Allowances (SA)
TFSA_ANNUAL_ALLOWANCE = Decimal('36000.00')   # ZAR for 2024/25
TFSA_LIFETIME_ALLOWANCE = Decimal('500000.00')  # ZAR

# Warning thresholds
WARNING_THRESHOLD_80 = Decimal('0.80')
WARNING_THRESHOLD_95 = Decimal('0.95')


# ===== TAX YEAR HELPERS =====

def get_current_uk_tax_year(as_of_date: Optional[date] = None) -> str:
    """
    Calculate UK tax year (April 6 - April 5).

    UK tax year runs from April 6 of one year to April 5 of the next year.
    For example, if the date is 2025-04-05, the tax year is "2024/25".
    If the date is 2025-04-06, the tax year is "2025/26".

    Args:
        as_of_date: Date to calculate tax year for (defaults to today)

    Returns:
        str: Tax year in format "YYYY/YY" (e.g., "2024/25")

    Examples:
        >>> get_current_uk_tax_year(date(2025, 4, 5))
        '2024/25'
        >>> get_current_uk_tax_year(date(2025, 4, 6))
        '2025/26'
    """
    if as_of_date is None:
        as_of_date = date.today()

    # UK tax year starts April 6
    if as_of_date.month < 4 or (as_of_date.month == 4 and as_of_date.day < 6):
        # Before April 6: use previous year
        start_year = as_of_date.year - 1
    else:
        # April 6 or later: use current year
        start_year = as_of_date.year

    end_year = start_year + 1
    return f"{start_year}/{str(end_year)[-2:]}"


def get_current_sa_tax_year(as_of_date: Optional[date] = None) -> str:
    """
    Calculate SA tax year (March 1 - February 28/29).

    SA tax year runs from March 1 of one year to February 28/29 of the next year.
    For example, if the date is 2025-02-28, the tax year is "2024/25".
    If the date is 2025-03-01, the tax year is "2025/26".

    Args:
        as_of_date: Date to calculate tax year for (defaults to today)

    Returns:
        str: Tax year in format "YYYY/YY" (e.g., "2024/25")

    Examples:
        >>> get_current_sa_tax_year(date(2025, 2, 28))
        '2024/25'
        >>> get_current_sa_tax_year(date(2025, 3, 1))
        '2025/26'
    """
    if as_of_date is None:
        as_of_date = date.today()

    # SA tax year starts March 1
    if as_of_date.month < 3:
        # Before March 1: use previous year
        start_year = as_of_date.year - 1
    else:
        # March 1 or later: use current year
        start_year = as_of_date.year

    end_year = start_year + 1
    return f"{start_year}/{str(end_year)[-2:]}"


def parse_tax_year(tax_year: str) -> Tuple[int, int]:
    """
    Parse tax year string into start and end years.

    Args:
        tax_year: Tax year string (e.g., "2024/25")

    Returns:
        Tuple[int, int]: (start_year, end_year)

    Raises:
        ValueError: If tax year format is invalid
    """
    parts = tax_year.split('/')
    if len(parts) != 2:
        raise ValueError(f"Invalid tax year format: {tax_year}. Expected 'YYYY/YY'")

    try:
        start_year = int(parts[0])
        end_year_short = int(parts[1])

        # Convert 2-digit year to 4-digit
        century = (start_year // 100) * 100
        end_year = century + end_year_short

        # Validate that end_year = start_year + 1
        if end_year != start_year + 1:
            raise ValueError(f"Invalid tax year: {tax_year}. End year must be start year + 1")

        return start_year, end_year
    except ValueError as e:
        raise ValueError(f"Invalid tax year format: {tax_year}. {str(e)}")


def get_uk_tax_year_dates(tax_year: str) -> Tuple[date, date]:
    """
    Get start and end dates for UK tax year.

    Args:
        tax_year: Tax year string (e.g., "2024/25")

    Returns:
        Tuple[date, date]: (start_date, end_date)

    Example:
        >>> get_uk_tax_year_dates("2024/25")
        (date(2024, 4, 6), date(2025, 4, 5))
    """
    start_year, end_year = parse_tax_year(tax_year)
    start_date = date(start_year, 4, 6)  # April 6
    end_date = date(end_year, 4, 5)      # April 5
    return start_date, end_date


def get_sa_tax_year_dates(tax_year: str) -> Tuple[date, date]:
    """
    Get start and end dates for SA tax year.

    Args:
        tax_year: Tax year string (e.g., "2024/25")

    Returns:
        Tuple[date, date]: (start_date, end_date)

    Example:
        >>> get_sa_tax_year_dates("2024/25")
        (date(2024, 3, 1), date(2025, 2, 28))
    """
    start_year, end_year = parse_tax_year(tax_year)
    start_date = date(start_year, 3, 1)  # March 1

    # Handle leap year for February 29
    if isleap(end_year):
        end_date = date(end_year, 2, 29)
    else:
        end_date = date(end_year, 2, 28)

    return start_date, end_date


# ===== ISA TRACKING SERVICE =====

class ISATrackingService:
    """Service for tracking ISA contributions and allowances."""

    def __init__(self, db: AsyncSession):
        """
        Initialize ISA tracking service.

        Args:
            db: SQLAlchemy async database session
        """
        self.db = db

    async def get_isa_allowance(
        self,
        user_id: uuid.UUID,
        tax_year: Optional[str] = None
    ) -> Dict:
        """
        Get ISA allowance for a tax year.

        Args:
            user_id: User's UUID
            tax_year: Tax year string (defaults to current UK tax year)

        Returns:
            Dict containing:
            - tax_year: str
            - total_allowance: Decimal
            - used: Decimal
            - remaining: Decimal
            - contributions: List[Dict]
            - percentage_used: float

        Example:
            >>> service.get_isa_allowance(user_id, "2024/25")
            {
                "tax_year": "2024/25",
                "total_allowance": Decimal("20000.00"),
                "used": Decimal("15000.00"),
                "remaining": Decimal("5000.00"),
                "percentage_used": 75.0,
                "contributions": [...]
            }
        """
        if tax_year is None:
            tax_year = get_current_uk_tax_year()

        # Get all contributions for this tax year
        stmt = select(ISAContribution).where(
            ISAContribution.user_id == user_id,
            ISAContribution.tax_year == tax_year
        ).order_by(ISAContribution.contribution_date.desc())
        result = await self.db.execute(stmt)
        contributions = result.scalars().all()

        # Calculate used allowance
        used = sum(c.contribution_amount for c in contributions)
        used = Decimal(str(used))

        # Calculate remaining
        remaining = ISA_ANNUAL_ALLOWANCE - used
        remaining = max(remaining, Decimal('0'))

        # Calculate percentage used
        percentage_used = float((used / ISA_ANNUAL_ALLOWANCE) * 100) if ISA_ANNUAL_ALLOWANCE > 0 else 0.0

        return {
            "tax_year": tax_year,
            "total_allowance": ISA_ANNUAL_ALLOWANCE,
            "used": used,
            "remaining": remaining,
            "percentage_used": round(percentage_used, 2),
            "contributions": [
                {
                    "id": str(c.id),
                    "amount": c.contribution_amount,
                    "date": c.contribution_date.isoformat(),
                    "notes": c.notes
                }
                for c in contributions
            ]
        }

    async def record_isa_contribution(
        self,
        user_id: uuid.UUID,
        account_id: Optional[uuid.UUID],
        amount: Decimal,
        contribution_date: date,
        notes: Optional[str] = None
    ) -> Dict:
        """
        Record an ISA contribution.

        Automatically determines tax year from contribution date.
        Validates that contribution doesn't exceed annual allowance.

        Args:
            user_id: User's UUID
            account_id: Savings account UUID (optional)
            amount: Contribution amount in GBP
            contribution_date: Date of contribution
            notes: Optional notes

        Returns:
            Dict: Updated allowance summary

        Raises:
            ValueError: If contribution exceeds remaining allowance
        """
        # Determine tax year from contribution date
        tax_year = get_current_uk_tax_year(contribution_date)

        # Check current allowance
        allowance = await self.get_isa_allowance(user_id, tax_year)

        # Validate against remaining allowance
        if amount > allowance['remaining']:
            excess = amount - allowance['remaining']
            raise ValueError(
                f"Contribution of £{amount} would exceed ISA allowance by £{excess}. "
                f"Remaining allowance for {tax_year}: £{allowance['remaining']}"
            )

        # Create contribution record
        contribution = ISAContribution(
            id=uuid.uuid4(),
            user_id=user_id,
            savings_account_id=account_id,
            tax_year=tax_year,
            contribution_amount=amount,
            contribution_date=contribution_date,
            notes=notes
        )

        self.db.add(contribution)
        await self.db.commit()
        await self.db.refresh(contribution)

        # Return updated allowance
        return await self.get_isa_allowance(user_id, tax_year)


# ===== TFSA TRACKING SERVICE =====

class TFSATrackingService:
    """Service for tracking TFSA contributions and allowances."""

    def __init__(self, db: AsyncSession):
        """
        Initialize TFSA tracking service.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    async def get_tfsa_allowance(
        self,
        user_id: uuid.UUID,
        tax_year: Optional[str] = None
    ) -> Dict:
        """
        Get TFSA allowance for a tax year.

        Calculates both annual and lifetime allowances.

        Args:
            user_id: User's UUID
            tax_year: Tax year string (defaults to current SA tax year)

        Returns:
            Dict containing:
            - tax_year: str
            - annual_allowance: Decimal
            - annual_used: Decimal
            - annual_remaining: Decimal
            - annual_percentage_used: float
            - lifetime_allowance: Decimal
            - lifetime_used: Decimal
            - lifetime_remaining: Decimal
            - lifetime_percentage_used: float
            - contributions: List[Dict]

        Example:
            >>> service.get_tfsa_allowance(user_id, "2024/25")
            {
                "tax_year": "2024/25",
                "annual_allowance": Decimal("36000.00"),
                "annual_used": Decimal("30000.00"),
                "annual_remaining": Decimal("6000.00"),
                "annual_percentage_used": 83.33,
                "lifetime_allowance": Decimal("500000.00"),
                "lifetime_used": Decimal("150000.00"),
                "lifetime_remaining": Decimal("350000.00"),
                "lifetime_percentage_used": 30.0,
                "contributions": [...]
            }
        """
        if tax_year is None:
            tax_year = get_current_sa_tax_year()

        # Get contributions for this tax year
        stmt_annual = select(TFSAContribution).where(
            TFSAContribution.user_id == user_id,
            TFSAContribution.tax_year == tax_year
        ).order_by(TFSAContribution.contribution_date.desc())
        result_annual = await self.db.execute(stmt_annual)
        annual_contributions = result_annual.scalars().all()

        # Calculate annual used
        annual_used = sum(c.contribution_amount for c in annual_contributions)
        annual_used = Decimal(str(annual_used))

        # Calculate annual remaining
        annual_remaining = TFSA_ANNUAL_ALLOWANCE - annual_used
        annual_remaining = max(annual_remaining, Decimal('0'))

        # Calculate annual percentage used
        annual_percentage_used = float((annual_used / TFSA_ANNUAL_ALLOWANCE) * 100) if TFSA_ANNUAL_ALLOWANCE > 0 else 0.0

        # Get lifetime contributions (all time)
        stmt_lifetime = select(TFSAContribution).where(
            TFSAContribution.user_id == user_id
        )
        result_lifetime = await self.db.execute(stmt_lifetime)
        lifetime_contributions = result_lifetime.scalars().all()

        # Calculate lifetime used
        lifetime_used = sum(c.contribution_amount for c in lifetime_contributions)
        lifetime_used = Decimal(str(lifetime_used))

        # Calculate lifetime remaining
        lifetime_remaining = TFSA_LIFETIME_ALLOWANCE - lifetime_used
        lifetime_remaining = max(lifetime_remaining, Decimal('0'))

        # Calculate lifetime percentage used
        lifetime_percentage_used = float((lifetime_used / TFSA_LIFETIME_ALLOWANCE) * 100) if TFSA_LIFETIME_ALLOWANCE > 0 else 0.0

        return {
            "tax_year": tax_year,
            "annual_allowance": TFSA_ANNUAL_ALLOWANCE,
            "annual_used": annual_used,
            "annual_remaining": annual_remaining,
            "annual_percentage_used": round(annual_percentage_used, 2),
            "lifetime_allowance": TFSA_LIFETIME_ALLOWANCE,
            "lifetime_used": lifetime_used,
            "lifetime_remaining": lifetime_remaining,
            "lifetime_percentage_used": round(lifetime_percentage_used, 2),
            "contributions": [
                {
                    "id": str(c.id),
                    "amount": c.contribution_amount,
                    "type": c.contribution_type.value,
                    "date": c.contribution_date.isoformat(),
                    "notes": c.notes,
                    "tax_year": c.tax_year
                }
                for c in annual_contributions
            ]
        }

    async def record_tfsa_contribution(
        self,
        user_id: uuid.UUID,
        account_id: Optional[uuid.UUID],
        amount: Decimal,
        contribution_type: str,
        contribution_date: date,
        notes: Optional[str] = None
    ) -> Dict:
        """
        Record a TFSA contribution.

        Automatically determines tax year from contribution date.
        Validates against both annual and lifetime allowances.

        Args:
            user_id: User's UUID
            account_id: Savings account UUID (optional)
            amount: Contribution amount in ZAR
            contribution_type: "DEPOSIT" or "GROWTH"
            contribution_date: Date of contribution
            notes: Optional notes

        Returns:
            Dict: Updated allowance summary

        Raises:
            ValueError: If contribution exceeds annual or lifetime allowance
        """
        # Validate contribution type
        if contribution_type not in ['DEPOSIT', 'GROWTH']:
            raise ValueError(f"Invalid contribution type: {contribution_type}. Must be 'DEPOSIT' or 'GROWTH'")

        # Determine tax year from contribution date
        tax_year = get_current_sa_tax_year(contribution_date)

        # Check current allowances
        allowance = await self.get_tfsa_allowance(user_id, tax_year)

        # Validate against annual allowance
        if amount > allowance['annual_remaining']:
            excess = amount - allowance['annual_remaining']
            raise ValueError(
                f"Contribution of R{amount} would exceed TFSA annual allowance by R{excess}. "
                f"Remaining annual allowance for {tax_year}: R{allowance['annual_remaining']}"
            )

        # Validate against lifetime allowance
        if amount > allowance['lifetime_remaining']:
            excess = amount - allowance['lifetime_remaining']
            raise ValueError(
                f"Contribution of R{amount} would exceed TFSA lifetime allowance by R{excess}. "
                f"Remaining lifetime allowance: R{allowance['lifetime_remaining']}"
            )

        # Create contribution record
        contribution = TFSAContribution(
            id=uuid.uuid4(),
            user_id=user_id,
            savings_account_id=account_id,
            tax_year=tax_year,
            contribution_amount=amount,
            contribution_type=TFSAContributionType[contribution_type],
            contribution_date=contribution_date,
            notes=notes
        )

        self.db.add(contribution)
        await self.db.commit()
        await self.db.refresh(contribution)

        # Return updated allowance
        return await self.get_tfsa_allowance(user_id, tax_year)


# ===== SHARED SERVICE =====

class AllowanceTrackingService:
    """
    Combined service for ISA and TFSA allowance tracking.

    Provides high-level methods for checking approaching limits
    and generating warnings.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize allowance tracking service.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.isa_service = ISATrackingService(db)
        self.tfsa_service = TFSATrackingService(db)

    async def check_approaching_limit(
        self,
        user_id: uuid.UUID,
        account_type: str,
        tax_year: Optional[str] = None
    ) -> Dict:
        """
        Check if user is approaching allowance limits.

        Triggers warnings at 80% and 95% of allowance used.

        Args:
            user_id: User's UUID
            account_type: "ISA" or "TFSA"
            tax_year: Tax year string (optional, defaults to current)

        Returns:
            Dict containing:
            - approaching_limit: bool
            - percentage_used: float
            - warning_level: str (None, "80%", "95%")
            - warning_message: str

        Example:
            >>> service.check_approaching_limit(user_id, "ISA")
            {
                "approaching_limit": True,
                "percentage_used": 85.5,
                "warning_level": "80%",
                "warning_message": "You've used 85.5% of your ISA allowance for 2024/25"
            }
        """
        if account_type == "ISA":
            allowance = await self.isa_service.get_isa_allowance(user_id, tax_year)
            percentage = Decimal(str(allowance['percentage_used'])) / Decimal('100')
            limit_type = "annual"
        elif account_type == "TFSA":
            allowance = await self.tfsa_service.get_tfsa_allowance(user_id, tax_year)
            # Use the higher of annual or lifetime percentage
            annual_pct = Decimal(str(allowance['annual_percentage_used'])) / Decimal('100')
            lifetime_pct = Decimal(str(allowance['lifetime_percentage_used'])) / Decimal('100')
            percentage = max(annual_pct, lifetime_pct)
            limit_type = "lifetime" if lifetime_pct > annual_pct else "annual"
        else:
            raise ValueError(f"Invalid account type: {account_type}. Must be 'ISA' or 'TFSA'")

        # Determine warning level
        warning_level = None
        warning_message = None
        approaching_limit = False

        if percentage >= WARNING_THRESHOLD_95:
            warning_level = "95%"
            approaching_limit = True
            warning_message = (
                f"Warning: You've used {percentage * 100:.1f}% of your {account_type} "
                f"{limit_type} allowance for {allowance['tax_year']}"
            )
        elif percentage >= WARNING_THRESHOLD_80:
            warning_level = "80%"
            approaching_limit = True
            warning_message = (
                f"Notice: You've used {percentage * 100:.1f}% of your {account_type} "
                f"{limit_type} allowance for {allowance['tax_year']}"
            )

        return {
            "approaching_limit": approaching_limit,
            "percentage_used": float(percentage * 100),
            "warning_level": warning_level,
            "warning_message": warning_message
        }
