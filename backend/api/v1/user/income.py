"""
Income management API endpoints.

This module provides CRUD operations for user income tracking:
- Create income records with currency conversion
- Retrieve income with filtering
- Update income (recalculates conversions)
- Soft delete income
- Income summary by tax year

Business logic:
- Automatic tax year allocation (UK and SA)
- Currency conversion on create/update
- Tax treatment calculation
- Foreign income and DTA tracking
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict
from uuid import UUID
from datetime import datetime
from decimal import Decimal
import logging

from database import get_db
from middleware.auth import get_current_user
from models.income import UserIncome, IncomeTaxWithholding
from schemas.income import (
    IncomeCreate,
    IncomeUpdate,
    IncomeResponse,
    IncomeSummary,
    TaxWithholdingCreate,
    TaxWithholdingResponse
)
from services.currency_conversion import (
    CurrencyConversionService,
    get_uk_tax_year,
    get_sa_tax_year
)
from services.income_tax_treatment import IncomeTaxTreatmentService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/income", tags=["Income"])


@router.post("", response_model=IncomeResponse, status_code=status.HTTP_201_CREATED)
async def create_income(
    data: IncomeCreate,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new income record.

    Business logic:
    1. Validate data
    2. Determine UK and SA tax years from income_date
    3. Convert amount to GBP and ZAR (cache conversions)
    4. Determine tax treatment (DTA applicable?)
    5. Store record

    Returns:
        Income record with calculated fields
    """
    try:
        # Initialize services
        currency_service = CurrencyConversionService(db)
        tax_treatment_service = IncomeTaxTreatmentService(db)

        # Calculate tax years
        tax_year_uk = get_uk_tax_year(data.incomeDate)
        tax_year_sa = get_sa_tax_year(data.incomeDate)

        # Convert to GBP and ZAR for caching
        amount_in_gbp = None
        amount_in_zar = None
        exchange_rate = None
        exchange_rate_date = None

        if data.currency.value != 'GBP':
            try:
                amount_in_gbp, rate_gbp, rate_date = await currency_service.convert_amount(
                    data.amount,
                    data.currency.value,
                    'GBP',
                    data.incomeDate
                )
                if data.currency.value == 'ZAR':
                    # We have the rate to GBP, calculate ZAR amount directly
                    amount_in_zar = data.amount
                    exchange_rate = rate_gbp
                    exchange_rate_date = rate_date
                else:
                    # Convert to ZAR as well
                    amount_in_zar, rate_zar, _ = await currency_service.convert_amount(
                        data.amount,
                        data.currency.value,
                        'ZAR',
                        data.incomeDate
                    )
                    exchange_rate = rate_gbp
                    exchange_rate_date = rate_date
            except Exception as e:
                logger.error(f"Currency conversion failed: {e}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Currency conversion service unavailable: {str(e)}"
                )
        else:
            # GBP is native, convert to ZAR
            amount_in_gbp = data.amount
            try:
                amount_in_zar, exchange_rate, exchange_rate_date = await currency_service.convert_amount(
                    data.amount,
                    'GBP',
                    'ZAR',
                    data.incomeDate
                )
            except Exception as e:
                logger.warning(f"ZAR conversion failed: {e}")
                # Continue without ZAR conversion

        if data.currency.value == 'ZAR':
            amount_in_zar = data.amount
            if not amount_in_gbp:
                try:
                    amount_in_gbp, exchange_rate, exchange_rate_date = await currency_service.convert_amount(
                        data.amount,
                        'ZAR',
                        'GBP',
                        data.incomeDate
                    )
                except Exception as e:
                    logger.warning(f"GBP conversion failed: {e}")

        # Determine if foreign income and DTA applicable
        is_foreign = data.sourceCountry not in ['UK', 'ZA']
        dta_applicable = False

        if data.sourceCountry in ['UK', 'ZA']:
            # Get tax treatment to determine DTA applicability
            try:
                tax_treatment = await tax_treatment_service.calculate_tax_treatment(
                    user_id=UUID(current_user_id),
                    income_type=data.incomeType.value,
                    source_country=data.sourceCountry,
                    amount=data.amount,
                    currency=data.currency.value,
                    tax_year=tax_year_uk
                )
                dta_applicable = tax_treatment.get('dta_relief', False)
            except Exception as e:
                logger.error(f"Tax treatment calculation failed: {e}")
                # Continue without DTA determination

        # Create income record
        income = UserIncome(
            user_id=UUID(current_user_id),
            income_type=data.incomeType.value,
            source_country=data.sourceCountry,
            description=data.description,
            employer_name=data.employerName,
            amount=data.amount,
            currency=data.currency.value,
            amount_in_gbp=amount_in_gbp,
            amount_in_zar=amount_in_zar,
            exchange_rate=exchange_rate,
            exchange_rate_date=exchange_rate_date,
            frequency=data.frequency.value,
            tax_year_uk=tax_year_uk,
            tax_year_sa=tax_year_sa,
            income_date=data.incomeDate,
            is_gross=data.isGross,
            tax_withheld_amount=data.taxWithheldAmount,
            tax_withheld_currency=data.taxWithheldCurrency.value if data.taxWithheldCurrency else None,
            is_foreign_income=is_foreign or data.isForeignIncome,
            foreign_tax_credit=data.foreignTaxCredit,
            dta_applicable=dta_applicable,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.add(income)
        await db.commit()
        await db.refresh(income)

        logger.info(
            f"Created income record {income.id} for user {UUID(current_user_id)}: "
            f"{data.amount} {data.currency.value} from {data.sourceCountry}"
        )

        return _map_income_to_response(income)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create income: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create income record: {str(e)}"
        )


