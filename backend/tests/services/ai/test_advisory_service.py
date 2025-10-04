"""
Tests for AI Advisory Service

This test suite covers:
- All 6 advisory methods (retirement, investment, tax, goal, question, monthly insights)
- Various financial scenarios
- Response quality and structure
- Mocked LLM API calls
- Confidence scoring
- Human review flagging
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, date, timedelta
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from services.ai.advisory_service import AIAdvisoryService
from services.ai.llm_service import LLMService
from models.user import User, CountryPreference, UserStatus
from models.tax_status import UserTaxStatus, UKDomicileStatus
from models.income import UserIncome, IncomeType, IncomeFrequency, Currency
from models.savings_account import SavingsAccount, AccountType
from models.investment import InvestmentAccount
from models.retirement import UKPension, SARetirementFund
from models.life_assurance import LifeAssurancePolicy
from models.goal import FinancialGoal, GoalStatus, GoalType


@pytest.fixture
async def advisory_service(db_session):
    """Create advisory service with mocked LLM service."""
    import os
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key-123"}):
        service = AIAdvisoryService(db_session)
        # Mock the LLM service's client to avoid real API calls
        service.llm_service.client = AsyncMock()
        return service


@pytest.fixture
async def test_user_full_data(db_session):
    """Create a test user with comprehensive financial data."""
    # Create user
    user = User(
        email="fulldata@example.com",
        password_hash="hashed",
        first_name="Jane",
        last_name="Smith",
        date_of_birth=date(1985, 3, 20),
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
        annual_amount=Decimal("85000.00"),
        currency=Currency.GBP,
        frequency=IncomeFrequency.ANNUAL,
        start_date=date(2020, 1, 1)
    )
    db_session.add(income)

    # Add savings
    savings = SavingsAccount(
        user_id=user.id,
        account_name="Emergency Fund",
        account_type=AccountType.EASY_ACCESS,
        current_balance=Decimal("25000.00"),
        currency=Currency.GBP,
        interest_rate=Decimal("4.5")
    )
    db_session.add(savings)

    # Add investment
    investment = InvestmentAccount(
        user_id=user.id,
        account_name="ISA Portfolio",
        provider="Vanguard",
        current_value=Decimal("75000.00"),
        currency=Currency.GBP
    )
    db_session.add(investment)

    # Add pension
    pension = UKPension(
        user_id=user.id,
        pension_name="Workplace Pension",
        provider="Aviva",
        current_value=Decimal("150000.00"),
        currency=Currency.GBP,
        employee_contribution_amount=Decimal("500.00"),
        employee_contribution_frequency="monthly"
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


@pytest.fixture
async def test_goal(db_session, test_user_full_data):
    """Create a test goal."""
    goal = FinancialGoal(
        user_id=test_user_full_data.id,
        name="House Deposit",
        goal_type=GoalType.HOUSE_PURCHASE,
        target_amount=Decimal("50000.00"),
        current_amount=Decimal("15000.00"),
        target_date=date.today() + timedelta(days=730),  # 2 years
        status=GoalStatus.IN_PROGRESS,
        currency=Currency.GBP
    )
    db_session.add(goal)
    await db_session.commit()
    await db_session.refresh(goal)

    return goal


def create_mock_llm_response(advice_text: str, requires_review: bool = False):
    """Helper to create mock LLM response."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = advice_text
    mock_response.usage.total_tokens = 500
    mock_response.usage.prompt_tokens = 300
    mock_response.usage.completion_tokens = 200

    return {
        "advice": advice_text,
        "confidence_score": 0.85,
        "requires_human_review": requires_review,
        "metadata": {
            "model": "gpt-4-turbo-preview",
            "tokens_used": 500,
            "prompt_tokens": 300,
            "completion_tokens": 200,
            "temperature": 0.7,
            "advice_type": "test",
            "timestamp": datetime.utcnow().isoformat()
        }
    }


