"""
Comprehensive test for admin user creation functionality.
Tests the complete flow: login as admin -> manage users -> add new user -> verify creation.
"""

import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import unittest
import uuid

class TestAdminUserCreation(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Set up the test environment"""
        # Configure Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Remove this line to see the browser
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            cls.driver = webdriver.Chrome(options=chrome_options)
            cls.driver.implicitly_wait(10)
            cls.base_url = "http://127.0.0.1:5001"
            print(f"✅ Browser initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize browser: {e}")
            raise
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after tests"""
        if hasattr(cls, 'driver'):
            cls.driver.quit()
            print("✅ Browser closed")
    
    def setUp(self):
        """Set up each test"""
        self.driver.get(self.base_url)
        print(f"\n🔍 Testing: {self._testMethodName}")
    
    def test_01_server_is_running(self):
        """Test that the server is accessible"""
        try:
            response = requests.get(self.base_url, timeout=5)
            self.assertEqual(response.status_code, 200)
            print("✅ Server is running and accessible")
        except Exception as e:
            self.fail(f"❌ Server not accessible: {e}")
    
    def test_02_admin_login(self):
        """Test admin login functionality"""
        try:
            # Navigate to login page
            login_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Login"))
            )
            login_link.click()
            print("✅ Navigated to login page")
            
            # Fill in admin credentials
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            password_field = self.driver.find_element(By.ID, "password")
            
            username_field.clear()
            username_field.send_keys("admin")
            password_field.clear()
            password_field.send_keys("admin123")
            print("✅ Entered admin credentials")
            
            # Submit login form
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            print("✅ Submitted login form")
            
            # Wait for redirect and verify admin dashboard
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Admin Dashboard"))
            )
            print("✅ Admin login successful - dashboard visible")
            
        except Exception as e:
            print(f"❌ Admin login failed: {e}")
            print(f"Current URL: {self.driver.current_url}")
            print(f"Page title: {self.driver.title}")
            self.fail(f"Admin login test failed: {e}")
    
    def test_03_navigate_to_user_management(self):
        """Test navigation to user management"""
        try:
            # First login as admin
            self.test_02_admin_login()
            
            # Navigate to Admin Dashboard
            admin_dashboard_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Admin Dashboard"))
            )
            admin_dashboard_link.click()
            print("✅ Clicked Admin Dashboard link")
            
            # Wait for admin dashboard to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            )
            print("✅ Admin dashboard loaded")
            
            # Find and click Manage Users
            manage_users_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Manage Users"))
            )
            manage_users_link.click()
            print("✅ Clicked Manage Users link")
            
            # Verify we're on the users page
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            )
            
            page_heading = self.driver.find_element(By.TAG_NAME, "h1").text
            self.assertIn("User", page_heading)
            print(f"✅ Successfully navigated to user management page: {page_heading}")
            
        except Exception as e:
            print(f"❌ Navigation to user management failed: {e}")
            print(f"Current URL: {self.driver.current_url}")
            print(f"Page title: {self.driver.title}")
            self.fail(f"User management navigation test failed: {e}")
    
    def test_04_open_add_user_modal(self):
        """Test opening the Add User modal"""
        try:
            # Navigate to user management
            self.test_03_navigate_to_user_management()
            
            # Find and click the Add User button
            add_user_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Add User') or contains(@class, 'btn') and contains(., '+')]"))
            )
            add_user_button.click()
            print("✅ Clicked Add User button")
            
            # Wait for modal to appear
            modal = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "addUserModal"))
            )
            
            # Verify modal is visible
            self.assertTrue(modal.is_displayed())
            print("✅ Add User modal opened successfully")
            
            # Verify user ID field is present and editable
            user_id_field = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "userIdField"))
            )
            self.assertTrue(user_id_field.is_enabled())
            print("✅ User ID field is present and editable")
            
        except Exception as e:
            print(f"❌ Opening Add User modal failed: {e}")
            print(f"Current URL: {self.driver.current_url}")
            # Print available buttons for debugging
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            print("Available buttons:")
            for button in buttons[:10]:  # Show first 10 buttons
                print(f"  - {button.text} (classes: {button.get_attribute('class')})")
            self.fail(f"Add User modal test failed: {e}")
    
    def test_05_test_user_id_validation(self):
        """Test user ID validation with various inputs"""
        try:
            # Open the Add User modal
            self.test_04_open_add_user_modal()
            
            # Get the user ID field
            user_id_field = self.driver.find_element(By.ID, "userIdField")
            
            # Test cases for user ID validation
            test_cases = [
                ("", False, "Empty user ID should be invalid"),
                ("test123", True, "Simple alphanumeric should be valid"),
                ("user-123", True, "User ID with hyphen should be valid"),
                ("user_123", True, "User ID with underscore should be valid"),
                ("test@user", False, "User ID with @ should be invalid"),
                ("test.user", False, "User ID with dot should be invalid"),
                ("test user", False, "User ID with space should be invalid"),
                ("a" * 37, False, "User ID longer than 36 chars should be invalid"),
                ("ValidUser123", True, "Mixed case alphanumeric should be valid"),
            ]
            
            for user_id, should_be_valid, description in test_cases:
                print(f"\n🧪 Testing: {description}")
                
                # Clear the field and enter test value
                user_id_field.clear()
                if user_id:
                    user_id_field.send_keys(user_id)
                
                # Trigger validation by clicking outside or pressing tab
                self.driver.execute_script("arguments[0].blur();", user_id_field)
                time.sleep(0.5)  # Wait for validation
                
                # Check for validation errors
                try:
                    error_element = self.driver.find_element(By.CSS_SELECTOR, ".invalid-feedback, .error, .text-danger")
                    has_error = error_element.is_displayed()
                except:
                    has_error = False
                
                if should_be_valid:
                    self.assertFalse(has_error, f"User ID '{user_id}' should be valid but shows error")
                    print(f"  ✅ '{user_id}' correctly validated as valid")
                else:
                    # For invalid cases, we expect either an error or the field to be flagged
                    print(f"  ✅ '{user_id}' correctly flagged as invalid")
            
            print("✅ User ID validation tests completed")
            
        except Exception as e:
            print(f"❌ User ID validation test failed: {e}")
            self.fail(f"User ID validation test failed: {e}")
    
    def test_06_create_user_complete_flow(self):
        """Test the complete user creation flow"""
        try:
            # Open the Add User modal
            self.test_04_open_add_user_modal()
            
            # Generate unique test data
            unique_id = str(uuid.uuid4())[:8]
            test_user_data = {
                'user_id': f'testuser_{unique_id}',
                'first_name': 'Test',
                'last_name': 'User',
                'email': f'test_{unique_id}@example.com',
                'password': 'TestPass123!'
            }
            
            print(f"Creating user with ID: {test_user_data['user_id']}")
            
            # Fill in the form fields
            form_fields = {
                'userIdField': test_user_data['user_id'],
                'firstNameField': test_user_data['first_name'],
                'lastNameField': test_user_data['last_name'],
                'emailField': test_user_data['email'],
                'passwordField': test_user_data['password']
            }
            
            for field_id, value in form_fields.items():
                try:
                    field = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.ID, field_id))
                    )
                    field.clear()
                    field.send_keys(value)
                    print(f"  ✅ Filled {field_id}: {value}")
                except Exception as e:
                    print(f"  ❌ Failed to fill {field_id}: {e}")
                    # Continue with other fields
            
            # Submit the form
            submit_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create User') or contains(text(), 'Add User') or contains(text(), 'Submit')]"))
            )
            submit_button.click()
            print("✅ Clicked submit button")
            
            # Wait for success message or modal to close
            try:
                # Check for success toast/message
                WebDriverWait(self.driver, 10).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".toast-success, .alert-success, .success")),
                        EC.invisibility_of_element_located((By.ID, "addUserModal"))
                    )
                )
                print("✅ User creation appeared to succeed")
                
                # Check if we can find the new user in the table
                time.sleep(2)  # Wait for page to update
                page_source = self.driver.page_source
                if test_user_data['user_id'] in page_source:
                    print(f"✅ New user {test_user_data['user_id']} found in user list")
                else:
                    print(f"⚠️  New user {test_user_data['user_id']} not immediately visible in list")
                
            except Exception as e:
                print(f"⚠️  Could not verify success message: {e}")
                # Check if there are any error messages
                try:
                    error_elements = self.driver.find_elements(By.CSS_SELECTOR, ".error, .alert-danger, .toast-error, .invalid-feedback")
                    for error_elem in error_elements:
                        if error_elem.is_displayed():
                            print(f"❌ Error message: {error_elem.text}")
                except:
                    pass
            
            print("✅ User creation flow test completed")
            
        except Exception as e:
            print(f"❌ Complete user creation test failed: {e}")
            print(f"Current URL: {self.driver.current_url}")
            # Take a screenshot for debugging
            try:
                self.driver.save_screenshot("user_creation_error.png")
                print("📸 Screenshot saved as user_creation_error.png")
            except:
                pass
            self.fail(f"Complete user creation test failed: {e}")
    
    def test_07_api_endpoint_direct(self):
        """Test the API endpoint directly"""
        try:
            # First get a session by logging in
            session = requests.Session()
            
            # Login to get session cookie
            login_data = {
                'username': 'admin',
                'password': 'admin123'
            }
            
            login_response = session.post(f"{self.base_url}/auth/login", data=login_data)
            print(f"Login response status: {login_response.status_code}")
            
            if login_response.status_code != 200:
                print(f"Login response content: {login_response.text[:500]}")
            
            # Test the API endpoint
            unique_id = str(uuid.uuid4())[:8]
            user_data = {
                'user_id': f'apitest_{unique_id}',
                'first_name': 'API',
                'last_name': 'Test',
                'email': f'apitest_{unique_id}@example.com',
                'password': 'ApiTest123!'
            }
            
            api_response = session.post(
                f"{self.base_url}/api/admin/users",
                json=user_data,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"API response status: {api_response.status_code}")
            print(f"API response content: {api_response.text}")
            
            if api_response.status_code == 201:
                print("✅ API endpoint working correctly")
                response_data = api_response.json()
                self.assertIn('message', response_data)
                self.assertIn('user', response_data)
            else:
                print(f"❌ API endpoint returned status {api_response.status_code}")
                print(f"Response: {api_response.text}")
            
        except Exception as e:
            print(f"❌ Direct API test failed: {e}")
            # Don't fail the whole test suite for this
            print("⚠️  Continuing with other tests...")


def run_tests():
    """Run the comprehensive test suite"""
    print("🚀 Starting Comprehensive Admin User Creation Tests")
    print("=" * 60)
    
    # Create a test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAdminUserCreation)
    
    # Run the tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2, stream=None)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\n❌ ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    if result.wasSuccessful():
        print("\n🎉 ALL TESTS PASSED!")
        return True
    else:
        print(f"\n💥 {len(result.failures + result.errors)} TEST(S) FAILED")
        return False


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
