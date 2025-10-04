"""
Tests for Investment Tax Service.

Test coverage:
- UK CGT calculation for GIA (with gains above exemption)
- UK CGT for ISA (should be 0 tax)
- UK CGT with gains below exemption (0 tax)
- UK dividend tax for GIA
- UK dividend tax for ISA (should be 0 tax)
- SA CGT with inclusion rate
- SA dividend withholding tax
- Edge cases: no gains/dividends, tax year filtering
"""

import pytest
from decimal import Decimal
from datetime import date, datetime
import uuid

from models.investment import (
    InvestmentAccount,
    InvestmentHolding,
    DividendIncome,
    CapitalGainRealized,
    AccountType,
    AccountCountry,
    SecurityType,
    AssetClass,
    Region,
    SourceCountry,
)
from services.investment.investment_tax_service import InvestmentTaxService


@pytest.fixture
async def uk_isa_account(db_session, test_user):
    """Create a UK ISA account for testing."""
    account = InvestmentAccount(
        id=uuid.uuid4(),
        user_id=test_user.id,
        account_type=AccountType.STOCKS_ISA,
        provider='Hargreaves Lansdown',
        account_number_encrypted='encrypted_isa_123',
        account_number_last_4='0123',
        country=AccountCountry.UK,
        base_currency='GBP',
        account_open_date=date(2020, 1, 1),
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)
    return account


@pytest.fixture
async def uk_gia_account(db_session, test_user):
    """Create a UK GIA account for testing."""
    account = InvestmentAccount(
        id=uuid.uuid4(),
        user_id=test_user.id,
        account_type=AccountType.GIA,
        provider='Interactive Investor',
        account_number_encrypted='encrypted_gia_456',
        account_number_last_4='0456',
        country=AccountCountry.UK,
        base_currency='GBP',
        account_open_date=date(2020, 1, 1),
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)
    return account


@pytest.fixture
async def sa_account(db_session, test_user):
    """Create a SA account for testing."""
    account = InvestmentAccount(
        id=uuid.uuid4(),
        user_id=test_user.id,
        account_type=AccountType.SA_UNIT_TRUST,
        provider='Allan Gray',
        account_number_encrypted='encrypted_sa_789',
        account_number_last_4='0789',
        country=AccountCountry.SA,
        base_currency='ZAR',
        account_open_date=date(2020, 1, 1),
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)
    return account


@pytest.fixture
async def isa_holding(db_session, uk_isa_account):
    """Create a holding in ISA account."""
    holding = InvestmentHolding(
        id=uuid.uuid4(),
        account_id=uk_isa_account.id,
        security_type=SecurityType.STOCK,
        ticker='VWRL',
        security_name='Vanguard FTSE All-World UCITS ETF',
        quantity=Decimal('100.0000'),
        purchase_date=date(2023, 1, 1),
        purchase_price=Decimal('85.00'),
        purchase_currency='GBP',
        current_price=Decimal('95.00'),
        asset_class=AssetClass.EQUITY,
        region=Region.GLOBAL,
        sector='ETF',
    )
    db_session.add(holding)
    await db_session.commit()
    await db_session.refresh(holding)
    return holding


@pytest.fixture
async def gia_holding(db_session, uk_gia_account):
    """Create a holding in GIA account."""
    holding = InvestmentHolding(
        id=uuid.uuid4(),
        account_id=uk_gia_account.id,
        security_type=SecurityType.STOCK,
        ticker='MSFT',
        security_name='Microsoft Corporation',
        quantity=Decimal('50.0000'),
        purchase_date=date(2023, 1, 1),
        purchase_price=Decimal('250.00'),
        purchase_currency='GBP',
        current_price=Decimal('350.00'),
        asset_class=AssetClass.EQUITY,
        region=Region.US,
        sector='Technology',
    )
    db_session.add(holding)
    await db_session.commit()
    await db_session.refresh(holding)
    return holding


@pytest.fixture
async def sa_holding(db_session, sa_account):
    """Create a holding in SA account."""
    holding = InvestmentHolding(
        id=uuid.uuid4(),
        account_id=sa_account.id,
        security_type=SecurityType.FUND,
        ticker='AGEGF',
        security_name='Allan Gray Equity Fund',
        quantity=Decimal('200.0000'),
        purchase_date=date(2023, 1, 1),
        purchase_price=Decimal('50.00'),
        purchase_currency='ZAR',
        current_price=Decimal('65.00'),
        asset_class=AssetClass.EQUITY,
        region=Region.EMERGING,
        sector='Fund',
    )
    db_session.add(holding)
    await db_session.commit()
    await db_session.refresh(holding)
    return holding


