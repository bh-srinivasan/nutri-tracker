#!/usr/bin/env python3

from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    print("=== User Database Check ===")
    users = User.query.all()
    print(f"Total users in database: {len(users)}")
    
    for user in users:
        print(f"ID: {user.id}")
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print(f"Is Admin: {user.is_admin}")
        print(f"Is Active: {user.is_active}")
        print(f"Created: {user.created_at}")
        print("-" * 30)
        
    # Create a test user if none exist or if admin doesn't exist
    admin_user = User.query.filter_by(username='admin').first()
    test_user = User.query.filter_by(username='testuser').first()
    
    if not admin_user:
        print("Creating admin user...")
        admin_user = User(
            username='admin',
            email='admin@example.com',
            is_admin=True,
            is_active=True
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        
    if not test_user:
        print("Creating test user...")
        test_user = User(
            username='testuser',
            email='test@example.com',
            is_admin=False,
            is_active=True
        )
        test_user.set_password('test123')
        db.session.add(test_user)
    
    try:
        db.session.commit()
        print("✅ Users created successfully!")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creating users: {e}")
        
    # Verify the users exist now
    print("\n=== Final User List ===")
    users = User.query.all()
    for user in users:
        print(f"Username: {user.username}, Admin: {user.is_admin}, Active: {user.is_active}")
