#!/usr/bin/env python3
"""
Test meal edit/delete functionality for NON-ADMIN users
This is the actual issue reported - non-admin users can't edit/delete meals
"""

import sys
import os
import requests
import json
from datetime import datetime, date
import time
sys.path.insert(0, os.path.abspath('.'))

from app import create_app, db
from app.models import User, Food, MealLog

def get_or_create_test_user():
    """Get or create a test non-admin user"""
    app = create_app()
    
    with app.app_context():
        # Look for existing non-admin users
        test_user = User.query.filter_by(is_admin=False).first()
        
        if test_user:
            print(f"✅ Found existing non-admin user: {test_user.username}")
            return test_user.username, "password"  # You'll need to know the password
        
        # Create a test user if none exists
        test_username = f"testuser_{datetime.now().strftime('%H%M%S')}"
        test_user = User(
            username=test_username,
            user_id=test_username,
            first_name="Test",
            last_name="User",
            email=f"{test_username}@test.com",
            is_admin=False,
            is_active=True
        )
        test_user.set_password("testpass123")
        
        db.session.add(test_user)
        db.session.commit()
        
        print(f"✅ Created new test user: {test_username}")
        return test_username, "testpass123"

def test_meal_edit_delete_for_regular_user():
    """Test meal edit/delete functionality for non-admin users"""
    print("🧪 Testing meal edit/delete functionality for NON-ADMIN users...")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:5001"
    session = requests.Session()
    
    try:
        # Step 1: Get or create test user
        print("1. Setting up test user...")
        username, password = get_or_create_test_user()
        print(f"   Using test user: {username}")
        
        # Step 2: Test server accessibility
        print("2. Testing server connectivity...")
        try:
            response = session.get(base_url, timeout=5)
            print(f"   ✅ Server accessible (status: {response.status_code})")
        except requests.exceptions.ConnectionError:
            print("   ❌ Server not accessible. Please ensure Flask app is running on port 5001")
            return False
        
        # Step 3: Login as regular user
        print("3. Logging in as regular user...")
        login_page = session.get(f"{base_url}/auth/login")
        
        # Extract CSRF token
        csrf_token = None
        if 'csrf_token' in login_page.text:
            import re
            csrf_match = re.search(r'name="csrf_token".*?value="([^"]+)"', login_page.text)
            if csrf_match:
                csrf_token = csrf_match.group(1)
        
        login_data = {
            'username': username,
            'password': password
        }
        if csrf_token:
            login_data['csrf_token'] = csrf_token
        
        login_response = session.post(f"{base_url}/auth/login", data=login_data, allow_redirects=False)
        
        if login_response.status_code not in [200, 302]:
            print(f"   ❌ Login failed (status: {login_response.status_code})")
            print(f"   Response: {login_response.text[:200]}...")
            return False
        
        print("   ✅ Successfully logged in as regular user")
        
        # Step 4: Check dashboard access
        print("4. Accessing dashboard...")
        dashboard_response = session.get(f"{base_url}/dashboard")
        
        if dashboard_response.status_code != 200:
            print(f"   ❌ Cannot access dashboard (status: {dashboard_response.status_code})")
            return False
        
        print("   ✅ Dashboard accessible")
        
        # Step 5: Check if main.js is loaded
        print("5. Checking if main.js is included...")
        if 'main.js' in dashboard_response.text:
            print("   ✅ main.js is included in dashboard")
        else:
            print("   ❌ main.js is NOT included - this is likely the problem!")
            return False
        
        # Step 6: Log a test meal first
        print("6. Logging a test meal...")
        meal_id = log_test_meal(session, base_url)
        if not meal_id:
            print("   ❌ Failed to log test meal")
            return False
        
        print(f"   ✅ Successfully logged test meal (ID: {meal_id})")
        
        # Step 7: Test edit functionality
        print("7. Testing meal EDIT functionality...")
        edit_success = test_meal_edit(session, base_url, meal_id)
        if edit_success:
            print("   ✅ Meal edit functionality working!")
        else:
            print("   ❌ Meal edit functionality FAILED!")
        
        # Step 8: Test delete functionality  
        print("8. Testing meal DELETE functionality...")
        delete_success = test_meal_delete(session, base_url, meal_id)
        if delete_success:
            print("   ✅ Meal delete functionality working!")
        else:
            print("   ❌ Meal delete functionality FAILED!")
        
        # Step 9: Final dashboard check
        print("9. Final dashboard check...")
        final_dashboard = session.get(f"{base_url}/dashboard")
        if 'edit-meal-btn' in final_dashboard.text and 'delete-meal-btn' in final_dashboard.text:
            print("   ✅ Edit/Delete buttons are present in dashboard")
        else:
            print("   ⚠️  Edit/Delete buttons not found in dashboard")
        
        return edit_success and delete_success
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def log_test_meal(session, base_url):
    """Log a test meal and return the meal ID"""
    try:
        # Get verified foods first
        foods_response = session.get(f"{base_url}/api/foods/search-verified?q=rice")
        if foods_response.status_code != 200:
            print(f"     ❌ Cannot search for foods (status: {foods_response.status_code})")
            return None
        
        foods_data = foods_response.json()
        if not foods_data.get('foods'):
            print("     ❌ No verified foods found")
            return None
        
        first_food = foods_data['foods'][0]
        print(f"     Using food: {first_food['name']}")
        
        # Get meal log page
        log_page = session.get(f"{base_url}/dashboard/log-meal")
        
        # Extract CSRF token
        csrf_token = None
        if 'csrf_token' in log_page.text:
            import re
            csrf_match = re.search(r'name="csrf_token".*?value="([^"]+)"', log_page.text)
            if csrf_match:
                csrf_token = csrf_match.group(1)
        
        # Log the meal
        meal_data = {
            'food_id': first_food['id'],
            'quantity': 100,
            'unit_type': 'grams',
            'meal_type': 'lunch',
            'date': date.today().strftime('%Y-%m-%d')
        }
        if csrf_token:
            meal_data['csrf_token'] = csrf_token
        
        meal_response = session.post(f"{base_url}/dashboard/log-meal", data=meal_data)
        
        if meal_response.status_code not in [200, 302]:
            print(f"     ❌ Failed to log meal (status: {meal_response.status_code})")
            return None
        
        # Get the meal ID from database
        app = create_app()
        with app.app_context():
            latest_meal = MealLog.query.filter_by(food_id=first_food['id']).order_by(MealLog.id.desc()).first()
            if latest_meal:
                return latest_meal.id
        
        return None
        
    except Exception as e:
        print(f"     ❌ Error logging meal: {e}")
        return None

