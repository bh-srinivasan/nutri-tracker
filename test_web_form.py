#!/usr/bin/env python3
"""
Final validation test - Test editing user via web form to ensure email optional works
"""

import requests
from bs4 import BeautifulSoup
import time

def test_web_form_edit():
    base_url = 'http://127.0.0.1:5001'
    session = requests.Session()
    
    print("🧪 Final Validation: Edit User via Web Form")
    print("=" * 55)
    
    # Step 1: Login
    print("Step 1: Login as admin...")
    login_response = session.post(f'{base_url}/auth/login', data={
        'username': 'admin',
        'password': 'admin123'
    })
    
    if login_response.status_code == 200:
        print("✅ Logged in successfully")
    else:
        print("❌ Login failed")
        return
    
    # Step 2: Get users page to find a user to edit
    print("\nStep 2: Getting users page...")
    users_response = session.get(f'{base_url}/admin/users')
    
    if users_response.status_code == 200:
        print("✅ Users page loaded")
    else:
        print("❌ Failed to load users page")
        return
    
    # Step 3: Get edit form for user ID 2
    print("\nStep 3: Getting edit form for user 2...")
    edit_response = session.get(f'{base_url}/admin/users/2/edit')
    
    if edit_response.status_code == 200:
        print("✅ Edit form loaded")
        
        # Parse form
        soup = BeautifulSoup(edit_response.text, 'html.parser')
        form = soup.find('form')
        
        if form:
            csrf_token = form.find('input', {'name': 'csrf_token'})['value']
            username_field = form.find('input', {'name': 'username'})
            first_name_field = form.find('input', {'name': 'first_name'})
            last_name_field = form.find('input', {'name': 'last_name'})
            
            username = username_field['value'] if username_field else 'testuser'
            first_name = first_name_field['value'] if first_name_field else 'Test'
            last_name = last_name_field['value'] if last_name_field else 'User'
            
            print(f"   Current username: {username}")
            print(f"   Current first name: {first_name}")
            print(f"   Current last name: {last_name}")
        else:
            print("❌ Could not find form")
            return
    else:
        print("❌ Failed to load edit form")
        return
    
    # Step 4: Submit form with NO email
    print("\nStep 4: Submitting form with empty email...")
    
    form_data = {
        'csrf_token': csrf_token,
        'username': username,
        'email': '',  # EMPTY EMAIL - this is the test
        'first_name': first_name,
        'last_name': last_name,
        'is_active': 'y'  # Checked
    }
    
    submit_response = session.post(
        f'{base_url}/admin/users/2/edit',
        data=form_data,
        allow_redirects=True  # Follow redirects
    )
    
    print(f"   Form submission status: {submit_response.status_code}")
    
    if submit_response.status_code == 200:
        # Check if we're back on the users page (success) or still on edit page (error)
        if '/admin/users' in submit_response.url and '2/edit' not in submit_response.url:
            print("✅ SUCCESS: Redirected to users page - update succeeded!")
            
            # Check for success message
            if 'updated successfully' in submit_response.text:
                print("✅ Success message found!")
            else:
                print("📝 No explicit success message, but redirect suggests success")
        else:
            print("❌ Still on edit page - likely validation error")
            
            # Look for error messages
            soup = BeautifulSoup(submit_response.text, 'html.parser')
            alerts = soup.find_all('div', class_='alert')
            errors = soup.find_all('span', class_='text-danger')
            
            if alerts:
                print("   Alert messages:")
                for alert in alerts:
                    print(f"   - {alert.get_text().strip()}")
            
            if errors:
                print("   Field errors:")
                for error in errors:
                    print(f"   - {error.get_text().strip()}")
                    
            if not alerts and not errors:
                print("   No specific error messages found")
    else:
        print(f"❌ Unexpected status: {submit_response.status_code}")
    
    # Step 5: Verify the user was actually updated
    print("\nStep 5: Verifying user was updated...")
    
    # Get the edit form again to see current values
    verify_response = session.get(f'{base_url}/admin/users/2/edit')
    
    if verify_response.status_code == 200:
        soup = BeautifulSoup(verify_response.text, 'html.parser')
        form = soup.find('form')
        
        if form:
            email_field = form.find('input', {'name': 'email'})
            current_email = email_field['value'] if email_field and email_field.get('value') else ''
            
            print(f"   Current email in database: '{current_email}'")
            
            if current_email == '':
                print("✅ SUCCESS: Email is empty - update worked!")
            else:
                print(f"❌ Email is not empty: '{current_email}'")
        else:
            print("❌ Could not verify - form not found")
    else:
        print("❌ Could not verify - failed to reload edit form")

if __name__ == '__main__':
    test_web_form_edit()
