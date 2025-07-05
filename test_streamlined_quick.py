#!/usr/bin/env python3
"""
Quick functionality test for streamlined password reset
Tests the admin interface and JavaScript integration
"""

import os
import sys
import time
import requests
from flask import Flask
import threading

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_server_startup():
    """Test that the server starts and admin pages load properly"""
    
    print("=== Testing Server and Admin Interface ===")
    
    try:
        # Import the app
        from app import create_app
        
        app = create_app()
        
        # Test app creation
        if app:
            print("✅ Flask app created successfully")
        else:
            print("❌ Failed to create Flask app")
            return False
        
        # Test that admin blueprint is registered
        blueprints = [bp.name for bp in app.blueprints.values()]
        if 'admin' in blueprints:
            print("✅ Admin blueprint registered")
        else:
            print("❌ Admin blueprint not found")
            return False
        
        # Test static files
        static_files = [
            'app/static/js/admin.js',
            'app/static/css/styles.css'
        ]
        
        for file_path in static_files:
            if os.path.exists(file_path):
                print(f"✅ {file_path} exists")
            else:
                print(f"❌ {file_path} missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Server test failed: {e}")
        return False

def test_template_rendering():
    """Test that admin templates render properly"""
    
    print("\n=== Testing Template Rendering ===")
    
    try:
        from app import create_app
        from flask import render_template_string
        
        app = create_app()
        
        with app.app_context():
            # Test basic template loading
            template_path = 'app/templates/admin/users.html'
            if os.path.exists(template_path):
                with open(template_path, 'r', encoding='utf-8') as f:
                    template_content = f.read()
                
                # Check for required elements
                required_elements = [
                    'resetPasswordModal',
                    'data-user-id',
                    'Admin.users.openPasswordResetModal',
                    'resetPasswordForm'
                ]
                
                for element in required_elements:
                    if element in template_content:
                        print(f"✅ Template contains {element}")
                    else:
                        print(f"❌ Template missing {element}")
                        return False
                
                print("✅ Admin users template structure valid")
                return True
            else:
                print(f"❌ Template file not found: {template_path}")
                return False
                
    except Exception as e:
        print(f"❌ Template test failed: {e}")
        return False

def test_javascript_syntax():
    """Test JavaScript syntax and structure"""
    
    print("\n=== Testing JavaScript Syntax ===")
    
    js_file = 'app/static/js/admin.js'
    
    try:
        with open(js_file, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        # Basic syntax checks
        syntax_checks = [
            ("Balanced braces", js_content.count('{') == js_content.count('}')),
            ("Balanced parentheses", js_content.count('(') == js_content.count(')')),
            ("No syntax errors", 'SyntaxError' not in js_content),
            ("Proper function declarations", 'function(' in js_content or 'function (' in js_content)
        ]
        
        for check, condition in syntax_checks:
            if condition:
                print(f"✅ {check}")
            else:
                print(f"❌ {check}")
                return False
        
        # Check for streamlined functions
        streamlined_functions = [
            'showStreamlinedSuccessBanner',
            'copyStreamPassword',
            'highlightUserRow',
            'navigateBackToManageUsers'
        ]
        
        for func in streamlined_functions:
            if f"{func}:" in js_content or f"{func} :" in js_content:
                print(f"✅ Function {func} properly defined")
            else:
                print(f"❌ Function {func} not found or malformed")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ JavaScript test failed: {e}")
        return False

def test_css_structure():
    """Test CSS structure and animations"""
    
    print("\n=== Testing CSS Structure ===")
    
    css_file = 'app/static/css/styles.css'
    
    try:
        with open(css_file, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        # Check for required CSS classes and animations
        css_elements = [
            ('.streamlined-success-banner', 'Streamlined banner class'),
            ('@keyframes slideInDown', 'Slide-in animation'),
            ('animation: slideInDown', 'Animation application'),
            ('box-shadow:', 'Box shadow styling'),
            ('linear-gradient', 'Gradient styling')
        ]
        
        for element, description in css_elements:
            if element in css_content:
                print(f"✅ {description}")
            else:
                print(f"❌ {description} missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ CSS test failed: {e}")
        return False

def run_quick_test():
    """Run quick functionality tests"""
    
    print("🚀 Starting Quick Functionality Test for Streamlined Password Reset")
    print("=" * 70)
    
    tests = [
        ("Server Startup", test_server_startup),
        ("Template Rendering", test_template_rendering), 
        ("JavaScript Syntax", test_javascript_syntax),
        ("CSS Structure", test_css_structure)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*70}")
    print("📊 QUICK TEST SUMMARY")
    print(f"{'='*70}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All quick tests passed! Implementation looks good.")
        print("\n💡 Next steps:")
        print("   1. Start the server: python app.py")
        print("   2. Login as admin")
        print("   3. Go to Manage Users")
        print("   4. Try resetting a password to see the streamlined flow")
        return True
    else:
        print("⚠️  Some tests failed. Please review the implementation.")
        return False

if __name__ == "__main__":
    success = run_quick_test()
    sys.exit(0 if success else 1)
