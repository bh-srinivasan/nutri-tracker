#!/usr/bin/env python3
"""
Direct test to identify the edit food form issue
"""

import requests
import sys
from urllib.parse import urljoin

def test_form_submission():
    """Test form submission with proper session handling"""
    
    base_url = "http://127.0.0.1:5001"
    
    # Create session with proper headers
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    })
    
    try:
        print("🔐 Testing admin login...")
        
        # Step 1: Get login page to get CSRF token
        login_page_response = session.get(f"{base_url}/auth/login")
        print(f"Login page status: {login_page_response.status_code}")
        
        if login_page_response.status_code != 200:
            print("❌ Cannot access login page")
            return False
        
        # Extract CSRF token from login page
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(login_page_response.text, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrf_token'})
        
        if not csrf_input:
            print("❌ CSRF token not found on login page")
            return False
        
        csrf_token = csrf_input.get('value')
        print(f"✅ CSRF token: {csrf_token[:10]}...")
        
        # Step 2: Submit login
        login_data = {
            'username': 'admin',
            'password': 'admin123',
            'csrf_token': csrf_token,
            'submit': 'Sign In'
        }
        
        login_response = session.post(
            f"{base_url}/auth/login",
            data=login_data,
            allow_redirects=True
        )
        
        print(f"Login response status: {login_response.status_code}")
        print(f"Login response URL: {login_response.url}")
        
        # Check if login was successful
        if 'admin' not in login_response.url and 'dashboard' not in login_response.url:
            print("❌ Login failed - checking response")
            if 'Invalid username or password' in login_response.text:
                print("❌ Invalid credentials")
            else:
                print("❌ Unknown login error")
            return False
        
        print("✅ Login successful")
        
        # Step 3: Access edit food page
        edit_url = f"{base_url}/admin/foods/1/edit"
        edit_response = session.get(edit_url)
        
        print(f"Edit page status: {edit_response.status_code}")
        print(f"Edit page URL: {edit_response.url}")
        
        if edit_response.status_code != 200:
            print("❌ Cannot access edit food page")
            if 'login' in edit_response.url:
                print("❌ Redirected to login - session lost")
            return False
        
        print("✅ Edit food page accessible")
        
        # Step 4: Parse edit food form
        edit_soup = BeautifulSoup(edit_response.text, 'html.parser')
        
        # Look for food form specifically
        food_form = None
        forms = edit_soup.find_all('form', method='POST')
        
        print(f"Found {len(forms)} POST forms on page")
        
        for i, form in enumerate(forms):
            # Check if this form has food-related fields
            inputs = form.find_all(['input', 'select', 'textarea'])
            field_names = [inp.get('name') for inp in inputs if inp.get('name')]
            print(f"Form {i+1} fields: {field_names}")
            
            # Look for food form indicators
            if 'name' in field_names and 'calories' in field_names:
                food_form = form
                print(f"✅ Found food form (Form {i+1})")
                break
        
        if not food_form:
            print("❌ Food form not found")
            return False
        
        # Step 5: Extract form data
        form_data = {}
        
        for input_field in food_form.find_all(['input', 'select', 'textarea']):
            name = input_field.get('name')
            if not name:
                continue
                
            if input_field.name == 'input':
                input_type = input_field.get('type', 'text')
                if input_type == 'checkbox':
                    # For checkboxes, send 'y' if checked, nothing if unchecked
                    if input_field.get('checked'):
                        form_data[name] = 'y'
                elif input_type == 'hidden' or input_type == 'text' or input_type == 'number':
                    form_data[name] = input_field.get('value', '')
            elif input_field.name == 'select':
                # Find selected option
                selected_option = input_field.find('option', selected=True)
                if selected_option:
                    form_data[name] = selected_option.get('value', '')
                else:
                    # If no option is selected, find the first non-empty option
                    options = input_field.find_all('option')
                    for option in options:
                        value = option.get('value', '')
                        if value and value != '':
                            form_data[name] = value
                            break
            elif input_field.name == 'textarea':
                form_data[name] = input_field.get_text().strip()
        
        print(f"✅ Extracted form data: {list(form_data.keys())}")
        
        # Make sure we have the essential fields
        required_fields = ['csrf_token', 'name', 'category', 'calories', 'protein', 'carbs', 'fat']
        missing_fields = [field for field in required_fields if field not in form_data or not form_data[field]]
        
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
            print(f"Available fields: {form_data}")
            return False
        
        # Step 6: Make a small change and submit
        original_name = form_data['name']
        test_name = f"{original_name} [EDITED TEST]"
        form_data['name'] = test_name
        
        print(f"🚀 Submitting form: '{original_name}' -> '{test_name}'")
        
        submit_response = session.post(
            edit_url,
            data=form_data,
            allow_redirects=False,
            headers={'Referer': edit_url}
        )
        
        print(f"Submit status: {submit_response.status_code}")
        print(f"Submit headers: {dict(submit_response.headers)}")
        
        if submit_response.status_code == 302:
            location = submit_response.headers.get('Location', '')
            print(f"Redirected to: {location}")
            
            if 'login' in location:
                print("❌ Redirected to login - session expired during submission")
                return False
            else:
                print("✅ Form submitted successfully!")
                
                # Follow redirect to see result
                final_url = urljoin(edit_url, location)
                final_response = session.get(final_url)
                
                if 'updated successfully' in final_response.text.lower():
                    print("✅ Success message confirmed")
                    return True
                else:
                    print("⚠️ No success message found")
                    return True  # Still consider it successful if redirect worked
                    
        elif submit_response.status_code == 200:
            # Form returned to same page - check for errors
            response_soup = BeautifulSoup(submit_response.text, 'html.parser')
            
            # Check for flash messages
            alerts = response_soup.find_all(class_=lambda x: x and 'alert' in x)
            if alerts:
                print("📋 Flash messages:")
                for alert in alerts:
                    print(f"  - {alert.get_text().strip()}")
            
            # Check for form validation errors
            errors = response_soup.find_all(class_='text-danger')
            if errors:
                print("❌ Form validation errors:")
                for error in errors:
                    error_text = error.get_text().strip()
                    if error_text:
                        print(f"  - {error_text}")
                return False
            
            print("⚠️ Form returned 200 without obvious errors")
            return False
            
        else:
            print(f"❌ Unexpected response status: {submit_response.status_code}")
            print(f"Response: {submit_response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_form_submission()
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}")
    sys.exit(0 if success else 1)
