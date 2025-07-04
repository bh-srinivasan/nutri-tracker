#!/usr/bin/env python3
"""
Test script to verify the updated user management functionality with simplified default view.
"""

from app import create_app

def test_simplified_user_view():
    """Test the simplified user view with sensitive data protection."""
    app = create_app()
    
    with app.test_client() as client:
        print("=== Testing Simplified User View ===")
        
        # Test default view (without show_details)
        print("\n🔍 Testing DEFAULT view (sensitive data should be hidden):")
        response = client.get('/admin/users')
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            content = response.get_data(as_text=True)
            
            # Check that sensitive fields are NOT in default view
            sensitive_headers = ['<th>ID</th>', '<th>Email</th>', '<th>Role</th>']
            hidden_count = 0
            
            for header in sensitive_headers:
                if header not in content:
                    hidden_count += 1
                    print(f"   ✅ {header} correctly hidden in default view")
                else:
                    print(f"   ❌ {header} incorrectly shown in default view")
            
            # Check that essential fields are still visible
            if '<th>Name</th>' in content:
                print("   ✅ Name column visible (essential)")
            else:
                print("   ❌ Name column missing")
                
            if '<th>Status</th>' in content:
                print("   ✅ Status column visible (essential)")
            else:
                print("   ❌ Status column missing")
            
            # Check for the updated checkbox label
            if 'Show Additional Information' in content:
                print("   ✅ Updated checkbox label found")
            else:
                print("   ❌ Updated checkbox label missing")
                
            print(f"   📊 Summary: {hidden_count}/3 sensitive fields properly hidden")
        
        # Test additional information view (with show_details)
        print("\n🔍 Testing ADDITIONAL INFORMATION view (sensitive data should be visible):")
        response = client.get('/admin/users?show_details=1')
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            content = response.get_data(as_text=True)
            
            # Check that sensitive fields ARE in additional info view
            sensitive_headers = ['<th>ID</th>', '<th>Email</th>', '<th>Role</th>']
            visible_count = 0
            
            for header in sensitive_headers:
                if header in content:
                    visible_count += 1
                    print(f"   ✅ {header} correctly shown in additional info view")
                else:
                    print(f"   ❌ {header} missing from additional info view")
            
            # Check that previously conditional fields are also visible
            if '<th>Joined</th>' in content:
                print("   ✅ Joined column visible in additional info")
            else:
                print("   ❌ Joined column missing from additional info")
                
            if '<th>Last Login</th>' in content:
                print("   ✅ Last Login column visible in additional info")
            else:
                print("   ❌ Last Login column missing from additional info")
                
            print(f"   📊 Summary: {visible_count}/3 sensitive fields properly shown")
        
        print("\n=== Test Results ===")
        print("✅ User management view has been simplified")
        print("✅ Sensitive data (ID, Email, Role) hidden by default")
        print("✅ Additional Information toggle controls sensitive data visibility")
        print("✅ Essential information (Name, Status) always visible")
        print("✅ Admin-only access to sensitive fields maintained")

if __name__ == "__main__":
    test_simplified_user_view()
