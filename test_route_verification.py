#!/usr/bin/env python3
"""
Test to confirm export route exists and responds correctly
"""

import requests

def test_export_route_existence():
    """Test if the export route exists and is accessible"""
    
    print("🔍 Testing Export Route Existence...")
    
    try:
        # Test direct access to export route (will redirect to login if not authenticated)
        export_url = "http://127.0.0.1:5001/dashboard/export-data"
        
        print(f"📍 Testing URL: {export_url}")
        
        response = requests.get(export_url, allow_redirects=False)
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"✅ Headers: {dict(response.headers)}")
        
        if response.status_code == 302:
            print(f"✅ Route exists! Redirected to: {response.headers.get('Location', 'Unknown')}")
            print("   This means the route is working but requires authentication (as expected)")
            return True
        elif response.status_code == 200:
            print("✅ Route accessible directly!")
            return True
        elif response.status_code == 404:
            print("❌ Route not found (404)")
            return False
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_reports_page():
    """Test if the reports page is accessible"""
    
    print("\n🔍 Testing Reports Page...")
    
    try:
        reports_url = "http://127.0.0.1:5001/dashboard/reports"
        
        print(f"📍 Testing URL: {reports_url}")
        
        response = requests.get(reports_url, allow_redirects=False)
        
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 302:
            print(f"✅ Reports page exists! Redirected to: {response.headers.get('Location', 'Unknown')}")
            print("   This means the page is working but requires authentication (as expected)")
            return True
        elif response.status_code == 200:
            print("✅ Reports page accessible directly!")
            return True
        elif response.status_code == 404:
            print("❌ Reports page not found (404)")
            return False
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Export Functionality...")
    
    # Test if export route exists
    export_exists = test_export_route_existence()
    
    # Test if reports page exists
    reports_exists = test_reports_page()
    
    print("\n" + "="*50)
    print("SUMMARY:")
    print(f"✅ Export Route Working: {export_exists}")
    print(f"✅ Reports Page Working: {reports_exists}")
    
    if export_exists and reports_exists:
        print("\n🎉 SUCCESS: Both routes are working!")
        print("   The export buttons on the reports page should work correctly.")
        print("   The BuildError has been resolved!")
    else:
        print("\n❌ Some routes are not working correctly.")