class TestUKCGT:
    """Test UK Capital Gains Tax calculations."""

    async def test_uk_cgt_gia_above_exemption(self, db_session, test_user, uk_gia_account, gia_holding):
        """Test UK CGT for GIA with gains above exemption."""
        # Create a realized gain of £5,000
        gain = CapitalGainRealized(
            id=uuid.uuid4(),
            holding_id=gia_holding.id,
            disposal_date=date(2024, 6, 1),
            quantity_sold=Decimal('50.0000'),
            sale_price=Decimal('350.00'),
            sale_value=Decimal('17500.00'),
            cost_basis=Decimal('12500.00'),
            gain_loss=Decimal('5000.00'),
            tax_year='2024/25',
            country=AccountCountry.UK,
        )
        db_session.add(gain)
        await db_session.commit()

        # Calculate CGT
        service = InvestmentTaxService(db_session)
        result = await service.calculate_cgt_uk(str(test_user.id), '2024/25')

        # Verify results
        assert result['total_gains'] == Decimal('5000.00')
        assert result['exempt_amount'] == Decimal('3000.00')  # Annual exemption
        assert result['taxable_gains'] == Decimal('2000.00')  # 5000 - 3000
        assert result['tax_rate'] == Decimal('0.20')  # Higher rate
        assert result['tax_owed'] == Decimal('400.00')  # 2000 * 0.20
        assert result['isa_gains_tax_free'] == Decimal('0.00')

    async def test_uk_cgt_isa_tax_free(self, db_session, test_user, uk_isa_account, isa_holding):
        """Test UK CGT for ISA - should be tax-free."""
        # Create a realized gain in ISA
        gain = CapitalGainRealized(
            id=uuid.uuid4(),
            holding_id=isa_holding.id,
            disposal_date=date(2024, 6, 1),
            quantity_sold=Decimal('100.0000'),
            sale_price=Decimal('95.00'),
            sale_value=Decimal('9500.00'),
            cost_basis=Decimal('8500.00'),
            gain_loss=Decimal('1000.00'),
            tax_year='2024/25',
            country=AccountCountry.UK,
        )
        db_session.add(gain)
        await db_session.commit()

        # Calculate CGT
        service = InvestmentTaxService(db_session)
        result = await service.calculate_cgt_uk(str(test_user.id), '2024/25')

        # Verify results - ISA gains are tax-free
        assert result['total_gains'] == Decimal('1000.00')
        assert result['exempt_amount'] == Decimal('0.00')  # No exemption used
        assert result['taxable_gains'] == Decimal('0.00')  # ISA is tax-free
        assert result['tax_rate'] == Decimal('0.00')
        assert result['tax_owed'] == Decimal('0.00')
        assert result['isa_gains_tax_free'] == Decimal('1000.00')

    async def test_uk_cgt_below_exemption(self, db_session, test_user, uk_gia_account, gia_holding):
        """Test UK CGT with gains below exemption - should be 0 tax."""
        # Create a realized gain of £2,000 (below £3,000 exemption)
        gain = CapitalGainRealized(
            id=uuid.uuid4(),
            holding_id=gia_holding.id,
            disposal_date=date(2024, 6, 1),
            quantity_sold=Decimal('20.0000'),
            sale_price=Decimal('350.00'),
            sale_value=Decimal('7000.00'),
            cost_basis=Decimal('5000.00'),
            gain_loss=Decimal('2000.00'),
            tax_year='2024/25',
            country=AccountCountry.UK,
        )
        db_session.add(gain)
        await db_session.commit()

        # Calculate CGT
        service = InvestmentTaxService(db_session)
        result = await service.calculate_cgt_uk(str(test_user.id), '2024/25')

        # Verify results
        assert result['total_gains'] == Decimal('2000.00')
        assert result['exempt_amount'] == Decimal('2000.00')  # Full exemption used
        assert result['taxable_gains'] == Decimal('0.00')  # Below exemption
        assert result['tax_rate'] == Decimal('0.00')
        assert result['tax_owed'] == Decimal('0.00')
        assert result['isa_gains_tax_free'] == Decimal('0.00')

    async def test_uk_cgt_no_gains(self, db_session, test_user):
        """Test UK CGT with no gains - should return 0."""
        service = InvestmentTaxService(db_session)
        result = await service.calculate_cgt_uk(str(test_user.id), '2024/25')

        # Verify results
        assert result['total_gains'] == Decimal('0.00')
        assert result['exempt_amount'] == Decimal('0.00')
        assert result['taxable_gains'] == Decimal('0.00')
        assert result['tax_rate'] == Decimal('0.00')
        assert result['tax_owed'] == Decimal('0.00')
        assert result['isa_gains_tax_free'] == Decimal('0.00')

    async def test_uk_cgt_tax_year_filtering(
        self, db_session, test_user, uk_gia_account, gia_holding
    ):
        """Test UK CGT tax year filtering."""
        # Create gains in two different tax years
        gain_2024 = CapitalGainRealized(
            id=uuid.uuid4(),
            holding_id=gia_holding.id,
            disposal_date=date(2024, 6, 1),
            quantity_sold=Decimal('25.0000'),
            sale_price=Decimal('350.00'),
            sale_value=Decimal('8750.00'),
            cost_basis=Decimal('6250.00'),
            gain_loss=Decimal('2500.00'),
            tax_year='2024/25',
            country=AccountCountry.UK,
        )
        gain_2023 = CapitalGainRealized(
            id=uuid.uuid4(),
            holding_id=gia_holding.id,
            disposal_date=date(2023, 6, 1),
            quantity_sold=Decimal('25.0000'),
            sale_price=Decimal('300.00'),
            sale_value=Decimal('7500.00'),
            cost_basis=Decimal('6250.00'),
            gain_loss=Decimal('1250.00'),
            tax_year='2023/24',
            country=AccountCountry.UK,
        )
        db_session.add_all([gain_2024, gain_2023])
        await db_session.commit()

        # Calculate CGT for 2024/25 only
        service = InvestmentTaxService(db_session)
        result = await service.calculate_cgt_uk(str(test_user.id), '2024/25')

        # Verify only 2024/25 gains are included
        assert result['total_gains'] == Decimal('2500.00')
        assert result['exempt_amount'] == Decimal('2500.00')
        assert result['taxable_gains'] == Decimal('0.00')


