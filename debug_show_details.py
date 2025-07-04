#!/usr/bin/env python3
"""
Debug test to check the show_details parameter processing.
"""

from app import create_app

def test_show_details_parameter():
    """Test how show_details parameter is processed."""
    app = create_app()
    
    with app.test_client() as client:
        print("=== Testing show_details Parameter Processing ===")
        
        # Test with show_details=1
        response = client.get('/admin/users?show_details=1')
        print(f"\n🔍 Request: /admin/users?show_details=1")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            content = response.get_data(as_text=True)
            
            # Check for checkbox state
            if 'checked' in content and 'showDetails' in content:
                print("   ✅ Checkbox should be checked")
            else:
                print("   ❌ Checkbox not checked")
            
            # Check for headers
            if '<th>Joined</th>' in content:
                print("   ✅ 'Joined' header found")
            else:
                print("   ❌ 'Joined' header NOT found")
                
            if '<th>Last Login</th>' in content:
                print("   ✅ 'Last Login' header found")
            else:
                print("   ❌ 'Last Login' header NOT found")
        
        # Test without show_details
        response = client.get('/admin/users')
        print(f"\n🔍 Request: /admin/users (no show_details)")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            content = response.get_data(as_text=True)
            
            # Check for checkbox state
            if 'checked' not in content or 'showDetails' not in content:
                print("   ✅ Checkbox should NOT be checked")
            else:
                print("   ❌ Checkbox incorrectly checked")
            
            # Check for headers
            if '<th>Joined</th>' not in content:
                print("   ✅ 'Joined' header correctly hidden")
            else:
                print("   ❌ 'Joined' header incorrectly shown")
                
            if '<th>Last Login</th>' not in content:
                print("   ✅ 'Last Login' header correctly hidden")
            else:
                print("   ❌ 'Last Login' header incorrectly shown")

if __name__ == "__main__":
    test_show_details_parameter()
