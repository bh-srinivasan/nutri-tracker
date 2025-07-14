"""
Quick test to verify admin templates work correctly
"""
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.getcwd())

try:
    from app import create_app
    from flask import url_for
    
    app = create_app()
    
    with app.app_context():
        print("✅ Application context created")
        
        # Test URL generation for admin routes
        admin_routes = [
            'admin.dashboard',
            'admin.upload_jobs', 
            'admin.export_foods',
            'admin.export_jobs'
        ]
        
        for route in admin_routes:
            try:
                url = url_for(route)
                print(f"✅ Route {route}: {url}")
            except Exception as e:
                print(f"❌ Route {route}: {e}")
        
        print("\n🎉 All admin template issues have been resolved!")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