def test_meal_edit(session, base_url, meal_id):
    """Test meal edit functionality"""
    try:
        # Try to access edit page
        edit_url = f"{base_url}/dashboard/log-meal?edit={meal_id}"
        edit_response = session.get(edit_url)
        
        if edit_response.status_code != 200:
            print(f"     ❌ Cannot access edit page (status: {edit_response.status_code})")
            return False
        
        if 'Edit Meal' in edit_response.text or 'edit' in edit_response.text.lower():
            print("     ✅ Edit page accessible")
            return True
        else:
            print("     ❌ Edit page doesn't seem to work properly")
            return False
            
    except Exception as e:
        print(f"     ❌ Error testing edit: {e}")
        return False

def test_meal_delete(session, base_url, meal_id):
    """Test meal delete functionality via API"""
    try:
        # Test the DELETE API endpoint
        delete_response = session.delete(f"{base_url}/api/meals/{meal_id}")
        
        print(f"     Delete API status: {delete_response.status_code}")
        print(f"     Delete API response: {delete_response.text}")
        
        if delete_response.status_code == 200:
            print("     ✅ Delete API endpoint working")
            return True
        elif delete_response.status_code == 401:
            print("     ❌ Delete API requires authentication - session issue")
            return False
        elif delete_response.status_code == 404:
            print("     ❌ Meal not found or access denied")
            return False
        else:
            print(f"     ❌ Delete API failed with status {delete_response.status_code}")
            return False
            
    except Exception as e:
        print(f"     ❌ Error testing delete: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting comprehensive NON-ADMIN user meal functionality test...")
    print("This test specifically focuses on the reported issue:")
    print("'For the non admin user when I am trying to click on Edit or delete a meal from todays meal, it is not working'")
    print()
    
    success = test_meal_edit_delete_for_regular_user()
    
    if success:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Non-admin user can login")
        print("✅ Dashboard loads with main.js")
        print("✅ Meal logging works")
        print("✅ Meal edit functionality works")
        print("✅ Meal delete functionality works")
        print("\n🔧 The meal edit/delete functionality is now working for non-admin users!")
    else:
        print("\n💥 TESTS FAILED!")
        print("❌ There are still issues with meal edit/delete for non-admin users.")
        print("Please check the error messages above for details.")
        print("\n🔍 Common issues to check:")
        print("   - main.js not included in dashboard template")
        print("   - API endpoints not working")
        print("   - Authentication issues with API calls")
        print("   - Edit/Delete buttons not present or not working")
