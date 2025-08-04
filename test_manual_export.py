#!/usr/bin/env python3
"""
Manual test to verify the export route is working
Tests the actual export endpoint with proper authentication
"""

import requests
import time

def test_export_endpoint():
    """Test the export endpoint manually"""
    
    print("🔍 Testing Export Endpoint...")
    
    # Start a session for login
    session = requests.Session()
    
    try:
        # First, try to login to get session cookie
        login_url = "http://127.0.0.1:5001/auth/login"
        
        print(f"📝 Attempting login at {login_url}")
        
        # Get the login page first to see if server is responding
        login_response = session.get(login_url)
        print(f"✅ Login page status: {login_response.status_code}")
        
        # Login with admin credentials
        login_data = {
            'username': 'admin',
            'password': 'admin123'  # Assuming default admin password
        }
        
        login_result = session.post(login_url, data=login_data)
        print(f"✅ Login attempt status: {login_result.status_code}")
        
        # Now test the export route
        export_url = "http://127.0.0.1:5001/dashboard/export-data"
        
        # Test CSV export with different periods
        test_cases = [
            {'format': 'csv', 'period': '7'},
            {'format': 'csv', 'period': '30'},
            {'format': 'pdf', 'period': '7'},
        ]
        
        for i, params in enumerate(test_cases, 1):
            print(f"\n🧪 Test Case {i}: {params}")
            
            response = session.get(export_url, params=params)
            print(f"   Status Code: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('Content-Type', 'Not set')}")
            print(f"   Content-Length: {len(response.content)} bytes")
            
            if response.status_code == 200:
                print(f"   ✅ Export successful!")
                if params['format'] == 'csv':
                    # Show first few characters of CSV
                    content_preview = response.text[:200] if response.text else "No content"
                    print(f"   CSV Preview: {content_preview}...")
            else:
                print(f"   ❌ Export failed!")
                print(f"   Response text: {response.text[:500]}")
        
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection Error: {e}")
        print("Make sure the Flask server is running on port 5001")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Starting Export Route Test...")
    success = test_export_endpoint()
    
    if success:
        print("\n✅ Test completed successfully!")
    else:
        print("\n❌ Test failed!")
