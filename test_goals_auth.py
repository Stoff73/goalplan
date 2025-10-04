#!/usr/bin/env python3
"""Test Goals API endpoint with authentication"""

import requests

# Login to get token
login_response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={"email": "test@goalplan.com", "password": "TestPass@123"}
)

if login_response.status_code == 200:
    token = login_response.json()["accessToken"]
    print(f"✅ Login successful")
    print(f"Token: {token[:50]}...")

    # Test Goals endpoint
    goals_response = requests.get(
        "http://localhost:8000/api/v1/goals/overview",
        headers={"Authorization": f"Bearer {token}"}
    )

    print(f"\n🎯 Goals API Response:")
    print(f"Status Code: {goals_response.status_code}")

    if goals_response.status_code == 200:
        print(f"✅ SUCCESS! Goals endpoint returned 200 with authentication")
        print(f"Response: {goals_response.json()}")
        print(f"\n🎉 DATABASE FIX VERIFIED!")
        print(f"   - Database exists ✅")
        print(f"   - Backend can query database ✅")
        print(f"   - Goals endpoint working ✅")
    else:
        print(f"Response: {goals_response.text}")
else:
    print(f"❌ Login failed: {login_response.status_code}")
    print(f"Response: {login_response.text}")
