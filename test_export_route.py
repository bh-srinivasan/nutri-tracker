#!/usr/bin/env python3
"""
Test script to verify the export_foods route is accessible
"""

from app import create_app
from flask import url_for

def test_export_foods_route():
    """Test that the export_foods route is properly registered"""
    app = create_app()
    
    with app.app_context():
        try:
            # Test if the route can be generated
            url = url_for('admin.export_foods')
            print(f"✅ Route 'admin.export_foods' is accessible: {url}")
            return True
        except Exception as e:
            print(f"❌ Route 'admin.export_foods' failed: {e}")
            return False

def list_admin_routes():
    """List all available admin routes"""
    app = create_app()
    
    print("\n📋 Available admin routes:")
    with app.app_context():
        for rule in app.url_map.iter_rules():
            if rule.endpoint and rule.endpoint.startswith('admin.'):
                print(f"  - {rule.endpoint}: {rule.rule}")

if __name__ == "__main__":
    print("Testing export_foods route...")
    print("=" * 50)
    
    success = test_export_foods_route()
    list_admin_routes()
    
    if success:
        print("\n🎉 Route test passed! The admin.export_foods route is working.")
    else:
        print("\n⚠️ Route test failed. Check the route definition.")
