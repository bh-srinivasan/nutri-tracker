#!/usr/bin/env python3
"""
Debug script to test edit user functionality and check what's happening with email validation
"""

import requests
import json

def test_edit_user_debug():
    base_url = 'http://127.0.0.1:5001'
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    print("🧪 Testing Edit User API Debug")
    print("=" * 50)
    
    # Step 1: Login as admin
    print("Step 1: Logging in as admin...")
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    login_response = session.post(f'{base_url}/auth/login', data=login_data, allow_redirects=False)
    print(f"Login status: {login_response.status_code}")
    
    if login_response.status_code in [200, 302]:
        print("✅ Logged in successfully")
    else:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    # Step 2: Get CSRF token
    dashboard_response = session.get(f'{base_url}/admin/users')
    if 'csrf_token' in dashboard_response.text:
        # Extract CSRF token from the page
        import re
        csrf_match = re.search(r'name="csrf_token".*?value="([^"]+)"', dashboard_response.text)
        csrf_token = csrf_match.group(1) if csrf_match else None
        print(f"CSRF token: {csrf_token[:20]}..." if csrf_token else "No CSRF token found")
    else:
        csrf_token = None
        print("No CSRF token found")
    
    # Step 3: Get list of users to find a test user
    print("\nStep 2: Getting user list...")
    users_response = session.get(f'{base_url}/api/admin/users')
    print(f"Users API status: {users_response.status_code}")
    
    if users_response.status_code == 200:
        try:
            users_data = users_response.json()
            if users_data.get('users') and len(users_data['users']) > 1:
                test_user = users_data['users'][1]  # Get second user (first is likely admin)
                user_id = test_user['id']
                print(f"✅ Found test user: {test_user['username']} (ID: {user_id})")
                print(f"Current email: {test_user.get('email', 'None')}")
            else:
                print("❌ No test users found")
                return
        except json.JSONDecodeError:
            print("❌ Failed to parse users response as JSON")
            return
    else:
        print(f"❌ Failed to get users: {users_response.status_code}")
        return
    
    # Step 4: Test editing user without email
    print(f"\n📝 Testing edit user {user_id} without email...")
    
    edit_data = {
        'username': test_user['username'],
        'email': '',  # Empty email
        'first_name': test_user['first_name'],
        'last_name': test_user['last_name'],
        'is_admin': test_user.get('is_admin', False),
        'is_active': test_user.get('is_active', True)
    }
    
    headers = {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    if csrf_token:
        headers['X-CSRFToken'] = csrf_token
    
    print(f"Sending data: {json.dumps(edit_data, indent=2)}")
    print(f"Headers: {headers}")
    
    edit_response = session.put(
        f'{base_url}/api/admin/users/{user_id}',
        json=edit_data,
        headers=headers
    )
    
    print(f"Edit response status: {edit_response.status_code}")
    print(f"Edit response headers: {dict(edit_response.headers)}")
    
    # Check content type
    content_type = edit_response.headers.get('Content-Type', '')
    if 'application/json' in content_type:
        try:
            response_data = edit_response.json()
            print(f"Response JSON: {json.dumps(response_data, indent=2)}")
            
            if edit_response.status_code == 200:
                print("✅ Edit user without email successful!")
            else:
                print(f"❌ Edit failed: {response_data.get('error', 'Unknown error')}")
        except json.JSONDecodeError:
            print("❌ Failed to parse response as JSON")
            print(f"Response text (first 500 chars): {edit_response.text[:500]}")
    else:
        print(f"❌ Response is not JSON (Content-Type: {content_type})")
        print(f"Response text (first 500 chars): {edit_response.text[:500]}")
    
    # Step 5: Test with null/None email
    print(f"\n📝 Testing edit user {user_id} with null email...")
    
    edit_data_null = {
        'username': test_user['username'],
        'email': None,  # Null email
        'first_name': test_user['first_name'],
        'last_name': test_user['last_name'],
        'is_admin': test_user.get('is_admin', False),
        'is_active': test_user.get('is_active', True)
    }
    
    edit_response_null = session.put(
        f'{base_url}/api/admin/users/{user_id}',
        json=edit_data_null,
        headers=headers
    )
    
    print(f"Edit response status (null email): {edit_response_null.status_code}")
    
    if 'application/json' in edit_response_null.headers.get('Content-Type', ''):
        try:
            response_data_null = edit_response_null.json()
            print(f"Response JSON (null): {json.dumps(response_data_null, indent=2)}")
            
            if edit_response_null.status_code == 200:
                print("✅ Edit user with null email successful!")
            else:
                print(f"❌ Edit failed: {response_data_null.get('error', 'Unknown error')}")
        except json.JSONDecodeError:
            print("❌ Failed to parse response as JSON")

if __name__ == '__main__':
    test_edit_user_debug()
