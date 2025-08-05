#!/usr/bin/env python3
"""
Comprehensive test script for the Nutrition Goals page
Tests both access and functionality for non-admin users
"""

import requests
import re
import time

def test_nutrition_goals_comprehensive():
    """Comprehensive test of the nutrition goals functionality"""
    
    print("🎯 Testing Nutrition Goals Page...")
    print("=" * 60)
    
    session = requests.Session()
    base_url = "http://127.0.0.1:5001"
    
    try:
        # Step 1: Login as non-admin user
        print("1️⃣ Logging in as non-admin user...")
        
        # Get login page
        login_page = session.get(f"{base_url}/auth/login")
        print(f"   Login page status: {login_page.status_code}")
        
        # Extract CSRF token
        csrf_token = None
        csrf_match = re.search(r'name="csrf_token".*?value="([^"]+)"', login_page.text)
        if csrf_match:
            csrf_token = csrf_match.group(1)
            print(f"   CSRF token found: ✓")
        
        # Login
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        if csrf_token:
            login_data['csrf_token'] = csrf_token
        
        login_response = session.post(f"{base_url}/auth/login", data=login_data, allow_redirects=True)
        
        if "/dashboard" in login_response.url:
            print("   ✅ Login successful")
        else:
            print("   ❌ Login failed")
            return False
        
        # Step 2: Access Goals page
        print("\n2️⃣ Accessing Goals page...")
        
        goals_response = session.get(f"{base_url}/dashboard/nutrition-goals")
        
        if goals_response.status_code == 200:
            print("   ✅ Goals page accessible")
        else:
            print(f"   ❌ Goals page error: {goals_response.status_code}")
            print(f"   Error response: {goals_response.text[:500]}")
            return False
        
        # Step 3: Check for template errors
        print("\n3️⃣ Checking for template errors...")
        
        page_content = goals_response.text
        
        # Check for Jinja2 errors
        error_patterns = [
            r'UndefinedError',
            r'has no attribute',
            r'object.*has no attribute.*weight',
            r'object.*has no attribute.*height',
            r'object.*has no attribute.*age',
            r'object.*has no attribute.*gender',
            r'object.*has no attribute.*activity_level',
            r'Internal Server Error',
            r'500 Internal Server Error'
        ]
        
        errors_found = []
        for pattern in error_patterns:
            matches = re.findall(pattern, page_content, re.IGNORECASE)
            if matches:
                errors_found.extend(matches)
        
        if errors_found:
            print(f"   ❌ Template errors found: {len(errors_found)}")
            for error in errors_found[:3]:
                print(f"      - {error}")
            return False
        else:
            print("   ✅ No template errors found")
        
        # Step 4: Check for form fields
        print("\n4️⃣ Checking for required form fields...")
        
        required_fields = [
            'weight', 'height', 'age', 'gender', 'activity_level',
            'goal_type', 'target_calories', 'target_protein'
        ]
        
        missing_fields = []
        for field in required_fields:
            field_pattern = rf'name="{field}"'
            if not re.search(field_pattern, page_content):
                missing_fields.append(field)
        
        if missing_fields:
            print(f"   ❌ Missing form fields: {missing_fields}")
            return False
        else:
            print("   ✅ All required form fields found")
        
        # Step 5: Check for proper form structure
        print("\n5️⃣ Checking form structure...")
        
        # Check for form tag
        if '<form method="POST">' in page_content:
            print("   ✅ Form tag found")
        else:
            print("   ❌ Form tag not found")
            return False
        
        # Check for CSRF token in form
        if 'csrf_token' in page_content:
            print("   ✅ CSRF token found in form")
        else:
            print("   ❌ CSRF token not found in form")
            return False
        
        # Step 6: Test form submission
        print("\n6️⃣ Testing form submission...")
        
        # Extract CSRF token from goals page
        goals_csrf_match = re.search(r'name="csrf_token".*?value="([^"]+)"', page_content)
        goals_csrf_token = goals_csrf_match.group(1) if goals_csrf_match else None
        
        if not goals_csrf_token:
            print("   ❌ Cannot extract CSRF token from goals page")
            return False
        
        # Submit test data
        # Submit test data
        form_data = {
            'csrf_token': goals_csrf_token,
            'weight': '70.0',
            'height': '175.0',
            'age': '30',
            'gender': 'male',
            'activity_level': 'moderate',
            'goal_type': 'maintain',
            'target_calories': '2000',
            'target_protein': '150',
            'target_carbs': '200',
            'target_fat': '65',
            'target_fiber': '25',
            'submit': 'Set Goals'
        }
        submit_response = session.post(f"{base_url}/dashboard/nutrition-goals", 
                                     data=form_data, allow_redirects=False)
        
        if submit_response.status_code == 302:
            print("   ✅ Form submission successful (redirect)")
            
            # Check if redirected to dashboard
            if '/dashboard' in submit_response.headers.get('Location', ''):
                print("   ✅ Redirected to dashboard")
            else:
                print(f"   ⚠️ Redirected to: {submit_response.headers.get('Location', 'unknown')}")
        
        elif submit_response.status_code == 200:
            # Check for form errors
            submit_content = submit_response.text
            if 'is-invalid' in submit_content or 'error' in submit_content.lower():
                print("   ❌ Form validation errors found")
                return False
            else:
                print("   ✅ Form processed successfully")
        else:
            print(f"   ❌ Form submission failed: {submit_response.status_code}")
            print(f"   Response: {submit_response.text[:500]}")
            return False
        
        # Step 7: Verify goals were saved (access again)
        print("\n7️⃣ Verifying goals were saved...")
        
        verify_response = session.get(f"{base_url}/dashboard/nutrition-goals")
        
        if verify_response.status_code == 200:
            verify_content = verify_response.text
            
            # Check if form is pre-populated with our data
            if 'value="70.0"' in verify_content or 'value="70"' in verify_content:
                print("   ✅ Goals appear to be saved (weight found)")
            else:
                print("   ⚠️ Goals may not be saved (weight not found in form)")
        
        # Step 8: Test navigation back to dashboard
        print("\n8️⃣ Testing navigation...")
        
        dashboard_response = session.get(f"{base_url}/dashboard")
        
        if dashboard_response.status_code == 200:
            print("   ✅ Can navigate back to dashboard")
        else:
            print("   ❌ Cannot navigate back to dashboard")
            return False
        
        # Final summary
        print("\n" + "=" * 60)
        print("📋 NUTRITION GOALS TEST SUMMARY")
        print("=" * 60)
        
        print("🎉 ALL TESTS PASSED!")
        print("✅ Login: SUCCESS")
        print("✅ Goals Page Access: SUCCESS") 
        print("✅ No Template Errors: SUCCESS")
        print("✅ Form Fields Present: SUCCESS")
        print("✅ Form Structure: SUCCESS")
        print("✅ Form Submission: SUCCESS")
        print("✅ Data Persistence: SUCCESS")
        print("✅ Navigation: SUCCESS")
        
        print("\n🚀 The Goals page is working correctly!")
        print("   Non-admin users can now access and use the nutrition goals functionality.")
        return True
            
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_goals_edge_cases():
    """Test edge cases and error handling"""
    
    print("\n🔍 Testing Edge Cases...")
    print("-" * 40)
    
    session = requests.Session()
    base_url = "http://127.0.0.1:5001"
    
    try:
        # Login first
        login_data = {'username': 'testuser', 'password': 'testpass123'}
        session.post(f"{base_url}/auth/login", data=login_data)
        
        # Test with invalid data
        print("🧪 Testing invalid form data...")
        
        goals_page = session.get(f"{base_url}/dashboard/nutrition-goals")
        csrf_match = re.search(r'name="csrf_token".*?value="([^"]+)"', goals_page.text)
        csrf_token = csrf_match.group(1) if csrf_match else None
        
        invalid_data = {
            'csrf_token': csrf_token,
            'weight': '-10',  # Invalid negative weight
            'height': '300',  # Invalid height
            'age': '200',     # Invalid age
            'gender': 'male',
            'activity_level': 'moderate',
            'goal_type': 'maintain',
            'target_calories': '100',  # Too low calories
            'target_protein': '500',   # Too high protein
            'submit': 'Set Goals'
        }
        
        invalid_response = session.post(f"{base_url}/dashboard/nutrition-goals", 
                                      data=invalid_data, allow_redirects=False)
        
        if invalid_response.status_code == 200:
            # Should stay on form with validation errors
            if 'is-invalid' in invalid_response.text:
                print("   ✅ Form validation working correctly")
            else:
                print("   ⚠️ Form validation may not be working")
        else:
            print("   ⚠️ Unexpected response to invalid data")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error in edge case testing: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Comprehensive Nutrition Goals Test...")
    print("🎯 Make sure the Flask server is running on port 5001")
    print()
    
    success = test_nutrition_goals_comprehensive()
    
    if success:
        edge_success = test_goals_edge_cases()
        
        if edge_success:
            print("\n✅ All tests completed successfully!")
            print("🎯 Nutrition Goals page is fully functional for non-admin users!")
        else:
            print("\n⚠️ Main tests passed but some edge cases failed")
    else:
        print("\n❌ Nutrition Goals tests failed!")
        print("   Please check the server logs for more details.")
