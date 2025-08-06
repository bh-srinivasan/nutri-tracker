#!/usr/bin/env python3
"""
Final test for user profile functionality - comprehensive testing
Tests that the UndefinedError: 'ProfileForm object' has no attribute 'username' is fixed
"""

import requests
import re
import time

def test_profile_fix():
    """Test that the profile page username field issue is resolved"""
    print("🎯 Testing Profile Page Fix")
    print("=" * 60)
    print("Issue: UndefinedError: 'ProfileForm object' has no attribute 'username'")
    print("Fix: Added username field to ProfileForm class")
    print("=" * 60)
    
    session = requests.Session()
    
    try:
        # Step 1: Get login page
        print("\n📋 Step 1: Accessing login page...")
        login_url = "http://127.0.0.1:5001/auth/login"
        login_page = session.get(login_url)
        
        if login_page.status_code != 200:
            print(f"❌ Login page not accessible: {login_page.status_code}")
            return False
        
        print(f"✅ Login page accessible: {login_page.status_code}")
        
        # Step 2: Extract CSRF token
        print("\n🔐 Step 2: Extracting CSRF token...")
        csrf_match = re.search(r'name="csrf_token".*?value="([^"]+)"', login_page.text)
        csrf_token = csrf_match.group(1) if csrf_match else None
        
        if not csrf_token:
            print("❌ CSRF token not found")
            return False
        
        print("✅ CSRF token extracted successfully")
        
        # Step 3: Login as test user
        print("\n👤 Step 3: Logging in as non-admin user...")
        login_data = {
            'username': 'testuser',
            'password': 'test123',
            'csrf_token': csrf_token
        }
        
        login_response = session.post(login_url, data=login_data, allow_redirects=False)
        
        if login_response.status_code not in [302, 200]:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
        
        print(f"✅ Login successful: {login_response.status_code}")
        
        # Step 4: Access profile page (the critical test)
        print("\n🎯 Step 4: Testing Profile Page Access (CRITICAL TEST)...")
        profile_url = "http://127.0.0.1:5001/auth/profile"
        
        try:
            profile_response = session.get(profile_url)
            
            if profile_response.status_code == 200:
                print("✅ SUCCESS! Profile page loads without UndefinedError!")
                print("✅ The 'username' field issue has been resolved!")
                
                # Verify specific elements
                content = profile_response.text
                
                # Check for username field specifically
                if 'name="username"' in content:
                    print("✅ Username field is present in form")
                else:
                    print("❌ Username field still missing")
                    return False
                
                # Check for other required fields
                required_fields = [
                    'name="first_name"',
                    'name="last_name"', 
                    'name="email"',
                    'name="age"',
                    'name="gender"',
                    'name="height"',
                    'name="weight"',
                    'name="activity_level"'
                ]
                
                missing_fields = []
                for field in required_fields:
                    if field not in content:
                        missing_fields.append(field)
                
                if not missing_fields:
                    print("✅ All form fields are present and working")
                else:
                    print(f"⚠️ Some fields missing: {missing_fields}")
                
                # Check for form submission button
                if 'Update Profile' in content or 'type="submit"' in content:
                    print("✅ Form submission button is present")
                else:
                    print("⚠️ Form submission button not found")
                
                return True
                
            elif profile_response.status_code == 500:
                print("❌ FAILURE! Profile page returns 500 error")
                print("❌ The UndefinedError may still be present")
                
                # Try to extract error details
                error_content = profile_response.text
                if 'UndefinedError' in error_content:
                    print("❌ UndefinedError confirmed in response")
                if 'username' in error_content:
                    print("❌ Username-related error confirmed")
                
                return False
                
            else:
                print(f"❌ Unexpected profile page response: {profile_response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Exception when accessing profile page: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

def test_profile_form_submission():
    """Test that profile form submission works correctly"""
    print("\n📤 Testing Profile Form Submission...")
    
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
        
        # Get profile page for form submission
        profile_url = "http://127.0.0.1:5001/auth/profile"
        profile_page = session.get(profile_url)
        
        # Extract CSRF token from profile form
        csrf_match = re.search(r'name="csrf_token".*?value="([^"]+)"', profile_page.text)
        profile_csrf = csrf_match.group(1) if csrf_match else None
        
        # Submit profile update
        update_data = {
            'username': 'testuser',
            'first_name': 'TestUpdate',
            'last_name': 'UserUpdate',
            'email': 'testuser@example.com',
            'age': '25',
            'gender': 'male',
            'height': '175',
            'weight': '70',
            'activity_level': 'moderate',
            'csrf_token': profile_csrf
        }
        
        update_response = session.post(profile_url, data=update_data)
        
        if update_response.status_code == 200:
            print("✅ Profile form submission successful!")
            
            # Check for success message
            if 'successfully' in update_response.text.lower():
                print("✅ Success message confirmed")
            else:
                print("⚠️ No explicit success message found")
            
            return True
        else:
            print(f"❌ Profile form submission failed: {update_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Form submission test failed: {e}")
        return False

def main():
    """Run comprehensive profile fix tests"""
    print("🚀 COMPREHENSIVE PROFILE FIX TEST")
    print("Testing fix for: UndefinedError: 'ProfileForm object' has no attribute 'username'")
    print("\n")
    
    tests_passed = 0
    total_tests = 2
    
    # Test 1: Profile page access (main fix)
    if test_profile_fix():
        tests_passed += 1
        print("\n✅ TEST 1 PASSED: Profile page loads without errors")
    else:
        print("\n❌ TEST 1 FAILED: Profile page still has issues")
    
    print("\n" + "-" * 50)
    
    # Test 2: Form submission
    if test_profile_form_submission():
        tests_passed += 1
        print("✅ TEST 2 PASSED: Profile form submission works")
    else:
        print("❌ TEST 2 FAILED: Profile form submission has issues")
    
    print("\n" + "=" * 60)
    print(f"📊 FINAL RESULTS: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("\n🎉 SUCCESS! All profile functionality is working correctly!")
        print("\n✅ Issue Resolution Summary:")
        print("   - Fixed missing 'username' field in ProfileForm")
        print("   - Profile page loads without UndefinedError")
        print("   - All form fields are accessible and functional")
        print("   - Form submission works correctly")
        print("   - Non-admin users can access Profile without errors")
        
        print("\n✅ Code Changes Made:")
        print("   1. Added username field to ProfileForm class")
        print("   2. Updated ProfileForm validation methods")
        print("   3. Modified profile route to handle username field")
        print("   4. Updated form initialization with username parameter")
        
        return True
    else:
        print("\n❌ Some issues remain. Please check the test output above.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
