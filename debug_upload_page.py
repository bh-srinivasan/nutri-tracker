#!/usr/bin/env python3
"""
Simple test to access the food servings upload page and see the error
"""

import requests
from bs4 import BeautifulSoup

def test_upload_page_direct():
    """Direct test of upload page"""
    
    session = requests.Session()
    
    # Login
    login_url = "http://localhost:5001/auth/login"
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    # Get CSRF token
    login_page = session.get(login_url)
    soup = BeautifulSoup(login_page.content, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
    login_data['csrf_token'] = csrf_token
    
    # Login
    login_response = session.post(login_url, data=login_data, allow_redirects=True)
    
    if "Admin Dashboard" not in login_response.text:
        print("❌ Login failed")
        return False
    
    print("✅ Login successful")
    
    # Test upload page
    upload_url = "http://localhost:5001/admin/food-servings/upload"
    
    try:
        upload_response = session.get(upload_url)
        print(f"Status: {upload_response.status_code}")
        
        if upload_response.status_code == 500:
            print("Error content preview:")
            print(upload_response.text[:1000])
            
        return upload_response.status_code == 200
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_upload_page_direct()
