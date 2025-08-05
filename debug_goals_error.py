#!/usr/bin/env python3
"""
Debug test to identify the exact error in Goals page
"""

import requests
import re

def debug_goals_error():
    """Debug the specific error in goals page"""
    
    session = requests.Session()
    base_url = "http://127.0.0.1:5001"
    
    # Login as testuser
    login_page = session.get(f"{base_url}/auth/login")
    csrf_match = re.search(r'name="csrf_token".*?value="([^"]+)"', login_page.text)
    csrf_token = csrf_match.group(1) if csrf_match else None
    
    login_data = {'username': 'testuser', 'password': 'testpass123'}
    if csrf_token:
        login_data['csrf_token'] = csrf_token
    
    login_response = session.post(f"{base_url}/auth/login", data=login_data, allow_redirects=True)
    
    if "/dashboard" not in login_response.url:
        print("❌ Login failed")
        return
    
    print("✅ Login successful")
    
    # Try to access goals page
    goals_response = session.get(f"{base_url}/dashboard/nutrition-goals")
    
    print(f"Status Code: {goals_response.status_code}")
    
    if goals_response.status_code != 200:
        print("Error content:")
        print(goals_response.text[:2000])
    else:
        print("✅ Goals page accessible")
        
        # Check for any template errors
        if 'UndefinedError' in goals_response.text:
            print("❌ UndefinedError found in response")
        if 'start_date' in goals_response.text:
            print("❌ start_date still referenced")
        if 'end_date' in goals_response.text:
            print("❌ end_date still referenced")

if __name__ == "__main__":
    debug_goals_error()
