#!/usr/bin/env python3
"""
Direct test of the delete serving endpoint
"""

import requests
import json

def test_delete_endpoint():
    """Test the delete serving endpoint directly"""
    
    # Base URL
    base_url = "http://127.0.0.1:5001"
    
    # Create session
    session = requests.Session()
    
    try:
        # Login first
        print("1. Logging in...")
        login_data = {
            'username': 'admin', 
            'password': 'admin'
        }
        
        login_response = session.post(f"{base_url}/auth/login", data=login_data)
        
        if login_response.status_code != 200:
            print(f"Login failed: {login_response.status_code}")
            return False
            
        print("✓ Login successful")
        
        # Get CSRF token from a form page
        print("2. Getting CSRF token...")
        edit_page = session.get(f"{base_url}/admin/foods/1/edit")
        
        if edit_page.status_code != 200:
            print(f"Failed to get edit page: {edit_page.status_code}")
            return False
            
        # Extract CSRF token (simple method)
        import re
        csrf_match = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', edit_page.text)
        
        if not csrf_match:
            print("CSRF token not found")
            return False
            
        csrf_token = csrf_match.group(1)
        print(f"✓ CSRF token found: {csrf_token[:10]}...")
        
        # Find serving to delete - let's check what servings exist
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(edit_page.text, 'html.parser')
        
        serving_rows = soup.find_all('tr', {'data-serving-id': True})
        print(f"Found {len(serving_rows)} servings")
        
        if not serving_rows:
            print("No servings found to test delete")
            return True  # Nothing to delete is not an error
            
        # Get first serving's ID
        serving_id = serving_rows[0].get('data-serving-id')
        serving_name = serving_rows[0].find('td', class_='serving-name')
        serving_name_text = serving_name.text.strip() if serving_name else "Unknown"
        
        print(f"Testing delete of serving ID {serving_id}: {serving_name_text}")
        
        # Test the delete endpoint
        print("3. Testing delete endpoint...")
        delete_url = f"{base_url}/admin/foods/1/servings/{serving_id}/delete"
        
        headers = {
            'X-CSRFToken': csrf_token,
            'Content-Type': 'application/json'
        }
        
        delete_response = session.post(delete_url, headers=headers)
        
        print(f"Delete response status: {delete_response.status_code}")
        print(f"Delete response content: {delete_response.text}")
        
        if delete_response.status_code == 200:
            try:
                data = delete_response.json()
                if data.get('success'):
                    print("✓ Delete successful!")
                    return True
                else:
                    print(f"✗ Delete failed: {data.get('error', 'Unknown error')}")
                    return False
            except json.JSONDecodeError:
                print("✗ Invalid JSON response")
                return False
        else:
            print(f"✗ Delete failed with status {delete_response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("=== Testing Delete Serving Endpoint ===")
    success = test_delete_endpoint()
    
    if success:
        print("\n✓ Test completed successfully")
    else:
        print("\n✗ Test failed")
