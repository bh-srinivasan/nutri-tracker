#!/usr/bin/env python3
"""
Test script to diagnose the edit food form submission issue
"""

import requests
import sys
from bs4 import BeautifulSoup
import re

def test_edit_food_form():
    """Test the edit food form submission functionality"""
    
    base_url = "http://127.0.0.1:5001"
    
    print("🧪 Testing Edit Food Form Submission")
    print("=" * 50)
    
    # Test login
    session = requests.Session()
    
    # Login as admin
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    try:
        # Step 1: Login
        login_response = session.post(f"{base_url}/auth/login", data=login_data)
        if login_response.status_code != 200:
            print("❌ Admin login failed")
            return False
        print("✅ Admin login successful")
        
        # Step 2: Get edit food page 
        edit_response = session.get(f"{base_url}/admin/foods/1/edit")
        if edit_response.status_code != 200:
            print("❌ Failed to access edit food page")
            print(f"Status: {edit_response.status_code}")
            print(f"Response: {edit_response.text[:500]}")
            return False
        
        print("✅ Edit food page loaded successfully")
        
        # Step 3: Parse the form to get CSRF token and current data
        soup = BeautifulSoup(edit_response.text, 'html.parser')
        form = soup.find('form', method='POST')
        
        if not form:
            print("❌ Form not found in edit food page")
            return False
        
        print("✅ Form found in edit food page")
        
        # Extract CSRF token
        csrf_token = None
        csrf_input = form.find('input', {'name': 'csrf_token'})
        if csrf_input:
            csrf_token = csrf_input.get('value')
            print(f"✅ CSRF token found: {csrf_token[:20]}...")
        else:
            print("❌ CSRF token not found")
            return False
        
        # Extract current form data
        form_data = {
            'csrf_token': csrf_token
        }
        
        # Get all form fields
        for input_field in form.find_all(['input', 'select', 'textarea']):
            name = input_field.get('name')
            if name and name != 'csrf_token':
                value = input_field.get('value', '')
                if input_field.name == 'select':
                    selected = input_field.find('option', selected=True)
                    value = selected.get('value') if selected else ''
                form_data[name] = value
        
        print(f"✅ Extracted form data: {list(form_data.keys())}")
        
        # Step 4: Make a small change to test update
        original_name = form_data.get('name', '')
        form_data['name'] = f"{original_name} - TEST UPDATE"
        
        print(f"✅ Modified name from '{original_name}' to '{form_data['name']}'")
        
        # Step 5: Submit the form
        print("🚀 Submitting form update...")
        
        update_response = session.post(
            f"{base_url}/admin/foods/1/edit", 
            data=form_data,
            allow_redirects=False  # Don't follow redirects to see what happens
        )
        
        print(f"📊 Update response status: {update_response.status_code}")
        print(f"📊 Update response headers: {dict(update_response.headers)}")
        
        if update_response.status_code == 302:
            redirect_location = update_response.headers.get('Location', '')
            print(f"✅ Form submitted successfully - Redirect to: {redirect_location}")
            
            # Follow the redirect to confirm
            if redirect_location:
                final_response = session.get(redirect_location)
                if 'updated successfully' in final_response.text.lower():
                    print("✅ Update success message found")
                else:
                    print("⚠️ No success message found, but redirect occurred")
            
            return True
            
        elif update_response.status_code == 200:
            # Check if there are form errors or if we're back on the same page
            response_soup = BeautifulSoup(update_response.text, 'html.parser')
            
            # Check for flash messages
            flash_messages = response_soup.find_all(class_=re.compile(r'alert'))
            if flash_messages:
                print("📋 Flash messages found:")
                for msg in flash_messages:
                    print(f"   - {msg.get_text().strip()}")
            
            # Check for form errors
            form_errors = response_soup.find_all(class_='text-danger')
            if form_errors:
                print("❌ Form validation errors found:")
                for error in form_errors:
                    print(f"   - {error.get_text().strip()}")
                return False
            
            print("⚠️ Form returned 200 but no obvious errors - might be validation issue")
            return False
            
        else:
            print(f"❌ Unexpected response status: {update_response.status_code}")
            print(f"Response text: {update_response.text[:500]}")
            return False
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure Flask app is running on port 5001")
        return False
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_edit_food_form()
    sys.exit(0 if success else 1)
