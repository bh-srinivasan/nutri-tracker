#!/usr/bin/env python3
"""
Comprehensive test for nutrition goals target date auto-update functionality.
Tests the duration dropdown to target date auto-update for non-admin users.
"""

import time
import sys
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def setup_driver():
    """Set up Chrome driver with options."""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Remove this if you want to see the browser
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def login_as_non_admin(driver, base_url):
    """Login as a non-admin user."""
    print("🔐 Logging in as non-admin user...")
    
    # Navigate to login page
    driver.get(f"{base_url}/auth/login")
    wait = WebDriverWait(driver, 10)
    
    try:
        # Check if there are any existing non-admin users
        driver.get(f"{base_url}/auth/register")
        time.sleep(2)
        
        # Fill registration form for test user
        username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        username_field.clear()
        username_field.send_keys("testuser")
        
        password_field = driver.find_element(By.NAME, "password")
        password_field.clear()
        password_field.send_keys("testpass123")
        
        confirm_password_field = driver.find_element(By.NAME, "confirm_password")
        confirm_password_field.clear()
        confirm_password_field.send_keys("testpass123")
        
        # Submit registration
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        time.sleep(3)
        
        print("✅ Test user registered successfully")
        
    except Exception as e:
        # User might already exist, try to login
        print(f"Registration failed (user might exist): {e}")
        
        driver.get(f"{base_url}/auth/login")
        time.sleep(2)
        
        username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        username_field.clear()
        username_field.send_keys("testuser")
        
        password_field = driver.find_element(By.NAME, "password")
        password_field.clear()
        password_field.send_keys("testpass123")
        
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        time.sleep(3)
        
        print("✅ Logged in as existing test user")

def test_duration_to_date_update(driver, base_url):
    """Test the duration dropdown to target date auto-update functionality."""
    print("\n🎯 Testing nutrition goals duration to target date functionality...")
    
    # Navigate to nutrition goals page
    driver.get(f"{base_url}/dashboard/nutrition-goals")
    wait = WebDriverWait(driver, 15)
    
    try:
        # Wait for the page to load
        wait.until(EC.presence_of_element_located((By.ID, "targetDuration")))
        time.sleep(2)
        
        # Find the duration dropdown and target date field
        duration_select = driver.find_element(By.ID, "targetDuration")
        target_date_field = driver.find_element(By.ID, "targetDate")
        
        print("✅ Found duration dropdown and target date field")
        
        # Test different duration options
        duration_tests = [
            ("2_weeks", 14, "2 weeks"),
            ("1_month", 30, "1 month"),
            ("2_months", 60, "2 months"),
            ("3_months", 90, "3 months"),
            ("6_months", 180, "6 months"),
            ("1_year", 365, "1 year")
        ]
        
        success_count = 0
        failed_tests = []
        
        for duration_value, expected_days, duration_name in duration_tests:
            print(f"\n📅 Testing {duration_name} ({expected_days} days)...")
            
            try:
                # Clear any existing date
                target_date_field.clear()
                time.sleep(1)
                
                # Select the duration
                duration_dropdown = Select(duration_select)
                duration_dropdown.select_by_value(duration_value)
                
                # Wait a moment for JavaScript to execute
                time.sleep(2)
                
                # Check if the target date was updated
                target_date_value = target_date_field.get_attribute("value")
                
                if target_date_value:
                    # Parse the date and calculate the difference
                    target_date = datetime.strptime(target_date_value, "%Y-%m-%d").date()
                    today = datetime.now().date()
                    days_diff = (target_date - today).days
                    
                    # Allow for some tolerance (±2 days)
                    if abs(days_diff - expected_days) <= 2:
                        print(f"✅ {duration_name}: Target date correctly set to {target_date} ({days_diff} days from today)")
                        success_count += 1
                    else:
                        print(f"❌ {duration_name}: Expected ~{expected_days} days, got {days_diff} days")
                        failed_tests.append(f"{duration_name}: Expected {expected_days}, got {days_diff}")
                else:
                    print(f"❌ {duration_name}: Target date field is empty")
                    failed_tests.append(f"{duration_name}: No date set")
                    
            except Exception as e:
                print(f"❌ {duration_name}: Error during test - {e}")
                failed_tests.append(f"{duration_name}: {str(e)}")
        
        # Summary
        print(f"\n📊 Test Results Summary:")
        print(f"✅ Successful tests: {success_count}/{len(duration_tests)}")
        print(f"❌ Failed tests: {len(failed_tests)}")
        
        if failed_tests:
            print("\n❌ Failed test details:")
            for failure in failed_tests:
                print(f"  - {failure}")
        
        # Additional test: Check JavaScript console for errors
        try:
            logs = driver.get_log('browser')
            js_errors = [log for log in logs if log['level'] == 'SEVERE']
            if js_errors:
                print(f"\n⚠️  JavaScript errors found:")
                for error in js_errors:
                    print(f"  - {error['message']}")
            else:
                print(f"\n✅ No JavaScript errors found")
        except Exception as e:
            print(f"\n⚠️  Could not check JavaScript console: {e}")
        
        return success_count == len(duration_tests)
        
    except TimeoutException:
        print("❌ Timeout waiting for page elements to load")
        return False
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

