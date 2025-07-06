#!/usr/bin/env python3
"""Simple test to verify User ID implementation basics"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models import User

def test_basic():
    print("Testing User ID generation...")
    
    # Test generate_user_id
    user_id = User.generate_user_id()
    print(f"Generated User ID: {user_id}")
    
    # Test validation
    result = User.validate_user_id(user_id)
    print(f"Validation result: {result}")
    
    # Test format validation
    valid_test = User.validate_user_id("test-user-123")
    print(f"Valid test: {valid_test}")
    
    invalid_test = User.validate_user_id("invalid@user")
    print(f"Invalid test: {invalid_test}")
    
    print("Basic tests completed!")

if __name__ == "__main__":
    test_basic()
