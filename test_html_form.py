#!/usr/bin/env python3
"""
Test to simulate the actual browser behavior when editing a user through the HTML form
"""

import requests
from bs4 import BeautifulSoup

def test_edit_user_html_form():
    base_url = 'http://127.0.0.1:5001'
    session = requests.Session()
    
    print("🧪 Test: Edit User via HTML Form (No Email)")
    print("=" * 50)
    
    # Step 1: Login as admin
    print("Step 1: Logging in as admin...")
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    login_response = session.post(f'{base_url}/auth/login', data=login_data, allow_redirects=True)
    
    if login_response.status_code == 200:
        print("✅ Logged in successfully")
    else:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    # Step 2: Access users page
    print("\nStep 2: Accessing users page...")
    users_response = session.get(f'{base_url}/admin/users')
    
    if users_response.status_code == 200:
        print("✅ Users page loaded")
        # Parse the page to find a user to edit
        soup = BeautifulSoup(users_response.text, 'html.parser')
        
        # Look for edit buttons
        edit_buttons = soup.find_all('button', {'class': 'btn-warning'})
        if edit_buttons:
            # Get the first edit button's onclick attribute to extract user ID
            onclick = edit_buttons[0].get('onclick', '')
            if 'Admin.users.edit(' in onclick:
                user_id = onclick.split('(')[1].split(')')[0]
                print(f"✅ Found user to edit: ID {user_id}")
            else:
                user_id = "2"  # Fallback
                print(f"📝 Using fallback user ID: {user_id}")
        else:
            user_id = "2"  # Fallback
            print(f"📝 No edit buttons found, using fallback user ID: {user_id}")
    else:
        print(f"❌ Failed to access users page: {users_response.status_code}")
        return
    
    # Step 3: Access the edit user page directly
    print(f"\nStep 3: Accessing edit user page for user {user_id}...")
    edit_page_response = session.get(f'{base_url}/admin/users/{user_id}/edit')
    
    if edit_page_response.status_code == 200:
        print("✅ Edit user page loaded")
        
        # Parse the form to get current values and CSRF token
        soup = BeautifulSoup(edit_page_response.text, 'html.parser')
        form = soup.find('form')
        
        if form:
            # Extract form data
            csrf_token = form.find('input', {'name': 'csrf_token'})['value']
            username = form.find('input', {'name': 'username'})['value']
            first_name = form.find('input', {'name': 'first_name'})['value']
            last_name = form.find('input', {'name': 'last_name'})['value']
            email_field = form.find('input', {'name': 'email'})
            email = email_field['value'] if email_field else ''
            
            print(f"✅ Form data extracted:")
            print(f"   Username: {username}")
            print(f"   First Name: {first_name}")
            print(f"   Last Name: {last_name}")
            print(f"   Current Email: '{email}'")
            print(f"   CSRF Token: {csrf_token[:20]}...")
        else:
            print("❌ Could not find form on edit page")
            return
    else:
        print(f"❌ Failed to access edit user page: {edit_page_response.status_code}")
        return
    
    # Step 4: Submit form with no email
    print(f"\nStep 4: Submitting form with empty email...")
    
    form_data = {
        'csrf_token': csrf_token,
        'username': username,
        'email': '',  # Empty email
        'first_name': first_name,
        'last_name': last_name,
        'is_admin': '',  # Unchecked
        'is_active': 'y'  # Checked
    }
    
    submit_response = session.post(
        f'{base_url}/admin/users/{user_id}/edit',
        data=form_data,
        allow_redirects=False
    )
    
    print(f"📥 Form submission response:")
    print(f"   Status: {submit_response.status_code}")
    print(f"   Headers: {dict(submit_response.headers)}")
    
    if submit_response.status_code == 302:
        # Successful redirect
        redirect_location = submit_response.headers.get('Location', '')
        print(f"✅ SUCCESS: Form submitted successfully!")
        print(f"   Redirected to: {redirect_location}")
        
        # Follow the redirect to see any flash messages
        final_response = session.get(redirect_location)
        if 'updated successfully' in final_response.text:
            print("✅ Success message found on redirect page")
        elif 'error' in final_response.text.lower():
            print("❌ Error message found on redirect page")
        else:
            print("📝 No clear success/error message found")
            
    elif submit_response.status_code == 200:
        # Form was resubmitted (validation errors)
        print("❌ Form has validation errors")
        
        # Parse the response to look for error messages
        soup = BeautifulSoup(submit_response.text, 'html.parser')
        error_messages = soup.find_all('div', {'class': 'alert-danger'})
        field_errors = soup.find_all('span', {'class': 'text-danger'})
        
        if error_messages:
            print("🔍 Alert error messages found:")
            for error in error_messages:
                print(f"   - {error.get_text().strip()}")
        
        if field_errors:
            print("🔍 Field error messages found:")
            for error in field_errors:
                print(f"   - {error.get_text().strip()}")
                
        if not error_messages and not field_errors:
            print("🔍 No specific error messages found in response")
    else:
        print(f"❌ Unexpected status code: {submit_response.status_code}")

if __name__ == '__main__':
    test_edit_user_html_form()
