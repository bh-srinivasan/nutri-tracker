#!/usr/bin/env python3
"""Test the fixed API endpoint for food servings with authentication."""

import requests
import json

# Create a session to maintain cookies
session = requests.Session()

# Login first
login_url = "http://127.0.0.1:5001/auth/login"
login_data = {
    'username': 'testuser',
    'password': 'testpass123'
}

print("🔐 Attempting to login as testuser...")
login_response = session.post(login_url, data=login_data)

if login_response.status_code == 200 and 'dashboard' in login_response.url:
    print("✅ Login successful!")
    
    # Now test the API endpoint
    api_url = "http://127.0.0.1:5001/api/foods/1/servings"
    print(f"🧪 Testing API endpoint: {api_url}")
    
    api_response = session.get(api_url)
    print(f"Status Code: {api_response.status_code}")
    
    if api_response.status_code == 200:
        data = api_response.json()
        print("✅ API call successful!")
        print(json.dumps(data, indent=2))
    else:
        print(f"❌ API call failed with status {api_response.status_code}")
        print(f"Response: {api_response.text}")
        
else:
    print(f"❌ Login failed with status {login_response.status_code}")
    print("Response:", login_response.text[:500])
