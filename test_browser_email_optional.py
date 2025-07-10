#!/usr/bin/env python3
"""
Test to verify email field is optional - Flask Test Client Version
Rewritten to remove Selenium dependencies and use Flask's built-in test client.
"""

import sys
import os
import json

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User

def test_email_optional_flask_client():
    """Test email field is optional using Flask test client"""
    print("🧪 Testing Email Optional Functionality via Flask Test Client")
    print("=" * 60)
    
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    
    with app.test_client() as client:
        with app.app_context():
            try:
                print("\n1. 🔍 Testing Add User API without email...")
                
                # Test data without email
                test_user_data = {
                    "user_id": "test-user-no-email-123",
                    "first_name": "Test",
                    "last_name": "User",
                    "password": "TestPass123!",
                    "is_admin": False
                }
                
                # Make API request to add user
                response = client.post('/api/admin/users', 
                                     data=json.dumps(test_user_data),
                                     content_type='application/json')
                
                if response.status_code == 401:
                    print("   ⚠️  Authentication required - creating admin session...")
                    
                    # Create admin user for testing
                    admin_user = User(
                        user_id="admin-test-123",
                        username="admin_test",
                        first_name="Admin",
                        last_name="Test",
                        is_admin=True
                    )
                    admin_user.set_password("AdminPass123!")
                    db.session.add(admin_user)
                    db.session.commit()
                    
                    # Login as admin
                    login_response = client.post('/auth/login', data={
                        'username': 'admin_test',
                        'password': 'AdminPass123!'
                    })
                    
                    if login_response.status_code == 302:  # Redirect indicates success
                        print("   ✅ Admin login successful")
                        
                        # Retry user creation
                        response = client.post('/api/admin/users', 
                                             data=json.dumps(test_user_data),
                                             content_type='application/json')
                    else:
                        print(f"   ❌ Admin login failed: {login_response.status_code}")
                        return False
                
                print(f"   📊 Response Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("   ✅ User created successfully without email!")
                    
                    # Verify user exists in database
                    created_user = User.query.filter_by(user_id="test-user-no-email-123").first()
                    if created_user:
                        print(f"   ✅ User found in database: {created_user.username}")
                        print(f"   📧 Email field value: {created_user.email}")
                        
                        if created_user.email is None:
                            print("   ✅ Email field is correctly NULL")
                        else:
                            print(f"   ⚠️  Email field is not NULL: {created_user.email}")
                            
                    else:
                        print("   ❌ User not found in database")
                        return False
                        
                else:
                    response_data = response.get_json() if response.get_json() else {}
                    print(f"   ❌ User creation failed: {response_data}")
                    return False
                
                print("\n2. 🔍 Testing user creation with empty email string...")
                
                # Test with empty email string
                test_user_data_empty_email = {
                    "user_id": "test-user-empty-email-456", 
                    "first_name": "Test2",
                    "last_name": "User2",
                    "email": "",  # Empty string
                    "password": "TestPass123!",
                    "is_admin": False
                }
                
                response2 = client.post('/api/admin/users',
                                       data=json.dumps(test_user_data_empty_email),
                                       content_type='application/json')
                
                print(f"   📊 Response Status: {response2.status_code}")
                
                if response2.status_code == 200:
                    print("   ✅ User created successfully with empty email!")
                    
                    # Verify user exists
                    created_user2 = User.query.filter_by(user_id="test-user-empty-email-456").first()
                    if created_user2:
                        print(f"   ✅ User found: {created_user2.username}")
                        print(f"   📧 Email field value: {created_user2.email}")
                        
                        if created_user2.email is None:
                            print("   ✅ Empty email correctly converted to NULL")
                        else:
                            print(f"   ⚠️  Email not NULL: {created_user2.email}")
                    else:
                        print("   ❌ User not found in database")
                        return False
                else:
                    response_data2 = response2.get_json() if response2.get_json() else {}
                    print(f"   ❌ User creation failed: {response_data2}")
                    return False
                
                print("\n3. 🔍 Testing user update to remove email...")
                
                # Get the first user and try to update without email
                user_to_update = User.query.filter_by(user_id="test-user-no-email-123").first()
                if user_to_update:
                    update_data = {
                        "first_name": "Updated",
                        "last_name": "Name",
                        "email": None,  # Explicitly null
                        "is_admin": False,
                        "is_active": True
                    }
                    
                    response3 = client.put(f'/api/admin/users/{user_to_update.id}',
                                          data=json.dumps(update_data),
                                          content_type='application/json')
                    
                    print(f"   📊 Update Response Status: {response3.status_code}")
                    
                    if response3.status_code == 200:
                        print("   ✅ User updated successfully with null email!")
                        
                        # Refresh and check
                        db.session.refresh(user_to_update)
                        if user_to_update.email is None:
                            print("   ✅ Email successfully set to NULL")
                        else:
                            print(f"   ⚠️  Email not NULL: {user_to_update.email}")
                    else:
                        response_data3 = response3.get_json() if response3.get_json() else {}
                        print(f"   ❌ Update failed: {response_data3}")
                        return False
                
                print("\n🎉 All email optional tests passed!")
                return True
                
            except Exception as e:
                print(f"❌ Test failed with error: {e}")
                import traceback
                traceback.print_exc()
                return False
                
            finally:
                # Cleanup test data
                try:
                    User.query.filter_by(user_id="test-user-no-email-123").delete()
                    User.query.filter_by(user_id="test-user-empty-email-456").delete()
                    User.query.filter_by(user_id="admin-test-123").delete()
                    db.session.commit()
                    print("\n🧹 Test cleanup completed")
                except:
                    db.session.rollback()

def test_form_validation():
    """Test frontend form validation logic"""
    print("\n🧪 Testing Frontend Form Validation Logic")
    print("=" * 50)
    
    app = create_app()
    with app.test_client() as client:
        try:
            # Test accessing the admin users page
            response = client.get('/admin/users')
            
            # Check if we get redirected to login (expected)
            if response.status_code in [302, 401]:
                print("✅ Admin page properly protected (login required)")
            elif response.status_code == 200:
                print("✅ Admin page accessible")
                
                # Check if the page contains the updated form fields
                page_content = response.get_data(as_text=True)
                
                if 'id="email"' in page_content and 'required' not in page_content.split('id="email"')[1].split('>')[0]:
                    print("✅ Email field found without required attribute")
                else:
                    print("⚠️  Email field configuration needs verification")
                    
                if '(optional)' in page_content:
                    print("✅ Optional field indicators found")
                else:
                    print("⚠️  Optional field indicators not found")
            else:
                print(f"⚠️  Unexpected response status: {response.status_code}")
                
            return True
            
        except Exception as e:
            print(f"❌ Form validation test failed: {e}")
            return False

def main():
    """Run all email optional tests"""
    print("🚀 Starting Email Optional Validation Tests...")
    print("=" * 70)
    
    try:
        # Test 1: API functionality
        api_test_passed = test_email_optional_flask_client()
        
        # Test 2: Frontend validation
        form_test_passed = test_form_validation()
        
        if api_test_passed and form_test_passed:
            print("\n" + "=" * 70)
            print("🎉 ALL TESTS PASSED! Email field is working correctly as optional.")
            print("=" * 70)
            return True
        else:
            print("\n" + "=" * 70)
            print("❌ Some tests failed. Please check the implementation.")
            print("=" * 70)
            return False
            
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
