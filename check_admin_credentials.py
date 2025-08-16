#!/usr/bin/env python3
"""
Check admin user credentials
"""

from app import create_app, db
from app.models import User
from werkzeug.security import check_password_hash

app = create_app()

with app.app_context():
    admin_user = User.query.filter_by(username='admin').first()
    if admin_user:
        print(f'Admin user found:')
        print(f'  Username: {admin_user.username}')
        print(f'  Is Admin: {admin_user.is_admin}')
        print(f'  Is Active: {admin_user.is_active}')
        print(f'  Password Hash: {admin_user.password_hash[:50]}...')
        
        # Test password verification
        test_passwords = ['admin123', 'admin', 'password', 'admin1']
        for pwd in test_passwords:
            is_valid = check_password_hash(admin_user.password_hash, pwd)
            print(f'  Password "{pwd}": {"✅ Valid" if is_valid else "❌ Invalid"}')
    else:
        print('❌ No admin user found!')
        
        # List all users
        all_users = User.query.all()
        print(f'Found {len(all_users)} users:')
        for user in all_users:
            print(f'  - {user.username} (admin: {user.is_admin}, active: {user.is_active})')
