#!/usr/bin/env python3
"""
Quick test to verify the password reset API endpoint is working.
"""

import requests
import json

def test_password_reset_api():
    """Test the password reset API directly."""
    base_url = "http://localhost:5001"
    
    # Create a session
    session = requests.Session()
    
    try:
        # First, login as admin
        print("🔐 Logging in as admin...")
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        login_response = session.post(f"{base_url}/auth/login", data=login_data, allow_redirects=True)
        print(f"Login status: {login_response.status_code}")
        print(f"Final URL: {login_response.url}")
        
        # Check if we're logged in by accessing the admin dashboard
        dashboard_response = session.get(f"{base_url}/admin/dashboard")
        print(f"Dashboard access: {dashboard_response.status_code}")
        
        if dashboard_response.status_code == 200:
            print("✅ Successfully logged in as admin")
            
            # Now test the password reset API
            print("\n🧪 Testing password reset API...")
            
            # Test with a test user (assuming user ID 2 exists and is not admin)
            test_user_id = 2
            test_password = "NewSecurePass123!"
            
            api_url = f"{base_url}/api/admin/users/{test_user_id}/reset-password"
            headers = {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
            data = {
                'new_password': test_password
            }
            
            print(f"API URL: {api_url}")
            print(f"Request data: {data}")
            
            response = session.post(api_url, json=data, headers=headers)
            print(f"Response status: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            
            try:
                response_json = response.json()
                print(f"Response body: {json.dumps(response_json, indent=2)}")
            except:
                print(f"Response text: {response.text}")
            
            if response.status_code == 200:
                print("✅ Password reset API is working!")
                return True
            else:
                print(f"❌ Password reset API failed with status {response.status_code}")
                return False
                
        else:
            print("❌ Failed to access admin dashboard")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_password_reset_api()
