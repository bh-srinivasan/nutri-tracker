#!/usr/bin/env python3
"""
Check admin user details and test login
"""

from app import create_app
from werkzeug.security import check_password_hash

def check_admin_user():
    """Check admin user in database"""
    
    print("=== CHECKING ADMIN USER ===\n")
    
    app = create_app()
    
    with app.app_context():
        from app.models import User
        
        # Check if admin user exists
        admin_user = User.query.filter_by(username='admin').first()
        
        if admin_user:
            print(f"✅ Admin user found:")
            print(f"   Username: {admin_user.username}")
            print(f"   Email: {admin_user.email}")
            print(f"   Is Admin: {admin_user.is_admin}")
            print(f"   Is Active: {admin_user.is_active}")
            print(f"   Password Hash: {admin_user.password_hash[:20]}...")
            
            # Test password verification
            test_passwords = ['admin', 'password', 'admin123', '']
            
            print(f"\n🔍 Testing passwords:")
            for pwd in test_passwords:
                if admin_user.password_hash:
                    result = check_password_hash(admin_user.password_hash, pwd)
                    print(f"   '{pwd}': {'✅ CORRECT' if result else '❌ wrong'}")
                else:
                    print(f"   No password hash set!")
                    
        else:
            print("❌ Admin user not found!")
            
            # Check all users
            all_users = User.query.all()
            print(f"\nAll users in database ({len(all_users)}):")
            for user in all_users:
                print(f"   {user.username} - admin: {user.is_admin} - active: {user.is_active}")

if __name__ == "__main__":
    check_admin_user()
