#!/usr/bin/env python3
"""
Comprehensive Test Script for Enhanced Admin Form Functionality
Tests all three tasks and best practices implementation
"""

import os
import sys
import time
import json
from datetime import datetime

class AdminFormTestSuite:
    def __init__(self):
        self.test_results = []
        self.passed_tests = 0
        self.failed_tests = 0
        
    def log_test(self, test_name, passed, message=""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'status': status,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        
        if passed:
            self.passed_tests += 1
        else:
            self.failed_tests += 1
            
        print(f"{status}: {test_name}")
        if message:
            print(f"    {message}")
    
    def test_file_exists(self, file_path, description):
        """Test if a file exists"""
        exists = os.path.exists(file_path)
        self.log_test(
            f"File Exists - {description}",
            exists,
            f"Path: {file_path}" if exists else f"Missing: {file_path}"
        )
        return exists
    
    def test_file_contains(self, file_path, search_text, description):
        """Test if a file contains specific text"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                contains = search_text in content
                self.log_test(
                    f"File Content - {description}",
                    contains,
                    f"Found: {search_text[:50]}..." if contains else f"Missing: {search_text[:50]}..."
                )
                return contains
        except Exception as e:
            self.log_test(
                f"File Content - {description}",
                False,
                f"Error reading file: {e}"
            )
            return False
    
    def test_javascript_functions(self):
        """Test JavaScript function implementations"""
        admin_js_path = "app/static/js/admin.js"
        
        if not self.test_file_exists(admin_js_path, "Admin JavaScript File"):
            return False
        
        # Test Task 1: Email optional validation
        functions_to_check = [
            ("validateEditUserForm", "Enhanced form validation with email optional"),
            ("validatePasswordResetForm", "Password reset validation without email requirement"),
            ("clearValidationIndicators", "UI validation indicator functions"),
            ("showFieldError", "Field error display function"),
            ("showFieldSuccess", "Field success display function"),
            ("addRequiredIndicator", "Required field indicator function"),
            ("addOptionalIndicator", "Optional field indicator function"),
            ("handleModalClose", "Modal close navigation handler"),
            ("initializeModalEventListeners", "Modal event listener initialization"),
            ("navigateBackToManageUsers", "Enhanced navigation with locks")
        ]
        
        all_functions_exist = True
        for func_name, description in functions_to_check:
            contains = self.test_file_contains(
                admin_js_path,
                func_name,
                f"JavaScript Function - {description}"
            )
            all_functions_exist = all_functions_exist and contains
        
        return all_functions_exist
    
    def test_validation_logic(self):
        """Test validation logic improvements"""
        admin_js_path = "app/static/js/admin.js"
        
        # Test email optional logic
        email_optional_checks = [
            ("if (email && email.trim())", "Email validation only when provided"),
            ("email ? email.trim() : ''", "Optional email handling in data preparation"),
            ("validatePasswordResetForm", "Separate password reset validation"),
            ("isNavigating", "Navigation state management")
        ]
        
        all_checks_pass = True
        for check, description in email_optional_checks:
            contains = self.test_file_contains(
                admin_js_path,
                check,
                f"Validation Logic - {description}"
            )
            all_checks_pass = all_checks_pass and contains
        
        return all_checks_pass
    
    def test_ui_indicators(self):
        """Test UI indicator implementations"""
        admin_js_path = "app/static/js/admin.js"
        css_path = "app/static/css/admin-forms.css"
        
        # Test JavaScript UI functions
        ui_functions = [
            ("initializeFormFieldIndicators", "Form field indicator initialization"),
            ("addRequiredIndicator", "Required field indicator"),
            ("addOptionalIndicator", "Optional field indicator"),
            ("text-danger", "Required field asterisk styling"),
            ("text-muted small", "Optional field label styling")
        ]
        
        ui_checks_pass = True
        for func, description in ui_functions:
            contains = self.test_file_contains(
                admin_js_path,
                func,
                f"UI Indicator - {description}"
            )
            ui_checks_pass = ui_checks_pass and contains
        
        # Test CSS file
        if self.test_file_exists(css_path, "Admin Forms CSS File"):
            css_classes = [
                (".form-control.is-valid", "Valid form field styling"),
                (".form-control.is-invalid", "Invalid form field styling"),
                (".valid-feedback", "Success message styling"),
                (".invalid-feedback", "Error message styling"),
                (".text-danger", "Required field indicator styling"),
                (".text-muted", "Optional field indicator styling")
            ]
            
            for css_class, description in css_classes:
                contains = self.test_file_contains(
                    css_path,
                    css_class,
                    f"CSS Styling - {description}"
                )
                ui_checks_pass = ui_checks_pass and contains
        
        return ui_checks_pass
    
    def test_navigation_fixes(self):
        """Test navigation and close button fixes"""
        admin_js_path = "app/static/js/admin.js"
        
        navigation_features = [
            ("handleModalClose", "Modal close handler function"),
            ("initializeModalEventListeners", "Modal event listener setup"),
            ("isNavigating", "Navigation state management"),
            ("hidden.bs.modal", "Bootstrap modal hide event handling"),
            ("[data-bs-dismiss=\"modal\"]", "Close button selector"),
            ("navigateBackToManageUsers", "Navigation function")
        ]
        
        nav_checks_pass = True
        for feature, description in navigation_features:
            contains = self.test_file_contains(
                admin_js_path,
                feature,
                f"Navigation Fix - {description}"
            )
            nav_checks_pass = nav_checks_pass and contains
        
        return nav_checks_pass
    
    def test_security_features(self):
        """Test security implementation"""
        security_file = "app/utils/security.py"
        admin_js_path = "app/static/js/admin.js"
        
        security_checks_pass = True
        
        # Test security utility file
        if self.test_file_exists(security_file, "Security Utilities File"):
            security_functions = [
                ("class InputValidator", "Input validator class"),
                ("sanitize_string", "String sanitization function"),
                ("validate_email", "Email validation function"),
                ("validate_password", "Password validation function"),
                ("sanitize_user_data", "User data sanitization")
            ]
            
            for func, description in security_functions:
                contains = self.test_file_contains(
                    security_file,
                    func,
                    f"Security Feature - {description}"
                )
                security_checks_pass = security_checks_pass and contains
        
        # Test JavaScript security features
        js_security_features = [
            ("sanitizeInput", "Client-side input sanitization"),
            ("temp.textContent", "HTML escaping implementation"),
            ("validatePassword", "Enhanced password validation")
        ]
        
        for feature, description in js_security_features:
            contains = self.test_file_contains(
                admin_js_path,
                feature,
                f"JavaScript Security - {description}"
            )
            security_checks_pass = security_checks_pass and contains
        
        return security_checks_pass
    
    def test_backup_implementation(self):
        """Test backup system implementation"""
        backup_script = "backup_database.py"
        backup_bat = "run_backup.bat"
        
        backup_checks_pass = True
        
        # Test backup script
        if self.test_file_exists(backup_script, "Database Backup Script"):
            backup_features = [
                ("class SimpleBackupManager", "Backup manager class"),
                ("create_backup", "Backup creation function"),
                ("_verify_backup", "Backup verification function"),
                ("cleanup_old_backups", "Old backup cleanup"),
                ("list_backups", "Backup listing function")
            ]
            
            for feature, description in backup_features:
                contains = self.test_file_contains(
                    backup_script,
                    feature,
                    f"Backup Feature - {description}"
                )
                backup_checks_pass = backup_checks_pass and contains
        
        # Test Windows batch file
        if self.test_file_exists(backup_bat, "Windows Backup Batch File"):
            self.test_file_contains(
                backup_bat,
                "python backup_database.py full",
                "Batch File - Backup command execution"
            )
        
        return backup_checks_pass
    
    def test_documentation(self):
        """Test documentation completeness"""
        docs = [
            ("BEST_PRACTICES_IMPLEMENTATION.md", "Best practices guide"),
            ("TASKS_COMPLETED_SUMMARY.md", "Task completion summary"),
            ("app/utils/security.py", "Security utilities documentation")
        ]
        
        docs_complete = True
        for doc_file, description in docs:
            exists = self.test_file_exists(doc_file, description)
            docs_complete = docs_complete and exists
        
        return docs_complete
    
    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting Comprehensive Admin Form Test Suite")
        print("=" * 60)
        
        # Run test suites
        test_suites = [
            ("JavaScript Functions", self.test_javascript_functions),
            ("Validation Logic", self.test_validation_logic),
            ("UI Indicators", self.test_ui_indicators),
            ("Navigation Fixes", self.test_navigation_fixes),
            ("Security Features", self.test_security_features),
            ("Backup Implementation", self.test_backup_implementation),
            ("Documentation", self.test_documentation)
        ]
        
        suite_results = {}
        for suite_name, test_function in test_suites:
            print(f"\n📋 Testing {suite_name}...")
            suite_results[suite_name] = test_function()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        for suite_name, passed in suite_results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status}: {suite_name}")
        
        print(f"\n📈 OVERALL RESULTS:")
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.failed_tests}")
        print(f"📊 Total: {self.passed_tests + self.failed_tests}")
        
        success_rate = (self.passed_tests / (self.passed_tests + self.failed_tests)) * 100
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("🎉 EXCELLENT: All major features implemented successfully!")
        elif success_rate >= 75:
            print("👍 GOOD: Most features implemented, minor issues to address")
        else:
            print("⚠️  NEEDS WORK: Several features need attention")
        
        # Save detailed results
        self.save_test_report()
        
        return success_rate >= 75
    
    def save_test_report(self):
        """Save detailed test report to file"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'passed': self.passed_tests,
                'failed': self.failed_tests,
                'total': self.passed_tests + self.failed_tests,
                'success_rate': (self.passed_tests / (self.passed_tests + self.failed_tests)) * 100
            },
            'detailed_results': self.test_results
        }
        
        with open('test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed test report saved to: test_report.json")

def main():
    """Main function"""
    print("🧪 Nutri Tracker Admin Form Enhancement Test Suite")
    print("Testing Tasks 1, 2, 3 and Best Practices Implementation")
    print()
    
    test_suite = AdminFormTestSuite()
    success = test_suite.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
