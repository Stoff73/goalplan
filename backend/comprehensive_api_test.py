"""
Comprehensive API Testing Script
Tests all API endpoints for the GoalPlan application
"""
import asyncio
import httpx
from typing import Dict, List, Optional

# Configuration
API_BASE = "http://localhost:8000"
TEST_USER = {
    "email": "testuser@example.com",
    "password": "TestPassword123"
}

class APITester:
    def __init__(self):
        self.client = None
        self.token = None
        self.results = []

    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def login(self):
        """Login and get access token"""
        print("\n" + "="*60)
        print("AUTHENTICATION TEST")
        print("="*60)

        try:
            response = await self.client.post(
                f"{API_BASE}/api/v1/auth/login",
                json=TEST_USER
            )
            print(f"✓ Login status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                # Handle both camelCase and snake_case
                self.token = data.get("accessToken") or data.get("access_token")
                print(f"✓ Token obtained: {self.token[:50]}...")
                self.results.append({
                    "endpoint": "POST /api/v1/auth/login",
                    "status": response.status_code,
                    "success": True
                })
                return True
            else:
                print(f"✗ Login failed: {response.json()}")
                self.results.append({
                    "endpoint": "POST /api/v1/auth/login",
                    "status": response.status_code,
                    "success": False,
                    "error": response.text
                })
                return False
        except Exception as e:
            print(f"✗ Login error: {e}")
            return False

    async def test_endpoint(self, method: str, path: str, name: str,
                           data: Optional[Dict] = None,
                           expected_statuses: List[int] = [200, 201]):
        """Test a single endpoint"""
        url = f"{API_BASE}{path}"
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}

        try:
            if method == "GET":
                response = await self.client.get(url, headers=headers)
            elif method == "POST":
                response = await self.client.post(url, headers=headers, json=data or {})
            elif method == "PUT":
                response = await self.client.put(url, headers=headers, json=data or {})
            elif method == "DELETE":
                response = await self.client.delete(url, headers=headers)
            else:
                print(f"  ✗ Unknown method: {method}")
                return

            success = response.status_code in expected_statuses
            symbol = "✓" if success else "✗"

            # Determine response type
            try:
                response_data = response.json()
                data_preview = str(response_data)[:100]
            except:
                data_preview = response.text[:100]

            print(f"  {symbol} {method} {path}")
            print(f"     Status: {response.status_code}")
            if not success or response.status_code >= 400:
                print(f"     Response: {data_preview}")

            self.results.append({
                "endpoint": f"{method} {path}",
                "name": name,
                "status": response.status_code,
                "success": success,
                "response_preview": data_preview if not success else None
            })

            return response

        except Exception as e:
            print(f"  ✗ {method} {path}")
            print(f"     Error: {str(e)}")
            self.results.append({
                "endpoint": f"{method} {path}",
                "name": name,
                "status": None,
                "success": False,
                "error": str(e)
            })
            return None

    async def test_user_endpoints(self):
        """Test user-related endpoints"""
        print("\n" + "="*60)
        print("USER ENDPOINTS")
        print("="*60)

        await self.test_endpoint("GET", "/api/v1/users/me", "Get current user")
        await self.test_endpoint("PUT", "/api/v1/users/profile", "Update user profile",
                                data={"firstName": "Test", "lastName": "User"})
        await self.test_endpoint("GET", "/api/v1/user/profile", "Get user profile")

    async def test_tax_status_endpoints(self):
        """Test tax status endpoints"""
        print("\n" + "="*60)
        print("TAX STATUS ENDPOINTS")
        print("="*60)

        await self.test_endpoint("GET", "/api/v1/tax-status", "Get tax status",
                                expected_statuses=[200, 404])
        await self.test_endpoint("GET", "/api/v1/user/tax-status/current", "Get current tax status",
                                expected_statuses=[200, 404])

    async def test_income_endpoints(self):
        """Test income endpoints"""
        print("\n" + "="*60)
        print("INCOME ENDPOINTS")
        print("="*60)

        await self.test_endpoint("GET", "/api/v1/income", "Get income list",
                                expected_statuses=[200])
        await self.test_endpoint("GET", "/api/v1/user/income", "Get user income",
                                expected_statuses=[200])

    async def test_dashboard_endpoints(self):
        """Test dashboard endpoints"""
        print("\n" + "="*60)
        print("DASHBOARD ENDPOINTS")
        print("="*60)

        await self.test_endpoint("GET", "/api/v1/dashboard/summary", "Get dashboard summary",
                                expected_statuses=[200, 404])
        await self.test_endpoint("GET", "/api/v1/dashboard/net-worth", "Get net worth",
                                expected_statuses=[200, 404])

    async def test_protection_endpoints(self):
        """Test protection endpoints"""
        print("\n" + "="*60)
        print("PROTECTION ENDPOINTS")
        print("="*60)

        await self.test_endpoint("GET", "/api/v1/protection/policies", "Get protection policies",
                                expected_statuses=[200])
        await self.test_endpoint("GET", "/api/v1/protection/coverage", "Get coverage summary",
                                expected_statuses=[200, 404])

    async def test_investment_endpoints(self):
        """Test investment endpoints"""
        print("\n" + "="*60)
        print("INVESTMENT ENDPOINTS")
        print("="*60)

        await self.test_endpoint("GET", "/api/v1/investments/portfolio", "Get investment portfolio",
                                expected_statuses=[200, 404])
        await self.test_endpoint("GET", "/api/v1/investments/accounts", "Get investment accounts",
                                expected_statuses=[200])

    async def test_retirement_endpoints(self):
        """Test retirement endpoints"""
        print("\n" + "="*60)
        print("RETIREMENT ENDPOINTS")
        print("="*60)

        await self.test_endpoint("GET", "/api/v1/retirement/overview", "Get retirement overview",
                                expected_statuses=[200, 404])
        await self.test_endpoint("GET", "/api/v1/retirement/uk-pensions", "Get UK pensions",
                                expected_statuses=[200])
        await self.test_endpoint("GET", "/api/v1/retirement/sa-funds", "Get SA retirement funds",
                                expected_statuses=[200])

    async def test_iht_endpoints(self):
        """Test IHT endpoints"""
        print("\n" + "="*60)
        print("IHT ENDPOINTS")
        print("="*60)

        await self.test_endpoint("GET", "/api/v1/iht/summary", "Get IHT summary",
                                expected_statuses=[200, 404])
        await self.test_endpoint("GET", "/api/v1/iht/assets", "Get estate assets",
                                expected_statuses=[200])

    async def test_goals_endpoints(self):
        """Test goals endpoints"""
        print("\n" + "="*60)
        print("GOALS ENDPOINTS")
        print("="*60)

        await self.test_endpoint("GET", "/api/v1/goals", "Get goals list",
                                expected_statuses=[200])
        await self.test_endpoint("GET", "/api/v1/goals/summary", "Get goals summary",
                                expected_statuses=[200, 404])

    async def test_scenarios_endpoints(self):
        """Test scenarios endpoints"""
        print("\n" + "="*60)
        print("SCENARIOS ENDPOINTS")
        print("="*60)

        await self.test_endpoint("GET", "/api/v1/scenarios", "Get scenarios list",
                                expected_statuses=[200])

    async def test_ai_endpoints(self):
        """Test AI endpoints"""
        print("\n" + "="*60)
        print("AI ENDPOINTS")
        print("="*60)

        await self.test_endpoint("GET", "/api/v1/ai/insights", "Get AI insights",
                                expected_statuses=[200, 404])

    async def test_recommendations_endpoints(self):
        """Test recommendations endpoints"""
        print("\n" + "="*60)
        print("RECOMMENDATIONS ENDPOINTS")
        print("="*60)

        await self.test_endpoint("GET", "/api/v1/recommendations", "Get recommendations",
                                expected_statuses=[200])

    async def test_tax_endpoints(self):
        """Test tax calculation endpoints"""
        print("\n" + "="*60)
        print("TAX CALCULATION ENDPOINTS")
        print("="*60)

        await self.test_endpoint("GET", "/api/v1/tax/uk/summary", "Get UK tax summary",
                                expected_statuses=[200, 404])
        await self.test_endpoint("GET", "/api/v1/tax/sa/summary", "Get SA tax summary",
                                expected_statuses=[200, 404])

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)

        total = len(self.results)
        successful = sum(1 for r in self.results if r["success"])
        failed = total - successful

        print(f"\nTotal endpoints tested: {total}")
        print(f"Successful: {successful} ({successful/total*100:.1f}%)")
        print(f"Failed: {failed} ({failed/total*100:.1f}%)")

        if failed > 0:
            print("\n" + "-"*60)
            print("FAILED ENDPOINTS:")
            print("-"*60)
            for result in self.results:
                if not result["success"]:
                    print(f"\n{result['endpoint']}")
                    print(f"  Status: {result.get('status', 'ERROR')}")
                    if "error" in result:
                        print(f"  Error: {result['error']}")
                    elif "response_preview" in result:
                        print(f"  Response: {result['response_preview']}")

        print("\n" + "="*60)
        print("CRITICAL ISSUES FOUND:")
        print("="*60)

        # Identify critical failures
        critical_endpoints = [
            "POST /api/v1/auth/login",
            "GET /api/v1/users/me",
            "GET /api/v1/dashboard/summary"
        ]

        critical_failures = [
            r for r in self.results
            if r["endpoint"] in critical_endpoints and not r["success"]
        ]

        if critical_failures:
            for failure in critical_failures:
                print(f"  ✗ {failure['endpoint']} - CRITICAL")
        else:
            print("  ✓ All critical endpoints working")

async def main():
    print("="*60)
    print("GOALPLAN API COMPREHENSIVE TEST")
    print("="*60)

    async with APITester() as tester:
        # Login first
        if not await tester.login():
            print("\n✗ FATAL: Cannot proceed without authentication")
            return

        # Test all endpoints
        await tester.test_user_endpoints()
        await tester.test_tax_status_endpoints()
        await tester.test_income_endpoints()
        await tester.test_dashboard_endpoints()
        await tester.test_protection_endpoints()
        await tester.test_investment_endpoints()
        await tester.test_retirement_endpoints()
        await tester.test_iht_endpoints()
        await tester.test_goals_endpoints()
        await tester.test_scenarios_endpoints()
        await tester.test_ai_endpoints()
        await tester.test_recommendations_endpoints()
        await tester.test_tax_endpoints()

        # Print summary
        tester.print_summary()

if __name__ == "__main__":
    asyncio.run(main())
