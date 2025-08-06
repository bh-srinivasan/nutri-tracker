#!/usr/bin/env python3
"""
Test the actual user flow for the search functionality.
This will login as a regular user and test the search.
"""

import requests
import json

def test_user_login_and_search():
    base_url = "http://localhost:5001"
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    print("1. Testing login page access...")
    login_page = session.get(f"{base_url}/auth/login")
    print(f"   Login page status: {login_page.status_code}")
    
    print("2. Attempting to login as testfood user...")
    login_data = {
        'username': 'testfood',
        'password': 'test123'  # We just set this password
    }
    
    login_response = session.post(f"{base_url}/auth/login", data=login_data, allow_redirects=False)
    print(f"   Login attempt: {login_response.status_code}")
    
    login_success = False
    if login_response.status_code == 302:  # Redirect indicates success
        login_success = True
        print(f"   ✅ Login successful")
    else:
        print(f"   ❌ Login failed, response text preview:")
        print(f"   {login_response.text[:200]}...")
        
        # Also try testsearch user
        login_data = {'username': 'testsearch', 'password': 'search123'}
        login_response = session.post(f"{base_url}/auth/login", data=login_data, allow_redirects=False)
        if login_response.status_code == 302:
            login_success = True
            print(f"   ✅ Login successful with testsearch user")
        else:
            print(f"   ❌ Both logins failed")
    
    if not login_success:
        print("   ❌ Could not login with any password, trying to access dashboard anyway...")
    
    print("3. Accessing log meal page...")
    log_meal_response = session.get(f"{base_url}/dashboard/log-meal")
    print(f"   Log meal page status: {log_meal_response.status_code}")
    
    if log_meal_response.status_code == 200:
        print("   ✅ Successfully accessed log meal page")
        
        # Check if the page contains the search input
        if 'id="foodSearch"' in log_meal_response.text:
            print("   ✅ Found foodSearch input element")
        else:
            print("   ❌ foodSearch input element not found")
            
        # Check if the JavaScript is present
        if 'EnhancedMealLogger' in log_meal_response.text:
            print("   ✅ Found EnhancedMealLogger JavaScript")
        else:
            print("   ❌ EnhancedMealLogger JavaScript not found")
            
    elif log_meal_response.status_code == 302:
        print(f"   ⚠️ Redirected (probably to login): {log_meal_response.headers.get('Location')}")
    else:
        print(f"   ❌ Failed to access log meal page")
    
    print("4. Testing search API directly...")
    search_response = session.get(f"{base_url}/api/foods/search-verified?q=milk")
    print(f"   Search API status: {search_response.status_code}")
    
    if search_response.status_code == 200:
        try:
            data = search_response.json()
            print(f"   ✅ Search API returned {len(data)} results")
            if data:
                print(f"   First result: {data[0].get('name', 'No name')}")
        except json.JSONDecodeError:
            print("   ❌ Search API returned invalid JSON")
    else:
        print(f"   ❌ Search API failed")
    
    print("5. Summary:")
    print(f"   - Login success: {login_success}")
    print(f"   - Log meal page accessible: {log_meal_response.status_code == 200}")
    print(f"   - Search API working: {search_response.status_code == 200}")

if __name__ == "__main__":
    test_user_login_and_search()
