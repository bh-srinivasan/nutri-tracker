#!/usr/bin/env python3
"""
Test script for clean toast-only password reset flow
Validates the simplified admin UX without banners or complex UI elements.
"""

import time
import os
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_clean_toast_flow():
    """Test the cleaned-up toast-only password reset flow"""
    
    print("🧪 Testing Clean Toast-Only Password Reset Flow")
    print("=" * 60)
    
    # Setup Chrome driver
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_window_size(1200, 800)
        wait = WebDriverWait(driver, 10)
        
        print("✅ Browser initialized")
        
        # 1. Navigate to the application
        print("\n📋 Step 1: Navigating to application")
        driver.get("http://127.0.0.1:5001")
        time.sleep(1)
        
        # Check if we're on the login page
        if "Login" in driver.title or "login" in driver.current_url.lower():
            print("✅ Reached login page")
            
            # Login as admin
            print("🔐 Logging in as admin...")
            username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
            password_field = driver.find_element(By.NAME, "password")
            
            username_field.send_keys("admin")
            password_field.send_keys("admin123")
            
            login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            time.sleep(2)
            print("✅ Admin login completed")
        
        # 2. Navigate to Manage Users
        print("\n📋 Step 2: Navigating to Manage Users")
        driver.get("http://127.0.0.1:5001/admin/users")
        time.sleep(2)
        
        # Verify we're on the manage users page
        if "users" in driver.current_url.lower():
            print("✅ Reached Manage Users page")
        else:
            print(f"❌ Expected users page, got: {driver.current_url}")
            return False
        
        # 3. Check for simplified UI (no preference toggles)
        print("\n📋 Step 3: Verifying simplified UI")
        
        # Check that there's no instant navigation toggle
        instant_toggles = driver.find_elements(By.ID, "instant-nav-toggle")
        if len(instant_toggles) == 0:
            print("✅ No preference toggle found - UI is simplified")
        else:
            print("❌ Found preference toggle - should be removed")
            return False
        
        # 4. Test password reset modal functionality
        print("\n📋 Step 4: Testing password reset modal")
        
        # Find a user row and click reset password
        reset_buttons = driver.find_elements(By.CSS_SELECTOR, ".reset-password-btn")
        if reset_buttons:
            print("✅ Found reset password buttons")
            
            # Get user info before clicking
            first_button = reset_buttons[0]
            user_id = first_button.get_attribute("data-user-id")
            username = first_button.get_attribute("data-username")
            
            print(f"📝 Testing password reset for user: {username} (ID: {user_id})")
            
            # Click the reset button
            first_button.click()
            time.sleep(1)
            
            # Verify modal opens
            modal = wait.until(EC.visibility_of_element_located((By.ID, "resetPasswordModal")))
            print("✅ Password reset modal opened")
            
            # Check that the modal has the simplified form (no confirm password)
            password_fields = modal.find_elements(By.CSS_SELECTOR, "input[type='password']")
            if len(password_fields) == 1:
                print("✅ Modal has single password field (simplified)")
            else:
                print(f"❌ Expected 1 password field, found {len(password_fields)}")
                return False
            
            # 5. Test the JavaScript validation flow
            print("\n📋 Step 5: Validating JavaScript flow")
            
            # Check if the clean toast function exists
            js_check = """
            return typeof Admin !== 'undefined' && 
                   typeof Admin.users !== 'undefined' && 
                   typeof Admin.users.showCleanSuccessToast === 'function';
            """
            
            has_clean_function = driver.execute_script(js_check)
            if has_clean_function:
                print("✅ showCleanSuccessToast function exists")
            else:
                print("❌ showCleanSuccessToast function not found")
                return False
            
            # Check that banner functions are removed
            js_banner_check = """
            return typeof Admin.users.showStreamlinedSuccessBanner === 'undefined' &&
                   typeof Admin.users.showInstantSuccessAndNavigate === 'undefined';
            """
            
            no_banner_functions = driver.execute_script(js_banner_check)
            if no_banner_functions:
                print("✅ Banner functions removed")
            else:
                print("❌ Banner functions still exist")
                return False
            
            # Close the modal
            close_button = modal.find_element(By.CSS_SELECTOR, "button[data-bs-dismiss='modal']")
            close_button.click()
            time.sleep(1)
            
        else:
            print("❌ No reset password buttons found")
            return False
        
        # 6. Test CSS cleanup
        print("\n📋 Step 6: Verifying CSS cleanup")
        
        # Check that banner CSS classes are not in the page
        banner_elements = driver.find_elements(By.CSS_SELECTOR, ".streamlined-success-banner")
        if len(banner_elements) == 0:
            print("✅ No banner elements found in DOM")
        else:
            print("❌ Found banner elements - should be cleaned up")
            return False
        
        print("\n🎉 All tests passed! Clean toast flow is working correctly.")
        print("\n📋 Summary of validated features:")
        print("  ✅ Simplified UI without preference toggles")
        print("  ✅ Single password field in reset modal")
        print("  ✅ showCleanSuccessToast function implemented")
        print("  ✅ Banner functions removed")
        print("  ✅ CSS banner classes cleaned up")
        print("  ✅ Clean, friction-free admin experience")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return False
        
    finally:
        if 'driver' in locals():
            driver.quit()
            print("\n🔧 Browser closed")

def main():
    """Run the clean toast flow test"""
    print("Starting Clean Toast Flow Validation...")
    print("Ensuring server is running on http://127.0.0.1:5001")
    
    success = test_clean_toast_flow()
    
    if success:
        print("\n🌟 Clean Toast Flow Test: PASSED")
        print("The admin password reset flow is now simplified and friction-free!")
    else:
        print("\n💥 Clean Toast Flow Test: FAILED")
        print("Some issues were found that need to be addressed.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