class TestUKDividendTax:
    """Test UK Dividend Tax calculations."""

    async def test_uk_dividend_tax_gia(self, db_session, test_user, uk_gia_account, gia_holding):
        """Test UK dividend tax for GIA."""
        # Create dividends totaling £1,500
        dividend = DividendIncome(
            id=uuid.uuid4(),
            holding_id=gia_holding.id,
            payment_date=date(2024, 6, 1),
            dividend_per_share=Decimal('30.00'),
            total_dividend_gross=Decimal('1500.00'),
            withholding_tax=Decimal('0.00'),
            total_dividend_net=Decimal('1500.00'),
            currency='GBP',
            source_country=SourceCountry.UK,
            uk_tax_year='2024/25',
        )
        db_session.add(dividend)
        await db_session.commit()

        # Calculate dividend tax
        service = InvestmentTaxService(db_session)
        result = await service.calculate_dividend_tax_uk(str(test_user.id), '2024/25')

        # Verify results
        assert result['total_dividends'] == Decimal('1500.00')
        assert result['allowance'] == Decimal('500.00')  # Dividend allowance
        assert result['taxable_dividends'] == Decimal('1000.00')  # 1500 - 500
        assert result['tax_rate'] == Decimal('0.09')  # Basic rate (8.75% rounded)
        assert result['tax_owed'] == Decimal('87.50')  # 1000 * 0.0875
        assert result['isa_dividends_tax_free'] == Decimal('0.00')

    async def test_uk_dividend_tax_isa_tax_free(
        self, db_session, test_user, uk_isa_account, isa_holding
    ):
        """Test UK dividend tax for ISA - should be tax-free."""
        # Create dividends in ISA
        dividend = DividendIncome(
            id=uuid.uuid4(),
            holding_id=isa_holding.id,
            payment_date=date(2024, 6, 1),
            dividend_per_share=Decimal('10.00'),
            total_dividend_gross=Decimal('1000.00'),
            withholding_tax=Decimal('0.00'),
            total_dividend_net=Decimal('1000.00'),
            currency='GBP',
            source_country=SourceCountry.UK,
            uk_tax_year='2024/25',
        )
        db_session.add(dividend)
        await db_session.commit()

        # Calculate dividend tax
        service = InvestmentTaxService(db_session)
        result = await service.calculate_dividend_tax_uk(str(test_user.id), '2024/25')

        # Verify results - ISA dividends are tax-free
        assert result['total_dividends'] == Decimal('1000.00')
        assert result['allowance'] == Decimal('0.00')  # No allowance used
        assert result['taxable_dividends'] == Decimal('0.00')  # ISA is tax-free
        assert result['tax_rate'] == Decimal('0.00')
        assert result['tax_owed'] == Decimal('0.00')
        assert result['isa_dividends_tax_free'] == Decimal('1000.00')

    async def test_uk_dividend_tax_below_allowance(
        self, db_session, test_user, uk_gia_account, gia_holding
    ):
        """Test UK dividend tax with dividends below allowance."""
        # Create dividends of £400 (below £500 allowance)
        dividend = DividendIncome(
            id=uuid.uuid4(),
            holding_id=gia_holding.id,
            payment_date=date(2024, 6, 1),
            dividend_per_share=Decimal('8.00'),
            total_dividend_gross=Decimal('400.00'),
            withholding_tax=Decimal('0.00'),
            total_dividend_net=Decimal('400.00'),
            currency='GBP',
            source_country=SourceCountry.UK,
            uk_tax_year='2024/25',
        )
        db_session.add(dividend)
        await db_session.commit()

        # Calculate dividend tax
        service = InvestmentTaxService(db_session)
        result = await service.calculate_dividend_tax_uk(str(test_user.id), '2024/25')

        # Verify results
        assert result['total_dividends'] == Decimal('400.00')
        assert result['allowance'] == Decimal('400.00')  # Full allowance used
        assert result['taxable_dividends'] == Decimal('0.00')  # Below allowance
        assert result['tax_rate'] == Decimal('0.00')
        assert result['tax_owed'] == Decimal('0.00')

    async def test_uk_dividend_tax_no_dividends(self, db_session, test_user):
        """Test UK dividend tax with no dividends."""
        service = InvestmentTaxService(db_session)
        result = await service.calculate_dividend_tax_uk(str(test_user.id), '2024/25')

        # Verify results
        assert result['total_dividends'] == Decimal('0.00')
        assert result['allowance'] == Decimal('0.00')
        assert result['taxable_dividends'] == Decimal('0.00')
        assert result['tax_rate'] == Decimal('0.00')
        assert result['tax_owed'] == Decimal('0.00')


