"""
Tests for savings allowances API endpoints.

Covers:
- ISA allowance endpoint
- TFSA allowance endpoint
- Emergency fund assessment endpoint
- Authentication and validation
"""

import pytest
from decimal import Decimal
from datetime import date
from uuid import uuid4

from models.savings_account import (
    SavingsAccount,
    AccountType,
    AccountPurpose,
    AccountCountry,
    Currency,
    ISAContribution,
    TFSAContribution
)
from services.isa_tfsa_tracking import get_current_uk_tax_year, get_current_sa_tax_year


@pytest.mark.asyncio
class TestISAAllowance:
    """Tests for GET /api/v1/savings/isa-allowance"""

    async def test_get_isa_allowance_no_contributions(
        self, test_client, authenticated_headers
    ):
        """Test ISA allowance with no contributions."""
        response = await test_client.get(
            "/api/v1/savings/isa-allowance",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["tax_year"] == get_current_uk_tax_year()
        assert Decimal(str(data["total_allowance"])) == Decimal("20000.00")
        assert Decimal(str(data["used"])) == Decimal("0.00")
        assert Decimal(str(data["remaining"])) == Decimal("20000.00")
        assert data["percentage_used"] == 0.0

    async def test_get_isa_allowance_with_contributions(
        self, test_client, authenticated_headers, test_user, db_session
    ):
        """Test ISA allowance with existing contributions."""
        # Create ISA contribution
        contribution = ISAContribution(
            user_id=test_user.id,
            tax_year=get_current_uk_tax_year(),
            contribution_amount=Decimal("5000.00"),
            contribution_date=date.today(),
            notes="Test contribution"
        )

        db_session.add(contribution)
        await db_session.commit()

        response = await test_client.get(
            "/api/v1/savings/isa-allowance",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert Decimal(str(data["used"])) == Decimal("5000.00")
        assert Decimal(str(data["remaining"])) == Decimal("15000.00")
        assert data["percentage_used"] == 25.0

    async def test_get_isa_allowance_specific_tax_year(
        self, test_client, authenticated_headers, test_user, db_session
    ):
        """Test ISA allowance for specific tax year."""
        # Create contribution for previous tax year
        prev_tax_year = "2023/24"
        contribution = ISAContribution(
            user_id=test_user.id,
            tax_year=prev_tax_year,
            contribution_amount=Decimal("10000.00"),
            contribution_date=date(2023, 5, 1),
            notes="Previous year"
        )

        db_session.add(contribution)
        await db_session.commit()

        response = await test_client.get(
            f"/api/v1/savings/isa-allowance?tax_year={prev_tax_year}",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["tax_year"] == prev_tax_year
        assert Decimal(str(data["used"])) == Decimal("10000.00")

    async def test_get_isa_allowance_requires_auth(self, test_client):
        """Test that ISA allowance requires authentication."""
        response = await test_client.get("/api/v1/savings/isa-allowance")

        assert response.status_code == 401


@pytest.mark.asyncio
class TestTFSAAllowance:
    """Tests for GET /api/v1/savings/tfsa-allowance"""

    async def test_get_tfsa_allowance_no_contributions(
        self, test_client, authenticated_headers
    ):
        """Test TFSA allowance with no contributions."""
        response = await test_client.get(
            "/api/v1/savings/tfsa-allowance",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["tax_year"] == get_current_sa_tax_year()
        assert Decimal(str(data["annual_allowance"])) == Decimal("36000.00")
        assert Decimal(str(data["annual_used"])) == Decimal("0.00")
        assert Decimal(str(data["annual_remaining"])) == Decimal("36000.00")
        assert Decimal(str(data["lifetime_allowance"])) == Decimal("500000.00")
        assert Decimal(str(data["lifetime_used"])) == Decimal("0.00")
        assert Decimal(str(data["lifetime_remaining"])) == Decimal("500000.00")

    async def test_get_tfsa_allowance_with_contributions(
        self, test_client, authenticated_headers, test_user, db_session
    ):
        """Test TFSA allowance with existing contributions."""
        from models.savings_account import TFSAContributionType

        # Create TFSA contributions
        contributions = [
            TFSAContribution(
                user_id=test_user.id,
                tax_year=get_current_sa_tax_year(),
                contribution_amount=Decimal("20000.00"),
                contribution_type=TFSAContributionType.DEPOSIT,
                contribution_date=date.today(),
                notes="Current year"
            ),
            TFSAContribution(
                user_id=test_user.id,
                tax_year="2023/24",
                contribution_amount=Decimal("30000.00"),
                contribution_type=TFSAContributionType.DEPOSIT,
                contribution_date=date(2023, 5, 1),
                notes="Previous year"
            ),
        ]

        for contribution in contributions:
            db_session.add(contribution)
        await db_session.commit()

        response = await test_client.get(
            "/api/v1/savings/tfsa-allowance",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Current year: 20000 used
        assert Decimal(str(data["annual_used"])) == Decimal("20000.00")
        assert Decimal(str(data["annual_remaining"])) == Decimal("16000.00")

        # Lifetime: 50000 total
        assert Decimal(str(data["lifetime_used"])) == Decimal("50000.00")
        assert Decimal(str(data["lifetime_remaining"])) == Decimal("450000.00")

    async def test_get_tfsa_allowance_specific_tax_year(
        self, test_client, authenticated_headers, test_user, db_session
    ):
        """Test TFSA allowance for specific tax year."""
        from models.savings_account import TFSAContributionType

        prev_tax_year = "2023/24"
        contribution = TFSAContribution(
            user_id=test_user.id,
            tax_year=prev_tax_year,
            contribution_amount=Decimal("30000.00"),
            contribution_type=TFSAContributionType.DEPOSIT,
            contribution_date=date(2023, 5, 1),
            notes="Previous year"
        )

        db_session.add(contribution)
        await db_session.commit()

        response = await test_client.get(
            f"/api/v1/savings/tfsa-allowance?tax_year={prev_tax_year}",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["tax_year"] == prev_tax_year
        assert Decimal(str(data["annual_used"])) == Decimal("30000.00")

    async def test_get_tfsa_allowance_requires_auth(self, test_client):
        """Test that TFSA allowance requires authentication."""
        response = await test_client.get("/api/v1/savings/tfsa-allowance")

        assert response.status_code == 401


@pytest.mark.asyncio
class TestEmergencyFundAssessment:
    """Tests for GET /api/v1/savings/emergency-fund-assessment"""

    async def test_emergency_fund_assessment_none(
        self, test_client, authenticated_headers
    ):
        """Test assessment with no emergency fund accounts."""
        response = await test_client.get(
            "/api/v1/savings/emergency-fund-assessment?monthly_expenses=2000",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "NONE"
        assert Decimal(str(data["current_emergency_fund"])) == Decimal("0.00")
        assert Decimal(str(data["recommended_emergency_fund"])) == Decimal("12000.00")
        assert data["months_covered"] == 0.0
        assert len(data["recommendations"]) > 0

    async def test_emergency_fund_assessment_adequate(
        self, test_client, authenticated_headers, test_user, db_session
    ):
        """Test assessment with adequate emergency fund."""
        # Create emergency fund account with 6+ months coverage
        account = SavingsAccount(
            user_id=test_user.id,
            bank_name="Emergency Bank",
            account_name="Emergency Fund",
            account_number_encrypted="encrypted",
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=Decimal("15000.00"),  # 7.5 months at £2000/month
            country=AccountCountry.UK,
            purpose=AccountPurpose.EMERGENCY_FUND
        )

        db_session.add(account)
        await db_session.commit()

        response = await test_client.get(
            "/api/v1/savings/emergency-fund-assessment?monthly_expenses=2000",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ADEQUATE"
        assert Decimal(str(data["current_emergency_fund"])) == Decimal("15000.00")
        assert Decimal(str(data["recommended_emergency_fund"])) == Decimal("12000.00")
        assert data["months_covered"] == 7.5
        assert data["ratio"] > 1.0

    async def test_emergency_fund_assessment_insufficient(
        self, test_client, authenticated_headers, test_user, db_session
    ):
        """Test assessment with insufficient emergency fund."""
        # Create emergency fund account with <6 months coverage
        account = SavingsAccount(
            user_id=test_user.id,
            bank_name="Emergency Bank",
            account_name="Emergency Fund",
            account_number_encrypted="encrypted",
            account_type=AccountType.SAVINGS,
            currency=Currency.GBP,
            current_balance=Decimal("8000.00"),  # 4 months at £2000/month
            country=AccountCountry.UK,
            purpose=AccountPurpose.EMERGENCY_FUND
        )

        db_session.add(account)
        await db_session.commit()

        response = await test_client.get(
            "/api/v1/savings/emergency-fund-assessment?monthly_expenses=2000",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "INSUFFICIENT"
        assert Decimal(str(data["current_emergency_fund"])) == Decimal("8000.00")
        assert data["months_covered"] == 4.0
        assert data["ratio"] < 1.0

    async def test_emergency_fund_assessment_zar_currency(
        self, test_client, authenticated_headers, test_user, db_session
    ):
        """Test assessment with ZAR currency."""
        account = SavingsAccount(
            user_id=test_user.id,
            bank_name="SA Bank",
            account_name="Emergency Fund ZAR",
            account_number_encrypted="encrypted",
            account_type=AccountType.SAVINGS,
            currency=Currency.ZAR,
            current_balance=Decimal("200000.00"),
            country=AccountCountry.SA,
            purpose=AccountPurpose.EMERGENCY_FUND
        )

        db_session.add(account)
        await db_session.commit()

        response = await test_client.get(
            "/api/v1/savings/emergency-fund-assessment?monthly_expenses=30000&base_currency=ZAR",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["base_currency"] == "ZAR"
        assert Decimal(str(data["current_emergency_fund"])) == Decimal("200000.00")
        assert Decimal(str(data["recommended_emergency_fund"])) == Decimal("180000.00")

    async def test_emergency_fund_assessment_missing_monthly_expenses(
        self, test_client, authenticated_headers
    ):
        """Test that monthly_expenses is required."""
        response = await test_client.get(
            "/api/v1/savings/emergency-fund-assessment",
            headers=authenticated_headers
        )

        assert response.status_code == 422  # Validation error

    async def test_emergency_fund_assessment_invalid_currency(
        self, test_client, authenticated_headers
    ):
        """Test that invalid base_currency is rejected."""
        response = await test_client.get(
            "/api/v1/savings/emergency-fund-assessment?monthly_expenses=2000&base_currency=USD",
            headers=authenticated_headers
        )

        assert response.status_code == 400

    async def test_emergency_fund_assessment_requires_auth(self, test_client):
        """Test that emergency fund assessment requires authentication."""
        response = await test_client.get(
            "/api/v1/savings/emergency-fund-assessment?monthly_expenses=2000"
        )

        assert response.status_code == 401
