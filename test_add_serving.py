#!/usr/bin/env python3
"""
Test the Add Serving functionality
"""

import requests
from bs4 import BeautifulSoup
import json

def test_add_serving():
    """Test adding a serving to a food item"""
    
    print("🧪 Testing Add Serving Functionality")
    print("====================================")
    
    # Create session to maintain login
    session = requests.Session()
    
    # Step 1: Login as admin
    login_url = "http://localhost:5001/auth/login"
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    try:
        # Get login page for CSRF token
        login_page = session.get(login_url)
        soup = BeautifulSoup(login_page.content, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
        login_data['csrf_token'] = csrf_token
        
        # Submit login
        login_response = session.post(login_url, data=login_data, allow_redirects=True)
        
        if "Admin Dashboard" not in login_response.text:
            print("❌ Login failed")
            return False
        
        print("✅ Login successful")
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # Step 2: Get edit food page
    edit_url = "http://localhost:5001/admin/foods/1/edit"
    
    try:
        edit_response = session.get(edit_url)
        if edit_response.status_code != 200:
            print(f"❌ Failed to load edit page: {edit_response.status_code}")
            return False
        
        print("✅ Edit food page loaded")
        
        # Parse the page to get CSRF token
        soup = BeautifulSoup(edit_response.content, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrf_token'})
        if not csrf_input:
            print("❌ CSRF token not found")
            return False
        
        csrf_token = csrf_input['value']
        print("✅ CSRF token found")
        
    except Exception as e:
        print(f"❌ Edit page error: {e}")
        return False
    
    # Step 3: Test adding a serving
    add_serving_url = "http://localhost:5001/admin/foods/1/servings/add"
    serving_data = {
        'serving_name': 'Test Cup',
        'unit': 'cup',
        'grams_per_unit': '240',
        'csrf_token': csrf_token
    }
    
    try:
        add_response = session.post(add_serving_url, data=serving_data)
        
        print(f"🔍 Add serving response status: {add_response.status_code}")
        
        if add_response.status_code == 200:
            response_data = add_response.json()
            if response_data.get('success'):
                print("✅ Serving added successfully!")
                print(f"   - Serving: {response_data['serving']['serving_name']}")
                print(f"   - Unit: {response_data['serving']['unit']}")
                print(f"   - Grams: {response_data['serving']['grams_per_unit']}")
                return True
            else:
                print(f"❌ Server returned error: {response_data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP error: {add_response.status_code}")
            try:
                error_data = add_response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   Response text: {add_response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Add serving error: {e}")
        return False

if __name__ == "__main__":
    try:
        success = test_add_serving()
        if success:
            print("\n🎉 SERVING ADDITION TEST PASSED!")
        else:
            print("\n❌ SERVING ADDITION TEST FAILED!")
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
