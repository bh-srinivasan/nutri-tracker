#!/usr/bin/env python3
"""Test the fixed API endpoint for food servings."""

import requests
import json

# Test the API endpoint
url = "http://127.0.0.1:5001/api/foods/1/servings"

# Make a request to test the endpoint
try:
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ API call successful!")
        print(json.dumps(data, indent=2))
    else:
        print(f"❌ API call failed with status {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Error making request: {e}")
