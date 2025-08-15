#!/usr/bin/env python3
"""
Test the Add Serving UI functionality by simulating browser interactions
"""

import requests
from bs4 import BeautifulSoup
import time

def test_serving_ui():
    """Test the serving UI functionality"""
    
    print("🧪 Testing Add Serving UI")
    print("=========================")
    
    # Test that we can load the edit food page and the form is properly structured
    session = requests.Session()
    
    # Login
    login_url = "http://localhost:5001/auth/login"
    login_data = {'username': 'admin', 'password': 'admin123'}
    
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
    
    # Get edit food page
    edit_url = "http://localhost:5001/admin/foods/1/edit"
    
    try:
        edit_response = session.get(edit_url)
        if edit_response.status_code != 200:
            print(f"❌ Failed to load edit page: {edit_response.status_code}")
            return False
        
        print("✅ Edit food page loaded")
        
        # Parse the page and check form structure
        soup = BeautifulSoup(edit_response.content, 'html.parser')
        
        # Check 1: Add serving form exists
        add_form = soup.find('form', {'id': 'add-serving-form'})
        if not add_form:
            print("❌ Add serving form not found")
            return False
        print("✅ Add serving form found")
        
        # Check 2: Form has required fields
        serving_name = add_form.find('input', {'name': 'serving_name'})
        unit = add_form.find('input', {'name': 'unit'})
        grams = add_form.find('input', {'name': 'grams_per_unit'})
        
        if not all([serving_name, unit, grams]):
            print("❌ Missing required form fields")
            return False
        print("✅ All required form fields present")
        
        # Check 3: Submit button exists and has correct type
        submit_btn = add_form.find('button', {'id': 'addServingBtn'})
        if not submit_btn:
            print("❌ Add serving button not found")
            return False
        
        if submit_btn.get('type') != 'submit':
            print(f"❌ Button type is '{submit_btn.get('type')}', should be 'submit'")
            return False
        print("✅ Add serving button found with correct type")
        
        # Check 4: Hidden food ID field exists
        food_id_field = add_form.find('input', {'data-food-id': True})
        if not food_id_field:
            print("❌ Food ID field not found")
            return False
        print("✅ Food ID field found")
        
        # Check 5: Admin.js script is loaded
        admin_script = soup.find('script', src=lambda x: x and 'admin.js' in x)
        if not admin_script:
            print("❌ Admin.js script not found")
            return False
        print("✅ Admin.js script found")
        
        # Check 6: Binding script exists
        binding_script = soup.find('script', string=lambda x: x and 'bindEvents' in x)
        if not binding_script:
            print("❌ Event binding script not found")
            return False
        print("✅ Event binding script found")
        
        # Check 7: Script loads without defer (should load before DOMContentLoaded)
        if admin_script.get('defer'):
            print("⚠️  Admin.js has defer attribute - this might cause timing issues")
        else:
            print("✅ Admin.js loads immediately")
        
        print("\n🎯 UI Structure Summary:")
        print("   1. ✅ Add serving form properly structured")
        print("   2. ✅ Submit button with correct type")
        print("   3. ✅ All required fields present")
        print("   4. ✅ JavaScript properly included")
        print("   5. ✅ Event binding code present")
        
        return True
        
    except Exception as e:
        print(f"❌ Edit page error: {e}")
        return False

if __name__ == "__main__":
    try:
        success = test_serving_ui()
        if success:
            print("\n🎉 UI STRUCTURE TEST PASSED!")
            print("\n💡 Manual test: Try adding a serving in the browser")
        else:
            print("\n❌ UI STRUCTURE TEST FAILED!")
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
