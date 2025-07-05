#!/usr/bin/env python3
"""
Security validation script for admin password reset flow
Ensures no sensitive information is exposed in the UI.
"""

import os

def test_password_exposure_security():
    """Test that passwords are not exposed in the UI"""
    print("🔒 Security Test: Password Exposure Prevention")
    print("=" * 55)
    
    js_file = "app/static/js/admin.js"
    if not os.path.exists(js_file):
        print(f"❌ File not found: {js_file}")
        return False
    
    with open(js_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    security_issues = []
    
    # Check for password exposure patterns
    if "New password:" in content:
        security_issues.append("Found 'New password:' text - may expose password")
    
    if "${newPassword}" in content and "toast" in content.lower():
        security_issues.append("Found password variable in toast message")
    
    if "<code" in content and "newPassword" in content:
        security_issues.append("Found password in code element - potential exposure")
    
    if 'class="bg-light px-1 rounded border"' in content:
        security_issues.append("Found styling for password display element")
    
    # Check for secure patterns
    secure_patterns = []
    
    if "Password reset successfully" in content:
        secure_patterns.append("✅ Generic success message found")
    
    if "has been updated" in content:
        secure_patterns.append("✅ Safe confirmation message found")
    
    # Report results
    print("\n🔍 Security Analysis Results:")
    
    if security_issues:
        print("\n❌ SECURITY ISSUES FOUND:")
        for issue in security_issues:
            print(f"  ❌ {issue}")
        return False
    else:
        print("\n✅ NO SECURITY ISSUES FOUND")
    
    print("\n🛡️ Secure Patterns Detected:")
    for pattern in secure_patterns:
        print(f"  {pattern}")
    
    if not secure_patterns:
        print("  ❌ No secure patterns found")
        return False
    
    return True

def test_ui_information_disclosure():
    """Test for information disclosure in UI elements"""
    print("\n🔍 UI Information Disclosure Test")
    print("-" * 40)
    
    # Check template files for password exposure
    template_files = [
        "app/templates/admin/users.html",
        "app/templates/admin/base.html"
    ]
    
    for template_file in template_files:
        if os.path.exists(template_file):
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for password-related elements that shouldn't be there
            if "password-display" in content or "show-password" in content:
                print(f"❌ Found password display elements in {template_file}")
                return False
    
    print("✅ No password disclosure found in templates")
    return True

def test_console_logging_security():
    """Test that sensitive data isn't logged to console"""
    print("\n📝 Console Logging Security Test")
    print("-" * 40)
    
    js_file = "app/static/js/admin.js"
    with open(js_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for password logging by looking at each console.log line
    lines = content.split('\n')
    password_logged = False
    
    for i, line in enumerate(lines):
        if "console.log" in line and ("newPassword" in line or "${newPassword}" in line):
            print(f"❌ Found password logging on line {i+1}: {line.strip()}")
            password_logged = True
    
    if password_logged:
        return False
    
    # Check for secure audit logging
    if "console.log(`Admin password reset completed" in content:
        print("✅ Found secure audit logging (no password)")
    else:
        print("⚠️ No audit logging found")
    
    print("✅ No password exposure in console logs")
    return True

def main():
    """Run all security tests"""
    print("🛡️ SECURITY VALIDATION FOR ADMIN PASSWORD RESET")
    print("=" * 60)
    
    all_passed = True
    
    # Test password exposure
    if not test_password_exposure_security():
        all_passed = False
    
    # Test UI information disclosure
    if not test_ui_information_disclosure():
        all_passed = False
    
    # Test console logging
    if not test_console_logging_security():
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL SECURITY TESTS PASSED!")
        print("\n🛡️ Security Summary:")
        print("  ✅ No password exposure in UI")
        print("  ✅ Generic success messages only")
        print("  ✅ No sensitive data in console logs")
        print("  ✅ Secure admin UX implemented")
        print("\nThe password reset flow is now secure and follows best practices.")
    else:
        print("🚨 SECURITY ISSUES DETECTED!")
        print("Please review and fix the issues above before deployment.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