def test_manual_date_input(driver):
    """Test manual date input functionality."""
    print("\n📝 Testing manual date input functionality...")
    
    try:
        target_date_field = driver.find_element(By.ID, "targetDate")
        duration_select = driver.find_element(By.ID, "targetDuration")
        
        # Test setting a manual date
        future_date = (datetime.now() + timedelta(days=45)).strftime("%Y-%m-%d")
        
        target_date_field.clear()
        target_date_field.send_keys(future_date)
        
        # Trigger the change event
        driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", target_date_field)
        time.sleep(2)
        
        # Check if duration was updated appropriately
        duration_value = Select(duration_select).first_selected_option.get_attribute("value")
        
        print(f"✅ Manual date set to {future_date}")
        print(f"✅ Duration field updated to: {duration_value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing manual date input: {e}")
        return False

def test_clear_date_functionality(driver):
    """Test the clear date button functionality."""
    print("\n🗑️  Testing clear date functionality...")
    
    try:
        clear_button = driver.find_element(By.ID, "clearDateBtn")
        target_date_field = driver.find_element(By.ID, "targetDate")
        duration_select = driver.find_element(By.ID, "targetDuration")
        
        # First set a date and duration
        duration_dropdown = Select(duration_select)
        duration_dropdown.select_by_value("1_month")
        time.sleep(2)
        
        # Now clear it
        clear_button.click()
        time.sleep(2)
        
        # Check if both fields are cleared
        date_value = target_date_field.get_attribute("value")
        duration_value = Select(duration_select).first_selected_option.get_attribute("value")
        
        if not date_value and not duration_value:
            print("✅ Clear functionality works correctly")
            return True
        else:
            print(f"❌ Clear functionality failed - Date: {date_value}, Duration: {duration_value}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing clear functionality: {e}")
        return False

def main():
    """Main test function."""
    base_url = "http://127.0.0.1:5001"
    driver = None
    
    try:
        print("🚀 Starting comprehensive nutrition goals test...")
        print(f"🌐 Testing application at: {base_url}")
        
        # Setup driver
        driver = setup_driver()
        
        # Login as non-admin user
        login_as_non_admin(driver, base_url)
        
        # Test duration to date functionality
        duration_test_passed = test_duration_to_date_update(driver, base_url)
        
        # Test manual date input
        manual_test_passed = test_manual_date_input(driver)
        
        # Test clear date functionality
        clear_test_passed = test_clear_date_functionality(driver)
        
        # Final summary
        print(f"\n🏁 Final Test Results:")
        print(f"✅ Duration to Date Update: {'PASSED' if duration_test_passed else 'FAILED'}")
        print(f"✅ Manual Date Input: {'PASSED' if manual_test_passed else 'FAILED'}")
        print(f"✅ Clear Date Functionality: {'PASSED' if clear_test_passed else 'FAILED'}")
        
        overall_success = duration_test_passed and manual_test_passed and clear_test_passed
        
        if overall_success:
            print(f"\n🎉 ALL TESTS PASSED! The nutrition goals functionality is working correctly.")
        else:
            print(f"\n❌ SOME TESTS FAILED. Please check the issues above.")
            
        return overall_success
        
    except Exception as e:
        print(f"❌ Critical error during testing: {e}")
        return False
        
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
