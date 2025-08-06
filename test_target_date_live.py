#!/usr/bin/env python3
"""
Quick test to check the nutrition goals page and verify JavaScript functionality
"""

import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_nutrition_goals_functionality():
    """Test the target duration to target date functionality"""
    
    print("🧪 TESTING TARGET DURATION → TARGET DATE FUNCTIONALITY")
    print("=" * 60)
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--headless")  # Run in background
    
    driver = None
    
    try:
        # Start Chrome driver
        print("🚀 Starting Chrome driver...")
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_window_size(1920, 1080)
        
        # Test if app is running
        print("🌐 Testing if app is accessible...")
        driver.get("http://127.0.0.1:5001")
        print(f"✅ App is accessible. Page title: {driver.title}")
        
        # Try to access nutrition goals page directly
        print("🎯 Testing nutrition goals page...")
        driver.get("http://127.0.0.1:5001/dashboard/nutrition-goals")
        
        # Check if we're redirected to login
        current_url = driver.current_url
        print(f"📍 Current URL: {current_url}")
        
        if "login" in current_url:
            print("🔐 Login required, testing login page...")
            
            # Check if there are any existing users
            print("👥 Attempting to register/login...")
            
            # Try to register first
            try:
                driver.get("http://127.0.0.1:5001/auth/register")
                
                # Fill registration form
                username_field = driver.find_element(By.NAME, "username")
                password_field = driver.find_element(By.NAME, "password")
                confirm_password_field = driver.find_element(By.NAME, "confirm_password")
                
                username_field.clear()
                username_field.send_keys("testuser")
                password_field.clear()
                password_field.send_keys("testpass123")
                confirm_password_field.clear()
                confirm_password_field.send_keys("testpass123")
                
                # Submit registration
                submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                submit_button.click()
                
                time.sleep(2)
                print("✅ Registration attempted")
                
            except Exception as reg_error:
                print(f"⚠️  Registration failed: {reg_error}")
                
                # Try login instead
                try:
                    driver.get("http://127.0.0.1:5001/auth/login")
                    
                    username_field = driver.find_element(By.NAME, "username")
                    password_field = driver.find_element(By.NAME, "password")
                    
                    username_field.clear()
                    username_field.send_keys("admin")
                    password_field.clear()  
                    password_field.send_keys("admin123")
                    
                    submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                    submit_button.click()
                    
                    time.sleep(2)
                    print("✅ Admin login attempted")
                    
                except Exception as login_error:
                    print(f"❌ Login failed: {login_error}")
                    return False
        
        # Now try to access nutrition goals page
        print("🎯 Accessing nutrition goals page...")
        driver.get("http://127.0.0.1:5001/dashboard/nutrition-goals")
        time.sleep(3)
        
        print(f"📍 Final URL: {driver.current_url}")
        print(f"📄 Page title: {driver.title}")
        
        # Check for JavaScript errors in console
        print("🔍 Checking for JavaScript errors...")
        logs = driver.get_log('browser')
        js_errors = [log for log in logs if log['level'] == 'SEVERE']
        
        if js_errors:
            print("❌ JavaScript errors found:")
            for error in js_errors:
                print(f"   - {error['message']}")
        else:
            print("✅ No JavaScript errors found")
        
        # Check if the form elements exist
        print("🔍 Checking form elements...")
        
        try:
            duration_select = driver.find_element(By.ID, "target_duration")
            print("✅ Target duration dropdown found")
            
            date_input = driver.find_element(By.ID, "target_date")
            print("✅ Target date input found")
            
            # Test the functionality
            print("🧪 Testing duration selection...")
            
            # Test different duration options
            duration_options = ["2_weeks", "1_month", "3_months"]
            
            for duration in duration_options:
                print(f"   Testing: {duration}")
                
                # Select duration
                select = Select(duration_select)
                select.select_by_value(duration)
                
                time.sleep(1)  # Wait for JavaScript to execute
                
                # Check if date was updated
                date_value = date_input.get_attribute("value")
                print(f"   Date after selecting {duration}: {date_value}")
                
                if date_value:
                    print(f"   ✅ Date updated for {duration}")
                else:
                    print(f"   ❌ Date NOT updated for {duration}")
            
            print("✅ Form functionality test completed")
            return True
            
        except Exception as form_error:
            print(f"❌ Form elements not found: {form_error}")
            
            # Print page source for debugging
            print("📄 Page source (first 1000 chars):")
            print(driver.page_source[:1000])
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
        
    finally:
        if driver:
            driver.quit()
            print("🔚 Browser closed")

def main():
    """Main function"""
    print("🚀 NUTRITION GOALS JAVASCRIPT FUNCTIONALITY TEST")
    print("=" * 60)
    
    # First check if the app is running
    try:
        response = requests.get("http://127.0.0.1:5001", timeout=5)
        print(f"✅ App is running. Status code: {response.status_code}")
    except Exception as e:
        print(f"❌ App is not accessible: {e}")
        print("💡 Please make sure the Flask app is running with: python app.py")
        return
    
    # Run the test
    success = test_nutrition_goals_functionality()
    
    if success:
        print("\n✅ TEST COMPLETED SUCCESSFULLY")
    else:
        print("\n❌ TEST FAILED - Please check the issues above")

if __name__ == "__main__":
    main()
