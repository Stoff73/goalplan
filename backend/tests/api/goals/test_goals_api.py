"""
Comprehensive tests for Goals API endpoints.

Tests cover:
- Goal CRUD operations
- Authentication and authorization
- Validation and error handling
- Filtering and sorting
- Milestone management
- Account linking
- Goal overview/statistics
- Optimization and allocation
"""

import pytest
from httpx import AsyncClient
from decimal import Decimal
from datetime import date, timedelta
from uuid import uuid4

from models.goal import GoalType, GoalPriority, GoalStatus


# ============================================================================
# GOAL CREATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_create_goal_success(
    async_client: AsyncClient,
    test_user_token: str
):
    """Test successful goal creation."""
    target_date = date.today() + timedelta(days=365)

    response = await async_client.post(
        "/api/v1/goals",
        json={
            "goal_name": "House Deposit",
            "goal_type": "PROPERTY_PURCHASE",
            "description": "Save for house deposit",
            "target_amount": "30000.00",
            "currency": "GBP",
            "target_date": target_date.isoformat(),
            "priority": "HIGH",
            "auto_contribution": True,
            "contribution_amount": "500.00",
            "contribution_frequency": "MONTHLY"
        },
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["goal_name"] == "House Deposit"
    assert data["goal_type"] == "PROPERTY_PURCHASE"
    assert Decimal(data["target_amount"]) == Decimal("30000.00")
    assert data["currency"] == "GBP"
    assert data["priority"] == "HIGH"
    assert data["status"] == "NOT_STARTED"
    assert Decimal(data["current_amount"]) == Decimal("0.00")
    assert Decimal(data["progress_percentage"]) == Decimal("0.00")
    assert data["auto_contribution"] is True
    assert "id" in data
    assert "user_id" in data


@pytest.mark.asyncio
async def test_create_goal_without_auto_contribution(
    async_client: AsyncClient,
    test_user_token: str
):
    """Test goal creation without auto-contribution."""
    target_date = date.today() + timedelta(days=365)

    response = await async_client.post(
        "/api/v1/goals",
        json={
            "goal_name": "Emergency Fund",
            "goal_type": "EMERGENCY_FUND",
            "target_amount": "10000.00",
            "currency": "GBP",
            "target_date": target_date.isoformat(),
            "priority": "HIGH"
        },
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["auto_contribution"] is False
    assert data["contribution_amount"] is None
    assert data["contribution_frequency"] is None


@pytest.mark.asyncio
async def test_create_goal_unauthorized(async_client: AsyncClient):
    """Test goal creation without authentication."""
    target_date = date.today() + timedelta(days=365)

    response = await async_client.post(
        "/api/v1/goals",
        json={
            "goal_name": "Test Goal",
            "goal_type": "RETIREMENT",
            "target_amount": "10000.00",
            "target_date": target_date.isoformat()
        }
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_goal_invalid_target_date(
    async_client: AsyncClient,
    test_user_token: str
):
    """Test goal creation with target date too soon."""
    target_date = date.today() + timedelta(days=90)  # Less than 6 months

    response = await async_client.post(
        "/api/v1/goals",
        json={
            "goal_name": "Invalid Goal",
            "goal_type": "HOLIDAY_TRAVEL",
            "target_amount": "5000.00",
            "target_date": target_date.isoformat()
        },
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_create_goal_invalid_amount(
    async_client: AsyncClient,
    test_user_token: str
):
    """Test goal creation with negative target amount."""
    target_date = date.today() + timedelta(days=365)

    response = await async_client.post(
        "/api/v1/goals",
        json={
            "goal_name": "Invalid Goal",
            "goal_type": "CUSTOM",
            "target_amount": "-1000.00",
            "target_date": target_date.isoformat()
        },
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 422  # Validation error


# ============================================================================
# GOAL RETRIEVAL TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_list_goals_success(
    async_client: AsyncClient,
    test_user_token: str,
    test_goal_id: str
):
    """Test listing user goals."""
    response = await async_client.get(
        "/api/v1/goals",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    # Check structure
    goal = data[0]
    assert "id" in goal
    assert "goal_name" in goal
    assert "goal_type" in goal
    assert "target_amount" in goal
    assert "current_amount" in goal
    assert "progress_percentage" in goal
    assert "status" in goal


@pytest.mark.asyncio
async def test_list_goals_with_filters(
    async_client: AsyncClient,
    test_user_token: str,
    test_goal_id: str
):
    """Test listing goals with filters."""
    response = await async_client.get(
        "/api/v1/goals?priority=HIGH&status=NOT_STARTED",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 200
    data = response.json()

    # Verify all results match filters
    for goal in data:
        assert goal["priority"] == "HIGH"
        assert goal["status"] in ["NOT_STARTED", "IN_PROGRESS", "ON_TRACK"]


@pytest.mark.asyncio
async def test_list_goals_sorted_by_target_date(
    async_client: AsyncClient,
    test_user_token: str
):
    """Test listing goals sorted by target date."""
    response = await async_client.get(
        "/api/v1/goals?sort_by=target_date",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 200
    data = response.json()

    if len(data) > 1:
        # Verify ascending order
        for i in range(len(data) - 1):
            assert data[i]["target_date"] <= data[i + 1]["target_date"]


@pytest.mark.asyncio
async def test_get_goal_success(
    async_client: AsyncClient,
    test_user_token: str,
    test_goal_id: str
):
    """Test getting a single goal."""
    response = await async_client.get(
        f"/api/v1/goals/{test_goal_id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_goal_id
    assert "goal_name" in data
    assert "target_amount" in data
    assert "days_remaining" in data
    assert "on_track" in data


@pytest.mark.asyncio
async def test_get_goal_not_found(
    async_client: AsyncClient,
    test_user_token: str
):
    """Test getting non-existent goal."""
    fake_id = str(uuid4())

    response = await async_client.get(
        f"/api/v1/goals/{fake_id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_goal_forbidden(
    async_client: AsyncClient,
    other_user_token: str,
    test_goal_id: str
):
    """Test accessing another user's goal."""
    response = await async_client.get(
        f"/api/v1/goals/{test_goal_id}",
        headers={"Authorization": f"Bearer {other_user_token}"}
    )

    assert response.status_code == 403


# ============================================================================
# GOAL UPDATE TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_update_goal_success(
    async_client: AsyncClient,
    test_user_token: str,
    test_goal_id: str
):
    """Test updating goal details."""
    response = await async_client.put(
        f"/api/v1/goals/{test_goal_id}",
        json={
            "goal_name": "Updated Goal Name",
            "target_amount": "35000.00",
            "priority": "MEDIUM"
        },
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["goal_name"] == "Updated Goal Name"
    assert Decimal(data["target_amount"]) == Decimal("35000.00")
    assert data["priority"] == "MEDIUM"


@pytest.mark.asyncio
async def test_update_goal_partial(
    async_client: AsyncClient,
    test_user_token: str,
    test_goal_id: str
):
    """Test partial goal update."""
    response = await async_client.put(
        f"/api/v1/goals/{test_goal_id}",
        json={"description": "Updated description only"},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Updated description only"


@pytest.mark.asyncio
async def test_update_goal_not_found(
    async_client: AsyncClient,
    test_user_token: str
):
    """Test updating non-existent goal."""
    fake_id = str(uuid4())

    response = await async_client.put(
        f"/api/v1/goals/{fake_id}",
        json={"goal_name": "New Name"},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_goal_forbidden(
    async_client: AsyncClient,
    other_user_token: str,
    test_goal_id: str
):
    """Test updating another user's goal."""
    response = await async_client.put(
        f"/api/v1/goals/{test_goal_id}",
        json={"goal_name": "Unauthorized Update"},
        headers={"Authorization": f"Bearer {other_user_token}"}
    )

    assert response.status_code == 403


# ============================================================================
# MILESTONE TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_add_milestone_success(
    async_client: AsyncClient,
    test_user_token: str,
    test_goal_id: str
):
    """Test adding milestone to goal."""
    milestone_date = date.today() + timedelta(days=180)

    response = await async_client.post(
        f"/api/v1/goals/{test_goal_id}/milestones",
        json={
            "milestone_name": "50% Progress",
            "milestone_target_amount": "15000.00",
            "milestone_target_date": milestone_date.isoformat()
        },
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["milestone_name"] == "50% Progress"
    assert Decimal(data["milestone_target_amount"]) == Decimal("15000.00")
    assert data["status"] == "PENDING"
    assert "id" in data
    assert "goal_id" in data


@pytest.mark.asyncio
async def test_add_milestone_invalid_date(
    async_client: AsyncClient,
    test_user_token: str,
    test_goal_id: str
):
    """Test adding milestone with invalid date."""
    # Date in the past
    milestone_date = date.today() - timedelta(days=30)

    response = await async_client.post(
        f"/api/v1/goals/{test_goal_id}/milestones",
        json={
            "milestone_name": "Invalid Milestone",
            "milestone_target_amount": "5000.00",
            "milestone_target_date": milestone_date.isoformat()
        },
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_add_milestone_forbidden(
    async_client: AsyncClient,
    other_user_token: str,
    test_goal_id: str
):
    """Test adding milestone to another user's goal."""
    milestone_date = date.today() + timedelta(days=180)

    response = await async_client.post(
        f"/api/v1/goals/{test_goal_id}/milestones",
        json={
            "milestone_name": "Unauthorized Milestone",
            "milestone_target_amount": "5000.00",
            "milestone_target_date": milestone_date.isoformat()
        },
        headers={"Authorization": f"Bearer {other_user_token}"}
    )

    assert response.status_code == 403


# ============================================================================
# ACCOUNT LINKING TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_link_account_success(
    async_client: AsyncClient,
    test_user_token: str,
    test_goal_id: str
):
    """Test linking account to goal."""
    account_id = str(uuid4())

    response = await async_client.post(
        f"/api/v1/goals/{test_goal_id}/link-account",
        params={
            "account_id": account_id,
            "account_type": "SAVINGS_ACCOUNT"
        },
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert account_id in data["linked_accounts"]


@pytest.mark.asyncio
async def test_link_account_forbidden(
    async_client: AsyncClient,
    other_user_token: str,
    test_goal_id: str
):
    """Test linking account to another user's goal."""
    account_id = str(uuid4())

    response = await async_client.post(
        f"/api/v1/goals/{test_goal_id}/link-account",
        params={
            "account_id": account_id,
            "account_type": "ISA"
        },
        headers={"Authorization": f"Bearer {other_user_token}"}
    )

    assert response.status_code == 403


# ============================================================================
# GOALS OVERVIEW TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_goals_overview_success(
    async_client: AsyncClient,
    test_user_token: str,
    test_goal_id: str
):
    """Test getting goals overview."""
    response = await async_client.get(
        "/api/v1/goals/overview",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 200
    data = response.json()

    # Check all required fields
    assert "total_goals" in data
    assert "active_goals" in data
    assert "achieved_goals" in data
    assert "total_target_amount" in data
    assert "total_current_amount" in data
    assert "overall_progress_percentage" in data
    assert "on_track_count" in data
    assert "at_risk_count" in data

    # Validate data types
    assert isinstance(data["total_goals"], int)
    assert isinstance(data["active_goals"], int)
    assert data["total_goals"] >= data["active_goals"]


@pytest.mark.asyncio
async def test_goals_overview_empty(
    async_client: AsyncClient,
    new_user_token: str
):
    """Test goals overview with no goals."""
    response = await async_client.get(
        "/api/v1/goals/overview",
        headers={"Authorization": f"Bearer {new_user_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total_goals"] == 0
    assert data["active_goals"] == 0
    assert Decimal(data["total_target_amount"]) == Decimal("0.00")


# ============================================================================
# OPTIMIZATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_optimize_allocation_success(
    async_client: AsyncClient,
    test_user_token: str,
    test_goal_id: str
):
    """Test goal allocation optimization."""
    response = await async_client.post(
        "/api/v1/goals/optimize",
        params={"available_monthly_savings": "1000.00"},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 200
    data = response.json()

    # Check required fields
    assert "total_available" in data
    assert "total_allocated" in data
    assert "total_required" in data
    assert "unallocated" in data
    assert "allocations" in data
    assert "fully_funded_goals" in data
    assert "partially_funded_goals" in data
    assert "unfunded_goals" in data

    # Validate allocation logic
    assert Decimal(data["total_available"]) == Decimal("1000.00")
    total_allocated = Decimal(data["total_allocated"])
    unallocated = Decimal(data["unallocated"])
    assert total_allocated + unallocated == Decimal("1000.00")

    # Check allocations structure
    if data["allocations"]:
        allocation = data["allocations"][0]
        assert "goal_id" in allocation
        assert "goal_name" in allocation
        assert "required_monthly" in allocation
        assert "allocated_monthly" in allocation
        assert "funding_status" in allocation


@pytest.mark.asyncio
async def test_optimize_allocation_insufficient_funds(
    async_client: AsyncClient,
    test_user_token: str,
    test_goal_id: str
):
    """Test optimization with insufficient funds."""
    response = await async_client.post(
        "/api/v1/goals/optimize",
        params={"available_monthly_savings": "100.00"},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 200
    data = response.json()

    # Should have unfunded or partially funded goals
    assert len(data["unfunded_goals"]) > 0 or len(data["partially_funded_goals"]) > 0


@pytest.mark.asyncio
async def test_optimize_allocation_negative_amount(
    async_client: AsyncClient,
    test_user_token: str
):
    """Test optimization with invalid (negative) amount."""
    response = await async_client.post(
        "/api/v1/goals/optimize",
        params={"available_monthly_savings": "-100.00"},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 422  # Validation error


# ============================================================================
# EDGE CASES AND ERROR HANDLING
# ============================================================================

@pytest.mark.asyncio
async def test_create_goal_limit_exceeded(
    async_client: AsyncClient,
    test_user_token: str
):
    """Test creating more than 10 goals (limit)."""
    target_date = date.today() + timedelta(days=365)

    # Create 10 goals
    for i in range(10):
        response = await async_client.post(
            "/api/v1/goals",
            json={
                "goal_name": f"Goal {i+1}",
                "goal_type": "CUSTOM",
                "target_amount": "1000.00",
                "target_date": target_date.isoformat()
            },
            headers={"Authorization": f"Bearer {test_user_token}"}
        )

    # 11th goal should fail
    response = await async_client.post(
        "/api/v1/goals",
        json={
            "goal_name": "Goal 11",
            "goal_type": "CUSTOM",
            "target_amount": "1000.00",
            "target_date": target_date.isoformat()
        },
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 400
    assert "maximum" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_missing_required_fields(
    async_client: AsyncClient,
    test_user_token: str
):
    """Test creating goal with missing required fields."""
    response = await async_client.post(
        "/api/v1/goals",
        json={"goal_name": "Incomplete Goal"},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_goals_unauthorized(async_client: AsyncClient):
    """Test listing goals without authentication."""
    response = await async_client.get("/api/v1/goals")
    assert response.status_code == 401