class TestRetirementAdvice:
    """Test retirement planning advice generation."""

    async def test_generate_retirement_advice_success(self, advisory_service, test_user_full_data):
        """Test successful retirement advice generation."""
        advice_text = """
        Based on your pension pot of £150,000 and expected retirement at age 65, here's my analysis:

        1. Increase pension contributions by £200/month to maximize employer match
        2. Consider using the full UK pension annual allowance (£60,000)
        3. Review your investment allocation to ensure it's age-appropriate

        You're currently on track for a comfortable retirement with projected income of £25,000/year.

        This is AI-generated informational advice, not regulated financial advice.
        """

        # Mock LLM response
        advisory_service.llm_service.generate_completion = AsyncMock(
            return_value=create_mock_llm_response(advice_text)
        )

        # Generate advice
        result = await advisory_service.generate_retirement_advice(test_user_full_data.id)

        # Verify structure
        assert "advice" in result
        assert "recommendations" in result
        assert "confidence_score" in result
        assert "requires_human_review" in result
        assert "sources" in result
        assert "metadata" in result

        # Verify content
        assert "pension" in result["advice"].lower()
        assert result["confidence_score"] >= 0.0
        assert result["confidence_score"] <= 1.0
        assert isinstance(result["recommendations"], list)
        assert len(result["sources"]) > 0

        # Verify LLM was called
        advisory_service.llm_service.generate_completion.assert_called_once()

    async def test_retirement_advice_user_not_found(self, advisory_service):
        """Test error when user doesn't exist."""
        fake_user_id = uuid4()

        with pytest.raises(ValueError, match="User .* not found"):
            await advisory_service.generate_retirement_advice(fake_user_id)

    async def test_retirement_advice_no_pension(self, advisory_service, db_session):
        """Test retirement advice when user has no pension."""
        # Create user without pension
        user = User(
            email="nopension@example.com",
            password_hash="hashed",
            first_name="No",
            last_name="Pension",
            date_of_birth=date(1990, 1, 1),
            country_preference=CountryPreference.UK,
            status=UserStatus.ACTIVE,
            email_verified=True,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        advice_text = """
        You currently have no pension savings. Starting a pension now is crucial.

        1. Open a workplace pension if your employer offers one
        2. Contribute at least enough to get employer match
        3. Consider opening a SIPP (Self-Invested Personal Pension)

        This is AI-generated informational advice, not regulated financial advice.
        """

        advisory_service.llm_service.generate_completion = AsyncMock(
            return_value=create_mock_llm_response(advice_text)
        )

        result = await advisory_service.generate_retirement_advice(user.id)

        assert "advice" in result
        assert "pension" in result["advice"].lower()


class TestInvestmentAdvice:
    """Test investment portfolio advice generation."""

    async def test_generate_investment_advice_success(self, advisory_service, test_user_full_data):
        """Test successful investment advice generation."""
        advice_text = """
        Your portfolio of £75,000 appears reasonably allocated:

        1. Consider rebalancing to 60/30/10 (equity/bonds/cash) for your moderate risk profile
        2. Ensure you're using your full ISA allowance (£20,000/year)
        3. Review fund fees to ensure you're not overpaying

        Your diversification looks good for someone in their late 30s.

        This is AI-generated informational advice, not regulated financial advice.
        """

        advisory_service.llm_service.generate_completion = AsyncMock(
            return_value=create_mock_llm_response(advice_text)
        )

        result = await advisory_service.generate_investment_advice(test_user_full_data.id)

        assert "advice" in result
        assert "recommendations" in result
        assert "portfolio" in result["advice"].lower() or "investment" in result["advice"].lower()
        assert len(result["sources"]) > 0

    async def test_investment_advice_no_investments(self, advisory_service, db_session):
        """Test investment advice when user has no investments."""
        # Create user without investments
        user = User(
            email="noinvest@example.com",
            password_hash="hashed",
            first_name="No",
            last_name="Invest",
            date_of_birth=date(1990, 1, 1),
            country_preference=CountryPreference.UK,
            status=UserStatus.ACTIVE,
            email_verified=True
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        result = await advisory_service.generate_investment_advice(user.id)

        # Should provide advice about starting to invest
        assert "advice" in result
        assert "ISA" in result["advice"] or "investment" in result["advice"].lower()
        assert len(result["recommendations"]) > 0


class TestTaxOptimizationAdvice:
    """Test tax optimization advice generation."""

    async def test_generate_tax_advice_success(self, advisory_service, test_user_full_data):
        """Test successful tax optimization advice generation."""
        advice_text = """
        Based on your income of £85,000, here are tax-saving opportunities:

        1. Increase pension contributions to reduce adjusted net income below £100,000 (avoid personal allowance taper)
        2. Use your full ISA allowance (£20,000) for tax-free investment returns
        3. Consider salary sacrifice for pension contributions (saves both income tax and NI)

        Estimated tax savings: £3,000-£5,000 per year.

        This is AI-generated informational advice, not regulated financial advice.
        """

        advisory_service.llm_service.generate_completion = AsyncMock(
            return_value=create_mock_llm_response(advice_text)
        )

        result = await advisory_service.generate_tax_optimization_advice(test_user_full_data.id)

        assert "advice" in result
        assert "tax" in result["advice"].lower()
        assert len(result["recommendations"]) > 0
        assert "UK Income Tax" in str(result["sources"])

    async def test_tax_advice_dual_resident(self, advisory_service, db_session, test_user_full_data):
        """Test tax advice for dual UK/SA resident."""
        # Update user to be dual resident
        result_query = await db_session.execute(
            UserTaxStatus.__table__.update()
            .where(UserTaxStatus.user_id == test_user_full_data.id)
            .values(sa_tax_resident=True)
        )
        await db_session.commit()

        advice_text = """
        As a dual UK/SA tax resident, you have unique opportunities:

        1. Consider DTA relief to avoid double taxation
        2. Use both ISA (UK) and TFSA (SA) allowances
        3. Review which country should tax each income source

        This is AI-generated informational advice, not regulated financial advice.
        """

        advisory_service.llm_service.generate_completion = AsyncMock(
            return_value=create_mock_llm_response(advice_text)
        )

        result = await advisory_service.generate_tax_optimization_advice(test_user_full_data.id)

        assert "advice" in result
        assert "Double Tax Agreement" in str(result["sources"]) or "DTA" in result["advice"]


class TestGoalAdvice:
    """Test goal achievement advice generation."""

    async def test_generate_goal_advice_success(self, advisory_service, test_goal):
        """Test successful goal advice generation."""
        advice_text = """
        For your house deposit goal of £50,000:

        Current progress: £15,000 (30%)
        Time remaining: 24 months
        Required monthly savings: £1,458

        1. Set up automatic monthly transfer of £1,500
        2. Consider high-interest savings account (4-5% APY)
        3. Look for bonus savers accounts for better rates

        You're making good progress!

        This is AI-generated informational advice, not regulated financial advice.
        """

        advisory_service.llm_service.generate_completion = AsyncMock(
            return_value=create_mock_llm_response(advice_text)
        )

        result = await advisory_service.generate_goal_advice(test_goal.id)

        assert "advice" in result
        assert "recommendations" in result
        assert "metadata" in result
        assert "goal_name" in result["metadata"]
        assert "progress_percentage" in result["metadata"]

        # Verify progress percentage is calculated correctly
        expected_progress = (15000 / 50000) * 100
        assert abs(result["metadata"]["progress_percentage"] - expected_progress) < 0.1

    async def test_goal_advice_not_found(self, advisory_service):
        """Test error when goal doesn't exist."""
        fake_goal_id = uuid4()

        with pytest.raises(ValueError, match="Goal .* not found"):
            await advisory_service.generate_goal_advice(fake_goal_id)


class TestFinancialQuestionAnswering:
    """Test free-form question answering."""

    async def test_answer_question_success(self, advisory_service, test_user_full_data):
        """Test answering a financial question."""
        question = "Should I pay off my mortgage early or invest the extra money?"

        advice_text = """
        This is a common financial dilemma. Here's my analysis:

        Mortgage early payoff:
        - Guaranteed return equal to your mortgage rate
        - Reduces financial stress
        - Less flexibility

        Investing:
        - Potentially higher returns (historically 7-10% annually)
        - Maintains liquidity
        - Market risk

        For your situation with moderate risk tolerance, a balanced approach might work best:
        1. Ensure emergency fund is fully funded (6 months expenses)
        2. Get employer pension match
        3. Then split extra funds 50/50 between mortgage and investing

        This is AI-generated informational advice, not regulated financial advice.
        """

        advisory_service.llm_service.generate_completion = AsyncMock(
            return_value=create_mock_llm_response(advice_text)
        )

        result = await advisory_service.answer_financial_question(
            test_user_full_data.id,
            question
        )

        assert "advice" in result
        assert "mortgage" in result["advice"].lower()
        assert len(result["recommendations"]) > 0

    async def test_answer_complex_question(self, advisory_service, test_user_full_data):
        """Test answering a complex multi-part question."""
        question = """
        I'm 39 years old with £150k in pension, £75k in investments, and £85k income.
        Should I:
        1. Max out my pension contributions?
        2. Focus on ISA investments?
        3. Pay off my mortgage early?
        """

        advice_text = """
        Let me address each option:

        1. Maxing pension: Good for tax relief (20-40%) but locked until 55+
        2. ISA investments: Tax-free growth, accessible, flexible
        3. Mortgage payoff: Guaranteed return, reduces debt, less liquid

        Recommended priority:
        1. Ensure you get employer pension match
        2. Build 6-month emergency fund
        3. Use ISA allowance for medium-term goals
        4. Additional pension contributions for tax relief

        This is AI-generated informational advice, not regulated financial advice.
        """

        advisory_service.llm_service.generate_completion = AsyncMock(
            return_value=create_mock_llm_response(advice_text)
        )

        result = await advisory_service.answer_financial_question(
            test_user_full_data.id,
            question
        )

        assert "advice" in result
        assert "pension" in result["advice"].lower()
        assert "ISA" in result["advice"]


class TestMonthlyInsights:
    """Test monthly financial insights generation."""

    async def test_generate_monthly_insights_success(self, advisory_service, test_user_full_data):
        """Test successful monthly insights generation."""
        advice_text = """
        Your Financial Month in Review:

        You're making excellent progress! Your net worth increased by £2,500 this month thanks to
        consistent savings and investment growth.

        Key Insights:
        1. Your emergency fund is well-established at £25,000 (6+ months expenses)
        2. You're on track with your house deposit goal (30% complete)
        3. Your pension contributions are maximizing employer match
        4. Investment portfolio has grown 2.3% this month
        5. You're effectively using your ISA allowance

        Next Month Recommendations:
        - Consider increasing pension contributions for additional tax relief
        - Review your investment allocation as markets have shifted
        - Great job maintaining your savings discipline!

        This is AI-generated informational advice, not regulated financial advice.
        """

        advisory_service.llm_service.generate_completion = AsyncMock(
            return_value=create_mock_llm_response(advice_text)
        )

        result = await advisory_service.generate_monthly_insights(test_user_full_data.id)

        assert "advice" in result
        assert "recommendations" in result
        assert "metadata" in result
        assert result["metadata"]["period"] == "monthly"
        assert result["requires_human_review"] is False  # Monthly insights don't need review

    async def test_monthly_insights_includes_goals(self, advisory_service, test_user_full_data, test_goal):
        """Test that monthly insights consider goal progress."""
        advice_text = """
        Monthly Summary:

        Goal Progress:
        - House Deposit: 30% complete, on track for 2-year deadline

        Keep up the great work on your savings goals!

        This is AI-generated informational advice, not regulated financial advice.
        """

        advisory_service.llm_service.generate_completion = AsyncMock(
            return_value=create_mock_llm_response(advice_text)
        )

        result = await advisory_service.generate_monthly_insights(test_user_full_data.id)

        assert "advice" in result
        # Insights should be generated even with goals
        assert len(result["advice"]) > 0


class TestRecommendationParsing:
    """Test recommendation parsing from advice text."""

    def test_parse_numbered_recommendations(self, advisory_service):
        """Test parsing numbered list recommendations."""
        advice_text = """
        Here are my recommendations:

        1. Increase pension contributions by £200/month
        2. Use your full ISA allowance before April 5
        3. Review your emergency fund target

        These will help optimize your finances.
        """

        recommendations = advisory_service._parse_recommendations(advice_text)

        assert len(recommendations) > 0
        assert any("pension" in rec["action"].lower() for rec in recommendations)

    def test_parse_no_numbered_list(self, advisory_service):
        """Test parsing when no numbered list present."""
        advice_text = """
        Consider increasing your savings rate and reviewing your investment allocation.
        """

        recommendations = advisory_service._parse_recommendations(advice_text)

        # Should return generic recommendation
        assert len(recommendations) == 1
        assert "review" in recommendations[0]["action"].lower()

    def test_parse_recommendations_max_five(self, advisory_service):
        """Test that parsing limits to 5 recommendations."""
        advice_text = """
        1. First recommendation
        2. Second recommendation
        3. Third recommendation
        4. Fourth recommendation
        5. Fifth recommendation
        6. Sixth recommendation
        7. Seventh recommendation
        """

        recommendations = advisory_service._parse_recommendations(advice_text)

        # Should limit to 5
        assert len(recommendations) <= 5


class TestAgeCalculation:
    """Test age calculation helper."""

    def test_calculate_age_normal(self, advisory_service):
        """Test normal age calculation."""
        dob = date(1985, 6, 15)
        age = advisory_service._calculate_age(dob)

        # Age should be current year - 1985 (approximately 39-40)
        assert age >= 38
        assert age <= 41

    def test_calculate_age_none(self, advisory_service):
        """Test age calculation with None DOB."""
        age = advisory_service._calculate_age(None)

        # Should return default age
        assert age == 35

    def test_calculate_age_birthday_not_yet(self, advisory_service):
        """Test age when birthday hasn't occurred this year."""
        today = date.today()
        # Create DOB with birthday in future this year
        future_month = today.month + 1 if today.month < 12 else 1
        dob = date(1985, future_month, 15)

        age = advisory_service._calculate_age(dob)

        # Should be one year less if birthday is in future
        current_year = today.year
        expected_age = current_year - 1985 - 1  # Subtract 1 because birthday not yet

        assert age == expected_age or age == expected_age + 1  # Allow for edge cases
