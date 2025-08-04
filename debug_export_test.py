#!/usr/bin/env python3
"""
Debug login process and test export functionality
"""

import requests
import re

def debug_login_and_export():
    """Debug the login process and test export"""
    
    session = requests.Session()
    base_url = "http://127.0.0.1:5001"
    
    print("🔍 Debugging login process...")
    
    # Step 1: Get login page and extract CSRF token if needed
    print("\n1️⃣ Getting login page...")
    login_page = session.get(f"{base_url}/auth/login")
    print(f"   Status: {login_page.status_code}")
    
    # Check for CSRF token in the form
    csrf_token = None
    csrf_match = re.search(r'name="csrf_token".*?value="([^"]+)"', login_page.text)
    if csrf_match:
        csrf_token = csrf_match.group(1)
        print(f"   Found CSRF token: {csrf_token[:20]}...")
    else:
        print("   No CSRF token found")
    
    # Step 2: Attempt login
    print("\n2️⃣ Attempting login...")
    login_data = {
        'username': 'testuser',
        'password': 'testpass123'
    }
    
    if csrf_token:
        login_data['csrf_token'] = csrf_token
    
    login_response = session.post(f"{base_url}/auth/login", data=login_data, allow_redirects=True)
    print(f"   Login status: {login_response.status_code}")
    print(f"   Final URL: {login_response.url}")
    
    # Check if we're logged in by looking for dashboard content
    if "dashboard" in login_response.url.lower() or "welcome" in login_response.text.lower():
        print("   ✅ Login successful!")
        logged_in = True
    elif "invalid" in login_response.text.lower() or "error" in login_response.text.lower():
        print("   ❌ Login failed - invalid credentials")
        logged_in = False
    else:
        print("   ⚠️  Login status unclear")
        print(f"   Response preview: {login_response.text[:200]}...")
        logged_in = False
    
    if not logged_in:
        return False
    
    # Step 3: Test reports page access
    print("\n3️⃣ Testing reports page...")
    reports_response = session.get(f"{base_url}/dashboard/reports")
    print(f"   Reports status: {reports_response.status_code}")
    
    if reports_response.status_code != 200:
        print(f"   ❌ Cannot access reports page")
        return False
    
    print("   ✅ Reports page accessible")
    
    # Step 4: Test export functionality
    print("\n4️⃣ Testing CSV export...")
    export_response = session.get(f"{base_url}/dashboard/export-data", params={'format': 'csv', 'period': '7'})
    print(f"   Export status: {export_response.status_code}")
    print(f"   Content type: {export_response.headers.get('Content-Type', 'Not set')}")
    print(f"   Content length: {len(export_response.content)} bytes")
    
    if export_response.status_code == 200:
        if 'csv' in export_response.headers.get('Content-Type', ''):
            print("   ✅ CSV export successful!")
            # Show first few lines of CSV
            lines = export_response.text.split('\n')[:3]
            for i, line in enumerate(lines):
                print(f"   Line {i+1}: {line}")
            return True
        else:
            print("   ❌ Export returned HTML instead of CSV")
            print(f"   Content preview: {export_response.text[:200]}...")
            return False
    else:
        print(f"   ❌ Export failed with status {export_response.status_code}")
        print(f"   Error content: {export_response.text[:300]}...")
        return False

def test_with_admin_user():
    """Also test with admin user for comparison"""
    
    session = requests.Session()
    base_url = "http://127.0.0.1:5001"
    
    print("\n🔧 Testing with admin user for comparison...")
    
    # Login as admin
    login_page = session.get(f"{base_url}/auth/login")
    
    csrf_token = None
    csrf_match = re.search(r'name="csrf_token".*?value="([^"]+)"', login_page.text)
    if csrf_match:
        csrf_token = csrf_match.group(1)
    
    login_data = {
        'username': 'admin',
        'password': 'admin123'  # Default admin password
    }
    
    if csrf_token:
        login_data['csrf_token'] = csrf_token
    
    login_response = session.post(f"{base_url}/auth/login", data=login_data, allow_redirects=True)
    
    if "dashboard" in login_response.url.lower():
        print("   ✅ Admin login successful")
        
        # Test export with admin
        export_response = session.get(f"{base_url}/dashboard/export-data", params={'format': 'csv', 'period': '7'})
        print(f"   Admin export status: {export_response.status_code}")
        
        if export_response.status_code == 200 and 'csv' in export_response.headers.get('Content-Type', ''):
            print("   ✅ Admin CSV export works")
            return True
        else:
            print("   ❌ Admin CSV export failed")
            return False
    else:
        print("   ❌ Admin login failed")
        return False

if __name__ == "__main__":
    print("🧪 Export Functionality Debug Test")
    print("=" * 50)
    
    # Test with regular user
    user_success = debug_login_and_export()
    
    # Test with admin user
    admin_success = test_with_admin_user()
    
    print("\n" + "=" * 50)
    print("📊 SUMMARY:")
    print(f"   Regular user export: {'✅ SUCCESS' if user_success else '❌ FAILED'}")
    print(f"   Admin user export: {'✅ SUCCESS' if admin_success else '❌ FAILED'}")
    
    if user_success:
        print("\n🎉 Export functionality working correctly!")
    else:
        print("\n⚠️  Export functionality has issues!")
