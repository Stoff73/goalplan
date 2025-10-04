"""
Pytest fixtures for Goals API tests.

Provides test data and setup for goal-related tests:
- Test users with authentication tokens
- Sample goals for testing
- Common test data
"""

import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import uuid4
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from models.goal import FinancialGoal, GoalType, GoalPriority, GoalStatus
from utils.password import hash_password
from utils.jwt import generate_access_token, decode_token
from services.session import SessionService


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """Create a test user for goal tests."""
    user = User(
        id=uuid4(),
        email="goaltest@example.com",
        password_hash=hash_password("TestPassword123!"),
        first_name="Goal",
        last_name="Tester",
        country_preference="UK",
        status="ACTIVE",
        email_verified=True,
        terms_accepted_at=datetime.utcnow()
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_user_token(test_user: User, db_session: AsyncSession) -> str:
    """Create an access token for the test user with session in Redis."""
    # Generate tokens
    access_token = generate_access_token(test_user.id)

    # Extract JTI from token
    payload = decode_token(access_token)
    access_jti = payload["jti"]

    # Create session in Redis (required for auth middleware)
    session_service = SessionService()
    await session_service.create_session(
        db=db_session,
        user_id=test_user.id,
        refresh_token_jti=access_jti,  # Using same JTI for simplicity in tests
        access_token_jti=access_jti,
        device_info="test_device",
        ip_address="127.0.0.1"
    )

    return access_token


@pytest.fixture
async def other_user(db_session: AsyncSession):
    """Create another user to test authorization."""
    user = User(
        id=uuid4(),
        email="otheruser@example.com",
        password_hash=hash_password("OtherPassword123!"),
        first_name="Other",
        last_name="User",
        country_preference="SA",
        status="ACTIVE",
        email_verified=True,
        terms_accepted_at=datetime.utcnow()
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def other_user_token(other_user: User, db_session: AsyncSession) -> str:
    """Create an access token for the other user with session in Redis."""
    # Generate tokens
    access_token = generate_access_token(other_user.id)

    # Extract JTI from token
    payload = decode_token(access_token)
    access_jti = payload["jti"]

    # Create session in Redis (required for auth middleware)
    session_service = SessionService()
    await session_service.create_session(
        db=db_session,
        user_id=other_user.id,
        refresh_token_jti=access_jti,  # Using same JTI for simplicity in tests
        access_token_jti=access_jti,
        device_info="test_device",
        ip_address="127.0.0.1"
    )

    return access_token


@pytest.fixture
async def new_user(db_session: AsyncSession):
    """Create a user with no goals."""
    user = User(
        id=uuid4(),
        email="newuser@example.com",
        password_hash=hash_password("NewPassword123!"),
        first_name="New",
        last_name="User",
        country_preference="BOTH",
        status="ACTIVE",
        email_verified=True,
        terms_accepted_at=datetime.utcnow()
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def new_user_token(new_user: User, db_session: AsyncSession) -> str:
    """Create an access token for the new user with session in Redis."""
    # Generate tokens
    access_token = generate_access_token(new_user.id)

    # Extract JTI from token
    payload = decode_token(access_token)
    access_jti = payload["jti"]

    # Create session in Redis (required for auth middleware)
    session_service = SessionService()
    await session_service.create_session(
        db=db_session,
        user_id=new_user.id,
        refresh_token_jti=access_jti,  # Using same JTI for simplicity in tests
        access_token_jti=access_jti,
        device_info="test_device",
        ip_address="127.0.0.1"
    )

    return access_token


@pytest.fixture
async def test_goal(db_session: AsyncSession, test_user: User):
    """Create a test goal."""
    target_date = date.today() + timedelta(days=365)

    goal = FinancialGoal(
        id=uuid4(),
        user_id=test_user.id,
        goal_name="House Deposit",
        goal_type=GoalType.PROPERTY_PURCHASE,
        description="Save for house deposit",
        target_amount=Decimal("30000.00"),
        currency="GBP",
        current_amount=Decimal("0.00"),
        progress_percentage=Decimal("0.00"),
        target_date=target_date,
        start_date=date.today(),
        priority=GoalPriority.HIGH,
        status=GoalStatus.NOT_STARTED,
        auto_contribution=True,
        contribution_amount=Decimal("500.00"),
        contribution_frequency="MONTHLY"
    )

    db_session.add(goal)
    await db_session.commit()
    await db_session.refresh(goal)
    return goal


@pytest.fixture
async def test_goal_id(test_goal: FinancialGoal) -> str:
    """Return the test goal ID as a string."""
    return str(test_goal.id)


@pytest.fixture
async def async_client(test_app, db_session: AsyncSession):
    """Create an async HTTP client for testing."""
    from database import get_db

    async def override_get_db():
        yield db_session

    test_app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=pytest.importorskip("httpx").ASGITransport(app=test_app),
        base_url="http://testserver"
    ) as client:
        yield client

    test_app.dependency_overrides.clear()
