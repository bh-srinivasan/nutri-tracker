#!/usr/bin/env python3
"""
Test login with proper CSRF token handling
"""

from app import create_app
import re

app = create_app()

def test_login_with_csrf():
    with app.test_client() as client:
        print("🔍 Testing login with CSRF token...")
        
        # Step 1: Get the login form to extract CSRF token
        print("\n1. Getting login form:")
        login_page = client.get('/auth/login')
        print(f"   Login page status: {login_page.status_code}")
        
        # Extract CSRF token from the form
        content = login_page.get_data(as_text=True)
        csrf_match = re.search(r'name="csrf_token".*?value="([^"]+)"', content)
        if csrf_match:
            csrf_token = csrf_match.group(1)
            print(f"   ✅ CSRF token found: {csrf_token[:20]}...")
        else:
            print("   ❌ No CSRF token found")
            print("   Login form content:", content[:500])
            return
        
        # Step 2: Submit login with CSRF token
        print("\n2. Submitting login with CSRF token:")
        login_response = client.post('/auth/login', data={
            'username': 'admin',
            'password': 'admin123',
            'csrf_token': csrf_token
        }, follow_redirects=False)
        
        print(f"   Login response status: {login_response.status_code}")
        if login_response.status_code == 302:
            print(f"   ✅ Login successful, redirected to: {login_response.location}")
        else:
            print(f"   ❌ Login failed, response: {login_response.get_data(as_text=True)[:200]}")
            return
        
        # Step 3: Follow the redirect and check session
        print("\n3. Following redirect:")
        follow_response = client.get(login_response.location)
        print(f"   Follow redirect status: {follow_response.status_code}")
        
        content = follow_response.get_data(as_text=True)
        if 'Admin Dashboard' in content or 'Dashboard' in content:
            print("   ✅ Successfully reached dashboard")
        else:
            print(f"   ❓ Unknown page content: {content[:200]}")
        
        # Step 4: Test our route
        print("\n4. Testing food-servings/uploads route:")
        response = client.get('/admin/food-servings/uploads')
        print(f"   Route status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Successfully accessed route")
            content = response.get_data(as_text=True)
            if 'ServingUploadJob' in content or 'Upload Servings' in content or 'History' in content:
                print("   ✅ Route content looks correct")
                
                # Check for upload history table
                if 'jobs' in content.lower() and 'table' in content.lower():
                    print("   ✅ Found job history table")
                else:
                    print("   ❓ No job history table visible")
                    
            else:
                print(f"   ❓ Unexpected content: {content[:300]}")
        else:
            print(f"   ❌ Route access failed: {response.status_code}")

if __name__ == '__main__':
    test_login_with_csrf()
