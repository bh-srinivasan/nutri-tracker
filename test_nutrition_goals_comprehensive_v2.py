#!/usr/bin/env python3
"""
Comprehensive Test Plan for Nutrition Goals Functionality
Tests all user flows, edge cases, and error scenarios
"""

import requests
import re
import time
from datetime import datetime

class NutritionGoalsTestSuite:
    """Complete test suite for nutrition goals functionality"""
    
    def __init__(self, base_url="http://127.0.0.1:5001"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name, status, message=""):
        """Log test result"""
        result = {
            'test': test_name,
            'status': status,
            'message': message,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
        self.test_results.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {status}")
        if message:
            print(f"   {message}")
    
    def login_user(self, username, password):
        """Login as specified user"""
        try:
            # Get login page for CSRF token
            login_page = self.session.get(f"{self.base_url}/auth/login")
            csrf_match = re.search(r'name="csrf_token".*?value="([^"]+)"', login_page.text)
            csrf_token = csrf_match.group(1) if csrf_match else None
            
            # Login
            login_data = {'username': username, 'password': password}
            if csrf_token:
                login_data['csrf_token'] = csrf_token
            
            response = self.session.post(f"{self.base_url}/auth/login", 
                                       data=login_data, allow_redirects=True)
            
            return "/dashboard" in response.url
            
        except Exception as e:
            self.log_test("Login", "FAIL", f"Exception: {e}")
            return False
    
    def test_1_goals_page_access(self):
        """Test 1: Basic Goals Page Access"""
        print("\n🎯 TEST 1: Goals Page Access")
        print("-" * 40)
        
        # Test with different users
        test_users = [
            ("testuser", "testpass123", "Non-admin user"),
            ("admin", "admin123", "Admin user")
        ]
        
        for username, password, user_type in test_users:
            try:
                # Fresh session for each user
                self.session = requests.Session()
                
                if not self.login_user(username, password):
                    self.log_test(f"Goals Access - {user_type}", "FAIL", "Login failed")
                    continue
                
                # Access goals page
                response = self.session.get(f"{self.base_url}/dashboard/nutrition-goals")
                
                if response.status_code == 200:
                    # Check for template errors
                    error_patterns = [
                        r'UndefinedError', r'has no attribute', 
                        r'start_date', r'end_date',
                        r'Internal Server Error', r'500'
                    ]
                    
                    errors_found = []
                    for pattern in error_patterns:
                        if re.search(pattern, response.text, re.IGNORECASE):
                            errors_found.append(pattern)
                    
                    if errors_found:
                        self.log_test(f"Goals Access - {user_type}", "FAIL", 
                                    f"Template errors: {errors_found}")
                    else:
                        self.log_test(f"Goals Access - {user_type}", "PASS")
                else:
                    self.log_test(f"Goals Access - {user_type}", "FAIL", 
                                f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Goals Access - {user_type}", "FAIL", f"Exception: {e}")
    
    def test_2_quick_actions_flow(self):
        """Test 2: Quick Actions 'Set Goals' Flow"""
        print("\n⚡ TEST 2: Quick Actions Flow")
        print("-" * 40)
        
        try:
            # Login as non-admin user
            self.session = requests.Session()
            if not self.login_user("testuser", "testpass123"):
                self.log_test("Quick Actions - Login", "FAIL", "Cannot login as testuser")
                return
            
            # Access dashboard first
            dashboard_response = self.session.get(f"{self.base_url}/dashboard")
            if dashboard_response.status_code != 200:
                self.log_test("Quick Actions - Dashboard", "FAIL", 
                            f"Dashboard access failed: {dashboard_response.status_code}")
                return
            else:
                self.log_test("Quick Actions - Dashboard", "PASS")
            
            # Check if "Set Goals" link exists in dashboard
            if 'nutrition-goals' in dashboard_response.text:
                self.log_test("Quick Actions - Link Present", "PASS")
            else:
                self.log_test("Quick Actions - Link Present", "WARN", 
                            "Set Goals link not found in dashboard")
            
            # Click on "Set Goals" (simulate the user action)
            goals_response = self.session.get(f"{self.base_url}/dashboard/nutrition-goals")
            
            if goals_response.status_code == 200:
                # Check for specific errors that user reported
                error_checks = [
                    (r'start_date', "start_date attribute error"),
                    (r'end_date', "end_date attribute error"),
                    (r'UndefinedError', "Undefined variable error"),
                    (r'500 Internal Server Error', "Server error"),
                    (r'has no attribute', "Attribute error")
                ]
                
                errors_found = []
                for pattern, description in error_checks:
                    if re.search(pattern, goals_response.text, re.IGNORECASE):
                        errors_found.append(description)
                
                if errors_found:
                    self.log_test("Quick Actions - Set Goals Click", "FAIL", 
                                f"Errors: {', '.join(errors_found)}")
                else:
                    self.log_test("Quick Actions - Set Goals Click", "PASS")
                    
                    # Check if form loads properly
                    if '<form method="POST">' in goals_response.text:
                        self.log_test("Quick Actions - Form Load", "PASS")
                    else:
                        self.log_test("Quick Actions - Form Load", "FAIL", "Form not found")
            else:
                self.log_test("Quick Actions - Set Goals Click", "FAIL", 
                            f"HTTP {goals_response.status_code}")
                
        except Exception as e:
            self.log_test("Quick Actions - Exception", "FAIL", f"Exception: {e}")
    
    def test_3_form_submission_flow(self):
        """Test 3: Complete Form Submission Flow"""
        print("\n📝 TEST 3: Form Submission Flow")
        print("-" * 40)
        
        try:
            # Login as non-admin user
            self.session = requests.Session()
            if not self.login_user("testuser", "testpass123"):
                self.log_test("Form Submission - Login", "FAIL")
                return
            
            # Get goals page
            goals_page = self.session.get(f"{self.base_url}/dashboard/nutrition-goals")
            if goals_page.status_code != 200:
                self.log_test("Form Submission - Page Load", "FAIL")
                return
            else:
                self.log_test("Form Submission - Page Load", "PASS")
            
            # Extract CSRF token
            csrf_match = re.search(r'name="csrf_token".*?value="([^"]+)"', goals_page.text)
            if not csrf_match:
                self.log_test("Form Submission - CSRF Token", "FAIL", "No CSRF token found")
                return
            else:
                self.log_test("Form Submission - CSRF Token", "PASS")
            
            csrf_token = csrf_match.group(1)
            
            # Test form submission with valid data
            form_data = {
                'csrf_token': csrf_token,
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
            
            submit_response = self.session.post(f"{self.base_url}/dashboard/nutrition-goals", 
                                              data=form_data, allow_redirects=False)
            
            if submit_response.status_code == 302:
                self.log_test("Form Submission - Valid Data", "PASS", "Redirected successfully")
                
                # Check redirect location
                redirect_url = submit_response.headers.get('Location', '')
                if '/dashboard' in redirect_url:
                    self.log_test("Form Submission - Redirect Target", "PASS")
                else:
                    self.log_test("Form Submission - Redirect Target", "WARN", 
                                f"Unexpected redirect: {redirect_url}")
            else:
                self.log_test("Form Submission - Valid Data", "FAIL", 
                            f"HTTP {submit_response.status_code}")
                
        except Exception as e:
            self.log_test("Form Submission - Exception", "FAIL", f"Exception: {e}")
    
    def test_4_existing_goals_display(self):
        """Test 4: Existing Goals Display"""
        print("\n📊 TEST 4: Existing Goals Display")
        print("-" * 40)
        
        try:
            # Login as user who should now have goals (from previous test)
            self.session = requests.Session()
            if not self.login_user("testuser", "testpass123"):
                self.log_test("Existing Goals - Login", "FAIL")
                return
            
            # Access goals page to see if existing goals display correctly
            goals_response = self.session.get(f"{self.base_url}/dashboard/nutrition-goals")
            
            if goals_response.status_code == 200:
                self.log_test("Existing Goals - Page Load", "PASS")
                
                # Check if current goals section appears
                if 'Current Goals' in goals_response.text:
                    self.log_test("Existing Goals - Display Section", "PASS")
                    
                    # Check for the specific error that was reported
                    if 'start_date' in goals_response.text:
                        self.log_test("Existing Goals - Date Display", "FAIL", 
                                    "start_date still referenced in template")
                    else:
                        self.log_test("Existing Goals - Date Display", "PASS")
                        
                    # Check if created_at is displayed instead
                    if 'Set on' in goals_response.text:
                        self.log_test("Existing Goals - Created Date", "PASS")
                    else:
                        self.log_test("Existing Goals - Created Date", "WARN", 
                                    "Created date not displayed")
                else:
                    self.log_test("Existing Goals - Display Section", "WARN", 
                                "Current Goals section not found")
            else:
                self.log_test("Existing Goals - Page Load", "FAIL", 
                            f"HTTP {goals_response.status_code}")
                
        except Exception as e:
            self.log_test("Existing Goals - Exception", "FAIL", f"Exception: {e}")
    
    def test_5_edge_cases(self):
        """Test 5: Edge Cases and Error Handling"""
        print("\n🧪 TEST 5: Edge Cases")
        print("-" * 40)
        
        try:
            # Test with invalid form data
            self.session = requests.Session()
            if not self.login_user("testuser", "testpass123"):
                self.log_test("Edge Cases - Login", "FAIL")
                return
            
            # Get CSRF token
            goals_page = self.session.get(f"{self.base_url}/dashboard/nutrition-goals")
            csrf_match = re.search(r'name="csrf_token".*?value="([^"]+)"', goals_page.text)
            csrf_token = csrf_match.group(1) if csrf_match else None
            
            if not csrf_token:
                self.log_test("Edge Cases - CSRF Token", "FAIL")
                return
            
            # Test with invalid data
            invalid_data = {
                'csrf_token': csrf_token,
                'weight': '-10',  # Invalid
                'height': '500',  # Invalid
                'age': '200',     # Invalid
                'gender': 'invalid',  # Invalid
                'activity_level': 'invalid',  # Invalid
                'goal_type': 'invalid',  # Invalid
                'target_calories': '50',  # Too low
                'target_protein': '1000',  # Too high
                'submit': 'Set Goals'
            }
            
            invalid_response = self.session.post(f"{self.base_url}/dashboard/nutrition-goals", 
                                               data=invalid_data, allow_redirects=False)
            
            if invalid_response.status_code == 200:
                # Should stay on form with validation errors
                if 'is-invalid' in invalid_response.text or 'error' in invalid_response.text.lower():
                    self.log_test("Edge Cases - Invalid Data Handling", "PASS")
                else:
                    self.log_test("Edge Cases - Invalid Data Handling", "WARN", 
                                "No validation errors shown")
            else:
                self.log_test("Edge Cases - Invalid Data Handling", "FAIL", 
                            f"Unexpected response: {invalid_response.status_code}")
                
        except Exception as e:
            self.log_test("Edge Cases - Exception", "FAIL", f"Exception: {e}")
    
    def test_6_navigation_flow(self):
        """Test 6: Navigation Flow"""
        print("\n🧭 TEST 6: Navigation Flow")
        print("-" * 40)
        
        try:
            # Test navigation from dashboard to goals and back
            self.session = requests.Session()
            if not self.login_user("testuser", "testpass123"):
                self.log_test("Navigation - Login", "FAIL")
                return
            
            # Start from dashboard
            dashboard_response = self.session.get(f"{self.base_url}/dashboard")
            if dashboard_response.status_code == 200:
                self.log_test("Navigation - Dashboard Access", "PASS")
            else:
                self.log_test("Navigation - Dashboard Access", "FAIL")
                return
            
            # Navigate to goals
            goals_response = self.session.get(f"{self.base_url}/dashboard/nutrition-goals")
            if goals_response.status_code == 200:
                self.log_test("Navigation - Goals Access", "PASS")
                
                # Check for back button
                if 'Back to Dashboard' in goals_response.text:
                    self.log_test("Navigation - Back Button Present", "PASS")
                else:
                    self.log_test("Navigation - Back Button Present", "WARN")
            else:
                self.log_test("Navigation - Goals Access", "FAIL")
                return
            
            # Navigate back to dashboard
            back_response = self.session.get(f"{self.base_url}/dashboard")
            if back_response.status_code == 200:
                self.log_test("Navigation - Return to Dashboard", "PASS")
            else:
                self.log_test("Navigation - Return to Dashboard", "FAIL")
                
        except Exception as e:
            self.log_test("Navigation - Exception", "FAIL", f"Exception: {e}")
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 STARTING COMPREHENSIVE NUTRITION GOALS TEST SUITE")
        print("=" * 60)
        print(f"Target URL: {self.base_url}")
        print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Run all tests
        self.test_1_goals_page_access()
        self.test_2_quick_actions_flow()
        self.test_3_form_submission_flow()
        self.test_4_existing_goals_display()
        self.test_5_edge_cases()
        self.test_6_navigation_flow()
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📋 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed = len([t for t in self.test_results if t['status'] == 'PASS'])
        failed = len([t for t in self.test_results if t['status'] == 'FAIL'])
        warnings = len([t for t in self.test_results if t['status'] == 'WARN'])
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️ Warnings: {warnings}")
        
        if failed > 0:
            print(f"\n❌ FAILED TESTS:")
            for test in self.test_results:
                if test['status'] == 'FAIL':
                    print(f"   - {test['test']}: {test['message']}")
        
        if warnings > 0:
            print(f"\n⚠️ WARNINGS:")
            for test in self.test_results:
                if test['status'] == 'WARN':
                    print(f"   - {test['test']}: {test['message']}")
        
        print("\n" + "=" * 60)
        if failed == 0:
            print("🎉 ALL CRITICAL TESTS PASSED!")
            print("✅ Nutrition Goals functionality is working correctly!")
        else:
            print("❌ SOME TESTS FAILED!")
            print("🔧 Please check the issues above and fix them.")
        print("=" * 60)

if __name__ == "__main__":
    # Check if server is running
    print("🔍 Checking if Flask server is running...")
    try:
        response = requests.get("http://127.0.0.1:5001", timeout=5)
        print("✅ Server is running!")
    except:
        print("❌ Server is not running on port 5001!")
        print("Please start the server first: python app.py")
        exit(1)
    
    # Run comprehensive test suite
    test_suite = NutritionGoalsTestSuite()
    test_suite.run_all_tests()
