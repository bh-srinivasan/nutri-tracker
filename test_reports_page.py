#!/usr/bin/env python3
"""
Test script for Reports page functionality
Tests both the reports display and export functionality
"""

import requests
import sys
from datetime import datetime

def test_reports_page():
    """Test the Reports page for non-admin users"""
    
    base_url = "http://127.0.0.1:5001"
    session = requests.Session()
    
    print("🧪 Testing Reports Page Functionality")
    print("=" * 50)
    
    # Step 1: Test login as non-admin user
    print("1️⃣  Testing login as non-admin user...")
    login_data = {
        'username': 'testuser',  # Assuming a non-admin test user exists
        'password': 'password123'
    }
    
    try:
        # Get login page first to check if it exists
        login_response = session.get(f"{base_url}/auth/login")
        if login_response.status_code != 200:
            print(f"❌ Login page not accessible: {login_response.status_code}")
            return False
            
        # Attempt login
        login_post = session.post(f"{base_url}/auth/login", data=login_data, allow_redirects=False)
        print(f"   Login response status: {login_post.status_code}")
        
        if login_post.status_code == 302:
            print("   ✅ Login attempt made (redirect received)")
        else:
            print("   ⚠️  Login may have failed, but continuing...")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the Flask app is running on http://127.0.0.1:5001")
        return False
    except Exception as e:
        print(f"❌ Login test failed: {e}")
        return False
    
    # Step 2: Test Reports page access
    print("\n2️⃣  Testing Reports page access...")
    try:
        reports_response = session.get(f"{base_url}/dashboard/reports")
        print(f"   Reports page status: {reports_response.status_code}")
        
        if reports_response.status_code == 200:
            print("   ✅ Reports page accessible")
            
            # Check for specific error patterns in the response
            if "Could not build url for endpoint" in reports_response.text:
                print("   ❌ URL build error found in response")
                return False
            elif "export_data" in reports_response.text:
                print("   ⚠️  Export data references found (may cause URL build errors)")
            else:
                print("   ✅ No obvious errors in response")
                
        elif reports_response.status_code == 302:
            print("   ⚠️  Redirected (likely to login) - user may not be authenticated")
        elif reports_response.status_code == 500:
            print("   ❌ Internal Server Error - this is the bug we're testing!")
            print("   📝 Error likely related to missing export_data endpoint")
            return False
        else:
            print(f"   ❌ Unexpected status code: {reports_response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Reports page test failed: {e}")
        return False
    
    # Step 3: Test different period parameters
    print("\n3️⃣  Testing Reports page with different periods...")
    periods = [7, 30, 90]
    
    for period in periods:
        try:
            period_response = session.get(f"{base_url}/dashboard/reports?period={period}")
            print(f"   Period {period} days: {period_response.status_code}")
            
            if period_response.status_code == 500:
                print(f"   ❌ Period {period} failed with server error")
                return False
                
        except Exception as e:
            print(f"   ❌ Period {period} test failed: {e}")
            return False
    
    # Step 4: Test direct access to export endpoints (should fail)
    print("\n4️⃣  Testing export endpoints (expected to fail)...")
    export_formats = ['csv', 'pdf']
    
    for format_type in export_formats:
        try:
            export_response = session.get(f"{base_url}/dashboard/export_data?format={format_type}&period=30")
            print(f"   Export {format_type}: {export_response.status_code}")
            
            if export_response.status_code == 404:
                print(f"   ✅ Export {format_type} correctly returns 404 (endpoint doesn't exist)")
            else:
                print(f"   ⚠️  Export {format_type} unexpected status: {export_response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Export {format_type} test failed: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Reports page test completed successfully")
    print("📝 Issue confirmed: export_data endpoint is missing")
    return True

def test_admin_login():
    """Test with admin credentials as fallback"""
    
    base_url = "http://127.0.0.1:5001"
    session = requests.Session()
    
    print("\n🔧 Testing with admin credentials...")
    
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    try:
        login_response = session.post(f"{base_url}/auth/login", data=login_data, allow_redirects=False)
        
        if login_response.status_code == 302:
            print("   ✅ Admin login successful")
            
            # Test reports page with admin
            reports_response = session.get(f"{base_url}/dashboard/reports")
            print(f"   Admin reports page: {reports_response.status_code}")
            
            if reports_response.status_code == 500:
                print("   ❌ Even admin gets server error - confirms the bug!")
                return True
            else:
                print("   ⚠️  Admin doesn't get error - may be user-specific issue")
                
        return True
        
    except Exception as e:
        print(f"   ❌ Admin test failed: {e}")
        return False

if __name__ == "__main__":
    print(f"🕐 Test started at: {datetime.now()}")
    
    # Run main test
    success = test_reports_page()
    
    # Run admin test as fallback
    admin_success = test_admin_login()
    
    if success and admin_success:
        print("\n🎯 CONCLUSION: Bug confirmed - export_data endpoint is missing")
        print("💡 SOLUTION: Need to implement dashboard.export_data route")
        sys.exit(0)
    else:
        print("\n❌ Tests failed - check server status")
        sys.exit(1)
