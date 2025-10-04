"""
Portfolio Management Service

Provides comprehensive investment portfolio management including:
- Investment account creation with encrypted account numbers
- Holding management (add, update, sell)
- Tax lot tracking for FIFO CGT calculations
- Dividend income recording
- Realized capital gains tracking

Business Rules:
- Account numbers are encrypted using Fernet symmetric encryption
- FIFO (First-In-First-Out) method for UK capital gains tax calculations
- Multi-currency support with GBP/ZAR conversion
- Soft delete for audit trail
- All prices must be non-negative
- All quantities must be positive

Performance:
- Target: <200ms for account/holding operations
- Target: <500ms for sell operations (due to FIFO calculation)
- Async database operations throughout
"""

import logging
import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import UUID

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from models.investment import (
    InvestmentAccount, InvestmentHolding, TaxLot, DividendIncome,
    CapitalGainRealized, AccountType, AccountCountry, AccountStatus,
    SecurityType, AssetClass, Region, DisposalMethod, SourceCountry
)
from utils.encryption import encrypt_value
from services.currency_conversion import CurrencyConversionService

logger = logging.getLogger(__name__)


class PortfolioService:
    """Service for portfolio management operations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize portfolio service.

        Args:
            db: Database session for operations
        """
        self.db = db
        self.currency_service = CurrencyConversionService(db)

    async def create_account(
        self,
        user_id: UUID,
        account_type: AccountType,
        provider: str,
        account_number: str,
        country: AccountCountry,
        base_currency: str = "GBP",
        account_open_date: Optional[date] = None
    ) -> InvestmentAccount:
        """
        Create a new investment account with encrypted account number.

        Args:
            user_id: User UUID
            account_type: Type of investment account (STOCKS_ISA, GIA, etc.)
            provider: Account provider name
            account_number: Plain text account number (will be encrypted)
            country: Country where account is held
            base_currency: Base currency for account (default GBP)
            account_open_date: Date account was opened (optional)

        Returns:
            Created InvestmentAccount

        Raises:
            ValueError: If account_type is invalid
        """
        logger.info(
            f"Creating investment account for user {user_id}: "
            f"type={account_type}, provider={provider}"
        )

        # Validate account type
        if not isinstance(account_type, AccountType):
            try:
                account_type = AccountType(account_type)
            except ValueError:
                raise ValueError(
                    f"Invalid account type: {account_type}. Must be one of: "
                    f"{', '.join([t.value for t in AccountType])}"
                )

        # Create account
        account = InvestmentAccount(
            id=uuid.uuid4(),
            user_id=user_id,
            account_type=account_type,
            provider=provider,
            country=country,
            base_currency=base_currency,
            account_open_date=account_open_date or date.today(),
            status=AccountStatus.ACTIVE,
            deleted=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Encrypt and set account number
        account.set_account_number(account_number)

        # Save to database
        self.db.add(account)
        await self.db.commit()
        await self.db.refresh(account)

        logger.info(
            f"Investment account created successfully: id={account.id}, "
            f"type={account_type}, provider={provider}"
        )

        return account

    async def add_holding(
        self,
        account_id: UUID,
        security_type: SecurityType,
        ticker: str,
        name: str,
        quantity: Decimal,
        purchase_price: Decimal,
        purchase_date: date,
        purchase_currency: str,
        asset_class: AssetClass,
        region: Region,
        sector: Optional[str] = None,
        isin: Optional[str] = None
    ) -> InvestmentHolding:
        """
        Add a new holding to an investment account.

        Creates both the holding and initial tax lot for CGT tracking.

        Args:
            account_id: Investment account UUID
            security_type: Type of security (STOCK, FUND, ETF, etc.)
            ticker: Security ticker symbol
            name: Security name
            quantity: Number of shares/units
            purchase_price: Purchase price per share/unit
            purchase_date: Date of purchase
            purchase_currency: Currency of purchase
            asset_class: Asset class (EQUITY, FIXED_INCOME, etc.)
            region: Geographic region
            sector: Sector (optional)
            isin: ISIN code (optional)

        Returns:
            Created InvestmentHolding

        Raises:
            ValueError: If quantity <= 0 or purchase_price < 0
            ValueError: If account not found
        """
        # Validate inputs
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")

        if purchase_price < 0:
            raise ValueError("Purchase price cannot be negative")

        # Verify account exists
        account_result = await self.db.execute(
            select(InvestmentAccount).where(
                and_(
                    InvestmentAccount.id == account_id,
                    InvestmentAccount.deleted == False
                )
            )
        )
        account = account_result.scalar_one_or_none()

        if not account:
            raise ValueError(f"Investment account not found: {account_id}")

        logger.info(
            f"Adding holding to account {account_id}: "
            f"ticker={ticker}, quantity={quantity}, price={purchase_price}"
        )

        # Create holding
        holding = InvestmentHolding(
            id=uuid.uuid4(),
            account_id=account_id,
            security_type=security_type,
            ticker=ticker,
            isin=isin,
            security_name=name,
            quantity=quantity,
            purchase_date=purchase_date,
            purchase_price=purchase_price,
            purchase_currency=purchase_currency,
            current_price=purchase_price,  # Initially same as purchase price
            asset_class=asset_class,
            region=region,
            sector=sector,
            last_price_update=datetime.utcnow(),
            deleted=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        self.db.add(holding)
        await self.db.flush()  # Flush to get holding ID

        # Create initial tax lot for FIFO tracking
        # Convert to GBP and ZAR for cost basis
        cost_basis_gbp = Decimal('0.00')
        cost_basis_zar = Decimal('0.00')
        exchange_rate = Decimal('1.00')

        if purchase_currency == "GBP":
            cost_basis_gbp = purchase_price * quantity
            # Convert to ZAR
            converted_zar, rate_zar, _ = await self.currency_service.convert_amount(
                cost_basis_gbp, "GBP", "ZAR"
            )
            cost_basis_zar = converted_zar
            exchange_rate = rate_zar
        elif purchase_currency == "ZAR":
            cost_basis_zar = purchase_price * quantity
            # Convert to GBP
            converted_gbp, rate_gbp, _ = await self.currency_service.convert_amount(
                cost_basis_zar, "ZAR", "GBP"
            )
            cost_basis_gbp = converted_gbp
            # Calculate ZAR/GBP exchange rate
            if converted_gbp > 0:
                exchange_rate = cost_basis_zar / converted_gbp
        else:
            # For other currencies, convert to both GBP and ZAR
            cost_in_currency = purchase_price * quantity
            converted_gbp, _, _ = await self.currency_service.convert_amount(
                cost_in_currency, purchase_currency, "GBP"
            )
            cost_basis_gbp = converted_gbp

            converted_zar, _, _ = await self.currency_service.convert_amount(
                cost_in_currency, purchase_currency, "ZAR"
            )
            cost_basis_zar = converted_zar

            # Calculate exchange rate (for tracking)
            if cost_basis_gbp > 0:
                exchange_rate = cost_basis_zar / cost_basis_gbp

        tax_lot = TaxLot(
            id=uuid.uuid4(),
            holding_id=holding.id,
            purchase_date=purchase_date,
            quantity=quantity,
            purchase_price=purchase_price,
            purchase_currency=purchase_currency,
            cost_basis_gbp=cost_basis_gbp,
            cost_basis_zar=cost_basis_zar,
            exchange_rate=exchange_rate,
            disposal_date=None,
            disposal_quantity=None,
            disposal_proceeds=None,
            realized_gain=None,
            cgt_tax_year=None,
            disposal_method=None,
            created_at=datetime.utcnow()
        )

        self.db.add(tax_lot)
        await self.db.commit()
        await self.db.refresh(holding)

        logger.info(
            f"Holding added successfully: id={holding.id}, ticker={ticker}, "
            f"quantity={quantity}, tax_lot_id={tax_lot.id}"
        )

        return holding

    async def update_holding_price(
        self,
        holding_id: UUID,
        new_current_price: Decimal
    ) -> InvestmentHolding:
        """
        Update the current price of a holding and recalculate gains.

        Args:
            holding_id: Holding UUID
            new_current_price: New current price per share/unit

        Returns:
            Updated InvestmentHolding

        Raises:
            ValueError: If holding not found or price is negative
        """
        if new_current_price < 0:
            raise ValueError("Current price cannot be negative")

        # Get holding
        result = await self.db.execute(
            select(InvestmentHolding).where(
                and_(
                    InvestmentHolding.id == holding_id,
                    InvestmentHolding.deleted == False
                )
            )
        )
        holding = result.scalar_one_or_none()

        if not holding:
            raise ValueError(f"Holding not found: {holding_id}")

        logger.info(
            f"Updating price for holding {holding_id}: "
            f"old_price={holding.current_price}, new_price={new_current_price}"
        )

        # Update price
        holding.current_price = new_current_price
        holding.last_price_update = datetime.utcnow()
        holding.updated_at = datetime.utcnow()

        # Note: current_value, unrealized_gain, and unrealized_gain_percentage
        # are calculated via @property methods in the model

        await self.db.commit()
        await self.db.refresh(holding)

        logger.info(
            f"Holding price updated: id={holding_id}, "
            f"current_value={holding.current_value}, "
            f"unrealized_gain={holding.unrealized_gain}"
        )

        return holding

    async def sell_holding(
        self,
        holding_id: UUID,
        quantity_to_sell: Decimal,
        sale_price: Decimal,
        sale_date: date
    ) -> Dict[str, Any]:
        """
        Sell a holding (partial or full) using FIFO method for CGT.

        Args:
            holding_id: Holding UUID
            quantity_to_sell: Quantity to sell
            sale_price: Sale price per share/unit
            sale_date: Date of sale

        Returns:
            Dict with sale details including:
            - holding_id: UUID
            - quantity_sold: Decimal
            - sale_price: Decimal
            - sale_value: Decimal
            - cost_basis: Decimal
            - realized_gain: Decimal
            - tax_year: str
            - remaining_quantity: Decimal

        Raises:
            ValueError: If holding not found, quantity exceeds available,
                       or sale parameters are invalid
        """
        # Validate inputs
        if quantity_to_sell <= 0:
            raise ValueError("Quantity to sell must be greater than 0")

        if sale_price < 0:
            raise ValueError("Sale price cannot be negative")

        # Get holding
        result = await self.db.execute(
            select(InvestmentHolding).where(
                and_(
                    InvestmentHolding.id == holding_id,
                    InvestmentHolding.deleted == False
                )
            )
        )
        holding = result.scalar_one_or_none()

        if not holding:
            raise ValueError(f"Holding not found: {holding_id}")

        # Check quantity available
        if quantity_to_sell > holding.quantity:
            raise ValueError(
                f"Cannot sell {quantity_to_sell} shares. "
                f"Only {holding.quantity} shares available."
            )

        logger.info(
            f"Selling holding {holding_id}: quantity={quantity_to_sell}, "
            f"price={sale_price}, date={sale_date}"
        )

        # Get account for country
        account_result = await self.db.execute(
            select(InvestmentAccount).where(
                InvestmentAccount.id == holding.account_id
            )
        )
        account = account_result.scalar_one()

        # Get tax lots using FIFO (oldest first, not yet disposed or partially disposed)
        # A tax lot is available if disposal_date is None (not sold at all)
        tax_lots_result = await self.db.execute(
            select(TaxLot)
            .where(
                and_(
                    TaxLot.holding_id == holding_id,
                    TaxLot.disposal_date.is_(None)  # Only lots that haven't been sold
                )
            )
            .order_by(TaxLot.purchase_date.asc())
        )
        tax_lots = tax_lots_result.scalars().all()

        if not tax_lots:
            raise ValueError(f"No tax lots found for holding {holding_id}")

        # Calculate total cost basis and process FIFO sales
        total_cost_basis = Decimal('0.00')
        total_proceeds = sale_price * quantity_to_sell
        remaining_to_sell = quantity_to_sell

        for tax_lot in tax_lots:
            if remaining_to_sell <= 0:
                break

            # Determine quantity from this lot
            lot_quantity_to_sell = min(remaining_to_sell, tax_lot.quantity)

            # Calculate cost basis from this lot (proportional)
            lot_cost_basis = (tax_lot.cost_basis_gbp / tax_lot.quantity) * lot_quantity_to_sell
            total_cost_basis += lot_cost_basis

            # Calculate tax year (UK: April 6 - April 5)
            if sale_date.month >= 4 and sale_date.day >= 6:
                tax_year = f"{sale_date.year}/{str(sale_date.year + 1)[-2:]}"
            else:
                tax_year = f"{sale_date.year - 1}/{str(sale_date.year)[-2:]}"

            # Update tax lot for disposal
            tax_lot.disposal_date = sale_date
            tax_lot.disposal_quantity = lot_quantity_to_sell
            tax_lot.disposal_proceeds = sale_price * lot_quantity_to_sell
            tax_lot.realized_gain = (sale_price * lot_quantity_to_sell) - lot_cost_basis
            tax_lot.disposal_method = DisposalMethod.FIFO
            tax_lot.cgt_tax_year = tax_year

            # Note: We keep the original quantity in tax_lot.quantity for record keeping
            # The disposal_date and disposal_quantity indicate it's been sold

            # Update remaining quantity to sell
            remaining_to_sell -= lot_quantity_to_sell

            logger.debug(
                f"Sold {lot_quantity_to_sell} from tax lot {tax_lot.id}, "
                f"cost_basis={lot_cost_basis}, gain={tax_lot.realized_gain}"
            )

        # Calculate realized gain
        realized_gain = total_proceeds - total_cost_basis

        # Determine tax year for capital gain record
        if sale_date.month >= 4 and sale_date.day >= 6:
            cg_tax_year = f"{sale_date.year}/{str(sale_date.year + 1)[-2:]}"
        else:
            cg_tax_year = f"{sale_date.year - 1}/{str(sale_date.year)[-2:]}"

        # Create capital gain record
        capital_gain = CapitalGainRealized(
            id=uuid.uuid4(),
            holding_id=holding_id,
            disposal_date=sale_date,
            quantity_sold=quantity_to_sell,
            sale_price=sale_price,
            sale_value=total_proceeds,
            cost_basis=total_cost_basis,
            gain_loss=realized_gain,
            tax_year=cg_tax_year,
            country=account.country,
            created_at=datetime.utcnow()
        )

        self.db.add(capital_gain)

        # Update holding quantity
        new_quantity = holding.quantity - quantity_to_sell
        # Handle edge case: if fully sold, keep a tiny amount to satisfy check constraint
        # In production, fully sold holdings should be soft deleted instead
        if new_quantity <= 0:
            new_quantity = Decimal('0')
            holding.deleted = True  # Soft delete when fully sold

        holding.quantity = new_quantity if new_quantity > 0 else Decimal('0.0001')  # Min quantity to satisfy constraint
        holding.updated_at = datetime.utcnow()

        # If fully sold, optionally mark as deleted or keep for historical tracking
        # For now, we keep it with quantity = 0

        await self.db.commit()

        sale_details = {
            "holding_id": str(holding_id),
            "quantity_sold": float(quantity_to_sell),
            "sale_price": float(sale_price),
            "sale_value": float(total_proceeds),
            "cost_basis": float(total_cost_basis),
            "realized_gain": float(realized_gain),
            "tax_year": cg_tax_year,
            "remaining_quantity": float(new_quantity),
            "capital_gain_id": str(capital_gain.id)
        }

        logger.info(
            f"Holding sold successfully: id={holding_id}, "
            f"quantity_sold={quantity_to_sell}, realized_gain={realized_gain}, "
            f"remaining={new_quantity}"
        )

        return sale_details

    async def record_dividend(
        self,
        holding_id: UUID,
        payment_date: date,
        amount: Decimal,
        currency: str,
        tax_withheld: Decimal = Decimal('0.00'),
        country_of_source: SourceCountry = SourceCountry.UK,
        ex_dividend_date: Optional[date] = None
    ) -> DividendIncome:
        """
        Record a dividend payment.

        Args:
            holding_id: Holding UUID
            payment_date: Date dividend was paid
            amount: Gross dividend amount
            currency: Currency of dividend
            tax_withheld: Tax withheld at source (default 0)
            country_of_source: Country where dividend originated
            ex_dividend_date: Ex-dividend date (optional)

        Returns:
            Created DividendIncome record

        Raises:
            ValueError: If holding not found or amounts are invalid
        """
        if amount < 0:
            raise ValueError("Dividend amount cannot be negative")

        if tax_withheld < 0:
            raise ValueError("Tax withheld cannot be negative")

        if tax_withheld > amount:
            raise ValueError("Tax withheld cannot exceed dividend amount")

        # Get holding to validate and get quantity
        result = await self.db.execute(
            select(InvestmentHolding).where(
                and_(
                    InvestmentHolding.id == holding_id,
                    InvestmentHolding.deleted == False
                )
            )
        )
        holding = result.scalar_one_or_none()

        if not holding:
            raise ValueError(f"Holding not found: {holding_id}")

        logger.info(
            f"Recording dividend for holding {holding_id}: "
            f"amount={amount}, tax_withheld={tax_withheld}"
        )

        # Calculate net dividend
        net_dividend = amount - tax_withheld

        # Calculate dividend per share (for tracking)
        dividend_per_share = amount / holding.quantity if holding.quantity > 0 else Decimal('0.00')

        # Determine tax years
        # UK tax year: April 6 - April 5
        if payment_date.month >= 4 and payment_date.day >= 6:
            uk_tax_year = f"{payment_date.year}/{str(payment_date.year + 1)[-2:]}"
        else:
            uk_tax_year = f"{payment_date.year - 1}/{str(payment_date.year)[-2:]}"

        # SA tax year: March 1 - February 28/29
        if payment_date.month >= 3:
            sa_tax_year = f"{payment_date.year}/{payment_date.year + 1}"
        else:
            sa_tax_year = f"{payment_date.year - 1}/{payment_date.year}"

        # Create dividend record
        dividend = DividendIncome(
            id=uuid.uuid4(),
            holding_id=holding_id,
            payment_date=payment_date,
            ex_dividend_date=ex_dividend_date,
            dividend_per_share=dividend_per_share,
            total_dividend_gross=amount,
            withholding_tax=tax_withheld,
            total_dividend_net=net_dividend,
            currency=currency,
            source_country=country_of_source,
            uk_tax_year=uk_tax_year,
            sa_tax_year=sa_tax_year,
            created_at=datetime.utcnow()
        )

        self.db.add(dividend)
        await self.db.commit()
        await self.db.refresh(dividend)

        logger.info(
            f"Dividend recorded successfully: id={dividend.id}, "
            f"holding_id={holding_id}, net_amount={net_dividend}"
        )

        return dividend


# Create singleton instance factory
def get_portfolio_service(db: AsyncSession) -> PortfolioService:
    """
    Get portfolio service instance.

    Args:
        db: Database session

    Returns:
        PortfolioService instance
    """
    return PortfolioService(db)
