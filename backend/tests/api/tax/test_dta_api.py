"""
Tests for DTA Relief API Endpoints

Tests all DTA API endpoints with various scenarios.
"""

import pytest
from fastapi.testclient import TestClient
from decimal import Decimal


class TestEmploymentIncomeEndpoint:
    """Test /employment-income endpoint."""

    def test_uk_resident_with_sa_income(self, client: TestClient):
        """UK resident earning SA income."""
        response = client.post(
            "/api/v1/tax/dta/employment-income",
            json={
                "uk_income": "50000.00",
                "sa_income": "200000.00",
                "uk_resident": True,
                "sa_resident": False
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "uk_tax" in data
        assert "sa_tax" in data
        assert "relief" in data
        assert "net_tax" in data
        assert "explanation" in data

    def test_invalid_negative_income(self, client: TestClient):
        """Negative income should fail validation."""
        response = client.post(
            "/api/v1/tax/dta/employment-income",
            json={
                "uk_income": "-50000.00",
                "sa_income": "200000.00",
                "uk_resident": True,
                "sa_resident": False
            }
        )

        assert response.status_code == 422  # Validation error


class TestDividendEndpoint:
    """Test /dividends endpoint."""

    def test_cross_border_dividend(self, client: TestClient):
        """Cross-border dividend with withholding."""
        response = client.post(
            "/api/v1/tax/dta/dividends",
            json={
                "dividend_amount": "10000.00",
                "source_country": "SA",
                "residence_country": "UK",
                "withholding_rate": None
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "withholding_tax" in data
        assert "foreign_tax_credit" in data
        assert float(data["withholding_tax"]) == 1500.00  # 15%

    def test_custom_withholding_rate(self, client: TestClient):
        """Custom withholding rate."""
        response = client.post(
            "/api/v1/tax/dta/dividends",
            json={
                "dividend_amount": "10000.00",
                "source_country": "SA",
                "residence_country": "UK",
                "withholding_rate": "0.10"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert float(data["withholding_tax"]) == 1000.00  # 10%

    def test_invalid_country_code(self, client: TestClient):
        """Invalid country code."""
        response = client.post(
            "/api/v1/tax/dta/dividends",
            json={
                "dividend_amount": "10000.00",
                "source_country": "US",
                "residence_country": "UK"
            }
        )

        assert response.status_code == 422  # Validation error


class TestInterestEndpoint:
    """Test /interest endpoint."""

    def test_interest_zero_withholding(self, client: TestClient):
        """Interest with 0% withholding."""
        response = client.post(
            "/api/v1/tax/dta/interest",
            json={
                "interest_amount": "5000.00",
                "source_country": "UK",
                "residence_country": "SA"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert float(data["withholding_tax"]) == 0.00
        assert float(data["residence_tax"]) > 0


class TestCapitalGainsEndpoint:
    """Test /capital-gains endpoint."""

    def test_immovable_property(self, client: TestClient):
        """Immovable property taxed at location."""
        response = client.post(
            "/api/v1/tax/dta/capital-gains",
            json={
                "gain_amount": "50000.00",
                "asset_type": "IMMOVABLE_PROPERTY",
                "asset_location": "UK",
                "residence_country": "SA"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["taxing_country"] == "UK"
        assert float(data["tax_amount"]) > 0

    def test_shares_taxed_in_residence(self, client: TestClient):
        """Shares taxed in residence country."""
        response = client.post(
            "/api/v1/tax/dta/capital-gains",
            json={
                "gain_amount": "30000.00",
                "asset_type": "SHARES",
                "asset_location": "UK",
                "residence_country": "SA"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["taxing_country"] == "SA"


class TestPensionEndpoint:
    """Test /pensions endpoint."""

    def test_private_pension(self, client: TestClient):
        """Private pension taxed in residence."""
        response = client.post(
            "/api/v1/tax/dta/pensions",
            json={
                "pension_amount": "30000.00",
                "pension_type": "PRIVATE",
                "source_country": "UK",
                "residence_country": "SA"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["taxing_country"] == "SA"

    def test_government_pension(self, client: TestClient):
        """Government pension taxed in source."""
        response = client.post(
            "/api/v1/tax/dta/pensions",
            json={
                "pension_amount": "30000.00",
                "pension_type": "GOVERNMENT",
                "source_country": "UK",
                "residence_country": "SA"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["taxing_country"] == "UK"


class TestTieBreakerEndpoint:
    """Test /tie-breaker endpoint."""

    def test_permanent_home_uk_only(self, client: TestClient):
        """Permanent home in UK only."""
        response = client.post(
            "/api/v1/tax/dta/tie-breaker",
            json={
                "has_uk_home": True,
                "has_sa_home": False,
                "uk_vital_interests": False,
                "sa_vital_interests": False,
                "uk_habitual_abode": False,
                "sa_habitual_abode": False,
                "nationality": "BOTH"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["sole_residence"] == "UK"
        assert data["test_applied"] == "Permanent home"

    def test_undetermined_residence(self, client: TestClient):
        """Cannot determine residence."""
        response = client.post(
            "/api/v1/tax/dta/tie-breaker",
            json={
                "has_uk_home": True,
                "has_sa_home": True,
                "uk_vital_interests": False,
                "sa_vital_interests": False,
                "uk_habitual_abode": True,
                "sa_habitual_abode": True,
                "nationality": "BOTH"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["sole_residence"] == "UNDETERMINED"
        assert "mutual agreement" in data["explanation"]
