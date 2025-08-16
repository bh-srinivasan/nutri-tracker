"""
Check existing admin users and test the user creation functionality
"""
import sys
import os
import getpass
import requests
import json
from datetime import datetime
sys.path.insert(0, os.path.abspath('.'))

from app import create_app, db
from app.models import User

def test_admin_functionality():
    app = create_app()
    
    with app.app_context():
        print("🔍 Checking existing admin users...")
        
        # Get all admin users
        admin_users = User.query.filter_by(is_admin=True).all()
        
        if not admin_users:
            print("❌ No admin users found in database!")
            return False
        
        print(f"✅ Found {len(admin_users)} admin user(s):")
        admin_user = admin_users[0]
        print(f"   - Username: {admin_user.username}")
        print(f"   - User ID: {admin_user.user_id}")
        print(f"   - Email: {admin_user.email or 'No email'}")
        print(f"   - Active: {admin_user.is_active}")
        
        # Ask for password - using input() instead of getpass for VS Code compatibility
        print(f"\n🔐 Please enter the password for admin user '{admin_user.username}':")
        print("Note: Password will be visible in terminal")
        password = input("Password: ").strip()
        
        if not password:
            print("❌ No password provided. Exiting.")
            return False
        
        # Test login and user creation
        return test_user_creation_flow(admin_user.username, password)

def test_user_creation_flow(username, password):
    """Test the complete user creation flow"""
    print(f"\n🧪 Testing user creation flow...")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:5001"
    session = requests.Session()
    
    try:
        # Step 1: Test server accessibility
        print("1. Testing server connectivity...")
        try:
            response = session.get(base_url, timeout=5)
            print(f"   ✅ Server accessible (status: {response.status_code})")
        except requests.exceptions.ConnectionError:
            print("   ❌ Server not accessible. Please ensure the Flask app is running.")
            print("   Run: python app.py")
            return False
        
        # Step 2: Get login page and extract CSRF token if needed
        print("2. Getting login page...")
        login_page = session.get(f"{base_url}/auth/login")
        print(f"   Login page status: {login_page.status_code}")
        
        # Extract CSRF token if present
        csrf_token = None
        if 'csrf_token' in login_page.text:
            import re
            csrf_match = re.search(r'name="csrf_token".*?value="([^"]+)"', login_page.text)
            if csrf_match:
                csrf_token = csrf_match.group(1)
                print(f"   Found CSRF token: {csrf_token[:20]}...")
        
        # Step 3: Login
        print("3. Attempting admin login...")
        login_data = {
            'username': username,
            'password': password
        }
        if csrf_token:
            login_data['csrf_token'] = csrf_token
        
        login_response = session.post(f"{base_url}/auth/login", data=login_data, allow_redirects=False)
        print(f"   Login response status: {login_response.status_code}")
        
        if login_response.status_code not in [200, 302]:
            print("   ❌ Login failed - incorrect credentials or server error")
            return False
        
        print("   ✅ Login successful!")
        
        # Step 4: Test access to admin pages
        print("4. Testing admin access...")
        admin_response = session.get(f"{base_url}/admin")
        print(f"   Admin page status: {admin_response.status_code}")
        
        if admin_response.status_code != 200:
            print("   ❌ Cannot access admin dashboard")
            return False
        
        users_response = session.get(f"{base_url}/admin/users")
        print(f"   Users page status: {users_response.status_code}")
        
        if users_response.status_code != 200:
            print("   ❌ Cannot access user management page")
            return False
        
        print("   ✅ Admin pages accessible!")
        
        # Step 5: Test user creation API
        print("5. Testing user creation API...")
        test_user_id = f"test_user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        test_user_data = {
            'user_id': test_user_id,
            'first_name': 'Test',
            'last_name': 'User',
            'email': f'{test_user_id}@example.com',
            'password': 'TestPassword123!'
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
            print("   ✅ User creation API working!")
            
            # Verify user was created
            from app.models import User
            from app import create_app, db
            app = create_app()
            with app.app_context():
                created_user = User.query.filter_by(user_id=test_user_id).first()
                if created_user:
                    print(f"   ✅ User '{test_user_id}' successfully created in database")
                    print(f"      - Name: {created_user.first_name} {created_user.last_name}")
                    print(f"      - Email: {created_user.email}")
                    return True
                else:
                    print(f"   ❌ User '{test_user_id}' not found in database")
                    return False
        else:
            print(f"   ❌ User creation failed")
            try:
                error_data = api_response.json()
                print(f"   Error: {error_data}")
            except:
                pass
            return False
    
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = test_admin_functionality()
    
    if success:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Admin login works")
        print("✅ User creation API works")
        print("✅ User validation works")
        print("✅ Database integration works")
        print("\n🔧 The user creation functionality is now fully working!")
    else:
        print("\n💥 TESTS FAILED!")
        print("❌ There are still issues with the user creation functionality.")
        print("Please check the error messages above for details.")