class TestSACGT:
    """Test SA Capital Gains Tax calculations."""

    async def test_sa_cgt_inclusion_rate(self, db_session, test_user, sa_account, sa_holding):
        """Test SA CGT with inclusion rate method."""
        # Create a realized gain of R10,000
        gain = CapitalGainRealized(
            id=uuid.uuid4(),
            holding_id=sa_holding.id,
            disposal_date=date(2024, 6, 1),
            quantity_sold=Decimal('200.0000'),
            sale_price=Decimal('65.00'),
            sale_value=Decimal('13000.00'),
            cost_basis=Decimal('10000.00'),
            gain_loss=Decimal('3000.00'),
            tax_year='2024/25',
            country=AccountCountry.SA,
        )
        db_session.add(gain)
        await db_session.commit()

        # Calculate SA CGT
        service = InvestmentTaxService(db_session)
        result = await service.calculate_cgt_sa(str(test_user.id), '2024/25')

        # Verify results
        # 40% inclusion rate * 45% marginal rate = 18% effective rate
        assert result['total_gains'] == Decimal('3000.00')
        assert result['inclusion_rate'] == Decimal('0.40')
        assert result['included_gain'] == Decimal('1200.00')  # 3000 * 0.40
        assert result['tax_rate'] == Decimal('0.18')  # 0.40 * 0.45
        assert result['tax_owed'] == Decimal('540.00')  # 3000 * 0.18

    async def test_sa_cgt_no_gains(self, db_session, test_user):
        """Test SA CGT with no gains."""
        service = InvestmentTaxService(db_session)
        result = await service.calculate_cgt_sa(str(test_user.id), '2024/25')

        # Verify results
        assert result['total_gains'] == Decimal('0.00')
        assert result['inclusion_rate'] == Decimal('0.40')
        assert result['included_gain'] == Decimal('0.00')
        assert result['tax_rate'] == Decimal('0.00')
        assert result['tax_owed'] == Decimal('0.00')

    async def test_sa_cgt_tax_year_filtering(self, db_session, test_user, sa_account, sa_holding):
        """Test SA CGT tax year filtering."""
        # Create gains in two different tax years
        gain_2024 = CapitalGainRealized(
            id=uuid.uuid4(),
            holding_id=sa_holding.id,
            disposal_date=date(2024, 6, 1),
            quantity_sold=Decimal('100.0000'),
            sale_price=Decimal('65.00'),
            sale_value=Decimal('6500.00'),
            cost_basis=Decimal('5000.00'),
            gain_loss=Decimal('1500.00'),
            tax_year='2024/25',
            country=AccountCountry.SA,
        )
        gain_2023 = CapitalGainRealized(
            id=uuid.uuid4(),
            holding_id=sa_holding.id,
            disposal_date=date(2023, 6, 1),
            quantity_sold=Decimal('100.0000'),
            sale_price=Decimal('60.00'),
            sale_value=Decimal('6000.00'),
            cost_basis=Decimal('5000.00'),
            gain_loss=Decimal('1000.00'),
            tax_year='2023/24',
            country=AccountCountry.SA,
        )
        db_session.add_all([gain_2024, gain_2023])
        await db_session.commit()

        # Calculate SA CGT for 2024/25 only
        service = InvestmentTaxService(db_session)
        result = await service.calculate_cgt_sa(str(test_user.id), '2024/25')

        # Verify only 2024/25 gains are included
        assert result['total_gains'] == Decimal('1500.00')
        assert result['tax_owed'] == Decimal('270.00')  # 1500 * 0.18


