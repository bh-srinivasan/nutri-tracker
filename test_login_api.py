#!/usr/bin/env python3
"""
Test script to login and check session state
"""

import requests
from bs4 import BeautifulSoup

def test_login_and_api():
    """Test login and then API call"""
    
    base_url = "http://127.0.0.1:5001"
    session = requests.Session()
    
    print("🔍 Testing Login and API Session...")
    
    # Step 1: Get the login page to get CSRF token
    print("\n1. Getting login page for CSRF token...")
    login_page = session.get(f"{base_url}/auth/login")
    print(f"   Login page status: {login_page.status_code}")
    
    # Parse CSRF token
    soup = BeautifulSoup(login_page.content, 'html.parser')
    csrf_token = None
    csrf_input = soup.find('input', {'name': 'csrf_token'})
    if csrf_input:
        csrf_token = csrf_input.get('value')
        print(f"   Found CSRF token: {csrf_token[:20]}...")
    else:
        print("   No CSRF token found")
    
    # Step 2: Login with CSRF token
    print("\n2. Attempting login...")
    login_data = {
        'username': 'demo',
        'password': 'password123'
    }
    if csrf_token:
        login_data['csrf_token'] = csrf_token
    
    login_response = session.post(f"{base_url}/auth/login", data=login_data, allow_redirects=False)
    print(f"   Login response status: {login_response.status_code}")
    print(f"   Login response headers: {dict(login_response.headers)}")
    
    if login_response.status_code == 302:
        print(f"   Redirect location: {login_response.headers.get('Location')}")
        
        # Follow redirect
        dashboard_response = session.get(login_response.headers.get('Location'))
        print(f"   Dashboard response status: {dashboard_response.status_code}")
        
        # Step 3: Try the API now
        print("\n3. Testing API after login...")
        api_response = session.get(f"{base_url}/api/foods/search-verified?q=milk")
        print(f"   API response status: {api_response.status_code}")
        print(f"   API response: {api_response.text[:200]}...")
        
    else:
        print(f"   Login failed: {login_response.text[:200]}...")

if __name__ == '__main__':
    test_login_and_api()
