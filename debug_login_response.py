#!/usr/bin/env python3
"""
Debug login response issue
"""

from app import create_app
from flask import url_for

app = create_app()

def test_login_response():
    with app.test_client() as client:
        print("🔍 Testing login response...")
        
        # Test login with follow_redirects=True
        print("\n1. Login with follow_redirects=True:")
        login_response = client.post('/auth/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        print(f"   Final status: {login_response.status_code}")
        print(f"   Final URL: {login_response.request.url}")
        
        content = login_response.get_data(as_text=True)
        if 'Admin Dashboard' in content:
            print("   ✅ Successfully reached admin dashboard")
        elif 'Login' in content:
            print("   ❌ Still on login page")
            if 'Invalid username or password' in content:
                print("   ❌ Login failed - invalid credentials")
            else:
                print("   ❓ Login page but no error message")
        else:
            print(f"   ❓ Unknown page - first 200 chars: {content[:200]}")
        
        # Now test the route
        print("\n2. Testing food-servings/uploads after login:")
        response = client.get('/admin/food-servings/uploads')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Successfully accessed route")
            content = response.get_data(as_text=True)
            if 'ServingUploadJob' in content:
                print("   ✅ Found ServingUploadJob in response") 
            elif 'Upload Servings' in content:
                print("   ✅ Found Upload Servings in response")
            else:
                print("   ❓ Unexpected content")
        else:
            print(f"   ❌ Failed to access route: {response.status_code}")

if __name__ == '__main__':
    test_login_response()
