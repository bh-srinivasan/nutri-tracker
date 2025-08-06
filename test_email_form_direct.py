#!/usr/bin/env python3
"""
Simple test to verify email field is optional - direct form testing
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.auth.forms import ProfileForm

def test_form_validation():
    """Test ProfileForm validation directly"""
    print("🔍 Testing ProfileForm Email Validation Directly")
    print("=" * 50)
    
    app = create_app()
    
    with app.app_context():
        # Test 1: Empty email should be valid
        print("\n📋 Test 1: Empty email validation")
        form_data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': '',  # Empty email
            'csrf_token': 'dummy_token'
        }
        
        form = ProfileForm('testuser', '', data=form_data)
        form.csrf_token.data = 'dummy_token'  # Bypass CSRF for testing
        
        # Manually validate (skip CSRF)
        form.csrf_token = None
        is_valid = form.validate()
        
        print(f"   Form valid with empty email: {is_valid}")
        if form.errors:
            print(f"   Form errors: {form.errors}")
        
        # Test 2: Valid email should be valid
        print("\n📧 Test 2: Valid email validation")
        form_data['email'] = 'test@example.com'
        
        form = ProfileForm('testuser', '', data=form_data)
        form.csrf_token = None
        is_valid = form.validate()
        
        print(f"   Form valid with valid email: {is_valid}")
        if form.errors:
            print(f"   Form errors: {form.errors}")
        
        # Test 3: Invalid email should be invalid
        print("\n❌ Test 3: Invalid email validation")
        form_data['email'] = 'invalid-email'
        
        form = ProfileForm('testuser', '', data=form_data)
        form.csrf_token = None
        is_valid = form.validate()
        
        print(f"   Form valid with invalid email: {is_valid}")
        if form.errors:
            print(f"   Form errors: {form.errors}")
        
        # Test 4: Whitespace only email should be valid (treated as empty)
        print("\n⚪ Test 4: Whitespace only email validation")
        form_data['email'] = '   '
        
        form = ProfileForm('testuser', '', data=form_data)
        form.csrf_token = None
        is_valid = form.validate()
        
        print(f"   Form valid with whitespace email: {is_valid}")
        if form.errors:
            print(f"   Form errors: {form.errors}")
        
        print("\n" + "=" * 50)
        print("✅ Direct form validation testing completed")

if __name__ == "__main__":
    test_form_validation()
