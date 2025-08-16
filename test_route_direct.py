#!/usr/bin/env python3
"""
Test the specific route to see the exact error.
"""

import sys
import os
import requests

# Test the route directly
def test_route():
    print("=== Testing Food Servings Upload Route ===")
    
    try:
        # Test the route directly via HTTP
        url = "http://127.0.0.1:5001/admin/food-servings/uploads"
        
        print(f"Testing URL: {url}")
        
        # Note: This will fail with authentication, but should show if the route works
        response = requests.get(url, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Route is accessible!")
        elif response.status_code == 401 or response.status_code == 302:
            print("✅ Route exists but requires authentication (expected)")
        elif response.status_code == 500:
            print("❌ Internal server error - there's a problem with the route")
            print(f"Response content: {response.text[:500]}")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"Response content: {response.text[:500]}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to the server. Is it running?")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_route()
