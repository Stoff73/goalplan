"""
Quick verification script to test the dashboard endpoint.

This script:
1. Registers a test user
2. Logs in to get a token
3. Calls the dashboard endpoint
4. Verifies the response format
"""

import asyncio
import httpx
from uuid import uuid4

BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"

async def main():
    print("=" * 60)
    print("Dashboard Endpoint Verification")
    print("=" * 60)

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Generate unique email
        test_email = f"dashboard_test_{uuid4().hex[:8]}@example.com"
        test_password = "TestPass123!"

        print(f"\n1. Registering user: {test_email}")
        register_data = {
            "email": test_email,
            "password": test_password,
            "firstName": "Dashboard",
            "lastName": "Test",
            "country": "UK",
            "termsAccepted": True
        }

        response = await client.post(f"{API_PREFIX}/auth/register", json=register_data)
        if response.status_code != 201:
            print(f"   ❌ Registration failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
        print(f"   ✓ Registration successful")

        # Login to get token
        print(f"\n2. Logging in...")
        login_data = {
            "email": test_email,
            "password": test_password
        }

        response = await client.post(f"{API_PREFIX}/auth/login", json=login_data)
        if response.status_code != 200:
            print(f"   ❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return

        login_result = response.json()
        access_token = login_result.get("accessToken")

        if not access_token:
            print(f"   ❌ No access token in response")
            return

        print(f"   ✓ Login successful")
        print(f"   Token: {access_token[:20]}...")

        # Call dashboard endpoint
        print(f"\n3. Calling dashboard endpoint...")
        headers = {"Authorization": f"Bearer {access_token}"}

        response = await client.get(f"{API_PREFIX}/dashboard/net-worth", headers=headers)

        if response.status_code != 200:
            print(f"   ❌ Dashboard request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return

        print(f"   ✓ Dashboard endpoint accessible")

        # Verify response format
        print(f"\n4. Verifying response format...")
        data = response.json()

        required_fields = [
            'netWorth', 'totalAssets', 'totalLiabilities', 'baseCurrency',
            'asOfDate', 'lastUpdated', 'breakdownByCountry', 'breakdownByAssetClass',
            'breakdownByCurrency', 'trendData', 'changes'
        ]

        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            print(f"   ❌ Missing fields: {', '.join(missing_fields)}")
            return

        print(f"   ✓ All required fields present")

        # Print summary
        print(f"\n5. Dashboard Summary:")
        print(f"   Net Worth: {data['netWorth']} {data['baseCurrency']}")
        print(f"   Total Assets: {data['totalAssets']} {data['baseCurrency']}")
        print(f"   Total Liabilities: {data['totalLiabilities']} {data['baseCurrency']}")
        print(f"   As of Date: {data['asOfDate']}")
        print(f"   Country Breakdowns: {len(data['breakdownByCountry'])}")
        print(f"   Asset Class Breakdowns: {len(data['breakdownByAssetClass'])}")
        print(f"   Currency Breakdowns: {len(data['breakdownByCurrency'])}")
        print(f"   Trend Data Points: {len(data['trendData'])}")

        if data.get('changes'):
            print(f"   Changes:")
            print(f"     - Day: {data['changes']['day']['amount']} ({data['changes']['day']['percentage']}%)")
            print(f"     - Month: {data['changes']['month']['amount']} ({data['changes']['month']['percentage']}%)")
            print(f"     - Year: {data['changes']['year']['amount']} ({data['changes']['year']['percentage']}%)")

        # Test with different currency
        print(f"\n6. Testing with ZAR currency...")
        response = await client.get(
            f"{API_PREFIX}/dashboard/net-worth?baseCurrency=ZAR",
            headers=headers
        )

        if response.status_code != 200:
            print(f"   ❌ ZAR request failed: {response.status_code}")
        else:
            data = response.json()
            print(f"   ✓ ZAR request successful")
            print(f"   Net Worth: {data['netWorth']} {data['baseCurrency']}")

        print(f"\n" + "=" * 60)
        print("✓ Dashboard Endpoint Verification Complete")
        print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
