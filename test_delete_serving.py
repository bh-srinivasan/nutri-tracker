#!/usr/bin/env python3
"""
Test script for verifying the delete serving functionality
"""

import requests
import sys
from bs4 import BeautifulSoup

def test_delete_serving():
    # Base URL for the local server
    base_url = "http://127.0.0.1:5001"
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    try:
        # Step 1: Login as admin
        print("1. Logging in as admin...")
        
        # First get the login page to extract CSRF token
        login_page = session.get(f"{base_url}/auth/login")
        if login_page.status_code != 200:
            print(f"Failed to get login page: {login_page.status_code}")
            return False
            
        soup = BeautifulSoup(login_page.text, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})
        
        if not csrf_token:
            print("CSRF token not found on login page")
            return False
            
        csrf_value = csrf_token.get('value')
        print(f"Found CSRF token: {csrf_value[:10]}...")
        
        # Login with credentials
        login_data = {
            'username': 'admin',
            'password': 'admin',
            'csrf_token': csrf_value
        }
        
        login_response = session.post(f"{base_url}/auth/login", data=login_data)
        
        if login_response.status_code == 200 and 'admin' in login_response.text.lower():
            print("✓ Login successful")
        else:
            print(f"✗ Login failed: {login_response.status_code}")
            return False
            
        # Step 2: Find food with existing servings
        print("\n2. Getting food edit page...")
        edit_page = session.get(f"{base_url}/admin/foods/1/edit")
        
        if edit_page.status_code != 200:
            print(f"Failed to get edit page: {edit_page.status_code}")
            return False
            
        soup = BeautifulSoup(edit_page.text, 'html.parser')
        
        # Find existing servings
        serving_rows = soup.find_all('tr', class_='serving-row')
        print(f"Found {len(serving_rows)} servings")
        
        if not serving_rows:
            print("No servings found to delete")
            return False
            
        # Get details of first serving
        first_serving = serving_rows[0]
        delete_btn = first_serving.find('button', class_='btn-outline-danger')
        
        if not delete_btn:
            print("Delete button not found")
            return False
            
        # Extract food and serving IDs from the onclick attribute
        onclick = delete_btn.get('onclick', '')
        print(f"Delete button onclick: {onclick}")
        
        # Parse the remove function call
        import re
        match = re.search(r'remove\((\d+),\s*(\d+)\)', onclick)
        if not match:
            print("Could not parse food_id and serving_id from onclick")
            return False
            
        food_id = match.group(1)
        serving_id = match.group(2)
        print(f"Found food_id: {food_id}, serving_id: {serving_id}")
        
        # Get CSRF token from the page
        csrf_input = soup.find('input', {'name': 'csrf_token'})
        if not csrf_input:
            print("CSRF token not found on edit page")
            return False
            
        csrf_value = csrf_input.get('value')
        
        # Step 3: Test delete functionality
        print(f"\n3. Testing delete serving {serving_id} from food {food_id}...")
        
        delete_url = f"{base_url}/admin/foods/{food_id}/servings/{serving_id}/delete"
        print(f"DELETE URL: {delete_url}")
        
        # Send delete request
        headers = {
            'X-CSRFToken': csrf_value,
            'Content-Type': 'application/json'
        }
        
        delete_response = session.post(delete_url, headers=headers)
        print(f"Delete response status: {delete_response.status_code}")
        print(f"Delete response text: {delete_response.text}")
        
        if delete_response.status_code == 200:
            print("✓ Delete request successful")
            return True
        else:
            print(f"✗ Delete request failed: {delete_response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error during test: {e}")
        return False

if __name__ == "__main__":
    print("=== Testing Delete Serving Functionality ===")
    success = test_delete_serving()
    
    if success:
        print("\n✓ Test completed successfully")
        sys.exit(0)
    else:
        print("\n✗ Test failed")
        sys.exit(1)
