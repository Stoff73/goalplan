"""
Investment Tax Calculation Service.

This module provides tax calculation services for investment accounts:
- UK Capital Gains Tax (CGT) with annual exemption
- UK Dividend Tax with dividend allowance
- SA Capital Gains Tax (inclusion rate method)
- SA Dividend Withholding Tax

Business logic:
- ISA holdings are tax-free for both gains and dividends
- GIA holdings subject to UK CGT and dividend tax
- SA holdings subject to SA tax rules
- Tax year filtering for accurate annual calculations
- Annual allowances and exemptions applied
"""

from decimal import Decimal
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from models.investment import (
    InvestmentAccount,
    InvestmentHolding,
    DividendIncome,
    CapitalGainRealized,
    AccountType,
    AccountCountry,
)


class InvestmentTaxService:
    """Service for calculating investment-related taxes."""

    # UK Tax Constants (2024/25)
    UK_CGT_ANNUAL_EXEMPTION = Decimal('3000.00')
    UK_CGT_BASIC_RATE = Decimal('0.10')
    UK_CGT_HIGHER_RATE = Decimal('0.20')
    UK_DIVIDEND_ALLOWANCE = Decimal('500.00')
    UK_DIVIDEND_BASIC_RATE = Decimal('0.0875')
    UK_DIVIDEND_HIGHER_RATE = Decimal('0.3375')
    UK_DIVIDEND_ADDITIONAL_RATE = Decimal('0.3935')

    # SA Tax Constants (2024/25)
    SA_CGT_INCLUSION_RATE = Decimal('0.40')
    SA_CGT_MAX_MARGINAL_RATE = Decimal('0.45')
    SA_DIVIDEND_WITHHOLDING_RATE = Decimal('0.20')

    def __init__(self, db: AsyncSession):
        """
        Initialize the Investment Tax Service.

        Args:
            db: Database session
        """
        self.db = db

    async def calculate_cgt_uk(
        self,
        user_id: str,
        tax_year: str,
    ) -> Dict[str, Any]:
        """
        Calculate UK Capital Gains Tax for the tax year.

        For ISA accounts, gains are tax-free.
        For GIA accounts, apply UK CGT rules:
        - Annual exempt amount: £3,000 (2024/25)
        - Basic rate taxpayers: 10% on gains above exemption
        - Higher/additional rate: 20% on gains above exemption

        Args:
            user_id: User ID
            tax_year: Tax year (e.g., "2024/25")

        Returns:
            Dict with:
                - total_gains: Total realized gains
                - exempt_amount: Annual exempt amount used
                - taxable_gains: Gains above exemption
                - tax_rate: Tax rate applied
                - tax_owed: Total CGT owed
                - isa_gains_tax_free: Gains from ISA (tax-free)
        """
        # Get all UK investment accounts for user
        accounts_query = select(InvestmentAccount).where(
            and_(
                InvestmentAccount.user_id == user_id,
                InvestmentAccount.country == AccountCountry.UK,
                InvestmentAccount.deleted == False,
            )
        )
        result = await self.db.execute(accounts_query)
        accounts = result.scalars().all()

        if not accounts:
            return {
                'total_gains': Decimal('0.00'),
                'exempt_amount': Decimal('0.00'),
                'taxable_gains': Decimal('0.00'),
                'tax_rate': Decimal('0.00'),
                'tax_owed': Decimal('0.00'),
                'isa_gains_tax_free': Decimal('0.00'),
            }

        # Separate ISA and GIA gains
        isa_gains = Decimal('0.00')
        gia_gains = Decimal('0.00')

        for account in accounts:
            # Get realized gains for this account in the tax year
            gains_query = (
                select(func.coalesce(func.sum(CapitalGainRealized.gain_loss), 0))
                .join(InvestmentHolding, CapitalGainRealized.holding_id == InvestmentHolding.id)
                .where(
                    and_(
                        InvestmentHolding.account_id == account.id,
                        CapitalGainRealized.tax_year == tax_year,
                        CapitalGainRealized.country == AccountCountry.UK,
                    )
                )
            )
            result = await self.db.execute(gains_query)
            account_gains = Decimal(str(result.scalar() or 0))

            # Only count positive gains (losses don't contribute)
            if account_gains > 0:
                if account.account_type == AccountType.STOCKS_ISA:
                    isa_gains += account_gains
                elif account.account_type == AccountType.GIA:
                    gia_gains += account_gains

        # ISA gains are tax-free
        total_gains = isa_gains + gia_gains

        # Apply annual exempt amount to GIA gains only
        exempt_amount_used = min(gia_gains, self.UK_CGT_ANNUAL_EXEMPTION)
        taxable_gains = max(Decimal('0'), gia_gains - self.UK_CGT_ANNUAL_EXEMPTION)

        # Calculate tax (assume higher rate for simplicity - can be enhanced later)
        tax_rate = self.UK_CGT_HIGHER_RATE if taxable_gains > 0 else Decimal('0.00')
        tax_owed = (taxable_gains * tax_rate).quantize(Decimal('0.01'))

        return {
            'total_gains': total_gains.quantize(Decimal('0.01')),
            'exempt_amount': exempt_amount_used.quantize(Decimal('0.01')),
            'taxable_gains': taxable_gains.quantize(Decimal('0.01')),
            'tax_rate': tax_rate.quantize(Decimal('0.01')),
            'tax_owed': tax_owed,
            'isa_gains_tax_free': isa_gains.quantize(Decimal('0.01')),
        }

    async def calculate_dividend_tax_uk(
        self,
        user_id: str,
        tax_year: str,
    ) -> Dict[str, Any]:
        """
        Calculate UK Dividend Tax for the tax year.

        For ISA accounts, dividends are tax-free.
        For GIA accounts, apply UK dividend tax:
        - Dividend allowance: £500 (2024/25)
        - Basic rate: 8.75% on dividends above allowance
        - Higher rate: 33.75%
        - Additional rate: 39.35%

        Args:
            user_id: User ID
            tax_year: Tax year (e.g., "2024/25")

        Returns:
            Dict with:
                - total_dividends: Total dividend income
                - allowance: Dividend allowance used
                - taxable_dividends: Dividends above allowance
                - tax_rate: Tax rate applied
                - tax_owed: Total dividend tax owed
                - isa_dividends_tax_free: Dividends from ISA (tax-free)
        """
        # Get all UK investment accounts for user
        accounts_query = select(InvestmentAccount).where(
            and_(
                InvestmentAccount.user_id == user_id,
                InvestmentAccount.country == AccountCountry.UK,
                InvestmentAccount.deleted == False,
            )
        )
        result = await self.db.execute(accounts_query)
        accounts = result.scalars().all()

        if not accounts:
            return {
                'total_dividends': Decimal('0.00'),
                'allowance': Decimal('0.00'),
                'taxable_dividends': Decimal('0.00'),
                'tax_rate': Decimal('0.00'),
                'tax_owed': Decimal('0.00'),
                'isa_dividends_tax_free': Decimal('0.00'),
            }

        # Separate ISA and GIA dividends
        isa_dividends = Decimal('0.00')
        gia_dividends = Decimal('0.00')

        for account in accounts:
            # Get dividends for this account in the tax year
            dividends_query = (
                select(func.coalesce(func.sum(DividendIncome.total_dividend_gross), 0))
                .join(InvestmentHolding, DividendIncome.holding_id == InvestmentHolding.id)
                .where(
                    and_(
                        InvestmentHolding.account_id == account.id,
                        DividendIncome.uk_tax_year == tax_year,
                    )
                )
            )
            result = await self.db.execute(dividends_query)
            account_dividends = Decimal(str(result.scalar() or 0))

            if account.account_type == AccountType.STOCKS_ISA:
                isa_dividends += account_dividends
            elif account.account_type == AccountType.GIA:
                gia_dividends += account_dividends

        # ISA dividends are tax-free
        total_dividends = isa_dividends + gia_dividends

        # Apply dividend allowance to GIA dividends only
        allowance_used = min(gia_dividends, self.UK_DIVIDEND_ALLOWANCE)
        taxable_dividends = max(Decimal('0'), gia_dividends - self.UK_DIVIDEND_ALLOWANCE)

        # Calculate tax (assume basic rate for simplicity - can be enhanced later)
        tax_rate = self.UK_DIVIDEND_BASIC_RATE if taxable_dividends > 0 else Decimal('0.00')
        tax_owed = (taxable_dividends * tax_rate).quantize(Decimal('0.01'))

        return {
            'total_dividends': total_dividends.quantize(Decimal('0.01')),
            'allowance': allowance_used.quantize(Decimal('0.01')),
            'taxable_dividends': taxable_dividends.quantize(Decimal('0.01')),
            'tax_rate': tax_rate.quantize(Decimal('0.01')),
            'tax_owed': tax_owed,
            'isa_dividends_tax_free': isa_dividends.quantize(Decimal('0.01')),
        }

    async def calculate_cgt_sa(
        self,
        user_id: str,
        tax_year: str,
    ) -> Dict[str, Any]:
        """
        Calculate SA Capital Gains Tax for the tax year.

        SA CGT uses inclusion rate method:
        - 40% of capital gain is included in taxable income
        - Apply SA income tax rates to the included gain
        - For simplicity, assume max marginal rate of 45%
        - Formula: tax = (realized_gain * 0.40) * 0.45 = realized_gain * 0.18

        Args:
            user_id: User ID
            tax_year: Tax year (e.g., "2024/25")

        Returns:
            Dict with:
                - total_gains: Total realized gains
                - inclusion_rate: Inclusion rate (40%)
                - included_gain: Gain included in taxable income
                - tax_rate: Effective tax rate
                - tax_owed: Total CGT owed
        """
        # Get all SA investment accounts for user
        accounts_query = select(InvestmentAccount).where(
            and_(
                InvestmentAccount.user_id == user_id,
                InvestmentAccount.country == AccountCountry.SA,
                InvestmentAccount.deleted == False,
            )
        )
        result = await self.db.execute(accounts_query)
        accounts = result.scalars().all()

        if not accounts:
            return {
                'total_gains': Decimal('0.00'),
                'inclusion_rate': self.SA_CGT_INCLUSION_RATE,
                'included_gain': Decimal('0.00'),
                'tax_rate': Decimal('0.00'),
                'tax_owed': Decimal('0.00'),
            }

        # Get all realized gains from SA accounts
        total_gains = Decimal('0.00')

        for account in accounts:
            # Get realized gains for this account in the tax year
            gains_query = (
                select(func.coalesce(func.sum(CapitalGainRealized.gain_loss), 0))
                .join(InvestmentHolding, CapitalGainRealized.holding_id == InvestmentHolding.id)
                .where(
                    and_(
                        InvestmentHolding.account_id == account.id,
                        CapitalGainRealized.tax_year == tax_year,
                        CapitalGainRealized.country == AccountCountry.SA,
                    )
                )
            )
            result = await self.db.execute(gains_query)
            account_gains = Decimal(str(result.scalar() or 0))

            # Only count positive gains
            if account_gains > 0:
                total_gains += account_gains

        # Apply inclusion rate (40%)
        included_gain = total_gains * self.SA_CGT_INCLUSION_RATE

        # Calculate tax at max marginal rate (simplified)
        effective_tax_rate = self.SA_CGT_INCLUSION_RATE * self.SA_CGT_MAX_MARGINAL_RATE
        tax_owed = (total_gains * effective_tax_rate).quantize(Decimal('0.01'))

        return {
            'total_gains': total_gains.quantize(Decimal('0.01')),
            'inclusion_rate': self.SA_CGT_INCLUSION_RATE,
            'included_gain': included_gain.quantize(Decimal('0.01')),
            'tax_rate': effective_tax_rate.quantize(Decimal('0.01')),
            'tax_owed': tax_owed,
        }

    async def calculate_dividend_tax_sa(
        self,
        user_id: str,
        tax_year: str,
    ) -> Dict[str, Any]:
        """
        Calculate SA Dividend Withholding Tax for the tax year.

        SA Dividend Tax:
        - Dividend withholding tax: 20% (typically withheld at source)

        Args:
            user_id: User ID
            tax_year: Tax year (e.g., "2024/25")

        Returns:
            Dict with:
                - total_dividends: Total dividend income
                - withholding_rate: Withholding tax rate (20%)
                - tax_withheld: Total tax withheld
        """
        # Get all SA investment accounts for user
        accounts_query = select(InvestmentAccount).where(
            and_(
                InvestmentAccount.user_id == user_id,
                InvestmentAccount.country == AccountCountry.SA,
                InvestmentAccount.deleted == False,
            )
        )
        result = await self.db.execute(accounts_query)
        accounts = result.scalars().all()

        if not accounts:
            return {
                'total_dividends': Decimal('0.00'),
                'withholding_rate': self.SA_DIVIDEND_WITHHOLDING_RATE,
                'tax_withheld': Decimal('0.00'),
            }

        # Get all dividends from SA accounts
        total_dividends = Decimal('0.00')

        for account in accounts:
            # Get dividends for this account in the tax year
            dividends_query = (
                select(func.coalesce(func.sum(DividendIncome.total_dividend_gross), 0))
                .join(InvestmentHolding, DividendIncome.holding_id == InvestmentHolding.id)
                .where(
                    and_(
                        InvestmentHolding.account_id == account.id,
                        DividendIncome.sa_tax_year == tax_year,
                    )
                )
            )
            result = await self.db.execute(dividends_query)
            account_dividends = Decimal(str(result.scalar() or 0))
            total_dividends += account_dividends

        # Calculate withholding tax (20%)
        tax_withheld = (total_dividends * self.SA_DIVIDEND_WITHHOLDING_RATE).quantize(Decimal('0.01'))

        return {
            'total_dividends': total_dividends.quantize(Decimal('0.01')),
            'withholding_rate': self.SA_DIVIDEND_WITHHOLDING_RATE,
            'tax_withheld': tax_withheld,
        }
