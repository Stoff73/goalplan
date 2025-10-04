"""
Tests for LLM Service - OpenAI Integration

This test suite covers:
- API integration (mocked)
- Context creation with PII anonymization
- Response validation (harmful content detection)
- Rate limiting
- Retry logic
- Error handling
"""

import pytest
import os
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, date
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from services.ai.llm_service import LLMService, AdviceType
from models.user import User, CountryPreference, UserStatus
from models.tax_status import UserTaxStatus, UKDomicileStatus
from models.income import UserIncome, IncomeType, IncomeFrequency, Currency
from models.savings_account import SavingsAccount, AccountType
from models.investment import InvestmentAccount
from models.retirement import UKPension, SARetirementFund
from models.life_assurance import LifeAssurancePolicy


@pytest.fixture
async def llm_service(db_session):
    """Create LLM service with mocked OpenAI client."""
    # Mock environment variable
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key-123"}):
        service = LLMService(db_session)
        # Mock the OpenAI client to avoid real API calls
        service.client = AsyncMock()
        return service


@pytest.fixture
async def test_user_with_data(db_session):
    """Create a test user with comprehensive financial data."""
    # Create user
    user = User(
        email="test@example.com",
        password_hash="hashed",
        first_name="John",
        last_name="Doe",
        date_of_birth=date(1985, 5, 15),
        country_preference=CountryPreference.UK,
        status=UserStatus.ACTIVE,
        email_verified=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Add tax status
    tax_status = UserTaxStatus(
        user_id=user.id,
        uk_tax_resident=True,
        sa_tax_resident=False,
        uk_domicile=UKDomicileStatus.UK_DOMICILE
    )
    db_session.add(tax_status)

    # Add income
    income = UserIncome(
        user_id=user.id,
        income_type=IncomeType.EMPLOYMENT,
        description="Software Engineer",
        annual_amount=Decimal("75000.00"),
        currency=Currency.GBP,
        frequency=IncomeFrequency.ANNUAL,
        start_date=date(2020, 1, 1)
    )
    db_session.add(income)

    # Add savings account
    savings = SavingsAccount(
        user_id=user.id,
        account_name="Emergency Fund",
        account_type=AccountType.EASY_ACCESS,
        current_balance=Decimal("15000.00"),
        currency=Currency.GBP,
        interest_rate=Decimal("4.5")
    )
    db_session.add(savings)

    # Add investment account
    investment = InvestmentAccount(
        user_id=user.id,
        account_name="ISA Portfolio",
        provider="Vanguard",
        current_value=Decimal("50000.00"),
        currency=Currency.GBP
    )
    db_session.add(investment)

    # Add pension
    pension = UKPension(
        user_id=user.id,
        pension_name="Company Pension",
        provider="Aviva",
        current_value=Decimal("120000.00"),
        currency=Currency.GBP
    )
    db_session.add(pension)

    # Add life insurance
    policy = LifeAssurancePolicy(
        user_id=user.id,
        policy_name="Term Life",
        provider="Legal & General",
        cover_amount=Decimal("500000.00"),
        currency=Currency.GBP
    )
    db_session.add(policy)

    await db_session.commit()

    return user


class TestLLMServiceInitialization:
    """Test LLM service initialization."""

    def test_initialization_without_api_key(self, db_session):
        """Test that service raises error if API key not set."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="OPENAI_API_KEY"):
                LLMService(db_session)

    def test_initialization_with_api_key(self, db_session):
        """Test that service initializes correctly with API key."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            service = LLMService(db_session)
            assert service.db == db_session
            assert service.client is not None


class TestFinancialContextCreation:
    """Test financial context creation and PII anonymization."""

    async def test_create_context_user_not_found(self, llm_service):
        """Test error when user doesn't exist."""
        fake_user_id = uuid4()

        with pytest.raises(ValueError, match="User .* not found"):
            await llm_service.create_financial_context(fake_user_id)

    async def test_create_context_with_full_data(self, llm_service, test_user_with_data):
        """Test context creation with comprehensive user data."""
        context = await llm_service.create_financial_context(test_user_with_data.id)

        # Verify structure
        assert "demographics" in context
        assert "financial_position" in context
        assert "tax_status" in context
        assert "modules" in context

        # Verify demographics (PII anonymized - no names)
        assert context["demographics"]["age"] == 39  # Calculated from DOB
        assert context["demographics"]["country_preference"] == "UK"

        # Verify financial position
        assert context["financial_position"]["annual_income_gbp"] == 75000.0
        assert context["financial_position"]["total_savings_gbp"] > 0
        assert context["financial_position"]["total_investments_gbp"] > 0
        assert context["financial_position"]["total_pension_pot_gbp"] > 0
        assert context["financial_position"]["life_insurance_cover_gbp"] > 0

        # Verify tax status
        assert context["tax_status"]["uk_tax_resident"] is True
        assert context["tax_status"]["sa_tax_resident"] is False
        assert context["tax_status"]["uk_domicile"] == "uk_domicile"

        # Verify modules flags
        assert context["modules"]["has_savings"] is True
        assert context["modules"]["has_investments"] is True
        assert context["modules"]["has_pensions"] is True
        assert context["modules"]["has_life_insurance"] is True

    async def test_pii_anonymization(self, llm_service, test_user_with_data):
        """Test that PII is properly anonymized in context."""
        context = await llm_service.create_financial_context(test_user_with_data.id)

        # Convert context to string to check for PII
        context_str = str(context)

        # Should NOT contain PII
        assert "John" not in context_str
        assert "Doe" not in context_str
        assert "test@example.com" not in context_str

        # Should NOT contain specific account details
        assert "Emergency Fund" not in context_str
        assert "Vanguard" not in context_str
        assert "Aviva" not in context_str

        # Should contain aggregated financial data
        assert "age" in context_str
        assert "net_worth" in context_str or "annual_income" in context_str


class TestResponseValidation:
    """Test AI response validation for safety and compliance."""

    def test_validate_safe_response(self, llm_service):
        """Test validation of safe, appropriate response."""
        safe_response = """
        Based on your pension pot of £120,000 and annual income of £75,000, here are my recommendations:

        1. Consider increasing pension contributions to maximize tax relief
        2. Review your asset allocation to ensure proper diversification
        3. Make full use of your ISA allowance before the tax year ends

        This is AI-generated informational advice, not regulated financial advice.
        """

        result = llm_service.validate_ai_response(safe_response)

        assert result["valid"] is True
        assert result["requires_review"] is False

    def test_validate_harmful_guaranteed_returns(self, llm_service):
        """Test detection of harmful 'guaranteed returns' claim."""
        harmful_response = """
        Invest in this fund for guaranteed returns of 20% per year with no risk.
        """

        result = llm_service.validate_ai_response(harmful_response)

        assert result["valid"] is False
        assert result["requires_review"] is True
        assert "guarantee" in result["reason"].lower()

    def test_validate_harmful_risk_free(self, llm_service):
        """Test detection of harmful 'risk-free' claim."""
        harmful_response = """
        This is a risk-free investment that cannot lose value.
        """

        result = llm_service.validate_ai_response(harmful_response)

        assert result["valid"] is False
        assert result["requires_review"] is True

    def test_validate_specific_stock_picks(self, llm_service):
        """Test detection of specific stock recommendations."""
        harmful_response = """
        You should buy AAPL stock immediately. Also purchase TSLA shares.
        """

        result = llm_service.validate_ai_response(harmful_response)

        assert result["valid"] is False
        assert result["requires_review"] is True
        assert "stock" in result["reason"].lower()

    def test_validate_large_amounts_require_review(self, llm_service):
        """Test that large amounts (>£50k) trigger human review."""
        response_with_large_amount = """
        Consider investing £75,000 in a diversified portfolio.
        """

        result = llm_service.validate_ai_response(response_with_large_amount)

        assert result["valid"] is True
        assert result["requires_review"] is True  # Large amount should trigger review

    def test_validate_review_keywords(self, llm_service):
        """Test detection of keywords requiring human review."""
        review_response = """
        You should sell everything and invest in bonds.
        """

        result = llm_service.validate_ai_response(review_response)

        # Should be valid but require review
        assert result["valid"] is True
        assert result["requires_review"] is True


class TestGenerateCompletion:
    """Test LLM completion generation with retry logic."""

    async def test_successful_completion(self, llm_service):
        """Test successful API call and completion generation."""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = """
        Based on your retirement goals, I recommend:
        1. Increase pension contributions by £200/month
        2. Review your asset allocation
        3. Consider using full ISA allowance

        This is AI-generated informational advice, not regulated financial advice.
        """
        mock_response.usage.total_tokens = 500
        mock_response.usage.prompt_tokens = 300
        mock_response.usage.completion_tokens = 200

        llm_service.client.chat.completions.create = AsyncMock(return_value=mock_response)

        # Create test context
        context = {
            "demographics": {"age": 39, "country_preference": "UK"},
            "financial_position": {"net_worth_gbp": 250000, "annual_income_gbp": 75000},
            "tax_status": {"uk_tax_resident": True, "sa_tax_resident": False},
            "modules": {}
        }

        # Generate completion
        result = await llm_service.generate_completion(
            prompt="How can I optimize my retirement savings?",
            context=context,
            advice_type=AdviceType.RETIREMENT
        )

        # Verify result structure
        assert "advice" in result
        assert "confidence_score" in result
        assert "requires_human_review" in result
        assert "metadata" in result

        assert result["confidence_score"] >= 0.0
        assert result["confidence_score"] <= 1.0

        # Verify API was called
        llm_service.client.chat.completions.create.assert_called_once()

    async def test_retry_on_rate_limit(self, llm_service):
        """Test exponential backoff retry on rate limit error."""
        from openai import RateLimitError

        # First call fails with rate limit, second succeeds
        mock_success_response = MagicMock()
        mock_success_response.choices = [MagicMock()]
        mock_success_response.choices[0].message.content = "Safe advice text."
        mock_success_response.usage.total_tokens = 100
        mock_success_response.usage.prompt_tokens = 50
        mock_success_response.usage.completion_tokens = 50

        llm_service.client.chat.completions.create = AsyncMock(
            side_effect=[
                RateLimitError("Rate limit exceeded"),
                mock_success_response
            ]
        )

        context = {
            "demographics": {"age": 39},
            "financial_position": {},
            "tax_status": {},
            "modules": {}
        }

        # Should succeed after retry
        result = await llm_service.generate_completion(
            prompt="Test question",
            context=context
        )

        assert result["advice"] == "Safe advice text."
        assert llm_service.client.chat.completions.create.call_count == 2

    async def test_max_retries_exceeded(self, llm_service):
        """Test that max retries raises error."""
        from openai import RateLimitError

        # All calls fail
        llm_service.client.chat.completions.create = AsyncMock(
            side_effect=RateLimitError("Rate limit exceeded")
        )

        context = {
            "demographics": {"age": 39},
            "financial_position": {},
            "tax_status": {},
            "modules": {}
        }

        # Should raise after max retries
        with pytest.raises(RateLimitError):
            await llm_service.generate_completion(
                prompt="Test question",
                context=context
            )

        # Should have tried MAX_RETRIES times
        assert llm_service.client.chat.completions.create.call_count == LLMService.MAX_RETRIES

    async def test_validation_failure_raises_error(self, llm_service):
        """Test that validation failure raises ValueError."""
        # Mock response with harmful content
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Guaranteed returns with no risk!"
        mock_response.usage.total_tokens = 50
        mock_response.usage.prompt_tokens = 25
        mock_response.usage.completion_tokens = 25

        llm_service.client.chat.completions.create = AsyncMock(return_value=mock_response)

        context = {
            "demographics": {"age": 39},
            "financial_position": {},
            "tax_status": {},
            "modules": {}
        }

        # Should raise ValueError due to validation failure
        with pytest.raises(ValueError, match="validation failed"):
            await llm_service.generate_completion(
                prompt="Test question",
                context=context
            )


class TestSystemMessageBuilding:
    """Test system message generation for different advice types."""

    def test_retirement_system_message(self, llm_service):
        """Test system message for retirement advice."""
        message = llm_service._build_system_message(AdviceType.RETIREMENT)

        assert "pension" in message.lower()
        assert "retirement" in message.lower()
        assert "regulated financial advice" in message.lower()
        assert "disclaimer" in message.lower()

    def test_investment_system_message(self, llm_service):
        """Test system message for investment advice."""
        message = llm_service._build_system_message(AdviceType.INVESTMENT)

        assert "asset allocation" in message.lower() or "diversification" in message.lower()
        assert "isa" in message.lower()

    def test_tax_system_message(self, llm_service):
        """Test system message for tax advice."""
        message = llm_service._build_system_message(AdviceType.TAX_OPTIMIZATION)

        assert "tax" in message.lower()
        assert "allowance" in message.lower() or "deduction" in message.lower()


class TestUserMessageBuilding:
    """Test user message construction with context."""

    def test_build_user_message(self, llm_service):
        """Test user message includes context and prompt."""
        context = {
            "demographics": {"age": 39, "country_preference": "UK"},
            "financial_position": {
                "net_worth_gbp": 250000,
                "annual_income_gbp": 75000,
                "total_savings_gbp": 15000,
                "total_investments_gbp": 50000,
                "total_pension_pot_gbp": 120000,
                "life_insurance_cover_gbp": 500000
            },
            "tax_status": {
                "uk_tax_resident": True,
                "sa_tax_resident": False,
                "domicile": "UK"
            }
        }

        prompt = "How should I optimize my retirement savings?"

        message = llm_service._build_user_message(context, prompt)

        # Verify context is included
        assert "Age: 39" in message
        assert "£250,000" in message  # Net worth
        assert "£75,000" in message   # Income
        assert "£120,000" in message  # Pension pot

        # Verify tax status
        assert "UK Tax Resident: True" in message
        assert "SA Tax Resident: False" in message

        # Verify prompt is included
        assert prompt in message


class TestPromptTemplates:
    """Test that prompt templates are available and properly formatted."""

    def test_retirement_template_exists(self):
        """Test retirement advice template exists."""
        from services.ai.llm_service import PROMPT_TEMPLATES

        assert "retirement_advice" in PROMPT_TEMPLATES
        assert "pension_pot" in PROMPT_TEMPLATES["retirement_advice"]
        assert "retirement_age" in PROMPT_TEMPLATES["retirement_advice"]

    def test_investment_template_exists(self):
        """Test investment template exists."""
        from services.ai.llm_service import PROMPT_TEMPLATES

        assert "investment_allocation" in PROMPT_TEMPLATES
        assert "portfolio_value" in PROMPT_TEMPLATES["investment_allocation"]

    def test_tax_template_exists(self):
        """Test tax optimization template exists."""
        from services.ai.llm_service import PROMPT_TEMPLATES

        assert "tax_optimization" in PROMPT_TEMPLATES
        assert "income" in PROMPT_TEMPLATES["tax_optimization"]
