#!/usr/bin/env python3
"""
Check the testuser details and verify session handling
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User

def check_testuser():
    """Check testuser details"""
    
    app = create_app()
    
    with app.app_context():
        # Get testuser
        testuser = User.query.filter_by(username='testuser').first()
        
        if not testuser:
            print("❌ Testuser not found!")
            return False
        
        print("✅ Testuser found:")
        print(f"   ID: {testuser.id}")
        print(f"   Username: {testuser.username}")
        print(f"   Email: {testuser.email}")
        print(f"   Is Admin: {testuser.is_admin}")
        print(f"   Is Active: {testuser.is_active}")
        print(f"   Created At: {testuser.created_at}")
        print(f"   Last Login: {testuser.last_login}")
        
        # Test password verification
        from werkzeug.security import check_password_hash
        password_valid = check_password_hash(testuser.password_hash, 'testpass123')
        print(f"   Password Valid: {password_valid}")
        
        return testuser.is_active and password_valid

if __name__ == "__main__":
    print("🔍 Checking testuser details...")
    check_testuser()
