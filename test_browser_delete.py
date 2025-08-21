#!/usr/bin/env python3
"""
Test admin delete with proper session handling like a browser
"""

from app import create_app
import json

def test_browser_like_delete():
    """Test delete with proper session handling"""
    
    print("=== BROWSER-LIKE DELETE TEST ===\n")
    
    app = create_app()
    
    with app.test_client() as client:
        with app.app_context():
            from app.models import User, Food, MealLog
            
            # Step 1: Go to login page to get session and CSRF token
            print("1. Getting login page...")
            login_page = client.get('/auth/login')
            print(f"   Status: {login_page.status_code}")
            
            # Extract CSRF token if present
            csrf_token = None
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(login_page.data, 'html.parser')
                csrf_input = soup.find('input', {'name': 'csrf_token'})
                if csrf_input:
                    csrf_token = csrf_input.get('value')
                    print(f"   Found CSRF token")
                else:
                    print("   No CSRF token found")
            except ImportError:
                print("   BeautifulSoup not available, skipping CSRF")
            
            # Step 2: Login properly
            print("\n2. Logging in as admin...")
            login_data = {
                'username': 'admin',
                'password': 'admin123'  # Correct password
            }
            
            if csrf_token:
                login_data['csrf_token'] = csrf_token
                
            login_response = client.post('/auth/login', data=login_data, follow_redirects=True)
            
            print(f"   Login response status: {login_response.status_code}")
            
            # Check if we're logged in by checking session
            with client.session_transaction() as sess:
                user_id = sess.get('_user_id')
                print(f"   Session user_id: {user_id}")
                
            if not user_id:
                print("   ❌ Login failed - no session")
                return
                
            # Step 3: Test a regular API endpoint first
            print("\n3. Testing regular API endpoint...")
            foods_response = client.get('/api/foods/search?q=rice')
            print(f"   Foods search status: {foods_response.status_code}")
            
            if foods_response.status_code == 401:
                print("   ❌ Even regular API calls are failing - session issue")
                return
            elif foods_response.status_code == 200:
                print("   ✅ Regular API calls work")
            
            # Step 4: Find a food to delete
            print("\n4. Finding test food...")
            test_food = Food.query.outerjoin(MealLog).filter(MealLog.id == None).first()
            
            if not test_food:
                print("   ❌ No food available for testing")
                return
                
            print(f"   Test food: {test_food.name} (ID: {test_food.id})")
            
            # Step 5: Try the delete API
            print(f"\n5. Testing DELETE API...")
            delete_response = client.delete(f'/api/admin/foods/{test_food.id}', 
                                          headers={'Content-Type': 'application/json'})
            
            print(f"   Delete response status: {delete_response.status_code}")
            
            if delete_response.status_code == 401:
                print("   ❌ Authentication failed")
                
                # Check if the user is actually admin
                admin_user = User.query.filter_by(username='admin').first()
                if admin_user:
                    print(f"   Admin user exists: {admin_user.username}, is_admin: {admin_user.is_admin}")
                else:
                    print("   ❌ Admin user doesn't exist!")
                    
            else:
                try:
                    if delete_response.content_type and 'json' in delete_response.content_type:
                        response_data = delete_response.get_json()
                        print(f"   Response: {json.dumps(response_data, indent=2)}")
                    else:
                        print(f"   Response text: {delete_response.get_data(as_text=True)}")
                except Exception as e:
                    print(f"   Response parse error: {e}")
                    
            # Step 6: Check what pages we can access
            print(f"\n6. Testing admin page access...")
            admin_foods_page = client.get('/admin/foods')
            print(f"   Admin foods page status: {admin_foods_page.status_code}")
            
            if admin_foods_page.status_code == 200:
                print("   ✅ Can access admin pages")
            else:
                print("   ❌ Cannot access admin pages")

if __name__ == "__main__":
    test_browser_like_delete()
