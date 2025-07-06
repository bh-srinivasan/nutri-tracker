#!/usr/bin/env python3
"""
Test to verify the email field is truly optional in Edit User flow
"""

import requests
import json
import time

def test_edit_user_complete():
    base_url = 'http://127.0.0.1:5001'
    session = requests.Session()
    
    print("🧪 Complete Test: Edit User Without Email")
    print("=" * 50)
    
    # Step 1: Login as admin
    print("Step 1: Logging in as admin...")
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    login_response = session.post(f'{base_url}/auth/login', data=login_data, allow_redirects=True)
    
    if login_response.status_code == 200:
        print("✅ Logged in successfully as admin")
    else:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    # Step 2: Access the users page to establish session
    print("\nStep 2: Accessing users page...")
    users_page_response = session.get(f'{base_url}/admin/users')
    
    if users_page_response.status_code == 200:
        print("✅ Users page accessed successfully")
        
        # Extract CSRF token
        import re
        csrf_match = re.search(r'name="csrf_token".*?value="([^"]+)"', users_page_response.text)
        csrf_token = csrf_match.group(1) if csrf_match else None
        
        if csrf_token:
            print(f"✅ CSRF token extracted: {csrf_token[:20]}...")
        else:
            print("❌ Could not extract CSRF token")
            return
    else:
        print(f"❌ Failed to access users page: {users_page_response.status_code}")
        return
    
    # Step 3: Get user data from API for user ID 2
    print("\nStep 3: Getting user data for editing...")
    user_api_response = session.get(f'{base_url}/api/admin/users/2')
    
    if user_api_response.status_code == 200:
        try:
            user_data = user_api_response.json()
            print(f"✅ Got user data: {user_data['username']}")
            print(f"   Current email: {user_data.get('email', 'None')}")
        except:
            print("❌ Failed to parse user data as JSON")
            print(f"   Response status: {user_api_response.status_code}")
            print(f"   Response content-type: {user_api_response.headers.get('Content-Type')}")
            print(f"   Response text (first 200 chars): {user_api_response.text[:200]}")
            return
    else:
        print(f"❌ Failed to get user data: {user_api_response.status_code}")
        # Create test data manually
        user_data = {
            'id': 2,
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'is_admin': False,
            'is_active': True
        }
        print(f"📝 Using fallback test data for user: {user_data['username']}")
    
    # Step 4: Test editing user without email
    print(f"\n📝 Step 4: Testing edit user {user_data['id']} without email...")
    
    edit_data = {
        'username': user_data['username'],
        'email': None,  # No email
        'first_name': user_data['first_name'],
        'last_name': user_data['last_name'],
        'is_admin': user_data.get('is_admin', False),
        'is_active': user_data.get('is_active', True)
    }
    
    headers = {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    if csrf_token:
        headers['X-CSRFToken'] = csrf_token
    
    print(f"📤 Sending edit request...")
    print(f"   Data: {json.dumps(edit_data, indent=2)}")
    
    edit_response = session.put(
        f'{base_url}/api/admin/users/{user_data["id"]}',
        json=edit_data,
        headers=headers
    )
    
    print(f"\n📥 Response received:")
    print(f"   Status: {edit_response.status_code}")
    print(f"   Content-Type: {edit_response.headers.get('Content-Type')}")
    
    # Check if we got JSON response
    if 'application/json' in edit_response.headers.get('Content-Type', ''):
        try:
            response_data = edit_response.json()
            print(f"   Response: {json.dumps(response_data, indent=2)}")
            
            if edit_response.status_code == 200:
                print("✅ SUCCESS: User updated without email!")
            else:
                error_msg = response_data.get('error', 'Unknown error')
                print(f"❌ FAILED: {error_msg}")
                
                # Check if the error is about email being required
                if 'email' in error_msg.lower() and 'required' in error_msg.lower():
                    print("🔍 ISSUE FOUND: Server still thinks email is required!")
                else:
                    print("🔍 Different error - not email related")
        except:
            print("❌ Failed to parse response as JSON")
    else:
        print(f"❌ Response is not JSON - got HTML instead")
        print(f"   This suggests authentication/session issue")
        # Check if it's a redirect to login
        if 'sign' in edit_response.text.lower() or 'login' in edit_response.text.lower():
            print("🔍 ISSUE: API request was redirected to login page")
    
    # Step 5: Test with empty string email
    print(f"\n📝 Step 5: Testing edit user {user_data['id']} with empty string email...")
    
    edit_data_empty = {
        'username': user_data['username'],
        'email': '',  # Empty string
        'first_name': user_data['first_name'],
        'last_name': user_data['last_name'],
        'is_admin': user_data.get('is_admin', False),
        'is_active': user_data.get('is_active', True)
    }
    
    edit_response_empty = session.put(
        f'{base_url}/api/admin/users/{user_data["id"]}',
        json=edit_data_empty,
        headers=headers
    )
    
    print(f"📥 Response (empty string):")
    print(f"   Status: {edit_response_empty.status_code}")
    
    if 'application/json' in edit_response_empty.headers.get('Content-Type', ''):
        try:
            response_data_empty = edit_response_empty.json()
            print(f"   Response: {json.dumps(response_data_empty, indent=2)}")
            
            if edit_response_empty.status_code == 200:
                print("✅ SUCCESS: User updated with empty email string!")
            else:
                error_msg = response_data_empty.get('error', 'Unknown error')
                print(f"❌ FAILED: {error_msg}")
        except:
            print("❌ Failed to parse response as JSON")
    else:
        print("❌ Response is not JSON")

if __name__ == '__main__':
    test_edit_user_complete()
