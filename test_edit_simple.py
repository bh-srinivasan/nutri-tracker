#!/usr/bin/env python3
"""
Simple test to check edit user functionality without email
"""

import requests
import json

def test_edit_user_simple():
    base_url = 'http://127.0.0.1:5001'
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    print("🧪 Testing Edit User without Email")
    print("=" * 40)
    
    # Step 1: Login as admin
    print("Step 1: Logging in as admin...")
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    login_response = session.post(f'{base_url}/auth/login', data=login_data, allow_redirects=False)
    
    if login_response.status_code in [200, 302]:
        print("✅ Logged in successfully")
    else:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    # Step 2: Get CSRF token
    dashboard_response = session.get(f'{base_url}/admin/users')
    if 'csrf_token' in dashboard_response.text:
        import re
        csrf_match = re.search(r'name="csrf_token".*?value="([^"]+)"', dashboard_response.text)
        csrf_token = csrf_match.group(1) if csrf_match else None
        print(f"✅ CSRF token found")
    else:
        csrf_token = None
        print("❌ No CSRF token found")
    
    # Step 3: Test editing user ID 2 (assuming it exists)
    user_id = 2
    print(f"\n📝 Testing edit user {user_id} without email...")
    
    # Test data with empty string email
    edit_data_empty = {
        'username': 'testuser',
        'email': '',  # Empty string
        'first_name': 'Test',
        'last_name': 'User',
        'is_admin': False,
        'is_active': True
    }
    
    headers = {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    if csrf_token:
        headers['X-CSRFToken'] = csrf_token
    
    print(f"📤 Sending data with empty string email...")
    edit_response = session.put(
        f'{base_url}/api/admin/users/{user_id}',
        json=edit_data_empty,
        headers=headers
    )
    
    print(f"Response status: {edit_response.status_code}")
    print(f"Content-Type: {edit_response.headers.get('Content-Type')}")
    
    if 'application/json' in edit_response.headers.get('Content-Type', ''):
        try:
            response_data = edit_response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
        except:
            print("Failed to parse JSON response")
    else:
        print("Response is not JSON - this indicates a problem")
        print(f"Response text (first 200 chars): {edit_response.text[:200]}")
    
    # Test with None email
    print(f"\n📤 Sending data with None email...")
    edit_data_none = {
        'username': 'testuser',
        'email': None,  # None value
        'first_name': 'Test',
        'last_name': 'User',
        'is_admin': False,
        'is_active': True
    }
    
    edit_response_none = session.put(
        f'{base_url}/api/admin/users/{user_id}',
        json=edit_data_none,
        headers=headers
    )
    
    print(f"Response status (None): {edit_response_none.status_code}")
    
    if 'application/json' in edit_response_none.headers.get('Content-Type', ''):
        try:
            response_data_none = edit_response_none.json()
            print(f"Response (None): {json.dumps(response_data_none, indent=2)}")
        except:
            print("Failed to parse JSON response")
    else:
        print("Response is not JSON - this indicates a problem")

if __name__ == '__main__':
    test_edit_user_simple()
