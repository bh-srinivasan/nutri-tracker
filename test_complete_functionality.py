#!/usr/bin/env python3
"""
Comprehensive test script to verify:
1. Admin user creation functionality
2. Meal edit/delete functionality for non-admin users
"""

import sys
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class NutriTrackerTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.driver = None
        self.wait = None
        
    def setup_driver(self):
        """Setup Chrome driver with options"""
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        
        try:
            self.driver = webdriver.Chrome(options=options)
            self.wait = WebDriverWait(self.driver, 10)
            print("✅ Chrome driver setup successful")
            return True
        except Exception as e:
            print(f"❌ Failed to setup Chrome driver: {e}")
            return False
    
    def admin_login(self, username="admin", password="admin123"):
        """Login as admin user"""
        print(f"\n🔐 Attempting admin login with {username}...")
        
        try:
            self.driver.get(f"{self.base_url}/admin/login")
            time.sleep(2)
            
            # Fill login form
            username_field = self.wait.until(EC.presence_of_element_located((By.NAME, "username")))
            password_field = self.driver.find_element(By.NAME, "password")
            
            username_field.clear()
            username_field.send_keys(username)
            password_field.clear()
            password_field.send_keys(password)
            
            # Submit form
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
            submit_button.click()
            
            time.sleep(3)
            
            # Check if login successful
            if "/admin/dashboard" in self.driver.current_url or "Admin Dashboard" in self.driver.page_source:
                print("✅ Admin login successful")
                return True
            else:
                print(f"❌ Admin login failed. Current URL: {self.driver.current_url}")
                print(f"Page title: {self.driver.title}")
                return False
                
        except Exception as e:
            print(f"❌ Admin login error: {e}")
            return False
    
    def test_admin_user_creation(self):
        """Test admin user creation functionality"""
        print(f"\n👤 Testing admin user creation...")
        
        try:
            # Navigate to admin user management
            self.driver.get(f"{self.base_url}/admin/users")
            time.sleep(2)
            
            # Look for create user button or form
            create_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Create') or contains(text(), 'Add') or contains(text(), 'New')]")
            if not create_buttons:
                create_buttons = self.driver.find_elements(By.XPATH, "//a[contains(text(), 'Create') or contains(text(), 'Add') or contains(text(), 'New')]")
            
            if create_buttons:
                create_buttons[0].click()
                time.sleep(2)
            
            # Generate unique test user data
            test_timestamp = str(int(time.time()))
            test_username = f"testuser{test_timestamp}"
            test_email = f"test{test_timestamp}@example.com"
            
            print(f"Creating user: {test_username}")
            
            # Fill user creation form
            username_field = self.wait.until(EC.presence_of_element_located((By.NAME, "username")))
            username_field.clear()
            username_field.send_keys(test_username)
            
            # Find email field (might be optional)
            try:
                email_field = self.driver.find_element(By.NAME, "email")
                email_field.clear()
                email_field.send_keys(test_email)
            except NoSuchElementException:
                print("Email field not found (might be optional)")
            
            # Find password field
            password_field = self.driver.find_element(By.NAME, "password")
            password_field.clear()
            password_field.send_keys("testpass123")
            
            # Submit form
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
            submit_button.click()
            
            time.sleep(3)
            
            # Check for success message or user in list
            page_source = self.driver.page_source.lower()
            if ("success" in page_source and "created" in page_source) or test_username.lower() in page_source:
                print("✅ Admin user creation successful")
                return True, test_username, "testpass123"
            else:
                print("❌ Admin user creation failed")
                print(f"Page source contains: {self.driver.page_source[:500]}...")
                return False, None, None
                
        except Exception as e:
            print(f"❌ Admin user creation error: {e}")
            return False, None, None
    
    def regular_user_login(self, username, password):
        """Login as regular user"""
        print(f"\n🔐 Logging in as regular user: {username}")
        
        try:
            # Logout first if logged in
            self.driver.get(f"{self.base_url}/auth/logout")
            time.sleep(2)
            
            # Navigate to login page
            self.driver.get(f"{self.base_url}/auth/login")
            time.sleep(2)
            
            # Fill login form
            username_field = self.wait.until(EC.presence_of_element_located((By.NAME, "username")))
            password_field = self.driver.find_element(By.NAME, "password")
            
            username_field.clear()
            username_field.send_keys(username)
            password_field.clear()
            password_field.send_keys(password)
            
            # Submit form
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
            submit_button.click()
            
            time.sleep(3)
            
            # Check if login successful
            if "/dashboard" in self.driver.current_url or "Dashboard" in self.driver.page_source:
                print("✅ Regular user login successful")
                return True
            else:
                print(f"❌ Regular user login failed. Current URL: {self.driver.current_url}")
                return False
                
        except Exception as e:
            print(f"❌ Regular user login error: {e}")
            return False
    
    def log_test_meal(self):
        """Log a test meal for the user"""
        print(f"\n🍎 Logging a test meal...")
        
        try:
            # Navigate to meal logging page
            self.driver.get(f"{self.base_url}/dashboard/log-meal")
            time.sleep(2)
            
            # Look for food search or selection
            food_fields = self.driver.find_elements(By.NAME, "food_id")
            if not food_fields:
                food_fields = self.driver.find_elements(By.ID, "food_id")
            
            if food_fields:
                # Try to select first available food
                select = Select(food_fields[0])
                options = select.options
                if len(options) > 1:  # Skip first empty option
                    select.select_by_index(1)
                    time.sleep(1)
            
            # Fill quantity
            quantity_field = self.driver.find_element(By.NAME, "quantity")
            quantity_field.clear()
            quantity_field.send_keys("100")
            
            # Select meal type
            meal_type_field = self.driver.find_element(By.NAME, "meal_type")
            select = Select(meal_type_field)
            select.select_by_value("lunch")
            
            # Submit form
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
            submit_button.click()
            
            time.sleep(3)
            
            # Check for success
            if "success" in self.driver.page_source.lower() or "/dashboard" in self.driver.current_url:
                print("✅ Test meal logged successfully")
                return True
            else:
                print("❌ Failed to log test meal")
                return False
                
        except Exception as e:
            print(f"❌ Meal logging error: {e}")
            return False
    
    def test_meal_edit_delete(self):
        """Test meal edit and delete functionality"""
        print(f"\n✏️ Testing meal edit/delete functionality...")
        
        try:
            # Navigate to dashboard to see today's meals
            self.driver.get(f"{self.base_url}/dashboard")
            time.sleep(3)
            
            # Look for edit buttons
            edit_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button.edit-meal, .edit-btn, [onclick*='edit'], [data-action='edit']")
            if not edit_buttons:
                edit_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Edit') or contains(@class, 'edit')]")
            
            # Look for delete buttons
            delete_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button.delete-meal, .delete-btn, [onclick*='delete'], [data-action='delete']")
            if not delete_buttons:
                delete_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Delete') or contains(@class, 'delete')]")
            
            print(f"Found {len(edit_buttons)} edit buttons and {len(delete_buttons)} delete buttons")
            
            # Test edit functionality
            if edit_buttons:
                print("Testing edit functionality...")
                edit_buttons[0].click()
                time.sleep(3)
                
                # Check if redirected to edit page
                if "edit=" in self.driver.current_url or "log-meal" in self.driver.current_url:
                    print("✅ Edit button works - redirected to edit page")
                    
                    # Try to modify the meal
                    try:
                        quantity_field = self.driver.find_element(By.NAME, "quantity")
                        quantity_field.clear()
                        quantity_field.send_keys("150")
                        
                        submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
                        submit_button.click()
                        time.sleep(3)
                        
                        if "success" in self.driver.page_source.lower() or "/dashboard" in self.driver.current_url:
                            print("✅ Meal edit successful")
                        else:
                            print("❌ Meal edit failed")
                    except Exception as e:
                        print(f"❌ Error during meal edit: {e}")
                else:
                    print("❌ Edit button didn't redirect properly")
            else:
                print("❌ No edit buttons found")
            
            # Navigate back to dashboard for delete test
            self.driver.get(f"{self.base_url}/dashboard")
            time.sleep(3)
            
            # Test delete functionality
            delete_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button.delete-meal, .delete-btn, [onclick*='delete'], [data-action='delete']")
            if not delete_buttons:
                delete_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Delete') or contains(@class, 'delete')]")
            
            if delete_buttons:
                print("Testing delete functionality...")
                # Click delete button (will trigger confirmation)
                delete_buttons[0].click()
                time.sleep(2)
                
                # Accept confirmation dialog if it appears
                try:
                    alert = self.driver.switch_to.alert
                    alert.accept()
                    time.sleep(3)
                    print("✅ Delete confirmation accepted")
                    
                    # Check for success message or meal removal
                    if "success" in self.driver.page_source.lower():
                        print("✅ Meal delete successful")
                        return True
                    else:
                        print("❌ No success message after delete")
                        return False
                        
                except Exception:
                    print("❌ No confirmation dialog appeared")
                    return False
            else:
                print("❌ No delete buttons found")
                return False
                
        except Exception as e:
            print(f"❌ Meal edit/delete test error: {e}")
            return False
    
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
            print("✅ Browser closed")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting comprehensive functionality tests...")
        
        if not self.setup_driver():
            return False
        
        try:
            # Test 1: Admin login
            if not self.admin_login():
                print("❌ Admin login failed - cannot proceed with tests")
                return False
            
            # Test 2: Admin user creation
            user_created, test_username, test_password = self.test_admin_user_creation()
            if not user_created:
                print("❌ Admin user creation failed")
                return False
            
            # Test 3: Regular user login
            if not self.regular_user_login(test_username, test_password):
                print("❌ Regular user login failed")
                return False
            
            # Test 4: Log a test meal
            if not self.log_test_meal():
                print("❌ Meal logging failed")
                return False
            
            # Test 5: Test meal edit/delete
            if not self.test_meal_edit_delete():
                print("❌ Meal edit/delete functionality failed")
                return False
            
            print("\n🎉 All tests completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Test execution error: {e}")
            return False
        finally:
            self.cleanup()

if __name__ == "__main__":
    tester = NutriTrackerTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
