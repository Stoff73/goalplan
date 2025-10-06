"""
Populate demo user with comprehensive mock data.

This script creates a demo user account with realistic mock data across all modules:
- User account and profile
- Tax status and domicile
- Income records
- Savings accounts (ISA, TFSA, regular accounts)
- Investments (Stocks & Shares ISA, Offshore bond)
- Retirement accounts (UK pensions, QROPS, SA retirement annuity)
- Life insurance protection
- Assets and liabilities

Run from backend directory:
    python populate_demo_data.py
"""

import asyncio
import sys
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from argon2 import PasswordHasher

# Import all models
from models.user import User, UserStatus, CountryPreference
from models.tax_status import (
    UserTaxStatus, UKDomicileStatus, UKSRTData, SAPresenceData
)
from models.income import (
    UserIncome, IncomeTaxWithholding, IncomeType, IncomeFrequency, Currency
)
from models.savings_account import (
    SavingsAccount, AccountType, AccountCountry, AccountPurpose, InterestFrequency,
    ISAContribution, TFSAContribution
)
from models.investment import (
    InvestmentAccount, InvestmentHolding, AccountType as InvAccountType,
    AccountCountry as InvAccountCountry, SecurityType, AssetClass, Region
)
from models.retirement import (
    UKPension, PensionType, PensionStatus, UKPensionContribution,
    ContributionFrequency, TaxReliefMethod, StatePensionForecast,
    SARetirementFund, SAFundType, SAFundStatus, SAFundContribution,
    InvestmentStrategy
)
from models.life_assurance import (
    LifeAssurancePolicy, PolicyBeneficiary, ProviderCountry, PolicyType,
    PremiumFrequency, BeneficiaryRelationship, PolicyStatus
)
from models.estate_iht import EstateAsset, EstateLiability, AssetType, LiabilityType
from database import get_db
from config import settings


# Password hasher
ph = PasswordHasher()


