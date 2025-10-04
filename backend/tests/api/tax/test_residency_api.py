"""
Tests for Tax Residency API Endpoints

Tests UK SRT and SA Presence Test API endpoints.
"""

import pytest
from fastapi.testclient import TestClient


class TestUKSRTEndpoint:
    """Test /uk-srt endpoint."""

    def test_automatic_overseas_test(self, client: TestClient):
        """Fewer than 16 days - automatically not resident."""
        response = client.post(
            "/api/v1/tax/residency/uk-srt",
            json={
                "days_in_uk": 10,
                "has_family": False,
                "has_accommodation": False,
                "accommodation_days": 0,
                "work_days": 0,
                "prior_year_days": [0, 0],
                "prior_residence": [False, False, False],
                "full_time_work_abroad": False,
                "uk_days_while_working_abroad": 0,
                "has_uk_home": False,
                "days_at_uk_home": 0,
                "full_time_work_uk": False
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["resident"] is False
        assert data["determination_method"] == "Automatic Overseas Test"

    def test_automatic_uk_test_183_days(self, client: TestClient):
        """183+ days - automatically resident."""
        response = client.post(
            "/api/v1/tax/residency/uk-srt",
            json={
                "days_in_uk": 183,
                "has_family": False,
                "has_accommodation": False,
                "accommodation_days": 0,
                "work_days": 0,
                "prior_year_days": [0, 0],
                "prior_residence": [False, False, False]
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["resident"] is True
        assert data["determination_method"] == "Automatic UK Test"

    def test_sufficient_ties_arriver(self, client: TestClient):
        """Arriver with sufficient ties."""
        response = client.post(
            "/api/v1/tax/residency/uk-srt",
            json={
                "days_in_uk": 100,
                "has_family": True,
                "has_accommodation": True,
                "accommodation_days": 50,
                "work_days": 45,
                "prior_year_days": [100, 95],
                "prior_residence": [False, False, False]
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["determination_method"] == "Sufficient Ties Test"
        assert data["ties_count"] >= 3
        assert data["resident"] is True  # Arriver, 100 days, 3+ ties

    def test_sufficient_ties_leaver(self, client: TestClient):
        """Leaver with sufficient ties."""
        response = client.post(
            "/api/v1/tax/residency/uk-srt",
            json={
                "days_in_uk": 100,
                "has_family": True,
                "has_accommodation": True,
                "accommodation_days": 50,
                "work_days": 0,
                "prior_year_days": [100, 95],
                "prior_residence": [True, True, False],
                "days_in_other_countries": {"SA": 200}
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["determination_method"] == "Sufficient Ties Test"
        assert data["resident"] is True  # Leaver, 100 days, 2 ties

    def test_invalid_days_negative(self, client: TestClient):
        """Negative days should fail validation."""
        response = client.post(
            "/api/v1/tax/residency/uk-srt",
            json={
                "days_in_uk": -10
            }
        )

        assert response.status_code == 422

    def test_invalid_days_over_366(self, client: TestClient):
        """More than 366 days should fail validation."""
        response = client.post(
            "/api/v1/tax/residency/uk-srt",
            json={
                "days_in_uk": 367
            }
        )

        assert response.status_code == 422


class TestSAPresenceEndpoint:
    """Test /sa-presence endpoint."""

    def test_ordinarily_resident(self, client: TestClient):
        """Ordinarily resident - automatically resident."""
        response = client.post(
            "/api/v1/tax/residency/sa-presence",
            json={
                "days_current_year": 0,
                "days_prior_years": [0, 0, 0, 0, 0],
                "ordinarily_resident": True
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["resident"] is True
        assert data["test_passed"] == "Ordinarily resident"

    def test_physical_presence_pass(self, client: TestClient):
        """Meets physical presence requirements."""
        response = client.post(
            "/api/v1/tax/residency/sa-presence",
            json={
                "days_current_year": 120,
                "days_prior_years": [110, 105, 100, 95, 92],
                "ordinarily_resident": False
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["resident"] is True
        assert data["test_passed"] == "Physical presence"

    def test_physical_presence_fail_current_year(self, client: TestClient):
        """Fails current year requirement (<=91 days)."""
        response = client.post(
            "/api/v1/tax/residency/sa-presence",
            json={
                "days_current_year": 91,
                "days_prior_years": [100, 100, 100, 100, 100],
                "ordinarily_resident": False
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["resident"] is False
        assert "not more than 91 days" in data["explanation"]

    def test_physical_presence_fail_prior_year(self, client: TestClient):
        """Fails prior year requirement."""
        response = client.post(
            "/api/v1/tax/residency/sa-presence",
            json={
                "days_current_year": 120,
                "days_prior_years": [100, 91, 100, 100, 100],
                "ordinarily_resident": False
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["resident"] is False

    def test_physical_presence_fail_total(self, client: TestClient):
        """Fails total days requirement (<915)."""
        response = client.post(
            "/api/v1/tax/residency/sa-presence",
            json={
                "days_current_year": 120,
                "days_prior_years": [183, 183, 183, 183, 182],
                "ordinarily_resident": False
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["resident"] is False
        assert "<915" in data["explanation"]

    def test_invalid_days_negative(self, client: TestClient):
        """Negative days should fail validation."""
        response = client.post(
            "/api/v1/tax/residency/sa-presence",
            json={
                "days_current_year": -10,
                "days_prior_years": [100, 100, 100, 100, 100]
            }
        )

        assert response.status_code == 422

    def test_invalid_days_over_366(self, client: TestClient):
        """More than 366 days should fail validation."""
        response = client.post(
            "/api/v1/tax/residency/sa-presence",
            json={
                "days_current_year": 367,
                "days_prior_years": [100, 100, 100, 100, 100]
            }
        )

        assert response.status_code == 422
