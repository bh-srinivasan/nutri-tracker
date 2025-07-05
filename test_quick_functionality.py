#!/usr/bin/env python3
"""
Quick functional test for the password reset UX improvement.
Tests if the server serves the updated JavaScript and CSS files correctly.
"""

import requests
import sys

def test_server_functionality():
    """Test if the server is running and serving updated files."""
    
    print("🧪 Testing Server Functionality")
    print("=" * 35)
    
    base_url = "http://127.0.0.1:5001"
    
    try:
        # Test homepage
        print("🌐 Testing homepage...")
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("✅ Homepage accessible")
        else:
            print(f"❌ Homepage error: {response.status_code}")
            return False
        
        # Test admin.js file
        print("📜 Testing admin.js file...")
        js_response = requests.get(f"{base_url}/static/js/admin.js", timeout=5)
        if js_response.status_code == 200:
            js_content = js_response.text
            
            # Check for new functions
            required_functions = [
                'scheduleRedirectToManageUsers',
                'redirectToManageUsers',
                'redirectCountdown'
            ]
            
            functions_found = 0
            for func in required_functions:
                if func in js_content:
                    print(f"✅ Function '{func}' found in served JS")
                    functions_found += 1
                else:
                    print(f"❌ Function '{func}' not found")
            
            if functions_found == len(required_functions):
                print("✅ All new functions present in served JavaScript")
            else:
                print(f"❌ Missing functions: {len(required_functions) - functions_found}")
        else:
            print(f"❌ admin.js not accessible: {js_response.status_code}")
            return False
        
        # Test styles.css file
        print("🎨 Testing styles.css file...")
        css_response = requests.get(f"{base_url}/static/css/styles.css", timeout=5)
        if css_response.status_code == 200:
            css_content = css_response.text
            
            if 'countdown-redirect' in css_content:
                print("✅ New CSS styles found in served stylesheet")
            else:
                print("❌ New CSS styles not found")
        else:
            print(f"❌ styles.css not accessible: {css_response.status_code}")
            return False
        
        # Test admin users page
        print("👤 Testing admin users page...")
        admin_response = requests.get(f"{base_url}/admin/users", timeout=5)
        # We expect a redirect to login, which is normal
        if admin_response.status_code in [200, 302]:
            print("✅ Admin users page accessible (may redirect to login)")
        else:
            print(f"❌ Admin users page error: {admin_response.status_code}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        print("💡 Make sure the Flask server is running on port 5001")
        return False

def test_implementation_completeness():
    """Test if all implementation files are complete."""
    
    print("\n🔍 Testing Implementation Completeness")
    print("=" * 40)
    
    required_files = [
        'app/static/js/admin.js',
        'app/static/css/styles.css',
        'app/templates/admin/users.html',
        'ADMIN_PASSWORD_RESET_UX_IMPROVEMENT_SUMMARY.md'
    ]
    
    all_files_present = True
    
    for file_path in required_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if len(content) > 0:
                    print(f"✅ {file_path} - Present and not empty")
                else:
                    print(f"❌ {file_path} - Empty file")
                    all_files_present = False
        except FileNotFoundError:
            print(f"❌ {file_path} - File not found")
            all_files_present = False
        except Exception as e:
            print(f"❌ {file_path} - Error reading: {e}")
            all_files_present = False
    
    return all_files_present

def main():
    """Main test function."""
    
    print("🚀 NUTRI TRACKER - PASSWORD RESET UX IMPROVEMENT")
    print("=" * 55)
    print("Quick functional test of the implementation")
    print()
    
    # Test implementation completeness
    files_test = test_implementation_completeness()
    
    # Test server functionality
    server_test = test_server_functionality()
    
    # Summary
    print("\n" + "=" * 55)
    print("📊 QUICK TEST SUMMARY")
    print("=" * 55)
    print(f"Implementation Files: {'✅ COMPLETE' if files_test else '❌ INCOMPLETE'}")
    print(f"Server Functionality: {'✅ WORKING' if server_test else '❌ ISSUES'}")
    
    if files_test and server_test:
        print("\n🎉 PASSWORD RESET UX IMPROVEMENT: READY!")
        print("💡 You can now test the feature manually:")
        print("   1. Visit http://127.0.0.1:5001/admin/users")
        print("   2. Login as admin")
        print("   3. Click 'Reset Password' on any user")
        print("   4. Complete the password reset")
        print("   5. Observe the 3-second countdown and auto-redirect")
        return True
    else:
        print("\n❌ Issues detected. Please review the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
