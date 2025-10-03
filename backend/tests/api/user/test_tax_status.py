"""
Tests for tax status API endpoints.

This module tests the complete tax status management API.
"""

import pytest
from datetime import date
from httpx import AsyncClient

from main import app


@pytest.mark.asyncio
class TestTaxStatusAPI:
    """Tests for tax status API endpoints."""

    async def test_create_tax_status(self, async_client: AsyncClient, authenticated_headers):
        """Test creating a new tax status record."""
        data = {
            "effectiveFrom": "2024-04-06",
            "effectiveTo": None,
            "ukTaxResident": True,
            "ukDomicile": "uk_domicile",
            "ukSplitYearTreatment": False,
            "ukRemittanceBasis": False,
            "saTaxResident": False,
            "saOrdinarilyResident": False,
            "dualResident": False,
            "dtaTieBreakerCountry": None
        }

        response = await async_client.post(
            "/api/v1/user/tax-status",
            json=data,
            headers=authenticated_headers
        )

        assert response.status_code == 201
        result = response.json()
        assert result["ukTaxResident"] is True
        assert result["ukDomicile"] == "uk_domicile"
        assert result["effectiveFrom"] == "2024-04-06"

    async def test_get_current_tax_status(self, async_client: AsyncClient, authenticated_headers, test_tax_status):
        """Test getting current tax status."""
        response = await async_client.get(
            "/api/v1/user/tax-status",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        result = response.json()
        assert "id" in result
        assert result["effectiveTo"] is None

    async def test_get_tax_status_history(self, async_client: AsyncClient, authenticated_headers, test_tax_status):
        """Test getting tax status history."""
        response = await async_client.get(
            "/api/v1/user/tax-status/history",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        result = response.json()
        assert isinstance(result, list)
        assert len(result) >= 1

    async def test_get_tax_status_at_date(self, async_client: AsyncClient, authenticated_headers, test_tax_status):
        """Test getting tax status at specific date."""
        response = await async_client.get(
            "/api/v1/user/tax-status/at-date?date=2024-04-06",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        result = response.json()
        assert "id" in result

    async def test_srt_calculator(self, async_client: AsyncClient, authenticated_headers):
        """Test UK SRT calculator endpoint."""
        data = {
            "taxYear": "2023/24",
            "daysInUk": 150,
            "familyTie": True,
            "accommodationTie": True,
            "workTie": False,
            "ninetyDayTie": True,
            "countryTie": False,
            "wasUkResidentPreviousYear": True
        }

        response = await async_client.post(
            "/api/v1/user/tax-status/srt-calculator",
            json=data,
            headers=authenticated_headers
        )

        assert response.status_code == 200
        result = response.json()
        assert "taxResident" in result
        assert "testResult" in result
        assert "explanation" in result

    async def test_sa_presence_test(self, async_client: AsyncClient, authenticated_headers):
        """Test SA presence test endpoint."""
        data = {
            "taxYear": "2023/24",
            "daysInSa": 120,
            "yearMinus1Days": 100,
            "yearMinus2Days": 95,
            "yearMinus3Days": 90,
            "yearMinus4Days": 85
        }

        response = await async_client.post(
            "/api/v1/user/tax-status/sa-presence-test",
            json=data,
            headers=authenticated_headers
        )

        assert response.status_code == 200
        result = response.json()
        assert "taxResident" in result
        assert "testResult" in result
        assert "explanation" in result

    async def test_deemed_domicile(self, async_client: AsyncClient, authenticated_headers, test_tax_status):
        """Test deemed domicile calculation endpoint."""
        response = await async_client.get(
            "/api/v1/user/tax-status/deemed-domicile",
            headers=authenticated_headers
        )

        assert response.status_code == 200
        result = response.json()
        assert "isDeemedDomiciled" in result
        assert "ukResidentYears" in result
        assert "reason" in result

    async def test_validation_effective_dates(self, async_client: AsyncClient, authenticated_headers):
        """Test validation: effectiveTo must be after effectiveFrom."""
        data = {
            "effectiveFrom": "2024-04-06",
            "effectiveTo": "2024-04-05",  # Before effectiveFrom
            "ukTaxResident": True,
            "saTaxResident": False
        }

        response = await async_client.post(
            "/api/v1/user/tax-status",
            json=data,
            headers=authenticated_headers
        )

        assert response.status_code == 422  # Validation error

    async def test_validation_dual_resident_requires_dta(self, async_client: AsyncClient, authenticated_headers):
        """Test validation: dual residents must have DTA tie-breaker."""
        data = {
            "effectiveFrom": "2024-04-06",
            "ukTaxResident": True,
            "saTaxResident": True,
            "dualResident": True,
            "dtaTieBreakerCountry": None  # Missing
        }

        response = await async_client.post(
            "/api/v1/user/tax-status",
            json=data,
            headers=authenticated_headers
        )

        assert response.status_code == 422  # Validation error


@pytest.fixture
async def test_tax_status(db_session, test_user):
    """Create a test tax status record."""
    from models.tax_status import UserTaxStatus, UKDomicileStatus

    tax_status = UserTaxStatus(
        user_id=test_user.id,
        effective_from=date(2024, 4, 6),
        effective_to=None,
        uk_tax_resident=True,
        uk_domicile=UKDomicileStatus.UK_DOMICILE,
        sa_tax_resident=False,
        dual_resident=False
    )

    db_session.add(tax_status)
    await db_session.commit()
    await db_session.refresh(tax_status)

    return tax_status
