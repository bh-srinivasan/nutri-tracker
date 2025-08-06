#!/usr/bin/env python3
"""
Quick manual test of profile page by directly accessing it
"""

import requests

def quick_profile_test():
    """Quick test of profile access"""
    print("🔍 Quick Profile Test")
    
    session = requests.Session()
    
    # Get login page to extract CSRF token
    login_url = "http://127.0.0.1:5001/auth/login"
    login_page = session.get(login_url)
    print(f"Login page status: {login_page.status_code}")
    
    # Extract CSRF token
    import re
    csrf_match = re.search(r'name="csrf_token".*?value="([^"]+)"', login_page.text)
    csrf_token = csrf_match.group(1) if csrf_match else None
    print(f"CSRF token found: {'Yes' if csrf_token else 'No'}")
    
    # Login with CSRF token
    login_data = {
        'username': 'testuser',
        'password': 'test123'
    }
    
    if csrf_token:
        login_data['csrf_token'] = csrf_token
    
    login_response = session.post(login_url, data=login_data, allow_redirects=False)
    print(f"Login response status: {login_response.status_code}")
    print(f"Login response headers: {dict(login_response.headers)}")
    
    # Follow redirect if any
    if login_response.status_code in [302, 301]:
        redirect_url = login_response.headers.get('Location')
        print(f"Redirect to: {redirect_url}")
        
        if redirect_url:
            if redirect_url.startswith('/'):
                redirect_url = "http://127.0.0.1:5001" + redirect_url
            follow_response = session.get(redirect_url)
            print(f"Follow redirect status: {follow_response.status_code}")
    
    # Now try profile page
    profile_url = "http://127.0.0.1:5001/auth/profile"
    profile_response = session.get(profile_url)
    print(f"Profile page status: {profile_response.status_code}")
    
    if profile_response.status_code == 200:
        print("✅ Profile page loads successfully!")
        
        # Check for the username field specifically
        if 'name="username"' in profile_response.text:
            print("✅ Username field found in profile form!")
        else:
            print("❌ Username field not found in profile form")
            
        # Check for form fields
        fields_found = []
        fields_to_check = ['username', 'first_name', 'last_name', 'email', 'age']
        for field in fields_to_check:
            if f'name="{field}"' in profile_response.text:
                fields_found.append(field)
        
        print(f"Form fields found: {', '.join(fields_found)}")
        
        return True
    else:
        print(f"❌ Profile page failed: {profile_response.status_code}")
        if profile_response.status_code == 302:
            print(f"Redirected to: {profile_response.headers.get('Location')}")
        else:
            print(f"Response preview: {profile_response.text[:500]}")
        return False

if __name__ == "__main__":
    quick_profile_test()