class TestSADividendTax:
    """Test SA Dividend Withholding Tax calculations."""

    async def test_sa_dividend_withholding_tax(self, db_session, test_user, sa_account, sa_holding):
        """Test SA dividend withholding tax."""
        # Create dividends totaling R5,000
        dividend = DividendIncome(
            id=uuid.uuid4(),
            holding_id=sa_holding.id,
            payment_date=date(2024, 6, 1),
            dividend_per_share=Decimal('25.00'),
            total_dividend_gross=Decimal('5000.00'),
            withholding_tax=Decimal('1000.00'),  # 20% withheld
            total_dividend_net=Decimal('4000.00'),
            currency='ZAR',
            source_country=SourceCountry.SA,
            sa_tax_year='2024/2025',
        )
        db_session.add(dividend)
        await db_session.commit()

        # Calculate SA dividend tax
        service = InvestmentTaxService(db_session)
        result = await service.calculate_dividend_tax_sa(str(test_user.id), '2024/2025')

        # Verify results
        assert result['total_dividends'] == Decimal('5000.00')
        assert result['withholding_rate'] == Decimal('0.20')
        assert result['tax_withheld'] == Decimal('1000.00')  # 5000 * 0.20

    async def test_sa_dividend_tax_no_dividends(self, db_session, test_user):
        """Test SA dividend tax with no dividends."""
        service = InvestmentTaxService(db_session)
        result = await service.calculate_dividend_tax_sa(str(test_user.id), '2024/2025')

        # Verify results
        assert result['total_dividends'] == Decimal('0.00')
        assert result['withholding_rate'] == Decimal('0.20')
        assert result['tax_withheld'] == Decimal('0.00')

    async def test_sa_dividend_tax_year_filtering(
        self, db_session, test_user, sa_account, sa_holding
    ):
        """Test SA dividend tax year filtering."""
        # Create dividends in two different tax years
        dividend_2024 = DividendIncome(
            id=uuid.uuid4(),
            holding_id=sa_holding.id,
            payment_date=date(2024, 6, 1),
            dividend_per_share=Decimal('15.00'),
            total_dividend_gross=Decimal('3000.00'),
            withholding_tax=Decimal('600.00'),
            total_dividend_net=Decimal('2400.00'),
            currency='ZAR',
            source_country=SourceCountry.SA,
            sa_tax_year='2024/2025',
        )
        dividend_2023 = DividendIncome(
            id=uuid.uuid4(),
            holding_id=sa_holding.id,
            payment_date=date(2023, 6, 1),
            dividend_per_share=Decimal('10.00'),
            total_dividend_gross=Decimal('2000.00'),
            withholding_tax=Decimal('400.00'),
            total_dividend_net=Decimal('1600.00'),
            currency='ZAR',
            source_country=SourceCountry.SA,
            sa_tax_year='2023/2024',
        )
        db_session.add_all([dividend_2024, dividend_2023])
        await db_session.commit()

        # Calculate SA dividend tax for 2024/2025 only
        service = InvestmentTaxService(db_session)
        result = await service.calculate_dividend_tax_sa(str(test_user.id), '2024/2025')

        # Verify only 2024/2025 dividends are included
        assert result['total_dividends'] == Decimal('3000.00')
        assert result['tax_withheld'] == Decimal('600.00')


