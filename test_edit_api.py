#!/usr/bin/env python3
"""
Simple test to verify the Edit User API works without email
"""

import requests
import json

def test_edit_user_without_email():
    """Test editing a user without email using the API"""
    print("🧪 Testing Edit User API without email")
    print("=" * 50)
    
    # Login and get session
    session = requests.Session()
    
    # Login
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    login_response = session.post('http://127.0.0.1:5001/auth/login', data=login_data)
    if login_response.status_code not in [200, 302]:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    print("✅ Logged in successfully")
    
    # Test editing user with ID 2 (demo user) without email
    user_id = 2
    edit_data = {
        'username': 'demo',
        'first_name': 'Demo',
        'last_name': 'User',
        'email': '',  # Empty email field
        'is_admin': False,
        'is_active': True
    }
    
    print(f"\n📝 Testing edit user {user_id} without email...")
    
    response = session.put(
        f'http://127.0.0.1:5001/api/admin/users/{user_id}',
        headers={'Content-Type': 'application/json'},
        json=edit_data
    )
    
    print(f"Response status: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    print(f"Response text: {response.text[:200]}...")
    
    if response.status_code == 200:
        try:
            result = response.json()
            print("✅ Edit user without email successful!")
            print(f"Response: {result}")
        except:
            print("✅ Edit user successful, but response not JSON")
    else:
        print("❌ Edit user failed")
        
    # Also test with a valid email
    print(f"\n📧 Testing edit user {user_id} with valid email...")
    
    edit_data_with_email = {
        'username': 'demo',
        'first_name': 'Demo',
        'last_name': 'User',
        'email': 'demo@example.com',  # Valid email
        'is_admin': False,
        'is_active': True
    }
    
    response2 = session.put(
        f'http://127.0.0.1:5001/api/admin/users/{user_id}',
        headers={'Content-Type': 'application/json'},
        json=edit_data_with_email
    )
    
    print(f"Response status: {response2.status_code}")
    
    if response2.status_code == 200:
        print("✅ Edit user with email also successful!")
    else:
        print("❌ Edit user with email failed")
        print(f"Response: {response2.text[:200]}")

if __name__ == "__main__":
    test_edit_user_without_email()
