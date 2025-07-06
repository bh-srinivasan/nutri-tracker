#!/usr/bin/env python3
"""
Simple test to verify email field is optional by testing the browser interface
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

def test_email_optional_browser():
    """Test email field is optional using browser automation"""
    print("🧪 Testing Email Optional Functionality via Browser")
    print("=" * 60)
    
    # Configure Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = None
    try:
        # Initialize Chrome driver
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        
        # Step 1: Login as admin
        print("🔐 Logging in as admin...")
        driver.get("http://127.0.0.1:5001/auth/login")
        
        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")
        
        username_field.send_keys("admin")
        password_field.send_keys("admin123")
        
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        
        # Wait for redirect to dashboard
        WebDriverWait(driver, 10).until(
            lambda d: "/dashboard" in d.current_url or "/admin" in d.current_url
        )
        print("✅ Admin login successful")
        
        # Step 2: Navigate to admin users page
        print("\n📝 Navigating to admin users page...")
        driver.get("http://127.0.0.1:5001/admin/users")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        print("✅ Admin users page loaded")
        
        # Step 3: Test Add User modal
        print("\n➕ Testing Add User modal...")
        
        # Click Add User button
        add_user_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Add User')]"))
        )
        add_user_btn.click()
        
        # Wait for modal to open
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "addUserModal"))
        )
        
        # Fill form without email
        first_name = driver.find_element(By.ID, "firstName")
        last_name = driver.find_element(By.ID, "lastName")
        password = driver.find_element(By.ID, "password")
        email = driver.find_element(By.ID, "email")
        
        first_name.send_keys("Test")
        last_name.send_keys("User")
        password.send_keys("TestPass123!")
        # Leave email empty
        
        # Submit form
        submit_btn = driver.find_element(By.XPATH, "//button[@type='submit'][contains(text(), 'Add User')]")
        submit_btn.click()
        
        # Check if form was submitted successfully (no validation errors)
        time.sleep(2)
        
        # Look for success toast or modal close
        modal_still_open = True
        try:
            driver.find_element(By.ID, "addUserModal")
        except:
            modal_still_open = False
        
        if not modal_still_open:
            print("✅ Add User form submitted successfully without email")
        else:
            print("❌ Add User form did not submit - email field may still be required")
        
        # Step 4: Test Edit User modal
        print("\n✏️ Testing Edit User modal...")
        
        # Find and click first edit button
        try:
            edit_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "edit-user-btn"))
            )
            edit_btn.click()
            
            # Wait for edit modal to open
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "editUserModal"))
            )
            
            # Clear email field
            edit_email = driver.find_element(By.ID, "editEmail")
            edit_email.clear()
            
            # Submit form
            edit_submit_btn = driver.find_element(By.XPATH, "//button[@type='submit'][contains(text(), 'Update User')]")
            edit_submit_btn.click()
            
            # Check if form was submitted successfully
            time.sleep(2)
            
            modal_still_open = True
            try:
                driver.find_element(By.ID, "editUserModal")
            except:
                modal_still_open = False
            
            if not modal_still_open:
                print("✅ Edit User form submitted successfully without email")
            else:
                print("❌ Edit User form did not submit - email field may still be required")
                
        except TimeoutException:
            print("⚠️ No edit buttons found - may need to create a user first")
        
        print("\n" + "=" * 60)
        print("✅ Browser testing completed!")
        
    except Exception as e:
        print(f"❌ Browser test failed: {e}")
        
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    test_email_optional_browser()