class TestMixedAccounts:
    """Test calculations with mixed account types."""

    async def test_uk_cgt_isa_and_gia(
        self, db_session, test_user, uk_isa_account, uk_gia_account, isa_holding, gia_holding
    ):
        """Test UK CGT with both ISA and GIA gains."""
        # Create gains in both ISA and GIA
        isa_gain = CapitalGainRealized(
            id=uuid.uuid4(),
            holding_id=isa_holding.id,
            disposal_date=date(2024, 6, 1),
            quantity_sold=Decimal('50.0000'),
            sale_price=Decimal('95.00'),
            sale_value=Decimal('4750.00'),
            cost_basis=Decimal('4250.00'),
            gain_loss=Decimal('500.00'),
            tax_year='2024/25',
            country=AccountCountry.UK,
        )
        gia_gain = CapitalGainRealized(
            id=uuid.uuid4(),
            holding_id=gia_holding.id,
            disposal_date=date(2024, 6, 1),
            quantity_sold=Decimal('30.0000'),
            sale_price=Decimal('350.00'),
            sale_value=Decimal('10500.00'),
            cost_basis=Decimal('7500.00'),
            gain_loss=Decimal('3000.00'),
            tax_year='2024/25',
            country=AccountCountry.UK,
        )
        db_session.add_all([isa_gain, gia_gain])
        await db_session.commit()

        # Calculate UK CGT
        service = InvestmentTaxService(db_session)
        result = await service.calculate_cgt_uk(str(test_user.id), '2024/25')

        # Verify results
        assert result['total_gains'] == Decimal('3500.00')  # 500 + 3000
        assert result['isa_gains_tax_free'] == Decimal('500.00')
        assert result['exempt_amount'] == Decimal('3000.00')  # Applied to GIA only
        assert result['taxable_gains'] == Decimal('0.00')  # GIA gain exactly equals exemption
        assert result['tax_owed'] == Decimal('0.00')

    async def test_uk_dividend_tax_isa_and_gia(
        self, db_session, test_user, uk_isa_account, uk_gia_account, isa_holding, gia_holding
    ):
        """Test UK dividend tax with both ISA and GIA dividends."""
        # Create dividends in both ISA and GIA
        isa_dividend = DividendIncome(
            id=uuid.uuid4(),
            holding_id=isa_holding.id,
            payment_date=date(2024, 6, 1),
            dividend_per_share=Decimal('5.00'),
            total_dividend_gross=Decimal('500.00'),
            withholding_tax=Decimal('0.00'),
            total_dividend_net=Decimal('500.00'),
            currency='GBP',
            source_country=SourceCountry.UK,
            uk_tax_year='2024/25',
        )
        gia_dividend = DividendIncome(
            id=uuid.uuid4(),
            holding_id=gia_holding.id,
            payment_date=date(2024, 6, 1),
            dividend_per_share=Decimal('20.00'),
            total_dividend_gross=Decimal('1000.00'),
            withholding_tax=Decimal('0.00'),
            total_dividend_net=Decimal('1000.00'),
            currency='GBP',
            source_country=SourceCountry.UK,
            uk_tax_year='2024/25',
        )
        db_session.add_all([isa_dividend, gia_dividend])
        await db_session.commit()

        # Calculate UK dividend tax
        service = InvestmentTaxService(db_session)
        result = await service.calculate_dividend_tax_uk(str(test_user.id), '2024/25')

        # Verify results
        assert result['total_dividends'] == Decimal('1500.00')  # 500 + 1000
        assert result['isa_dividends_tax_free'] == Decimal('500.00')
        assert result['allowance'] == Decimal('500.00')  # Applied to GIA only
        assert result['taxable_dividends'] == Decimal('500.00')  # 1000 - 500
        assert result['tax_owed'] == Decimal('43.75')  # 500 * 0.0875
