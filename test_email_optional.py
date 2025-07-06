#!/usr/bin/env python3
"""
Test script to verify that the email field is optional in both Add User and Edit User flows.
This script tests the admin panel email field functionality.
"""

import time
import requests
import json

# Server configuration
BASE_URL = "http://127.0.0.1:5001"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def test_admin_login():
    """Login as admin and get session cookies"""
    print("🔐 Testing admin login...")
    session = requests.Session()
    
    # Get login page first to get CSRF token if needed
    login_response = session.post(f"{BASE_URL}/auth/login", data={
        'username': ADMIN_USERNAME,
        'password': ADMIN_PASSWORD
    }, allow_redirects=False)
    
    if login_response.status_code in [200, 302]:
        print("✅ Admin login successful")
        return session
    else:
        print(f"❌ Admin login failed: {login_response.status_code}")
        return None

def test_add_user_without_email(session):
    """Test adding a user without email"""
    print("\n📝 Testing Add User without email...")
    
    test_user_data = {
        'first_name': 'Test',
        'last_name': 'UserNoEmail',
        'password': 'TestPass123!',
        'is_admin': False
    }
    
    try:
        response = session.post(f"{BASE_URL}/api/admin/users", 
                              headers={'Content-Type': 'application/json'},
                              json=test_user_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Add User without email successful: User ID {result.get('id', 'N/A')}")
            return result.get('id')
        else:
            print(f"❌ Add User without email failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Add User without email error: {e}")
        return None

def test_edit_user_without_email(session, user_id):
    """Test editing a user and removing email"""
    print(f"\n✏️ Testing Edit User {user_id} without email...")
    
    edit_user_data = {
        'username': 'testusernomail',
        'first_name': 'TestEdited',
        'last_name': 'UserNoEmailEdited',
        'email': '',  # Empty email
        'is_admin': False,
        'is_active': True
    }
    
    try:
        response = session.put(f"{BASE_URL}/api/admin/users/{user_id}", 
                              headers={'Content-Type': 'application/json'},
                              json=edit_user_data)
        
        if response.status_code == 200:
            print("✅ Edit User without email successful")
            return True
        else:
            print(f"❌ Edit User without email failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Edit User without email error: {e}")
        return False

def test_edit_user_with_invalid_email(session, user_id):
    """Test editing a user with invalid email (should fail)"""
    print(f"\n⚠️ Testing Edit User {user_id} with invalid email...")
    
    edit_user_data = {
        'username': 'testusernomail',
        'first_name': 'TestEdited',
        'last_name': 'UserNoEmailEdited',
        'email': 'invalid-email',  # Invalid email
        'is_admin': False,
        'is_active': True
    }
    
    try:
        response = session.put(f"{BASE_URL}/api/admin/users/{user_id}", 
                              headers={'Content-Type': 'application/json'},
                              json=edit_user_data)
        
        if response.status_code != 200:
            print("✅ Edit User with invalid email correctly rejected")
            return True
        else:
            print("❌ Edit User with invalid email was incorrectly accepted")
            return False
    except Exception as e:
        print(f"❌ Edit User with invalid email error: {e}")
        return False

def test_edit_user_with_valid_email(session, user_id):
    """Test editing a user with valid email"""
    print(f"\n📧 Testing Edit User {user_id} with valid email...")
    
    edit_user_data = {
        'username': 'testusernomail',
        'first_name': 'TestFinal',
        'last_name': 'UserWithEmail',
        'email': 'test@example.com',  # Valid email
        'is_admin': False,
        'is_active': True
    }
    
    try:
        response = session.put(f"{BASE_URL}/api/admin/users/{user_id}", 
                              headers={'Content-Type': 'application/json'},
                              json=edit_user_data)
        
        if response.status_code == 200:
            print("✅ Edit User with valid email successful")
            return True
        else:
            print(f"❌ Edit User with valid email failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Edit User with valid email error: {e}")
        return False

def cleanup_test_user(session, user_id):
    """Clean up test user"""
    if user_id:
        print(f"\n🧹 Cleaning up test user {user_id}...")
        try:
            response = session.delete(f"{BASE_URL}/api/admin/users/{user_id}")
            if response.status_code == 200:
                print("✅ Test user cleaned up successfully")
            else:
                print(f"⚠️ Could not clean up test user: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")

def main():
    """Main test function"""
    print("🧪 Testing Email Optional Functionality in Admin Panel")
    print("=" * 60)
    
    # Login as admin
    session = test_admin_login()
    if not session:
        print("❌ Cannot proceed without admin login")
        return
    
    # Test adding user without email
    user_id = test_add_user_without_email(session)
    if not user_id:
        print("❌ Cannot proceed without creating test user")
        return
    
    # Test editing user without email
    test_edit_user_without_email(session, user_id)
    
    # Test editing user with invalid email
    test_edit_user_with_invalid_email(session, user_id)
    
    # Test editing user with valid email
    test_edit_user_with_valid_email(session, user_id)
    
    # Cleanup
    cleanup_test_user(session, user_id)
    
    print("\n" + "=" * 60)
    print("✅ Email optional functionality testing completed!")
    print("📝 Summary: Email field should be optional in both Add User and Edit User flows")
    print("🔍 If all tests passed, the email field is working correctly as optional")

if __name__ == "__main__":
    main()
