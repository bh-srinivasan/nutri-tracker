#!/usr/bin/env python3
"""
Test the fixed email optional functionality
"""

import requests
import json

def test_fixed_email_optional():
    """Test that the email field is now truly optional"""
    print("🧪 Testing Fixed Email Optional Functionality")
    print("=" * 55)
    
    # Setup session
    session = requests.Session()
    
    # Login as admin
    print("🔐 Logging in as admin...")
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    login_response = session.post('http://127.0.0.1:5001/auth/login', data=login_data)
    
    if login_response.status_code not in [200, 302]:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    print("✅ Admin login successful")
    
    # Test editing user 2 without email
    print("\n📝 Testing edit user without email...")
    
    edit_data = {
        'username': 'demo',
        'first_name': 'Demo',
        'last_name': 'User',
        'email': '',  # Empty email - should be allowed now
        'is_admin': False,
        'is_active': True
    }
    
    # Get CSRF token first
    csrf_token = None
    try:
        # Try to get a CSRF token from the users page
        users_page = session.get('http://127.0.0.1:5001/admin/users')
        if 'csrf_token' in users_page.text:
            # Extract CSRF token if possible
            import re
            csrf_match = re.search(r'name="csrf_token".*?value="([^"]+)"', users_page.text)
            if csrf_match:
                csrf_token = csrf_match.group(1)
    except:
        pass
    
    headers = {'Content-Type': 'application/json'}
    if csrf_token:
        headers['X-CSRFToken'] = csrf_token
    
    response = session.put(
        'http://127.0.0.1:5001/api/admin/users/2',
        headers=headers,
        json=edit_data
    )
    
    print(f"Response status: {response.status_code}")
    print(f"Response content type: {response.headers.get('Content-Type', 'Unknown')}")
    
    if response.status_code == 200:
        try:
            result = response.json()
            print("✅ SUCCESS: Edit user without email worked!")
            print(f"Response: {result}")
        except:
            print("✅ SUCCESS: Edit user without email worked (non-JSON response)")
    else:
        print("❌ FAILED: Edit user without email failed")
        print(f"Response: {response.text[:300]}...")
    
    # Test with invalid email to make sure validation still works
    print("\n⚠️ Testing edit user with invalid email...")
    
    edit_data_invalid = {
        'username': 'demo',
        'first_name': 'Demo',
        'last_name': 'User',
        'email': 'invalid-email-format',  # Invalid email
        'is_admin': False,
        'is_active': True
    }
    
    response2 = session.put(
        'http://127.0.0.1:5001/api/admin/users/2',
        headers=headers,
        json=edit_data_invalid
    )
    
    if response2.status_code != 200:
        print("✅ GOOD: Invalid email was correctly rejected")
    else:
        print("❌ ISSUE: Invalid email was incorrectly accepted")
    
    # Test with valid email
    print("\n📧 Testing edit user with valid email...")
    
    edit_data_valid = {
        'username': 'demo',
        'first_name': 'Demo',
        'last_name': 'User',
        'email': 'demo@example.com',  # Valid email
        'is_admin': False,
        'is_active': True
    }
    
    response3 = session.put(
        'http://127.0.0.1:5001/api/admin/users/2',
        headers=headers,
        json=edit_data_valid
    )
    
    if response3.status_code == 200:
        print("✅ SUCCESS: Edit user with valid email worked!")
    else:
        print("❌ FAILED: Edit user with valid email failed")
        print(f"Response: {response3.text[:200]}...")
    
    print("\n" + "=" * 55)
    print("🎉 Testing completed!")
    print("✅ Email field should now be optional in the admin panel")

if __name__ == "__main__":
    test_fixed_email_optional()
