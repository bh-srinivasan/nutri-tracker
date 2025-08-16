#!/usr/bin/env python3
"""Test the fixed API endpoint for food servings."""

import requests
import json

def test_debug_endpoint():
    """Test the debug API endpoint"""
    try:
        url = "http://localhost:5001/api/foods/93/debug"
        print(f"Testing: {url}")
        
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS!")
            print(json.dumps(data, indent=2))
        else:
            print("❌ FAILED!")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - Flask server may not be running")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_debug_endpoint()
