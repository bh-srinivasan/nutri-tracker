#!/usr/bin/env python3
"""
Debug authentication issue with food-servings/uploads route
"""

from app import create_app
from flask import url_for

app = create_app()

def test_authentication():
    with app.test_client() as client:
        print("🔍 Testing authentication flow...")
        
        # Step 1: Try to access the route without login
        print("\n1. Accessing route without login:")
        response = client.get('/admin/food-servings/uploads')
        print(f"   Status: {response.status_code}")
        print(f"   Redirected to: {response.location if response.status_code == 302 else 'No redirect'}")
        
        # Step 2: Login
        print("\n2. Logging in as admin:")
        login_response = client.post('/auth/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=False)
        print(f"   Login status: {login_response.status_code}")
        print(f"   Login redirected to: {login_response.location if login_response.status_code == 302 else 'No redirect'}")
        
        # Check cookies after login
        print(f"   Cookies: {client.cookie_jar}")
        
        # Step 3: Try the route again after login
        print("\n3. Accessing route after login:")
        response = client.get('/admin/food-servings/uploads', follow_redirects=False)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 302:
            print(f"   Still redirected to: {response.location}")
        else:
            print(f"   Response length: {len(response.data)} bytes")
            content = response.get_data(as_text=True)
            if 'ServingUploadJob' in content:
                print("   ✅ Found ServingUploadJob in response")
            elif 'Error' in content or 'error' in content:
                print("   ❌ Error detected in response")
                print("   First 500 chars:", content[:500])
            else:
                print("   ❓ Unknown response type")
                print("   First 200 chars:", content[:200])
        
        # Step 4: Try accessing admin dashboard for comparison
        print("\n4. Testing admin dashboard for comparison:")
        dash_response = client.get('/admin/dashboard')
        print(f"   Dashboard status: {dash_response.status_code}")
        if dash_response.status_code == 302:
            print(f"   Dashboard redirected to: {dash_response.location}")
        
        # Step 5: Check specific admin route 
        print("\n5. Testing other admin route:")
        users_response = client.get('/admin/users')
        print(f"   Users status: {users_response.status_code}")
        if users_response.status_code == 302:
            print(f"   Users redirected to: {users_response.location}")

if __name__ == '__main__':
    test_authentication()
