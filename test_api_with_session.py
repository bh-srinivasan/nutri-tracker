#!/usr/bin/env python3
"""
Test script to properly login and test the password reset API.
"""

import requests
from bs4 import BeautifulSoup
import json

def test_password_reset_with_proper_session():
    """Test password reset with proper session handling."""
    base_url = "http://localhost:5001"
    session = requests.Session()
    
    try:
        # Step 1: Get the login page and extract CSRF token
        print("1️⃣ Getting login page...")
        login_page = session.get(f"{base_url}/auth/login")
        soup = BeautifulSoup(login_page.content, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
        print(f"✅ CSRF token: {csrf_token[:20]}...")
        
        # Step 2: Login with CSRF token
        print("2️⃣ Logging in with CSRF token...")
        login_data = {
            'username': 'admin',
            'password': 'admin123',
            'csrf_token': csrf_token
        }
        
        login_response = session.post(f"{base_url}/auth/login", data=login_data, allow_redirects=True)
        print(f"✅ Login response: {login_response.status_code}")
        print(f"✅ Final URL: {login_response.url}")
        
        # Step 3: Verify admin access
        admin_page = session.get(f"{base_url}/admin/dashboard")
        if admin_page.status_code == 200 and 'admin' in admin_page.url.lower():
            print("✅ Admin access confirmed")
            
            # Step 4: Create a test user first if needed
            print("3️⃣ Checking for test users...")
            users_page = session.get(f"{base_url}/admin/users")
            if users_page.status_code == 200:
                print("✅ Users page accessible")
                
                # Step 5: Test the password reset API
                print("4️⃣ Testing password reset API...")
                
                # Use user ID 2 (assuming it exists and is not admin)
                test_user_id = 2
                test_password = "NewSecurePass123!"
                
                api_url = f"{base_url}/api/admin/users/{test_user_id}/reset-password"
                headers = {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Referer': f"{base_url}/admin/users"
                }
                data = {'new_password': test_password}
                
                print(f"API URL: {api_url}")
                print(f"Headers: {headers}")
                print(f"Data: {data}")
                
                # Make the API call
                api_response = session.post(api_url, json=data, headers=headers)
                
                print(f"✅ API Response Status: {api_response.status_code}")
                print(f"✅ API Response Headers: {dict(api_response.headers)}")
                
                if api_response.headers.get('Content-Type', '').startswith('application/json'):
                    response_json = api_response.json()
                    print(f"✅ API Response JSON: {json.dumps(response_json, indent=2)}")
                    
                    if api_response.status_code == 200 and response_json.get('success'):
                        print("🎉 PASSWORD RESET API IS WORKING!")
                        return True
                    else:
                        print(f"❌ API returned error: {response_json.get('message')}")
                        return False
                else:
                    print(f"❌ API returned HTML instead of JSON:")
                    print(f"Response text (first 200 chars): {api_response.text[:200]}...")
                    return False
            else:
                print(f"❌ Cannot access users page: {users_page.status_code}")
                return False
        else:
            print(f"❌ Admin access failed: {admin_page.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Password Reset API with Proper Session Handling\n")
    success = test_password_reset_with_proper_session()
    
    if success:
        print("\n✅ ALL TESTS PASSED!")
    else:
        print("\n❌ TEST FAILED!")
