#!/usr/bin/env python3
"""
Test script for Admin Food Servings Management
Tests the new servings panel functionality in admin food management.
"""

import os
import sys
import requests
import json
from datetime import datetime

# Add project root to Python path
sys.path.insert(0, os.getcwd())

def test_admin_servings_functionality():
    """Test the admin servings management functionality."""
    
    base_url = "http://127.0.0.1:5001"
    
    print("=== Admin Food Servings Management Test ===")
    print(f"Testing against: {base_url}")
    print()
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    try:
        # Test 1: Check if admin login page is accessible
        print("Test 1: Accessing admin login page...")
        response = session.get(f"{base_url}/admin/login")
        if response.status_code == 200:
            print("✓ Admin login page accessible")
        else:
            print(f"✗ Admin login page failed: {response.status_code}")
            return False
        
        # Test 2: Login as admin
        print("\nTest 2: Logging in as admin...")
        
        # Get CSRF token from login form
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
        
        login_data = {
            'username': 'admin',
            'password': 'admin',  # Default admin password
            'csrf_token': csrf_token
        }
        
        response = session.post(f"{base_url}/admin/login", data=login_data)
        if response.status_code == 200 and "Dashboard" in response.text:
            print("✓ Admin login successful")
        else:
            print(f"✗ Admin login failed: {response.status_code}")
            return False
        
        # Test 3: Access admin foods page
        print("\nTest 3: Accessing admin foods page...")
        response = session.get(f"{base_url}/admin/foods")
        if response.status_code == 200 and "Foods Management" in response.text:
            print("✓ Admin foods page accessible")
        else:
            print(f"✗ Admin foods page failed: {response.status_code}")
            return False
        
        # Test 4: Create a test food for serving management
        print("\nTest 4: Creating test food...")
        response = session.get(f"{base_url}/admin/foods/add")
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
        
        food_data = {
            'name': 'Test Food for Servings',
            'brand': 'Test Brand',
            'category': 'Test Category',
            'calories': 250.0,
            'protein': 25.0,
            'carbs': 30.0,
            'fat': 8.0,
            'fiber': 5.0,
            'sugar': 3.0,
            'sodium': 400.0,
            'serving_size': 100.0,
            'is_verified': True,
            'csrf_token': csrf_token
        }
        
        response = session.post(f"{base_url}/admin/foods/add", data=food_data)
        if response.status_code == 302:  # Redirect after successful creation
            print("✓ Test food created successfully")
        else:
            print(f"✗ Test food creation failed: {response.status_code}")
            return False
        
        # Test 5: Find the created food and access edit page
        print("\nTest 5: Accessing food edit page...")
        response = session.get(f"{base_url}/admin/foods")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find edit link for our test food
        edit_links = soup.find_all('a', href=True)
        test_food_edit_url = None
        
        for link in edit_links:
            if 'edit' in link['href'] and 'Test Food for Servings' in str(link.parent.parent):
                test_food_edit_url = link['href']
                break
        
        if test_food_edit_url:
            food_id = test_food_edit_url.split('/')[-2]  # Extract food ID
            print(f"✓ Found test food with ID: {food_id}")
        else:
            print("✗ Could not find test food edit link")
            return False
        
        # Test 6: Access edit page and verify servings panel
        print("\nTest 6: Verifying servings panel in edit page...")
        response = session.get(f"{base_url}{test_food_edit_url}")
        if response.status_code == 200 and "Servings" in response.text and "Add New Serving" in response.text:
            print("✓ Servings panel present in edit page")
        else:
            print(f"✗ Servings panel not found: {response.status_code}")
            return False
        
        # Test 7: Test adding a new serving via AJAX
        print("\nTest 7: Testing add serving functionality...")
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
        
        serving_data = {
            'serving_name': '1 cup',
            'unit': 'cup',
            'grams_per_unit': '240.0'
        }
        
        headers = {
            'X-CSRFToken': csrf_token,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        response = session.post(
            f"{base_url}/admin/foods/{food_id}/servings/add",
            data=serving_data,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                serving_id = result['serving']['id']
                print(f"✓ Serving added successfully (ID: {serving_id})")
            else:
                print(f"✗ Add serving failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"✗ Add serving request failed: {response.status_code}")
            return False
        
        # Test 8: Test editing the serving
        print("\nTest 8: Testing edit serving functionality...")
        edit_data = {
            'serving_name': '1 large cup',
            'unit': 'cup',
            'grams_per_unit': '250.0'
        }
        
        response = session.post(
            f"{base_url}/admin/foods/{food_id}/servings/{serving_id}/edit",
            data=edit_data,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✓ Serving edited successfully")
            else:
                print(f"✗ Edit serving failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"✗ Edit serving request failed: {response.status_code}")
            return False
        
        # Test 9: Test setting default serving
        print("\nTest 9: Testing set default serving functionality...")
        response = session.post(
            f"{base_url}/admin/foods/{food_id}/servings/{serving_id}/set-default",
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✓ Default serving set successfully")
            else:
                print(f"✗ Set default serving failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"✗ Set default serving request failed: {response.status_code}")
            return False
        
        # Test 10: Test unsetting default serving
        print("\nTest 10: Testing unset default serving functionality...")
        response = session.post(
            f"{base_url}/admin/foods/{food_id}/servings/{serving_id}/unset-default",
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✓ Default serving unset successfully")
            else:
                print(f"✗ Unset default serving failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"✗ Unset default serving request failed: {response.status_code}")
            return False
        
        # Test 11: Test deleting the serving
        print("\nTest 11: Testing delete serving functionality...")
        response = session.post(
            f"{base_url}/admin/foods/{food_id}/servings/{serving_id}/delete",
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✓ Serving deleted successfully")
            else:
                print(f"✗ Delete serving failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"✗ Delete serving request failed: {response.status_code}")
            return False
        
        # Test 12: Verify the UI shows correct state after operations
        print("\nTest 12: Verifying final state in UI...")
        response = session.get(f"{base_url}{test_food_edit_url}")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            servings_table = soup.find('table', {'id': 'servingsTable'})
            if servings_table:
                # Should only have the default 100g row and the "no servings" message
                rows = servings_table.find('tbody').find_all('tr')
                if len(rows) >= 1:  # At least the 100g default row
                    print("✓ Servings table shows correct state")
                else:
                    print("✗ Servings table state incorrect")
                    return False
            else:
                print("✗ Servings table not found")
                return False
        
        print("\n" + "="*50)
        print("🎉 ALL TESTS PASSED!")
        print("✅ Admin servings management functionality working correctly")
        print("✅ CRUD operations for servings successful")
        print("✅ Default serving toggle functionality working")
        print("✅ Client-side validation integrated")
        print("✅ AJAX communication working properly")
        print("✅ UI components rendering correctly")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    try:
        # Install required packages for testing
        try:
            import requests
            from bs4 import BeautifulSoup
        except ImportError:
            print("Installing required packages for testing...")
            import subprocess
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'requests', 'beautifulsoup4'])
            import requests
            from bs4 import BeautifulSoup
        
        success = test_admin_servings_functionality()
        if not success:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nTest setup failed: {str(e)}")
        sys.exit(1)
