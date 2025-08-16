#!/usr/bin/env python3
"""
Test the corrected form structure and flash messages
"""

import requests
import sys
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def test_corrected_form():
    """Test that both issues are now fixed"""
    
    base_url = "http://127.0.0.1:5001"
    session = requests.Session()
    
    try:
        print("🧪 Testing Corrected Edit Food Form")
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
        
        print("\n🔍 Checking Form Structure:")
        
        # Check main food form
        main_form = soup.find('form', {'data-food-id': True})
        if not main_form:
            print("❌ Main food form not found")
            return False
        
        print("✅ Main food form found")
        
        # Check for nested forms (should be none)
        nested_forms = main_form.find_all('form')
        if nested_forms:
            print(f"❌ Found {len(nested_forms)} nested forms")
            return False
        
        print("✅ No nested forms in main form")
        
        # Check that Update Food button is in main form
        update_button = main_form.find('button', type='submit')
        if not update_button:
            print("❌ Submit button not found in main form")
            return False
        
        button_text = update_button.get_text().strip()
        if 'Update Food' not in button_text:
            print(f"❌ Submit button found but wrong text: '{button_text}'")
            return False
        
        print("✅ Update Food button found in main form")
        
        # Check that servings section is outside main form
        servings_card = soup.find('div', class_='card')
        servings_header = None
        for card in soup.find_all('div', class_='card'):
            header = card.find('h5')
            if header and 'Servings' in header.get_text():
                servings_header = header
                servings_card = card
                break
        
        if not servings_header:
            print("❌ Servings section not found")
            return False
        
        print("✅ Servings section found")
        
        # Check that add serving form is in servings section but outside main form
        add_serving_form = soup.find('form', {'id': 'add-serving-form'})
        if not add_serving_form:
            print("❌ Add serving form not found")
            return False
        
        # Check if add serving form is inside main form (should not be)
        if main_form.find('form', {'id': 'add-serving-form'}):
            print("❌ Add serving form is still nested in main form")
            return False
        
        print("✅ Add serving form found outside main form")
        
        # Check placement: add serving form should be in servings section
        if servings_card.find('form', {'id': 'add-serving-form'}):
            print("✅ Add serving form correctly placed in servings section")
        else:
            print("⚠️ Add serving form not in servings section")
        
        print("\n🚀 Testing Form Submission:")
        
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
        
        # Test form submission with a change
        original_name = form_data.get('name', '')
        test_name = f"{original_name} [CORRECTED TEST]"
        form_data['name'] = test_name
        
        print(f"📝 Updating name: '{original_name}' -> '{test_name}'")
        
        submit_response = session.post(edit_url, data=form_data, allow_redirects=False)
        
        print(f"📊 Submit status: {submit_response.status_code}")
        
        if submit_response.status_code == 302:
            location = submit_response.headers.get('Location', '')
            print(f"📍 Redirect location: {location}")
            
            if 'login' in location:
                print("❌ Redirected to login - session issue")
                return False
            elif f'/admin/foods/1/edit' in location:
                print("✅ Correctly redirected back to edit page")
                
                # Follow redirect to check for flash message
                final_url = urljoin(edit_url, location)
                final_response = session.get(final_url)
                
                if final_response.status_code == 200:
                    final_soup = BeautifulSoup(final_response.text, 'html.parser')
                    
                    # Check for flash messages
                    alerts = final_soup.find_all('div', class_=lambda x: x and 'alert' in x)
                    flash_found = False
                    
                    if alerts:
                        print("📢 Flash messages found:")
                        for alert in alerts:
                            message = alert.get_text().strip()
                            if message:
                                print(f"   - {message}")
                                if 'updated successfully' in message.lower():
                                    flash_found = True
                    
                    if flash_found:
                        print("✅ Success flash message confirmed")
                    else:
                        print("⚠️ No success flash message found")
                    
                    return True
                else:
                    print(f"❌ Error following redirect: {final_response.status_code}")
                    return False
            else:
                print(f"⚠️ Unexpected redirect location: {location}")
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
    success = test_corrected_form()
    print(f"\n{'🎉 ALL ISSUES FIXED!' if success else '❌ ISSUES REMAIN'}")
    sys.exit(0 if success else 1)
