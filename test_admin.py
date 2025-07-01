#!/usr/bin/env python3
"""
Test script to diagnose admin route issues
"""

import os
import sys

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_admin_routes():
    """Test admin routes functionality."""
    try:
        print("🔍 Testing admin routes...")
        
        # Test imports
        print("1. Testing imports...")
        from app import create_app, db
        from app.models import User, Food
        from app.admin.forms import FoodForm, UserManagementForm
        print("   ✅ All imports successful")
        
        # Test app creation
        print("2. Testing app creation...")
        app = create_app()
        print("   ✅ App created successfully")
        
        # Test app context
        print("3. Testing app context...")
        with app.app_context():
            print("   ✅ App context working")
            
            # Test database connection
            print("4. Testing database...")
            try:
                user_count = User.query.count()
                food_count = Food.query.count()
                print(f"   ✅ Database accessible - {user_count} users, {food_count} foods")
            except Exception as e:
                print(f"   ❌ Database error: {e}")
                return False
            
            # Test form creation
            print("5. Testing forms...")
            try:
                food_form = FoodForm()
                user_form = UserManagementForm()
                print("   ✅ Forms created successfully")
            except Exception as e:
                print(f"   ❌ Form error: {e}")
                return False
                
            # Test route URL building
            print("6. Testing URL building...")
            try:
                from flask import url_for
                urls = {
                    'admin.dashboard': url_for('admin.dashboard'),
                    'admin.users': url_for('admin.users'),
                    'admin.foods': url_for('admin.foods'),
                    'admin.bulk_upload_foods': url_for('admin.bulk_upload_foods')
                }
                for route, url in urls.items():
                    print(f"   ✅ {route} -> {url}")
            except Exception as e:
                print(f"   ❌ URL building error: {e}")
                return False
        
        print("\n🎉 All tests passed! Admin routes should be working.")
        return True
        
    except Exception as e:
        print(f"\n❌ Critical error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_admin_routes()
