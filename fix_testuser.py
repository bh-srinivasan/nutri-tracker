#!/usr/bin/env python3
"""
Fix testuser password
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

def fix_testuser_password():
    """Fix testuser password"""
    
    app = create_app()
    
    with app.app_context():
        # Get testuser
        testuser = User.query.filter_by(username='testuser').first()
        
        if not testuser:
            print("❌ Testuser not found!")
            return False
        
        try:
            # Update password
            testuser.password_hash = generate_password_hash('testpass123')
            db.session.commit()
            
            print("✅ Testuser password updated successfully")
            print("   Username: testuser")
            print("   Password: testpass123")
            
            # Verify the fix
            from werkzeug.security import check_password_hash
            password_valid = check_password_hash(testuser.password_hash, 'testpass123')
            print(f"   Password verification: {password_valid}")
            
            return password_valid
            
        except Exception as e:
            print(f"❌ Error updating password: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    print("🔧 Fixing testuser password...")
    success = fix_testuser_password()
    
    if success:
        print("\n✅ Testuser password fixed!")
    else:
        print("\n❌ Failed to fix testuser password!")
