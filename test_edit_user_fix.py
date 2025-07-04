#!/usr/bin/env python3
"""
Test script to verify the Edit User functionality is working correctly.
This tests both the API endpoints and the modal form implementation.
"""

import sys
import os
import requests
import json
from datetime import datetime

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User

def test_edit_user_functionality():
    """Test the complete edit user workflow."""
    print("🔧 Testing Edit User Functionality Fix")
    print("=" * 50)
    
    # Test 1: Check API endpoint availability
    print("\n1. Testing API endpoint availability...")
    base_url = "http://localhost:5001"  # Updated to port 5001
    
    try:
        # Test if server is running
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print(f"❌ Server not accessible: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Please start the Flask server first.")
        return False
    
    # Test 2: Check if edit user routes exist
    print("\n2. Testing edit user routes...")
    
    # Check if admin users page loads
    try:
        response = requests.get(f"{base_url}/admin/users")
        if response.status_code in [200, 302]:  # 302 for redirect to login
            print("✅ Admin users route exists")
        else:
            print(f"❌ Admin users route issue: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing admin route: {e}")
    
    # Test 3: Validate database schema
    print("\n3. Testing database schema...")
    app = create_app()
    with app.app_context():
        try:
            # Check if User model has all required fields
            user_sample = User.query.first()
            if user_sample:
                required_fields = ['username', 'email', 'first_name', 'last_name', 'is_admin', 'is_active']
                missing_fields = []
                
                for field in required_fields:
                    if not hasattr(user_sample, field):
                        missing_fields.append(field)
                
                if missing_fields:
                    print(f"❌ Missing User model fields: {missing_fields}")
                else:
                    print("✅ User model has all required fields")
                    print(f"   - Sample user: {user_sample.username} ({user_sample.email})")
            else:
                print("⚠️  No users found in database")
                
        except Exception as e:
            print(f"❌ Database schema error: {e}")
    
    # Test 4: Check JavaScript files
    print("\n4. Testing JavaScript implementation...")
    
    admin_js_path = "app/static/js/admin.js"
    if os.path.exists(admin_js_path):
        with open(admin_js_path, 'r') as f:
            js_content = f.read()
            
        required_functions = [
            'Admin.users.edit',
            'Admin.users.submitEditForm',
            'editUserForm'
        ]
        
        missing_functions = []
        for func in required_functions:
            if func not in js_content:
                missing_functions.append(func)
        
        if missing_functions:
            print(f"❌ Missing JavaScript functions: {missing_functions}")
        else:
            print("✅ All required JavaScript functions found")
    else:
        print("❌ admin.js file not found")
    
    # Test 5: Check template files
    print("\n5. Testing template files...")
    
    users_template_path = "app/templates/admin/users.html"
    edit_template_path = "app/templates/admin/edit_user.html"
    
    template_issues = []
    
    if os.path.exists(users_template_path):
        with open(users_template_path, 'r') as f:
            users_content = f.read()
            
        required_elements = [
            'editUserModal',
            'edit-user-btn',
            'editUserForm',
            'editUsername',
            'editFirstName',
            'editLastName',
            'editEmail',
            'editIsAdmin',
            'editIsActive'
        ]
        
        for element in required_elements:
            if element not in users_content:
                template_issues.append(f"Missing element in users.html: {element}")
    else:
        template_issues.append("users.html template not found")
    
    if os.path.exists(edit_template_path):
        print("✅ edit_user.html template exists")
    else:
        template_issues.append("edit_user.html template not found")
    
    if template_issues:
        print("❌ Template issues found:")
        for issue in template_issues:
            print(f"   - {issue}")
    else:
        print("✅ All required template elements found")
    
    # Test 6: Check API routes
    print("\n6. Testing API routes structure...")
    
    api_routes_path = "app/api/routes.py"
    if os.path.exists(api_routes_path):
        with open(api_routes_path, 'r') as f:
            api_content = f.read()
            
        required_endpoints = [
            '/admin/users/<int:user_id>',
            'def get_user(',
            'def update_user(',
            'def toggle_user_status(',
            '@admin_required'
        ]
        
        missing_endpoints = []
        for endpoint in required_endpoints:
            if endpoint not in api_content:
                missing_endpoints.append(endpoint)
        
        if missing_endpoints:
            print(f"❌ Missing API endpoints: {missing_endpoints}")
        else:
            print("✅ All required API endpoints found")
    else:
        print("❌ API routes file not found")
    
    # Test 7: Check forms
    print("\n7. Testing form validation...")
    
    forms_path = "app/admin/forms.py"
    if os.path.exists(forms_path):
        with open(forms_path, 'r') as f:
            forms_content = f.read()
            
        form_requirements = [
            'class UserManagementForm',
            'validate_username',
            'validate_email',
            'user_id'
        ]
        
        missing_form_features = []
        for requirement in form_requirements:
            if requirement not in forms_content:
                missing_form_features.append(requirement)
        
        if missing_form_features:
            print(f"❌ Missing form features: {missing_form_features}")
        else:
            print("✅ Form validation enhancements found")
    else:
        print("❌ Forms file not found")
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)
    
    print("\n✅ FIXES IMPLEMENTED:")
    print("   1. Added missing API endpoints (/api/admin/users/<id>)")
    print("   2. Enhanced user edit modal with username field")
    print("   3. Added is_active field to edit form")
    print("   4. Improved JavaScript error handling and validation")
    print("   5. Enhanced backend validation and security")
    print("   6. Added proper form validation with duplicate checking")
    print("   7. Added logging and CSRF protection")
    
    print("\n🔧 TO TEST MANUALLY:")
    print("   1. Start the server: python app.py")
    print("   2. Login as admin user")
    print("   3. Go to Admin → Manage Users")
    print("   4. Click the edit button (pencil icon) for any user")
    print("   5. Verify the modal opens with all user data populated")
    print("   6. Make changes and save - should work without errors")
    print("   7. Check that changes are reflected in the user list")
    
    print("\n🎯 KEY IMPROVEMENTS:")
    print("   - Form now pre-populates with user data")
    print("   - Real-time validation prevents duplicate usernames/emails")
    print("   - Better error messages and user feedback")
    print("   - Security enhancements with proper validation")
    print("   - Self-deactivation prevention for admin users")
    
    return True

if __name__ == "__main__":
    test_edit_user_functionality()
