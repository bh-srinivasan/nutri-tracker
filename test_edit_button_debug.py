#!/usr/bin/env python3
"""
Quick test script to verify Edit User functionality by checking browser console logs.
"""

import requests
from bs4 import BeautifulSoup
import sys

def test_edit_user_page():
    """Test if the edit user page loads correctly with all required elements."""
    print("🔍 Testing Edit User Functionality")
    print("=" * 40)
    
    base_url = "http://localhost:5001"
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    try:
        # First try to access users page to see if we need to login
        response = session.get(f"{base_url}/admin/users", timeout=5)
        print(f"✅ Initial response: {response.status_code}")
        
        # If redirected to login, let's try to login
        if response.status_code == 302 or 'login' in response.url.lower():
            print("🔐 Need to login first, attempting admin login...")
            
            # Get login page to get CSRF token if needed
            login_response = session.get(f"{base_url}/auth/login")
            if login_response.status_code == 200:
                print("✅ Login page accessible")
                
                # Try to login with admin credentials
                login_data = {
                    'username': 'admin',
                    'password': 'admin123'  # Common default password
                }
                
                login_post = session.post(f"{base_url}/auth/login", data=login_data, allow_redirects=True)
                print(f"✅ Login attempt result: {login_post.status_code}")
                
                # Now try to access users page again
                response = session.get(f"{base_url}/admin/users", timeout=5)
                print(f"✅ Users page after login: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Check for edit buttons
            edit_buttons = soup.find_all('button', class_='edit-user-btn')
            print(f"✅ Found {len(edit_buttons)} edit buttons")
            
            # Check if there are any users displayed at all
            user_rows = soup.find_all('tr')  # Look for table rows
            print(f"✅ Found {len(user_rows)} table rows (including headers)")
            
            # Check for "No users found" message
            no_users_msg = soup.find(string=lambda text: text and 'no users' in text.lower())
            print(f"✅ No users message: {no_users_msg is not None}")
            
            # Check if JavaScript files are included
            script_tags = soup.find_all('script', src=True)
            js_files = [tag['src'] for tag in script_tags]
            
            admin_js_found = any('admin.js' in js for js in js_files)
            main_js_found = any('main.js' in js for js in js_files)
            
            print(f"✅ admin.js included: {admin_js_found}")
            print(f"✅ main.js included: {main_js_found}")
            
            # Check for edit modal
            edit_modal = soup.find('div', id='editUserModal')
            print(f"✅ Edit modal present: {edit_modal is not None}")
            
            # Check if debug script is present
            debug_script = soup.find('script', string=lambda text: text and 'Debug: Users page scripts loaded' in text)
            print(f"✅ Debug script present: {debug_script is not None}")
            
            # Let's also check the actual page title and content to debug what we're getting
            page_title = soup.find('title')
            print(f"✅ Page title: {page_title.get_text() if page_title else 'None'}")
            
            # Check for any error messages
            error_divs = soup.find_all('div', class_='alert-danger')
            if error_divs:
                print(f"❌ Found error messages:")
                for error in error_divs:
                    print(f"   - {error.get_text().strip()}")
            
            print("\n🎯 RECOMMENDATIONS:")
            if len(edit_buttons) == 0:
                print("❌ NO EDIT BUTTONS FOUND - This is the core issue!")
                print("   - Check if users are being displayed in the table")
                print("   - Verify that non-admin users exist in the database")
                print("   - Ensure the template is rendering the user list correctly")
            
            if not admin_js_found:
                print("❌ ADMIN.JS NOT LOADED - JavaScript won't work!")
                print("   - Check template block structure")
                print("   - Verify static file serving is working")
            
            return True
            
        else:
            print(f"❌ Could not access users page: {response.status_code}")
            print(f"   Response URL: {response.url}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_edit_user_page()
