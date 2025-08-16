#!/usr/bin/env python3
"""
Test authenticated route access.
"""

import sys
import os
import requests

def test_authenticated_route():
    print("=== Testing Authenticated Food Servings Upload Route ===")
    
    try:
        session = requests.Session()
        
        # Step 1: Get login page to get CSRF token
        login_url = "http://127.0.0.1:5001/auth/login"
        response = session.get(login_url)
        print(f"Login page status: {response.status_code}")
        
        # Extract CSRF token from login page
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_token = None
        
        # Look for CSRF token in hidden input
        csrf_input = soup.find('input', {'name': 'csrf_token'})
        if csrf_input:
            csrf_token = csrf_input.get('value')
            print(f"Found CSRF token: {csrf_token[:20]}...")
        else:
            print("No CSRF token found in login page")
            return
        
        # Step 2: Login as admin
        login_data = {
            'username': 'admin',
            'password': 'admin123',  # Assuming this is the admin password
            'csrf_token': csrf_token
        }
        
        response = session.post(login_url, data=login_data)
        print(f"Login attempt status: {response.status_code}")
        
        if response.status_code == 302 or 'dashboard' in response.text.lower():
            print("✅ Login successful!")
        else:
            print("❌ Login failed")
            print(f"Response: {response.text[:300]}")
            return
        
        # Step 3: Test the servings upload route
        servings_url = "http://127.0.0.1:5001/admin/food-servings/uploads"
        response = session.get(servings_url)
        
        print(f"Servings upload page status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Servings upload page accessible!")
            if 'Error loading upload interface' in response.text:
                print("❌ But contains error message!")
            else:
                print("✅ Page loaded successfully without errors!")
        else:
            print(f"❌ Error accessing servings upload: {response.status_code}")
            print(f"Response: {response.text[:300]}")
            
    except ImportError:
        print("❌ BeautifulSoup not installed. Install with: pip install beautifulsoup4")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_authenticated_route()
