#!/usr/bin/env python3
"""
Simple test without BeautifulSoup
"""

import requests
import re

def test_simple_login():
    """Test login and API call"""
    
    base_url = "http://127.0.0.1:5001"
    session = requests.Session()
    
    print("🔍 Testing Simple Login and API...")
    
    # Step 1: Get login page
    print("\n1. Getting login page...")
    login_page = session.get(f"{base_url}/auth/login")
    print(f"   Status: {login_page.status_code}")
    
    # Extract CSRF token using regex
    csrf_match = re.search(r'name="csrf_token".*?value="([^"]+)"', login_page.text)
    csrf_token = csrf_match.group(1) if csrf_match else None
    print(f"   CSRF token found: {bool(csrf_token)}")
    
    # Step 2: Login
    print("\n2. Logging in...")
    login_data = {
        'username': 'demo',
        'password': 'password123'
    }
    if csrf_token:
        login_data['csrf_token'] = csrf_token
    
    login_response = session.post(f"{base_url}/auth/login", data=login_data, allow_redirects=True)
    print(f"   Final status: {login_response.status_code}")
    print(f"   Final URL: {login_response.url}")
    
    # Check if we're logged in by looking for dashboard content
    if "Dashboard" in login_response.text or "Welcome" in login_response.text:
        print("   ✅ Login appears successful")
        
        # Step 3: Try API
        print("\n3. Testing API...")
        api_response = session.get(f"{base_url}/api/foods/search-verified?q=milk")
        print(f"   API status: {api_response.status_code}")
        
        if api_response.status_code == 200:
            import json
            data = api_response.json()
            print(f"   ✅ API working! Found {len(data.get('foods', []))} foods")
        else:
            print(f"   ❌ API failed: {api_response.text}")
    else:
        print("   ❌ Login failed")
        print(f"   Response contains: {login_response.text[:200]}...")

if __name__ == '__main__':
    test_simple_login()
