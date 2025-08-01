#!/usr/bin/env python3
"""
Test script to check the food search API functionality
"""

import requests
import sys

def test_food_search():
    """Test the food search API endpoint"""
    
    # Test the API endpoint
    base_url = "http://127.0.0.1:5001"
    
    print("🧪 Testing Food Search API...")
    print("=" * 50)
    
    # First, we need to login to get a session
    login_data = {
        'username': 'demo',
        'password': 'password',  # This might need to be changed
        'csrf_token': ''  # We'll need to handle CSRF
    }
    
    session = requests.Session()
    
    # Get login page to get CSRF token
    try:
        login_page = session.get(f"{base_url}/auth/login")
        print(f"✅ Login page accessible: {login_page.status_code}")
    except Exception as e:
        print(f"❌ Failed to access login page: {e}")
        return
    
    # Try to access API without authentication
    try:
        api_response = session.get(f"{base_url}/api/foods/search-verified?q=rice")
        print(f"📡 API Response without auth: {api_response.status_code}")
        if api_response.status_code == 401:
            print("   ✅ Correctly requires authentication")
        elif api_response.status_code == 200:
            data = api_response.json()
            print(f"   ⚠️  API responded without auth - found {len(data.get('foods', []))} foods")
        else:
            print(f"   ❓ Unexpected response: {api_response.text}")
    except Exception as e:
        print(f"❌ Failed to test API: {e}")

if __name__ == "__main__":
    test_food_search()
