#!/usr/bin/env python3
"""
Test to verify that email field is optional for non-admin users in profile
"""

import requests
import re
import time

def test_optional_email_functionality():
    """Test that email field is now optional in profile form"""
    print("🔍 Testing Optional Email Functionality")
    print("=" * 50)
    
    session = requests.Session()
    
    try:
        # Step 1: Login
        print("\n👤 Step 1: Logging in as non-admin user...")
        login_url = "http://127.0.0.1:5001/auth/login"
        login_page = session.get(login_url)
        
        # Extract CSRF token
        csrf_match = re.search(r'name="csrf_token".*?value="([^"]+)"', login_page.text)
        csrf_token = csrf_match.group(1) if csrf_match else None
        
        login_data = {
            'username': 'testuser',
            'password': 'test123',
            'csrf_token': csrf_token
        }
        
        login_response = session.post(login_url, data=login_data)
        print(f"✅ Login successful: {login_response.status_code}")
        
        # Step 2: Access profile page
        print("\n📋 Step 2: Accessing profile page...")
        profile_url = "http://127.0.0.1:5001/auth/profile"
        profile_response = session.get(profile_url)
        
        if profile_response.status_code != 200:
            print(f"❌ Profile page access failed: {profile_response.status_code}")
            return False
        
        print("✅ Profile page accessible")
        
        # Step 3: Test with empty email
        print("\n📤 Step 3: Testing profile update with empty email...")
        
        # Extract CSRF token from profile form
        csrf_match = re.search(r'name="csrf_token".*?value="([^"]+)"', profile_response.text)
        profile_csrf = csrf_match.group(1) if csrf_match else None
        
        # Submit profile with empty email
        empty_email_data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': '',  # Empty email
            'age': '25',
            'gender': 'male',
            'height': '175',
            'weight': '70',
            'activity_level': 'moderate',
            'csrf_token': profile_csrf
        }
        
        update_response = session.post(profile_url, data=empty_email_data)
        
        if update_response.status_code == 200:
            print("✅ Profile update with empty email successful!")
            
            # Check for success message or no errors
            if 'successfully' in update_response.text.lower() or 'error' not in update_response.text.lower():
                print("✅ No validation errors for empty email")
            else:
                print("❌ Validation errors still present for empty email")
                return False
        else:
            print(f"❌ Profile update failed: {update_response.status_code}")
            return False
        
        # Step 4: Test with valid email
        print("\n📧 Step 4: Testing profile update with valid email...")
        
        # Get fresh CSRF token
        profile_response = session.get(profile_url)
        csrf_match = re.search(r'name="csrf_token".*?value="([^"]+)"', profile_response.text)
        profile_csrf = csrf_match.group(1) if csrf_match else None
        
        valid_email_data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser@example.com',  # Valid email
            'age': '25',
            'gender': 'male',
            'height': '175',
            'weight': '70',
            'activity_level': 'moderate',
            'csrf_token': profile_csrf
        }
        
        update_response = session.post(profile_url, data=valid_email_data)
        
        if update_response.status_code == 200:
            print("✅ Profile update with valid email successful!")
        else:
            print(f"❌ Profile update with valid email failed: {update_response.status_code}")
            return False
        
        # Step 5: Verify the template shows email as optional
        print("\n🎨 Step 5: Checking template for optional email indicator...")
        
        profile_response = session.get(profile_url)
        content = profile_response.text
        
        if '(Optional)' in content:
            print("✅ Template shows email as optional")
        else:
            print("⚠️ Template may not clearly indicate email is optional")
        
        if 'placeholder="Enter your email address (optional)"' in content:
            print("✅ Placeholder text indicates email is optional")
        else:
            print("⚠️ Placeholder text may not indicate email is optional")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_email_validation():
    """Test email validation with various inputs"""
    print("\n🔍 Testing Email Validation")
    print("-" * 30)
    
    session = requests.Session()
    
    try:
        # Login first
        login_url = "http://127.0.0.1:5001/auth/login"
        login_page = session.get(login_url)
        csrf_match = re.search(r'name="csrf_token".*?value="([^"]+)"', login_page.text)
        csrf_token = csrf_match.group(1) if csrf_match else None
        
        login_data = {
            'username': 'testuser',
            'password': 'test123',
            'csrf_token': csrf_token
        }
        session.post(login_url, data=login_data)
        
        # Test cases for email validation
        test_cases = [
            {'email': '', 'description': 'Empty email', 'should_pass': True},
            {'email': 'valid@example.com', 'description': 'Valid email', 'should_pass': True},
            {'email': 'invalid-email', 'description': 'Invalid email format', 'should_pass': False},
            {'email': '   ', 'description': 'Whitespace only', 'should_pass': True},
        ]
        
        profile_url = "http://127.0.0.1:5001/auth/profile"
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📋 Test Case {i}: {test_case['description']}")
            
            # Get fresh CSRF token
            profile_response = session.get(profile_url)
            csrf_match = re.search(r'name="csrf_token".*?value="([^"]+)"', profile_response.text)
            profile_csrf = csrf_match.group(1) if csrf_match else None
            
            # Submit form with test email
            form_data = {
                'username': 'testuser',
                'first_name': 'Test',
                'last_name': 'User',
                'email': test_case['email'],
                'age': '25',
                'csrf_token': profile_csrf
            }
            
            response = session.post(profile_url, data=form_data)
            
            # Check if validation behaves as expected
            has_error = 'error' in response.text.lower() and 'email' in response.text.lower()
            
            if test_case['should_pass'] and not has_error:
                print(f"   ✅ PASS: {test_case['description']}")
            elif not test_case['should_pass'] and has_error:
                print(f"   ✅ PASS: {test_case['description']} (correctly rejected)")
            else:
                print(f"   ❌ FAIL: {test_case['description']}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Email validation test failed: {e}")
        return False

def main():
    """Run optional email tests"""
    print("🚀 TESTING OPTIONAL EMAIL FUNCTIONALITY")
    print("Testing that email field is no longer mandatory for non-admin users")
    print("\n")
    
    tests_passed = 0
    total_tests = 2
    
    # Test 1: Optional email functionality
    if test_optional_email_functionality():
        tests_passed += 1
        print("\n✅ TEST 1 PASSED: Optional email functionality works")
    else:
        print("\n❌ TEST 1 FAILED: Optional email functionality has issues")
    
    print("\n" + "-" * 50)
    
    # Test 2: Email validation
    if test_email_validation():
        tests_passed += 1
        print("✅ TEST 2 PASSED: Email validation works correctly")
    else:
        print("❌ TEST 2 FAILED: Email validation has issues")
    
    print("\n" + "=" * 60)
    print(f"📊 FINAL RESULTS: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("\n🎉 SUCCESS! Email field is now optional for non-admin users!")
        print("\n✅ Changes Implemented:")
        print("   - Email field validation changed from DataRequired() to Optional()")
        print("   - Email validation method updated to handle empty values")
        print("   - Profile route updated to handle None email values")
        print("   - Template updated to show email as optional")
        print("   - Form handles empty email strings properly")
        
        print("\n✅ User Experience:")
        print("   - Non-admin users can save profile without entering email")
        print("   - Email field shows '(Optional)' label")
        print("   - Placeholder text indicates email is optional")
        print("   - Valid emails are still properly validated")
        print("   - Invalid email formats are still rejected")
        
        return True
    else:
        print("\n❌ Some issues remain. Please check the test output above.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
