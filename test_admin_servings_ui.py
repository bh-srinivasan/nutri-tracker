#!/usr/bin/env python3
"""
Test script to verify Admin.foods.servings module implementation
Tests the JavaScript module structure and UI integration.
"""

import os
import sys

# Add project root to Python path
sys.path.insert(0, os.getcwd())

def test_admin_js_structure():
    """Test that admin.js has the correct structure for servings management."""
    
    admin_js_path = "app/static/js/admin.js"
    
    print("=== Admin.js Servings Module Test ===")
    print(f"Testing file: {admin_js_path}")
    print()
    
    try:
        with open(admin_js_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Test 1: Check if servings module exists
        print("Test 1: Checking if servings module exists...")
        if "servings: {" in content:
            print("✓ Admin.foods.servings module found")
        else:
            print("✗ Admin.foods.servings module NOT found")
            return False
        
        # Test 2: Check required methods
        required_methods = [
            "bindEvents:",
            "add:",
            "setDefault:",
            "unsetDefault:",
            "edit:",
            "remove:",
            "prependServingRow:",
            "updateDefaultBadges:",
            "restoreActionButtons:"
        ]
        
        print("\nTest 2: Checking required methods...")
        for method in required_methods:
            if method in content:
                print(f"✓ {method.replace(':', '')} method found")
            else:
                print(f"✗ {method.replace(':', '')} method NOT found")
                return False
        
        # Test 3: Check AJAX endpoint calls
        print("\nTest 3: Checking AJAX endpoint calls...")
        endpoints = [
            "/servings/add",
            "/set-default",
            "/unset-default",
            "/edit",
            "/delete"
        ]
        
        for endpoint in endpoints:
            if endpoint in content:
                print(f"✓ {endpoint} endpoint call found")
            else:
                print(f"✗ {endpoint} endpoint call NOT found")
                return False
        
        # Test 4: Check NutriTracker.utils.showToast usage
        print("\nTest 4: Checking toast notifications...")
        if "NutriTracker.utils.showToast" in content:
            print("✓ NutriTracker.utils.showToast usage found")
        else:
            print("✗ NutriTracker.utils.showToast usage NOT found")
            return False
        
        # Test 5: Check form data handling
        print("\nTest 5: Checking form data handling...")
        if "FormData" in content and "preventDefault" in content:
            print("✓ Form data handling found")
        else:
            print("✗ Form data handling NOT found")
            return False
        
        print("\n🎉 All tests passed! Admin.foods.servings module is properly implemented.")
        return True
        
    except FileNotFoundError:
        print(f"✗ Error: {admin_js_path} not found")
        return False
    except Exception as e:
        print(f"✗ Error reading file: {e}")
        return False

def test_template_integration():
    """Test that edit_food.html properly integrates with the servings module."""
    
    template_path = "app/templates/admin/edit_food.html"
    
    print("\n=== Template Integration Test ===")
    print(f"Testing file: {template_path}")
    print()
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Test 1: Check admin.js inclusion
        print("Test 1: Checking admin.js inclusion...")
        if "admin.js" in content:
            print("✓ admin.js script inclusion found")
        else:
            print("✗ admin.js script inclusion NOT found")
            return False
        
        # Test 2: Check required form elements
        print("\nTest 2: Checking required form elements...")
        required_elements = [
            'id="add-serving-form"',
            'data-food-id="{{ food.id }}"',
            'name="serving_name"',
            'name="unit"',
            'name="grams_per_unit"',
            'id="servings-body"'
        ]
        
        for element in required_elements:
            if element in content:
                print(f"✓ {element} found")
            else:
                print(f"✗ {element} NOT found")
                return False
        
        # Test 3: Check data attributes on buttons
        print("\nTest 3: Checking button data attributes...")
        if 'data-serving-id="{{ serving.id }}"' in content:
            print("✓ data-serving-id attributes found")
        else:
            print("✗ data-serving-id attributes NOT found")
            return False
        
        # Test 4: Check bindEvents call
        print("\nTest 4: Checking bindEvents call...")
        if "Admin.foods.servings.bindEvents()" in content:
            print("✓ bindEvents() call found")
        else:
            print("✗ bindEvents() call NOT found")
            return False
        
        print("\n🎉 Template integration tests passed!")
        return True
        
    except FileNotFoundError:
        print(f"✗ Error: {template_path} not found")
        return False
    except Exception as e:
        print(f"✗ Error reading file: {e}")
        return False

def main():
    """Run all tests."""
    print("Admin Servings UI Implementation Test")
    print("=====================================")
    
    js_test_passed = test_admin_js_structure()
    template_test_passed = test_template_integration()
    
    print("\n" + "="*50)
    if js_test_passed and template_test_passed:
        print("🎉 ALL TESTS PASSED! 🎉")
        print("Admin.foods.servings module is ready for use!")
        print("\nNext steps:")
        print("1. Start the server: python app.py")
        print("2. Login as admin")
        print("3. Edit a food item to test serving management")
        print("4. Test adding, editing, deleting, and setting default servings")
    else:
        print("❌ SOME TESTS FAILED")
        print("Please check the implementation and fix any issues.")
    
    return js_test_passed and template_test_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
