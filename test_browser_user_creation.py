"""
Simple browser test using requests-html to test the user creation flow.
This will test the actual flow: login -> navigate to admin -> open modal -> submit form
"""

import time
from requests_html import HTMLSession

def test_user_creation_flow():
    """Test the complete user creation flow"""
    print("🔍 Testing User Creation Flow")
    print("=" * 50)
    
    session = HTMLSession()
    base_url = "http://127.0.0.1:5001"
    
    try:
        # Step 1: Load login page
        print("1. Loading login page...")
        login_page = session.get(f"{base_url}/auth/login")
        print(f"   Status: {login_page.status_code}")
        
        if login_page.status_code != 200:
            print(f"   ❌ Failed to load login page")
            return False
        
        # Step 2: Extract form and login
        print("2. Logging in as admin...")
        
        # Find the login form
        login_form = login_page.html.find('form', first=True)
        if not login_form:
            print("   ❌ No login form found")
            return False
        
        # Get form action
        form_action = login_form.attrs.get('action', '/auth/login')
        
        # Prepare login data
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        # Check for CSRF token
        csrf_input = login_page.html.find('input[name="csrf_token"]', first=True)
        if csrf_input:
            csrf_token = csrf_input.attrs.get('value')
            if csrf_token:
                login_data['csrf_token'] = csrf_token
                print(f"   Found CSRF token: {csrf_token[:20]}...")
        
        # Submit login
        login_response = session.post(f"{base_url}{form_action}", data=login_data, allow_redirects=False)
        print(f"   Login response: {login_response.status_code}")
        
        if login_response.status_code not in [200, 302]:
            print(f"   ❌ Login failed")
            return False
        
        print("   ✅ Login successful")
        
        # Step 3: Navigate to admin dashboard
        print("3. Loading admin dashboard...")
        admin_page = session.get(f"{base_url}/admin")
        print(f"   Admin page status: {admin_page.status_code}")
        
        if admin_page.status_code != 200:
            print(f"   ❌ Failed to access admin dashboard")
            return False
        
        # Step 4: Navigate to user management
        print("4. Loading user management...")
        users_page = session.get(f"{base_url}/admin/users")
        print(f"   Users page status: {users_page.status_code}")
        
        if users_page.status_code != 200:
            print(f"   ❌ Failed to access user management")
            return False
        
        print("   ✅ Successfully accessed user management page")
        
        # Step 5: Test API endpoint directly with session cookies
        print("5. Testing user creation API...")
        test_user_data = {
            'user_id': 'browsertest123',
            'first_name': 'Browser',
            'last_name': 'Test',
            'email': 'browsertest@example.com',
            'password': 'BrowserTest123!'
        }
        
        api_response = session.post(
            f"{base_url}/api/admin/users",
            json=test_user_data,
            headers={
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        )
        
        print(f"   API response status: {api_response.status_code}")
        print(f"   API response: {api_response.text}")
        
        if api_response.status_code == 201:
            print("   ✅ User creation successful!")
            return True
        elif api_response.status_code == 401:
            print("   ❌ Authentication failed - session not properly maintained")
            return False
        else:
            print(f"   ❌ User creation failed with status {api_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = test_user_creation_flow()
    
    if success:
        print("\n🎉 User creation flow test PASSED!")
    else:
        print("\n💥 User creation flow test FAILED!")
        print("\nTry manually:")
        print("1. Open http://127.0.0.1:5001 in your browser")
        print("2. Login as admin/admin123")
        print("3. Go to Admin Dashboard -> Manage Users")
        print("4. Click '+Add User' button")
        print("5. Fill in the form and submit")
    
    exit(0 if success else 1)