async def create_demo_user(db: AsyncSession):
    """Create demo user account."""
    print("Creating demo user account...")

    # Check if user already exists
    from sqlalchemy import select
    result = await db.execute(
        select(User).where(User.email == "demo@goalplan.com")
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        print("  ⚠️  Demo user already exists. Deleting and recreating...")
        await db.delete(existing_user)
        await db.commit()

    # Create user
    user = User(
        email="demo@goalplan.com",
        password_hash=ph.hash("Demo123!"),
        first_name="John",
        last_name="Smith",
        country_preference=CountryPreference.BOTH,
        status=UserStatus.ACTIVE,
        email_verified=True,
        terms_accepted_at=datetime.utcnow(),
        marketing_consent=False,
        date_of_birth=date(1980, 5, 15),  # 44 years old
        phone="+44 7700 900123",
        address={
            "line1": "123 High Street",
            "line2": "",
            "city": "London",
            "postcode": "SW1A 1AA",
            "country": "UK"
        },
        timezone="Europe/London"
    )

    db.add(user)
    await db.flush()  # Get user.id
    print(f"  ✓ Created user: {user.email} (ID: {user.id})")

    return user


async def create_tax_status(db: AsyncSession, user: User):
    """Create tax status and domicile records."""
    print("\nCreating tax status records...")

    # Current tax status
    tax_status = UserTaxStatus(
        user_id=user.id,
        effective_from=date(2020, 1, 1),
        effective_to=None,  # Current
        uk_tax_resident=True,
        uk_domicile=UKDomicileStatus.NON_UK_DOMICILE,  # Born in SA
        uk_deemed_domicile_date=None,
        uk_split_year_treatment=False,
        uk_remittance_basis=False,
        sa_tax_resident=False,  # Not currently SA resident
        sa_ordinarily_resident=False,
        dual_resident=False,
        dta_tie_breaker_country=None
    )
    db.add(tax_status)
    print(f"  ✓ Tax Status: UK resident, SA-born (non-UK domicile)")

    # UK SRT data for current tax year
    uk_srt = UKSRTData(
        user_id=user.id,
        tax_year="2024/25",
        days_in_uk=320,  # Well over 183 days threshold
        family_tie=True,  # Wife and kids in UK
        accommodation_tie=True,  # Has UK home
        work_tie=True,  # Works in UK
        ninety_day_tie=True,
        country_tie=True,
        tax_resident=True,
        test_result="automatic_uk"
    )
    db.add(uk_srt)
    print(f"  ✓ UK SRT 2024/25: {uk_srt.days_in_uk} days, resident (automatic UK test)")

    # SA presence data
    sa_presence = SAPresenceData(
        user_id=user.id,
        tax_year="2024/25",
        days_in_sa=25,  # Visits SA occasionally
        year_minus_1_days=30,
        year_minus_2_days=20,
        year_minus_3_days=28,
        year_minus_4_days=22,
        tax_resident=False,  # < 91 days
        ordinarily_resident=False,
        test_result="non_resident",
        five_year_average=Decimal("25.00")
    )
    db.add(sa_presence)
    print(f"  ✓ SA Presence 2024/25: {sa_presence.days_in_sa} days, non-resident")


async def create_income_records(db: AsyncSession, user: User):
    """Create income records."""
    print("\nCreating income records...")

    # UK Employment income - £140,000/year
    uk_employment = UserIncome(
        user_id=user.id,
        income_type=IncomeType.EMPLOYMENT,
        source_country="UK",
        description="Senior Software Engineer",
        employer_name="Tech Solutions Ltd",
        amount=Decimal("140000.00"),
        currency=Currency.GBP,
        amount_in_gbp=Decimal("140000.00"),
        amount_in_zar=Decimal("3360000.00"),  # ~24 ZAR/GBP
        exchange_rate=Decimal("24.00"),
        exchange_rate_date=date.today(),
        frequency=IncomeFrequency.ANNUAL,
        tax_year_uk="2024/25",
        tax_year_sa=None,
        income_date=date(2024, 4, 6),
        is_gross=True,
        tax_withheld_amount=Decimal("42000.00"),  # ~30% PAYE
        tax_withheld_currency=Currency.GBP,
        is_foreign_income=False,
        foreign_tax_credit=None,
        dta_applicable=False
    )
    db.add(uk_employment)
    print(f"  ✓ UK Employment: £{uk_employment.amount:,.2f}/year ({uk_employment.employer_name})")

    # SA Rental income - R15,000/month (£625/month)
    sa_rental = UserIncome(
        user_id=user.id,
        income_type=IncomeType.RENTAL,
        source_country="ZA",
        description="Rental property in Cape Town",
        employer_name=None,
        amount=Decimal("15000.00"),
        currency=Currency.ZAR,
        amount_in_gbp=Decimal("625.00"),  # 15000 / 24
        amount_in_zar=Decimal("15000.00"),
        exchange_rate=Decimal("24.00"),
        exchange_rate_date=date.today(),
        frequency=IncomeFrequency.MONTHLY,
        tax_year_uk="2024/25",
        tax_year_sa="2024/2025",
        income_date=date(2024, 1, 1),
        is_gross=True,
        tax_withheld_amount=None,
        tax_withheld_currency=None,
        is_foreign_income=True,
        foreign_tax_credit=None,
        dta_applicable=True
    )
    db.add(sa_rental)
    print(f"  ✓ SA Rental: R{sa_rental.amount:,.2f}/month (Cape Town property)")

    # Flush income records
    await db.flush()


async def create_savings_accounts(db: AsyncSession, user: User):
    """Create savings accounts."""
    print("\nCreating savings accounts...")

    # UK Current Account
    uk_current = SavingsAccount(
        user_id=user.id,
        bank_name="Barclays",
        account_name="Current Account",
        account_number_encrypted="encrypted_12345678",  # Mock encrypted
        account_type=AccountType.CURRENT.value,
        currency=Currency.GBP,
        current_balance=Decimal("8500.00"),
        interest_rate=Decimal("0.50"),
        interest_payment_frequency=InterestFrequency.MONTHLY.value,
        is_isa=False,
        is_tfsa=False,
        purpose=AccountPurpose.GENERAL.value,
        country=AccountCountry.UK.value,
        is_active=True
    )
    db.add(uk_current)
    print(f"  ✓ {uk_current.bank_name} {uk_current.account_type}: £{uk_current.current_balance:,.2f}")

    # UK Cash ISA
    uk_cash_isa = SavingsAccount(
        user_id=user.id,
        bank_name="Nationwide",
        account_name="Cash ISA",
        account_number_encrypted="encrypted_87654321",
        account_type=AccountType.ISA.value,
        currency=Currency.GBP,
        current_balance=Decimal("35000.00"),
        interest_rate=Decimal("4.25"),
        interest_payment_frequency=InterestFrequency.ANNUALLY.value,
        is_isa=True,
        is_tfsa=False,
        purpose=AccountPurpose.SAVINGS_GOAL.value,
        country=AccountCountry.UK.value,
        is_active=True
    )
    db.add(uk_cash_isa)
    print(f"  ✓ {uk_cash_isa.bank_name} {uk_cash_isa.account_name}: £{uk_cash_isa.current_balance:,.2f} @{uk_cash_isa.interest_rate}%")

    # ISA Contribution for current year
    isa_contribution = ISAContribution(
        user_id=user.id,
        savings_account_id=None,  # Will be set after flush
        tax_year="2024/25",
        contribution_amount=Decimal("15000.00"),
        contribution_date=date(2024, 6, 1),
        notes="Regular savings contributions"
    )
    db.add(isa_contribution)
    await db.flush()
    isa_contribution.savings_account_id = uk_cash_isa.id
    print(f"  ✓ ISA Contribution 2024/25: £{isa_contribution.contribution_amount:,.2f}")

    # SA Savings Account
    sa_savings = SavingsAccount(
        user_id=user.id,
        bank_name="Standard Bank SA",
        account_name="Savings Account",
        account_number_encrypted="encrypted_11223344",
        account_type=AccountType.SAVINGS.value,
        currency=Currency.ZAR,
        current_balance=Decimal("180000.00"),
        interest_rate=Decimal("6.50"),
        interest_payment_frequency=InterestFrequency.MONTHLY.value,
        is_isa=False,
        is_tfsa=False,
        purpose=AccountPurpose.EMERGENCY_FUND.value,
        country=AccountCountry.SA.value,
        is_active=True
    )
    db.add(sa_savings)
    print(f"  ✓ {sa_savings.bank_name}: R{sa_savings.current_balance:,.2f} @{sa_savings.interest_rate}%")


async def create_investments(db: AsyncSession, user: User):
    """Create investment accounts and holdings."""
    print("\nCreating investment accounts...")

    # Stocks & Shares ISA
    stocks_isa_account = InvestmentAccount(
        user_id=user.id,
        account_type=InvAccountType.STOCKS_ISA.value,
        provider="Hargreaves Lansdown",
        account_number_encrypted="encrypted_isa123",
        account_number_last_4="0123",
        country=InvAccountCountry.UK.value,
        base_currency="GBP",
        account_open_date=date(2018, 1, 15),
        status="ACTIVE",
        deleted=False
    )
    db.add(stocks_isa_account)
    await db.flush()
    print(f"  ✓ Investment Account: {stocks_isa_account.provider} {stocks_isa_account.account_type}")

    # Holdings in Stocks & Shares ISA
    holdings = [
        {
            "security_name": "Vanguard FTSE Global All Cap Index Fund",
            "ticker": "VWRP",
            "isin": "IE00BK5BQT80",
            "security_type": SecurityType.ETF,
            "quantity": Decimal("1250.5000"),
            "purchase_price": Decimal("85.50"),
            "current_price": Decimal("112.30"),
            "asset_class": AssetClass.EQUITY,
            "region": Region.GLOBAL
        },
        {
            "security_name": "iShares UK Gilts UCITS ETF",
            "ticker": "IGLT",
            "isin": "IE00B1FZSC47",
            "security_type": SecurityType.ETF,
            "quantity": Decimal("850.0000"),
            "purchase_price": Decimal("12.25"),
            "current_price": Decimal("11.85"),
            "asset_class": AssetClass.FIXED_INCOME,
            "region": Region.UK
        }
    ]

    for h in holdings:
        holding = InvestmentHolding(
            account_id=stocks_isa_account.id,
            security_type=h["security_type"],
            ticker=h["ticker"],
            isin=h["isin"],
            security_name=h["security_name"],
            quantity=h["quantity"],
            purchase_date=date(2020, 3, 15),
            purchase_price=h["purchase_price"],
            purchase_currency="GBP",
            current_price=h["current_price"],
            asset_class=h["asset_class"],
            region=h["region"],
            sector="Diversified" if h["asset_class"] == AssetClass.EQUITY else "Fixed Income",
            last_price_update=datetime.utcnow(),
            deleted=False
        )
        db.add(holding)
        current_value = holding.current_value
        print(f"    • {h['security_name']}: {h['quantity']} units @ £{h['current_price']} = £{current_value:,.2f}")

    # Offshore Bond
    offshore_bond_account = InvestmentAccount(
        user_id=user.id,
        account_type=InvAccountType.OFFSHORE_BOND.value,
        provider="Old Mutual International",
        account_number_encrypted="encrypted_bond789",
        account_number_last_4="0789",
        country=InvAccountCountry.OFFSHORE.value,
        base_currency="GBP",
        account_open_date=date(2019, 6, 1),
        status="ACTIVE",
        deleted=False
    )
    db.add(offshore_bond_account)
    await db.flush()
    print(f"  ✓ Investment Account: {offshore_bond_account.provider} {offshore_bond_account.account_type}")

    offshore_holding = InvestmentHolding(
        account_id=offshore_bond_account.id,
        security_type=SecurityType.FUND,
        ticker=None,
        isin=None,
        security_name="Multi-Asset Balanced Portfolio",
        quantity=Decimal("1.0000"),
        purchase_date=date(2019, 6, 1),
        purchase_price=Decimal("75000.00"),
        purchase_currency="GBP",
        current_price=Decimal("95500.00"),
        asset_class=AssetClass.EQUITY,
        region=Region.GLOBAL,
        sector="Multi-Asset",
        last_price_update=datetime.utcnow(),
        deleted=False
    )
    db.add(offshore_holding)
    print(f"    • {offshore_holding.security_name}: £{offshore_holding.current_price:,.2f}")


async def create_retirement_accounts(db: AsyncSession, user: User):
    """Create retirement accounts."""
    print("\nCreating retirement accounts...")

    # UK Occupational Pension (current employer)
    uk_occupational = UKPension(
        user_id=user.id,
        pension_type=PensionType.OCCUPATIONAL_DC.value,
        provider="Scottish Widows",
        scheme_reference_encrypted="encrypted_occ123",
        employer_name="Tech Solutions Ltd",
        current_value=Decimal("185000.00"),
        start_date=date(2015, 1, 1),
        expected_retirement_date=date(2045, 5, 15),  # Age 65
        investment_strategy=InvestmentStrategy.BALANCED.value,
        assumed_growth_rate=Decimal("5.50"),
        assumed_inflation_rate=Decimal("2.50"),
        mpaa_triggered=False,
        mpaa_date=None,
        status=PensionStatus.ACTIVE.value,
        is_deleted=False
    )
    db.add(uk_occupational)
    await db.flush()
    print(f"  ✓ UK Occupational Pension: {uk_occupational.provider} - £{uk_occupational.current_value:,.2f}")

    # Contribution for occupational pension
    occ_contribution = UKPensionContribution(
        pension_id=uk_occupational.id,
        employee_contribution=Decimal("1166.67"),  # 10% of £140k/12
        employer_contribution=Decimal("1166.67"),  # 10% match
        personal_contribution=Decimal("0.00"),
        frequency=ContributionFrequency.MONTHLY.value,
        tax_relief_method=TaxReliefMethod.NET_PAY.value,
        contribution_date=date(2024, 1, 1),
        tax_year="2024/25",
        effective_from=date(2024, 1, 1),
        effective_to=None
    )
    db.add(occ_contribution)
    print(f"    • Contributions: Employee £{occ_contribution.employee_contribution:,.2f}/mo + Employer £{occ_contribution.employer_contribution:,.2f}/mo")

    # UK Personal Pension (SIPP)
    uk_personal = UKPension(
        user_id=user.id,
        pension_type=PensionType.PERSONAL_PENSION.value,
        provider="Vanguard",
        scheme_reference_encrypted="encrypted_sipp456",
        employer_name=None,
        current_value=Decimal("125000.00"),
        start_date=date(2012, 3, 1),
        expected_retirement_date=date(2045, 5, 15),
        investment_strategy=InvestmentStrategy.AGGRESSIVE.value,
        assumed_growth_rate=Decimal("6.50"),
        assumed_inflation_rate=Decimal("2.50"),
        mpaa_triggered=False,
        mpaa_date=None,
        status=PensionStatus.ACTIVE.value,
        is_deleted=False
    )
    db.add(uk_personal)
    await db.flush()
    print(f"  ✓ UK Personal Pension (SIPP): {uk_personal.provider} - £{uk_personal.current_value:,.2f}")

    # Personal pension contribution
    personal_contribution = UKPensionContribution(
        pension_id=uk_personal.id,
        employee_contribution=Decimal("0.00"),
        employer_contribution=Decimal("0.00"),
        personal_contribution=Decimal("2083.33"),  # £25k/year
        frequency=ContributionFrequency.MONTHLY.value,
        tax_relief_method=TaxReliefMethod.RELIEF_AT_SOURCE.value,
        contribution_date=date(2024, 1, 1),
        tax_year="2024/25",
        effective_from=date(2024, 1, 1),
        effective_to=None
    )
    db.add(personal_contribution)
    print(f"    • Contributions: £{personal_contribution.personal_contribution:,.2f}/mo (£25k/year)")

    # State Pension Forecast
    state_pension = StatePensionForecast(
        user_id=user.id,
        forecast_date=date(2024, 1, 15),
        qualifying_years=24,  # 24 years of NI contributions
        years_needed_for_full=35,
        estimated_weekly_amount=Decimal("184.50"),  # Partial entitlement
        estimated_annual_amount=Decimal("9594.00"),
        state_pension_age=67
    )
    db.add(state_pension)
    print(f"  ✓ State Pension Forecast: £{state_pension.estimated_annual_amount:,.2f}/year (Age {state_pension.state_pension_age})")
    print(f"    • Qualifying years: {state_pension.qualifying_years}/{state_pension.years_needed_for_full}")

    # SA Retirement Annuity
    sa_ra = SARetirementFund(
        user_id=user.id,
        fund_type=SAFundType.RETIREMENT_ANNUITY.value,
        provider="Allan Gray",
        fund_name="Balanced Fund",
        fund_number_encrypted="encrypted_ra789",
        employer_name=None,
        current_value=Decimal("450000.00"),  # ~£18,750
        start_date=date(2010, 1, 1),
        retirement_age=65,
        investment_strategy=InvestmentStrategy.BALANCED.value,
        assumed_growth_rate=Decimal("8.00"),
        status=SAFundStatus.PRESERVED.value,  # No longer contributing (moved to UK)
        is_deleted=False
    )
    db.add(sa_ra)
    print(f"  ✓ SA Retirement Annuity: {sa_ra.provider} - R{sa_ra.current_value:,.2f} (preserved)")


async def create_life_insurance(db: AsyncSession, user: User):
    """Create life insurance policies."""
    print("\nCreating life insurance policies...")

    # Life Insurance Policy (NOT in trust)
    life_policy = LifeAssurancePolicy(
        user_id=user.id,
        policy_number_encrypted="encrypted_life001",
        provider="Legal & General",
        provider_country=ProviderCountry.UK.value,
        policy_type=PolicyType.LEVEL_TERM.value,
        cover_amount=Decimal("500000.00"),
        currency=Currency.GBP,
        cover_amount_gbp=Decimal("500000.00"),
        cover_amount_zar=Decimal("12000000.00"),
        premium_amount=Decimal("45.00"),
        premium_frequency=PremiumFrequency.MONTHLY.value,
        annual_premium=Decimal("540.00"),
        start_date=date(2018, 3, 1),
        end_date=date(2048, 3, 1),  # 30-year term
        written_in_trust=False,  # NOT written in trust (as per mockData.md)
        trust_type=None,
        critical_illness_rider=False,
        waiver_of_premium=True,
        indexation_rate=Decimal("3.00"),
        uk_iht_impact=True,  # Will be in estate (not in trust)
        sa_estate_duty_impact=False,
        status=PolicyStatus.ACTIVE.value,
        notes=None,
        is_deleted=False
    )
    db.add(life_policy)
    await db.flush()
    print(f"  ✓ Life Insurance: {life_policy.provider} - £{life_policy.cover_amount:,.2f} cover")
    print(f"    • Premium: £{life_policy.premium_amount}/month")
    print(f"    • NOT written in trust (will form part of estate)")

    # Beneficiary - Wife
    beneficiary = PolicyBeneficiary(
        policy_id=life_policy.id,
        name_encrypted="encrypted_jane_smith",
        date_of_birth_encrypted="encrypted_1982-08-20",
        address_encrypted="encrypted_123_high_street",
        beneficiary_relationship=BeneficiaryRelationship.SPOUSE.value,
        percentage=Decimal("100.00")
    )
    db.add(beneficiary)
    print(f"    • Beneficiary: Spouse (100%)")


async def create_assets_and_liabilities(db: AsyncSession, user: User):
    """Create estate assets and liabilities."""
    print("\nCreating assets and liabilities...")

    # UK House (primary residence)
    uk_house = EstateAsset(
        user_id=user.id,
        asset_type=AssetType.PROPERTY.value,
        description="Primary residence - 3-bed house in London",
        estimated_value=Decimal("650000.00"),
        currency="GBP",
        owned_individually=False,
        joint_ownership="Jane Smith (wife)",
        included_in_uk_estate=True,
        included_in_sa_estate=False,
        effective_from=date(2018, 1, 1),
        effective_to=None,
        is_deleted=False
    )
    db.add(uk_house)
    print(f"  ✓ Asset: {uk_house.description} - £{uk_house.estimated_value:,.2f} (joint ownership)")

    # SA House (rental property)
    sa_house = EstateAsset(
        user_id=user.id,
        asset_type=AssetType.PROPERTY.value,
        description="Rental property - 2-bed apartment in Cape Town",
        estimated_value=Decimal("2400000.00"),  # ZAR
        currency="ZAR",
        owned_individually=True,
        joint_ownership=None,
        included_in_uk_estate=False,
        included_in_sa_estate=True,
        effective_from=date(2015, 6, 1),
        effective_to=None,
        is_deleted=False
    )
    db.add(sa_house)
    print(f"  ✓ Asset: {sa_house.description} - R{sa_house.estimated_value:,.2f} (sole ownership)")

    # UK Mortgage
    uk_mortgage = EstateLiability(
        user_id=user.id,
        liability_type=LiabilityType.MORTGAGE.value,
        description="UK mortgage on primary residence",
        amount_outstanding=Decimal("320000.00"),
        currency="GBP",
        deductible_from_estate=True,
        effective_from=date(2018, 1, 1),
        effective_to=None,
        is_deleted=False
    )
    db.add(uk_mortgage)
    print(f"  ✓ Liability: {uk_mortgage.description} - £{uk_mortgage.amount_outstanding:,.2f}")

    # Credit Card (small balance)
    credit_card = EstateLiability(
        user_id=user.id,
        liability_type=LiabilityType.CREDIT_CARD.value,
        description="Barclaycard",
        amount_outstanding=Decimal("2500.00"),
        currency="GBP",
        deductible_from_estate=True,
        effective_from=date.today(),
        effective_to=None,
        is_deleted=False
    )
    db.add(credit_card)
    print(f"  ✓ Liability: {credit_card.description} - £{credit_card.amount_outstanding:,.2f}")


async def main():
    """Main function to populate demo data."""
    print("=" * 80)
    print("POPULATING DEMO USER DATA")
    print("=" * 80)

    # Create async engine
    engine = create_async_engine(
        settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
        echo=False
    )

    # Create async session
    AsyncSessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with AsyncSessionLocal() as db:
        try:
            # Create all mock data
            user = await create_demo_user(db)
            await create_tax_status(db, user)
            await create_income_records(db, user)
            await create_savings_accounts(db, user)
            await create_investments(db, user)
            await create_retirement_accounts(db, user)
            await create_life_insurance(db, user)
            await create_assets_and_liabilities(db, user)

            # Commit all changes
            await db.commit()

            print("\n" + "=" * 80)
            print("✅ DEMO DATA POPULATION COMPLETE")
            print("=" * 80)
            print(f"\nDemo User Credentials:")
            print(f"  Email:    demo@goalplan.com")
            print(f"  Password: Demo123!")
            print(f"\nYou can now log in with these credentials to see all the mock data.")
            print("=" * 80)

        except Exception as e:
            await db.rollback()
            print(f"\n❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
