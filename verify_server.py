#!/usr/bin/env python3
"""
Verification script to confirm server is working
"""

import requests
import time

def verify_server():
    """Verify that the server is running and responding."""
    base_url = "http://127.0.0.1:5001"
    
    tests = [
        {
            'name': 'Home Page',
            'url': f'{base_url}/',
            'expected_status': [200, 302]  # 302 for redirect to login
        },
        {
            'name': 'API Health Check',
            'url': f'{base_url}/api/foods/search-verified?q=test',
            'expected_status': [200, 401]  # 401 if auth required
        }
    ]
    
    print("🔍 Verifying server status...")
    
    for test in tests:
        try:
            response = requests.get(test['url'], timeout=5)
            if response.status_code in test['expected_status']:
                print(f"✅ {test['name']}: OK (Status: {response.status_code})")
            else:
                print(f"⚠️  {test['name']}: Unexpected status {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"❌ {test['name']}: Connection failed")
        except Exception as e:
            print(f"❌ {test['name']}: Error - {e}")
    
    print("\n🎯 Server verification complete!")
    print("🌐 Access the application at: http://127.0.0.1:5001")

if __name__ == '__main__':
    verify_server()
