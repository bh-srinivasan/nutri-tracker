"""
Simple manual test for admin user creation API.
This script logs in and tests the user creation endpoint.
"""

import requests
import json

def test_admin_user_creation():
    base_url = "http://127.0.0.1:5001"
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    print("🔍 Testing Admin User Creation API")
    print("=" * 50)
    
    # Step 1: Login as admin
    print("1. Logging in as admin...")
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    login_response = session.post(f"{base_url}/auth/login", data=login_data, allow_redirects=False)
    print(f"   Login status code: {login_response.status_code}")
    print(f"   Login response headers: {dict(login_response.headers)}")
    
    if login_response.status_code == 302:  # Redirect means success
        print("   ✅ Login successful (redirected)")
    else:
        print(f"   ❌ Login failed. Response: {login_response.text[:200]}")
        return False
    
    # Step 2: Test the API endpoint
    print("\n2. Testing user creation API...")
    user_data = {
        'user_id': 'testuser123',
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'test@example.com',
        'password': 'TestPass123!'
    }
    
    api_response = session.post(
        f"{base_url}/api/admin/users",
        json=user_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"   API status code: {api_response.status_code}")
    print(f"   API response: {api_response.text}")
    
    if api_response.status_code == 201:
        print("   ✅ User creation successful")
        return True
    elif api_response.status_code == 401:
        print("   ❌ Authentication failed")
        return False
    else:
        print(f"   ❌ User creation failed")
        try:
            error_data = api_response.json()
            print(f"   Error details: {error_data}")
        except:
            pass
        return False

def test_with_browser_session():
    """Test by attempting to use cookies from a browser session"""
    print("\n3. Testing with manual session...")
    print("   Please log in manually in your browser first, then press Enter")
    input("   Press Enter when you've logged in as admin in your browser...")
    
    # This would require extracting cookies from browser - for now just show the URL
    print(f"   You can manually test the API at: http://127.0.0.1:5001/api/admin/users")
    print(f"   Use this JSON data:")
    print(f"   {json.dumps({'user_id': 'manual_test', 'first_name': 'Manual', 'last_name': 'Test', 'email': 'manual@test.com', 'password': 'ManualTest123!'}, indent=2)}")

if __name__ == "__main__":
    success = test_admin_user_creation()
    
    if not success:
        test_with_browser_session()
    
    print("\n" + "=" * 50)
    print("Test completed.")
