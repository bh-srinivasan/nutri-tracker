#!/usr/bin/env python3
"""
Test to verify the nested form fix is working
"""

import requests
import sys
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def test_form_fix():
    """Test that the form structure is now correct and works"""
    
    base_url = "http://127.0.0.1:5001"
    session = requests.Session()
    
    try:
        print("🔍 Testing Fixed Edit Food Form")
        print("=" * 40)
        
        # Login
        login_page = session.get(f"{base_url}/auth/login")
        soup = BeautifulSoup(login_page.text, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
        
        login_data = {
            'username': 'admin', 
            'password': 'admin123',
            'csrf_token': csrf_token
        }
        
        login_response = session.post(f"{base_url}/auth/login", data=login_data, allow_redirects=True)
        
        if 'admin' not in login_response.url:
            print("❌ Login failed")
            return False
        
        print("✅ Login successful")
        
        # Get edit food page
        edit_url = f"{base_url}/admin/foods/1/edit"
        edit_response = session.get(edit_url)
        
        if edit_response.status_code != 200:
            print("❌ Cannot access edit food page")
            return False
        
        print("✅ Edit food page loaded")
        
        # Check form structure
        soup = BeautifulSoup(edit_response.text, 'html.parser')
        
        # Check that we don't have nested forms
        main_form = soup.find('form', {'data-food-id': True})
        if not main_form:
            print("❌ Main food form not found")
            return False
        
        print("✅ Main food form found")
        
        # Check for nested forms (should be none)
        nested_forms = main_form.find_all('form')
        if nested_forms:
            print(f"❌ Found {len(nested_forms)} nested forms - this is still a problem!")
            return False
        
        print("✅ No nested forms found - structure is clean")
        
        # Check that add serving form exists outside main form
        add_serving_form = soup.find('form', {'id': 'add-serving-form'})
        if not add_serving_form:
            print("❌ Add serving form not found")
            return False
        
        print("✅ Add serving form found outside main form")
        
        # Extract main form data
        form_data = {}
        for input_field in main_form.find_all(['input', 'select', 'textarea']):
            name = input_field.get('name')
            if not name:
                continue
                
            if input_field.name == 'input':
                input_type = input_field.get('type', 'text')
                if input_type == 'checkbox':
                    if input_field.get('checked'):
                        form_data[name] = 'y'
                else:
                    form_data[name] = input_field.get('value', '')
            elif input_field.name == 'select':
                selected_option = input_field.find('option', selected=True)
                if selected_option:
                    form_data[name] = selected_option.get('value', '')
                else:
                    options = input_field.find_all('option')
                    for option in options:
                        value = option.get('value', '')
                        if value:
                            form_data[name] = value
                            break
        
        print(f"✅ Extracted {len(form_data)} form fields")
        
        # Test form submission
        original_name = form_data.get('name', '')
        test_name = f"{original_name} [FIXED TEST]"
        form_data['name'] = test_name
        
        print(f"🚀 Testing form submission: '{original_name}' -> '{test_name}'")
        
        submit_response = session.post(edit_url, data=form_data, allow_redirects=False)
        
        print(f"📊 Submit status: {submit_response.status_code}")
        
        if submit_response.status_code == 302:
            location = submit_response.headers.get('Location', '')
            if 'login' in location:
                print("❌ Redirected to login - session issue")
                return False
            else:
                print("✅ Form submitted successfully!")
                
                # Follow redirect
                final_url = urljoin(edit_url, location)
                final_response = session.get(final_url)
                
                if 'updated successfully' in final_response.text.lower():
                    print("✅ Success message confirmed")
                else:
                    print("⚠️ No success message, but redirect worked")
                
                return True
        else:
            print(f"❌ Unexpected status: {submit_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_form_fix()
    print(f"\n{'🎉 FORM FIX SUCCESSFUL!' if success else '❌ FORM FIX FAILED'}")
    sys.exit(0 if success else 1)