@router.get("", response_model=List[IncomeResponse])
async def get_all_income(
    current_user_id: str = Depends(get_current_user),
    tax_year_uk: Optional[str] = Query(None, description="Filter by UK tax year (e.g., '2023/24')"),
    tax_year_sa: Optional[str] = Query(None, description="Filter by SA tax year (e.g., '2023/24')"),
    income_type: Optional[str] = Query(None, description="Filter by income type"),
    source_country: Optional[str] = Query(None, description="Filter by source country"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all income records with optional filters.

    Query params:
    - tax_year_uk: Filter by UK tax year (e.g., '2023/24')
    - tax_year_sa: Filter by SA tax year
    - income_type: Filter by income type
    - source_country: Filter by source country

    Returns:
        List of income records (excluding soft-deleted)
    """
    try:
        # Build query with filters
        conditions = [
            UserIncome.user_id == UUID(current_user_id),
            UserIncome.deleted_at.is_(None)  # Exclude soft-deleted
        ]

        if tax_year_uk:
            conditions.append(UserIncome.tax_year_uk == tax_year_uk)

        if tax_year_sa:
            conditions.append(UserIncome.tax_year_sa == tax_year_sa)

        if income_type:
            conditions.append(UserIncome.income_type == income_type)

        if source_country:
            conditions.append(UserIncome.source_country == source_country)

        stmt = select(UserIncome).where(and_(*conditions)).order_by(UserIncome.income_date.desc())

        result = await db.execute(stmt)
        income_records = result.scalars().all()

        return [_map_income_to_response(income) for income in income_records]

    except Exception as e:
        logger.error(f"Failed to retrieve income: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve income records"
        )


@router.get("/{income_id}", response_model=IncomeResponse)
async def get_income(
    income_id: UUID,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get single income record by ID."""
    income = await _get_income_or_404(income_id, UUID(current_user_id), db)
    return _map_income_to_response(income)


@router.patch("/{income_id}", response_model=IncomeResponse)
async def update_income(
    income_id: UUID,
    data: IncomeUpdate,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update income record.

    Recalculates currency conversions and tax years if amount or date changed.
    """
    try:
        income = await _get_income_or_404(income_id, UUID(current_user_id), db)

        # Track if we need to recalculate conversions
        recalculate = False

        # Update fields
        if data.incomeType is not None:
            income.income_type = data.incomeType.value

        if data.sourceCountry is not None:
            income.source_country = data.sourceCountry

        if data.description is not None:
            income.description = data.description

        if data.employerName is not None:
            income.employer_name = data.employerName

        if data.amount is not None:
            income.amount = data.amount
            recalculate = True

        if data.currency is not None:
            income.currency = data.currency.value
            recalculate = True

        if data.frequency is not None:
            income.frequency = data.frequency.value

        if data.incomeDate is not None:
            income.income_date = data.incomeDate
            recalculate = True
            # Recalculate tax years
            income.tax_year_uk = get_uk_tax_year(data.incomeDate)
            income.tax_year_sa = get_sa_tax_year(data.incomeDate)

        if data.isGross is not None:
            income.is_gross = data.isGross

        if data.taxWithheldAmount is not None:
            income.tax_withheld_amount = data.taxWithheldAmount

        if data.taxWithheldCurrency is not None:
            income.tax_withheld_currency = data.taxWithheldCurrency.value

        if data.isForeignIncome is not None:
            income.is_foreign_income = data.isForeignIncome

        if data.foreignTaxCredit is not None:
            income.foreign_tax_credit = data.foreignTaxCredit

        # Recalculate currency conversions if needed
        if recalculate:
            currency_service = CurrencyConversionService(db)

            # Re-convert amounts
            if income.currency != 'GBP':
                try:
                    income.amount_in_gbp, income.exchange_rate, income.exchange_rate_date = \
                        await currency_service.convert_amount(
                            income.amount,
                            income.currency,
                            'GBP',
                            income.income_date
                        )
                except Exception as e:
                    logger.warning(f"GBP conversion failed on update: {e}")

            if income.currency != 'ZAR':
                try:
                    income.amount_in_zar, _, _ = await currency_service.convert_amount(
                        income.amount,
                        income.currency,
                        'ZAR',
                        income.income_date
                    )
                except Exception as e:
                    logger.warning(f"ZAR conversion failed on update: {e}")

        income.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(income)

        logger.info(f"Updated income record {income_id} for user {UUID(current_user_id)}")

        return _map_income_to_response(income)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to update income: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update income record"
        )


@router.delete("/{income_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_income(
    income_id: UUID,
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Soft delete income record.

    Sets deleted_at timestamp. Record remains in database for audit trail.
    """
    try:
        income = await _get_income_or_404(income_id, UUID(current_user_id), db)

        income.deleted_at = datetime.utcnow()

        await db.commit()

        logger.info(f"Soft deleted income record {income_id} for user {UUID(current_user_id)}")

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to delete income: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete income record"
        )


@router.get("/summary/{tax_year}", response_model=IncomeSummary)
async def get_income_summary(
    tax_year: str,
    country: str = Query('UK', description="UK or SA"),
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get income summary for a tax year.

    Aggregates:
    - Total income (in GBP and ZAR)
    - Income by type
    - Income by source country
    - Total tax withheld
    - Foreign income and tax credits
    """
    try:
        # Validate country
        if country.upper() not in ['UK', 'SA']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Country must be 'UK' or 'SA'"
            )

        # Select appropriate tax year field
        tax_year_field = UserIncome.tax_year_uk if country.upper() == 'UK' else UserIncome.tax_year_sa

        # Get all income for tax year
        stmt = select(UserIncome).where(
            and_(
                UserIncome.user_id == UUID(current_user_id),
                tax_year_field == tax_year,
                UserIncome.deleted_at.is_(None)
            )
        )

        result = await db.execute(stmt)
        income_records = result.scalars().all()

        # Calculate aggregations
        total_gbp = Decimal('0')
        total_zar = Decimal('0')
        income_by_type: Dict[str, Decimal] = {}
        income_by_source: Dict[str, Decimal] = {}
        total_tax_withheld = Decimal('0')
        foreign_income_total = Decimal('0')
        foreign_tax_credit_total = Decimal('0')

        for income in income_records:
            # Total income
            if income.amount_in_gbp:
                total_gbp += income.amount_in_gbp
            if income.amount_in_zar:
                total_zar += income.amount_in_zar

            # By type (use GBP amounts)
            income_type = income.income_type
            amount = income.amount_in_gbp or Decimal('0')
            income_by_type[income_type] = income_by_type.get(income_type, Decimal('0')) + amount

            # By source
            source = income.source_country
            income_by_source[source] = income_by_source.get(source, Decimal('0')) + amount

            # Tax withheld (convert to GBP)
            if income.tax_withheld_amount:
                if income.tax_withheld_currency == 'GBP':
                    total_tax_withheld += income.tax_withheld_amount
                else:
                    # Simplified conversion
                    total_tax_withheld += income.tax_withheld_amount / Decimal('20')

            # Foreign income
            if income.is_foreign_income:
                foreign_income_total += (income.amount_in_gbp or Decimal('0'))
                if income.foreign_tax_credit:
                    foreign_tax_credit_total += income.foreign_tax_credit

        return IncomeSummary(
            taxYear=tax_year,
            country=country.upper(),
            totalIncomeGbp=total_gbp,
            totalIncomeZar=total_zar,
            incomeByType={k: float(v) for k, v in income_by_type.items()},
            incomeBySource={k: float(v) for k, v in income_by_source.items()},
            totalTaxWithheld=total_tax_withheld,
            foreignIncome=foreign_income_total,
            foreignTaxCredit=foreign_tax_credit_total,
            recordCount=len(income_records)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate income summary: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate income summary"
        )


@router.get("/summary/{year_start}/{year_end}", response_model=IncomeSummary)
async def get_income_summary_slash_format(
    year_start: str,
    year_end: str,
    country: str = Query('UK', description="UK or SA"),
    current_user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get income summary for a tax year (alternative route accepting slash format).

    This endpoint handles frontend calls like /summary/2025/26
    and forwards to the main summary endpoint logic.
    """
    # Construct tax year string in standard format
    tax_year = f"{year_start}-{year_end}"

    # Call the main summary endpoint logic
    return await get_income_summary(
        tax_year=tax_year,
        country=country,
        current_user_id=current_user_id,
        db=db
    )


# Helper functions

async def _get_income_or_404(
    income_id: UUID,
    user_id: UUID,
    db: AsyncSession
) -> UserIncome:
    """Get income record or raise 404."""
    stmt = select(UserIncome).where(
        and_(
            UserIncome.id == income_id,
            UserIncome.user_id == user_id,
            UserIncome.deleted_at.is_(None)
        )
    )

    result = await db.execute(stmt)
    income = result.scalar_one_or_none()

    if not income:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Income record {income_id} not found"
        )

    return income


def _map_income_to_response(income: UserIncome) -> IncomeResponse:
    """Map UserIncome model to IncomeResponse schema."""
    return IncomeResponse(
        id=income.id,
        userId=income.user_id,
        incomeType=income.income_type,
        sourceCountry=income.source_country,
        description=income.description,
        employerName=income.employer_name,
        amount=income.amount,
        currency=income.currency,
        amountInGbp=income.amount_in_gbp,
        amountInZar=income.amount_in_zar,
        exchangeRate=income.exchange_rate,
        exchangeRateDate=income.exchange_rate_date,
        frequency=income.frequency,
        taxYearUk=income.tax_year_uk,
        taxYearSa=income.tax_year_sa,
        incomeDate=income.income_date,
        isGross=income.is_gross,
        taxWithheldAmount=income.tax_withheld_amount,
        taxWithheldCurrency=income.tax_withheld_currency,
        isForeignIncome=income.is_foreign_income,
        foreignTaxCredit=income.foreign_tax_credit,
        dtaApplicable=income.dta_applicable,
        createdAt=income.created_at,
        updatedAt=income.updated_at
    )
