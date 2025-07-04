#!/usr/bin/env python3
"""
Final test to simulate actual HTTP requests to the admin users endpoint.
"""

import requests
from requests.auth import HTTPBasicAuth

def test_admin_users_endpoint():
    """Test the admin users endpoint via HTTP requests."""
    base_url = "http://127.0.0.1:5001"
    
    print("=== Testing Admin Users Endpoint ===")
    
    # Test URLs to check
    test_urls = [
        f"{base_url}/admin/users",
        f"{base_url}/admin/users?show_details=1",
        f"{base_url}/admin/users?search=demo",
        f"{base_url}/admin/users?status=active",
        f"{base_url}/admin/users?show_details=1&search=test",
        f"{base_url}/admin/users?page=1&show_details=1&status=active"
    ]
    
    for url in test_urls:
        try:
            print(f"\n🔗 Testing URL: {url}")
            response = requests.get(url, timeout=5)
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ Request successful")
                # Check if admin user is mentioned in the response
                if 'admin@nutritracker.com' in response.text:
                    print("   ❌ WARNING: Admin user found in response!")
                else:
                    print("   ✅ Admin user properly excluded")
                
                # Check for show_details functionality
                if 'show_details=1' in url:
                    if 'Joined' in response.text and 'Last Login' in response.text:
                        print("   ✅ Additional details columns present")
                    else:
                        print("   ❌ Additional details columns missing")
                
            elif response.status_code == 302:
                print("   🔀 Redirect (likely to login page)")
            else:
                print(f"   ❌ Unexpected status code: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request failed: {e}")
    
    print(f"\n✅ Endpoint testing completed!")
    print(f"📝 Note: If you see redirects (302), you may need to log in as admin first")
    print(f"🌐 You can manually test at: {base_url}/admin/users")

if __name__ == "__main__":
    test_admin_users_endpoint()
