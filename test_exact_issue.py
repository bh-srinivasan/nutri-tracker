#!/usr/bin/env python3
"""
Final test to isolate the exact issue with email validation
"""

import requests
import json

def test_exact_issue():
    base_url = 'http://127.0.0.1:5001'
    session = requests.Session()
    
    print("🧪 Final Test: Exact Issue Isolation")
    print("=" * 50)
    
    # Login
    print("Step 1: Login as admin...")
    login_response = session.post(f'{base_url}/auth/login', data={
        'username': 'admin',
        'password': 'admin123'
    })
    
    if login_response.status_code == 200:
        print("✅ Logged in")
    else:
        print("❌ Login failed")
        return
    
    # Get users page to get CSRF token
    print("Step 2: Get CSRF token...")
    users_page = session.get(f'{base_url}/admin/users')
    
    import re
    csrf_match = re.search(r'name="csrf_token".*?value="([^"]+)"', users_page.text)
    csrf_token = csrf_match.group(1) if csrf_match else None
    
    if csrf_token:
        print(f"✅ CSRF token: {csrf_token[:20]}...")
    else:
        print("❌ No CSRF token")
        return
    
    # Test the exact data that would be sent by the JavaScript
    print("Step 3: Test edit user API...")
    
    # This is the exact data format the JavaScript would send
    test_data = {
        'username': 'testuser',
        'email': None,  # This is what the updated JS sends
        'first_name': 'Test',
        'last_name': 'User',
        'is_admin': False,
        'is_active': True
    }
    
    headers = {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': csrf_token
    }
    
    print(f"📤 Sending: {json.dumps(test_data, indent=2)}")
    
    # Try to use the session directly with cookies
    response = session.put(
        f'{base_url}/api/admin/users/2',
        json=test_data,
        headers=headers
    )
    
    print(f"📥 Response:")
    print(f"   Status: {response.status_code}")
    print(f"   Content-Type: {response.headers.get('Content-Type', 'None')}")
    print(f"   Cookies: {session.cookies.get_dict()}")
    
    if response.status_code == 200:
        print("✅ API call successful!")
        if 'application/json' in response.headers.get('Content-Type', ''):
            try:
                result = response.json()
                print(f"   Response: {json.dumps(result, indent=2)}")
            except:
                print("   Could not parse JSON")
        else:
            print("   Response is HTML, not JSON")
    else:
        print(f"❌ API call failed")
        if response.text:
            print(f"   Response text (first 300 chars): {response.text[:300]}")
    
    # Test with empty string
    print("\nStep 4: Test with empty string email...")
    test_data_empty = test_data.copy()
    test_data_empty['email'] = ''
    
    response_empty = session.put(
        f'{base_url}/api/admin/users/2',
        json=test_data_empty,
        headers=headers
    )
    
    print(f"📥 Response (empty string):")
    print(f"   Status: {response_empty.status_code}")
    
    if response_empty.status_code == 200:
        print("✅ Empty string email also works!")
    else:
        print(f"❌ Empty string email failed")

if __name__ == '__main__':
    test_exact_issue()
