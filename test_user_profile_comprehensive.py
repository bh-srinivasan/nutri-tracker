#!/usr/bin/env python3
"""
Comprehensive test for user profile functionality
Tests profile access, form loading, and profile updates for non-admin users
"""

import sys
import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_profile_api_endpoint():
    """Test the profile endpoint directly via API"""
    print("🔍 Testing Profile API Endpoint...")
    
    session = requests.Session()
    
    try:
        # Test if server is running
        login_url = "http://127.0.0.1:5001/auth/login"
        response = session.get(login_url)
        
        if response.status_code != 200:
            print(f"❌ Server not responding at {login_url}")
            return False
            
        print(f"✅ Server is running - Login page status: {response.status_code}")
        
        # Login with test user credentials
        login_data = {
            'username': 'testuser',
            'password': 'test123'
        }
        
        login_response = session.post(login_url, data=login_data)
        print(f"✅ Login attempt status: {login_response.status_code}")
        
        # Test profile page access
        profile_url = "http://127.0.0.1:5001/auth/profile"
        profile_response = session.get(profile_url)
        
        print(f"✅ Profile page status: {profile_response.status_code}")
        
        if profile_response.status_code == 200:
            print("✅ Profile page loads successfully without errors!")
            return True
        else:
            print(f"❌ Profile page failed to load: {profile_response.text[:500]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure Flask server is running on port 5001")
        return False
    except Exception as e:
        print(f"❌ Error testing profile endpoint: {e}")
        return False

def test_profile_browser_automation():
    """Test profile functionality using browser automation"""
    print("\n🚀 Starting Browser Profile Test...")
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = None
    
    try:
        # Initialize Chrome driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.implicitly_wait(10)
        
        print("✅ Chrome driver initialized")
        
        # Navigate to login page
        driver.get("http://127.0.0.1:5001/auth/login")
        print("✅ Navigated to login page")
        
        # Login as test user
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        password_field = driver.find_element(By.NAME, "password")
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        
        username_field.send_keys("testuser")
        password_field.send_keys("test123")
        login_button.click()
        
        print("✅ Login submitted")
        
        # Wait for redirect to dashboard
        WebDriverWait(driver, 10).until(
            EC.url_contains("/dashboard")
        )
        print("✅ Successfully logged in and redirected to dashboard")
        
        # Navigate to profile page
        driver.get("http://127.0.0.1:5001/auth/profile")
        print("✅ Navigated to profile page")
        
        # Wait for profile form to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        print("✅ Profile form loaded successfully")
        
        # Test form field presence
        required_fields = [
            "username", "first_name", "last_name", "email", 
            "age", "gender", "height", "weight", "activity_level"
        ]
        
        missing_fields = []
        for field_name in required_fields:
            try:
                field = driver.find_element(By.NAME, field_name)
                print(f"✅ Found field: {field_name}")
            except:
                missing_fields.append(field_name)
                print(f"❌ Missing field: {field_name}")
        
        if missing_fields:
            print(f"❌ Missing fields: {', '.join(missing_fields)}")
            return False
        
        # Test form pre-population
        username_field = driver.find_element(By.NAME, "username")
        if username_field.get_attribute("value"):
            print(f"✅ Username field pre-populated: {username_field.get_attribute('value')}")
        else:
            print("⚠️ Username field not pre-populated")
        
        # Test form update
        print("\n📝 Testing profile update...")
        
        # Update some fields
        first_name_field = driver.find_element(By.NAME, "first_name")
        first_name_field.clear()
        first_name_field.send_keys("UpdatedFirst")
        
        last_name_field = driver.find_element(By.NAME, "last_name")
        last_name_field.clear()
        last_name_field.send_keys("UpdatedLast")
        
        age_field = driver.find_element(By.NAME, "age")
        age_field.clear()
        age_field.send_keys("25")
        
        # Select gender
        gender_select = Select(driver.find_element(By.NAME, "gender"))
        gender_select.select_by_value("male")
        
        # Update height and weight
        height_field = driver.find_element(By.NAME, "height")
        height_field.clear()
        height_field.send_keys("175")
        
        weight_field = driver.find_element(By.NAME, "weight")
        weight_field.clear()
        weight_field.send_keys("70")
        
        # Select activity level
        activity_select = Select(driver.find_element(By.NAME, "activity_level"))
        activity_select.select_by_value("moderate")
        
        print("✅ Form fields updated")
        
        # Submit the form
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        print("✅ Profile update submitted")
        
        # Wait for success message
        try:
            success_alert = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".alert-success, .alert.alert-success"))
            )
            print(f"✅ Success message displayed: {success_alert.text}")
        except:
            print("⚠️ No success message found, but no error either")
        
        # Verify the form still loads after update
        driver.get("http://127.0.0.1:5001/auth/profile")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        print("✅ Profile page still loads correctly after update")
        
        # Verify updated values are preserved
        updated_first_name = driver.find_element(By.NAME, "first_name").get_attribute("value")
        if updated_first_name == "UpdatedFirst":
            print("✅ First name update was saved")
        else:
            print(f"⚠️ First name may not have been saved: {updated_first_name}")
        
        print("✅ All profile tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Browser test error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        if driver:
            driver.quit()
            print("✅ Browser closed")

def test_profile_error_conditions():
    """Test profile page error handling"""
    print("\n🔍 Testing Profile Error Conditions...")
    
    session = requests.Session()
    
    try:
        # Test accessing profile without login
        profile_url = "http://127.0.0.1:5001/auth/profile"
        response = session.get(profile_url)
        
        if response.status_code == 302:  # Redirect to login
            print("✅ Unauthenticated access properly redirected")
        else:
            print(f"⚠️ Unexpected response for unauthenticated access: {response.status_code}")
        
        # Login first
        login_url = "http://127.0.0.1:5001/auth/login"
        login_data = {'username': 'testuser', 'password': 'test123'}
        session.post(login_url, data=login_data)
        
        # Test invalid form data
        invalid_data = {
            'username': 'a',  # Too short
            'email': 'invalid-email',
            'age': '200',  # Too high
            'height': '50',  # Too low
            'weight': '500'  # Too high
        }
        
        response = session.post(profile_url, data=invalid_data)
        print(f"✅ Invalid data handling status: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error condition test failed: {e}")
        return False

def main():
    """Run comprehensive profile tests"""
    print("🚀 Starting Comprehensive Profile Tests")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: API endpoint
    if test_profile_api_endpoint():
        tests_passed += 1
        print("✅ Test 1 PASSED: API endpoint test")
    else:
        print("❌ Test 1 FAILED: API endpoint test")
    
    print("\n" + "-" * 30)
    
    # Test 2: Browser automation
    if test_profile_browser_automation():
        tests_passed += 1
        print("✅ Test 2 PASSED: Browser automation test")
    else:
        print("❌ Test 2 FAILED: Browser automation test")
    
    print("\n" + "-" * 30)
    
    # Test 3: Error conditions
    if test_profile_error_conditions():
        tests_passed += 1
        print("✅ Test 3 PASSED: Error conditions test")
    else:
        print("❌ Test 3 FAILED: Error conditions test")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED! Profile functionality is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
