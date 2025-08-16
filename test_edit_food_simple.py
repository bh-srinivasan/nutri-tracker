#!/usr/bin/env python3
"""
Simplified test to check edit food form submission
"""

import requests
import sys
from bs4 import BeautifulSoup

def test_edit_food_simple():
    """Simple test for edit food form"""
    
    base_url = "http://127.0.0.1:5001"
    session = requests.Session()
    
    try:
        # Login
        login_data = {'username': 'admin', 'password': 'admin123'}
        login_response = session.post(f"{base_url}/auth/login", data=login_data)
        
        if 'admin' not in login_response.url and login_response.status_code == 200:
            print("❌ Login failed")
            return False
        
        print("✅ Login successful")
        
        # Get edit food page
        edit_response = session.get(f"{base_url}/admin/foods/1/edit")
        print(f"Edit page status: {edit_response.status_code}")
        
        if edit_response.status_code != 200:
            print("❌ Can't access edit page")
            return False
        
        # Parse the form data properly
        soup = BeautifulSoup(edit_response.text, 'html.parser')
        
        # Find the main food form (not the login form or serving forms)
        food_form = soup.find('form', {'method': 'POST', 'data-food-id': True})
        
        if not food_form:
            # Try to find any POST form that contains food fields
            forms = soup.find_all('form', method='POST')
            print(f"Found {len(forms)} POST forms")
            for i, form in enumerate(forms):
                inputs = form.find_all(['input', 'select'])
                field_names = [inp.get('name') for inp in inputs if inp.get('name')]
                print(f"Form {i}: {field_names}")
                if 'name' in field_names and 'calories' in field_names:
                    food_form = form
                    break
        
        if not food_form:
            print("❌ Food form not found")
            return False
        
        print("✅ Food form found")
        
        # Extract form data
        form_data = {}
        for input_field in food_form.find_all(['input', 'select', 'textarea']):
            name = input_field.get('name')
            if name:
                if input_field.name == 'input':
                    if input_field.get('type') == 'checkbox':
                        form_data[name] = 'y' if input_field.get('checked') else ''
                    else:
                        form_data[name] = input_field.get('value', '')
                elif input_field.name == 'select':
                    selected = input_field.find('option', selected=True)
                    if selected:
                        form_data[name] = selected.get('value', '')
                    else:
                        # Get first non-empty option
                        options = input_field.find_all('option')
                        for opt in options:
                            if opt.get('value'):
                                form_data[name] = opt.get('value')
                                break
        
        print(f"Form fields: {list(form_data.keys())}")
        
        # Make sure we have required fields
        required_fields = ['csrf_token', 'name', 'category', 'calories', 'protein', 'carbs', 'fat']
        missing_fields = [field for field in required_fields if field not in form_data]
        
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
            return False
        
        # Make a minimal change to test
        original_name = form_data.get('name', '')
        form_data['name'] = f"{original_name} UPDATED"
        
        print(f"Updating name to: {form_data['name']}")
        
        # Submit form
        submit_response = session.post(
            f"{base_url}/admin/foods/1/edit",
            data=form_data,
            allow_redirects=False
        )
        
        print(f"Submit status: {submit_response.status_code}")
        print(f"Submit headers: {dict(submit_response.headers)}")
        
        if submit_response.status_code == 302:
            location = submit_response.headers.get('Location', '')
            print(f"Redirected to: {location}")
            if 'login' in location:
                print("❌ Redirected to login - authentication issue")
                return False
            else:
                print("✅ Form submitted successfully")
                return True
        elif submit_response.status_code == 200:
            # Check for errors in response
            response_soup = BeautifulSoup(submit_response.text, 'html.parser')
            errors = response_soup.find_all(class_='text-danger')
            if errors:
                print("❌ Form errors:")
                for error in errors:
                    print(f"  - {error.get_text().strip()}")
            else:
                print("⚠️ Form returned 200 without obvious errors")
            return False
        else:
            print(f"❌ Unexpected status: {submit_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_edit_food_simple()
    sys.exit(0 if success else 1)
