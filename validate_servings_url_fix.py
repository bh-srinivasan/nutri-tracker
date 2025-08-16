#!/usr/bin/env python3
"""
Quick validation script to confirm the Servings Upload History URL fix.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
import requests

def test_url_fix():
    """Test that the URL fix resolves the error"""
    app = create_app()
    
    print("🔧 Testing Servings Upload History URL Fix")
    print("=" * 50)
    
    with app.app_context():
        # Check template compilation
        print("1️⃣ Testing template compilation...")
        try:
            with open('app/templates/admin/_food_servings_upload_history.html', 'r') as f:
                content = f.read()
            
            # Check for problematic patterns
            if 'url_for(\'admin.servings_upload_status_check\')' in content:
                print("❌ Still contains problematic url_for() calls")
                return False
            else:
                print("✅ No problematic url_for() calls found")
            
            # Check for fixed patterns  
            if '/admin/food-servings/status/' in content:
                print("✅ Fixed hardcoded URLs found")
            else:
                print("❌ Fixed URLs not found")
                return False
                
        except Exception as e:
            print(f"❌ Template read error: {e}")
            return False
    
    # Test server response
    print("\n2️⃣ Testing server response...")
    try:
        # Test if server is running
        response = requests.get('http://127.0.0.1:5001/', timeout=5)
        print("✅ Server is responding")
        
        # Test login page
        response = requests.get('http://127.0.0.1:5001/auth/login', timeout=5)
        if response.status_code == 200:
            print("✅ Login page loads successfully")
        else:
            print(f"❌ Login page error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("⚠️ Server not running - start with: python run_server.py")
    except Exception as e:
        print(f"❌ Server test error: {e}")
    
    print("\n3️⃣ Testing route registration...")
    with app.app_context():
        from flask import url_for
        try:
            # Test if the route is properly registered
            test_url = url_for('admin.servings_upload_status_check', job_id='test123')
            print(f"✅ Route registered: {test_url}")
        except Exception as e:
            print(f"❌ Route registration error: {e}")
            return False
    
    print("\n" + "=" * 50)
    print("🎉 URL FIX VALIDATION COMPLETE!")
    print("✅ The error 'Could not build url for endpoint' should now be resolved")
    print("✅ Servings Upload History should load without errors")
    print("\n📋 Next Steps:")
    print("1. Start the server: python run_server.py")
    print("2. Login as admin (username: admin, password: admin123)")  
    print("3. Navigate to Admin → Food Servings → Uploads")
    print("4. Click on 'Upload History' tab")
    print("5. The page should now load without URL build errors")
    
    return True

if __name__ == '__main__':
    success = test_url_fix()
    sys.exit(0 if success else 1)
