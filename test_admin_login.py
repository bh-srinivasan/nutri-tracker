"""
Test script to access the food uploads page with admin authentication
"""
import requests
from requests.sessions import Session

def test_with_admin_login():
    """Test the food uploads page with proper admin authentication."""
    base_url = "http://localhost:5001"
    session = Session()
    
    print("🔐 Testing Food Uploads with Admin Authentication")
    print("=" * 60)
    
    try:
        # Step 1: Get the login page to get CSRF token if needed
        print("1. Getting login page...")
        login_page = session.get(f"{base_url}/auth/login")
        print(f"   Login page status: {login_page.status_code}")
        
        # Step 2: Try to login as admin
        print("2. Attempting admin login...")
        login_data = {
            'username': 'admin',
            'password': 'admin123',  # Default admin password
            'submit': 'Sign In'
        }
        
        login_response = session.post(f"{base_url}/auth/login", data=login_data, allow_redirects=False)
        print(f"   Login response status: {login_response.status_code}")
        
        if login_response.status_code == 302:
            redirect_location = login_response.headers.get('Location', '')
            print(f"   Redirected to: {redirect_location}")
            
            # Step 3: Follow redirect and check if we're logged in
            dashboard_response = session.get(f"{base_url}{redirect_location}", allow_redirects=True)
            print(f"   Dashboard access status: {dashboard_response.status_code}")
            
            if dashboard_response.status_code == 200:
                print("   ✅ Successfully logged in as admin")
                
                # Step 4: Now try to access food uploads
                print("3. Accessing food uploads page...")
                uploads_response = session.get(f"{base_url}/admin/food-uploads")
                print(f"   Food uploads status: {uploads_response.status_code}")
                
                if uploads_response.status_code == 200:
                    print("   ✅ Food uploads page loads successfully")
                    
                    # Check if it contains the expected content
                    content = uploads_response.text
                    if "Food Uploads" in content and "Upload Food Data" in content:
                        print("   ✅ Page contains expected content")
                    else:
                        print("   ⚠️  Page loads but missing expected content")
                        print(f"   Content length: {len(content)} characters")
                        
                elif uploads_response.status_code == 500:
                    print("   ❌ Internal Server Error (500)")
                    print("   Check server logs for detailed error information")
                else:
                    print(f"   ❌ Unexpected status: {uploads_response.status_code}")
                
                # Step 5: Test with tab=history parameter
                print("4. Testing Upload History tab...")
                history_response = session.get(f"{base_url}/admin/food-uploads?tab=history")
                print(f"   History tab status: {history_response.status_code}")
                
                if history_response.status_code == 200:
                    print("   ✅ Upload History tab loads successfully")
                elif history_response.status_code == 500:
                    print("   ❌ Upload History tab causes Internal Server Error")
                    print("   This is likely where the error occurs!")
                else:
                    print(f"   ❌ Unexpected status: {history_response.status_code}")
                    
            else:
                print("   ❌ Failed to access dashboard after login")
        else:
            print("   ❌ Login failed")
            print(f"   Response: {login_response.text[:200]}...")
            
    except Exception as e:
        print(f"   ❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Summary:")
    print("- If login succeeds but food uploads fails, check server logs")
    print("- Look for template rendering errors or missing variables")
    print("- Check if BulkUploadJob model is properly imported")

if __name__ == "__main__":
    test_with_admin_login()
