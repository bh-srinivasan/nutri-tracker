"""
Test script to debug the Upload History tab error
"""
import requests
import json

def test_upload_history_error():
    """Test the upload history tab specifically."""
    base_url = "http://localhost:5001"
    
    print("🔍 Testing Upload History Tab Error")
    print("=" * 50)
    
    # Test with admin login simulation
    session = requests.Session()
    
    # Test 1: Try accessing with tab=history parameter
    try:
        print("1. Testing /admin/food-uploads?tab=history")
        response = session.get(f"{base_url}/admin/food-uploads?tab=history", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 302:
            print(f"   Redirect to: {response.headers.get('Location', 'Unknown')}")
        elif response.status_code == 500:
            print("   ❌ Server Error (500) - Internal Server Error")
            print("   This is likely the source of the error!")
        elif response.status_code == 200:
            print("   ✅ Page loads successfully")
        else:
            print(f"   ⚠️  Unexpected status: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
    
    # Test 2: Try the base route without tab parameter
    try:
        print("\n2. Testing /admin/food-uploads (base route)")
        response = session.get(f"{base_url}/admin/food-uploads", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 302:
            print(f"   Redirect to: {response.headers.get('Location', 'Unknown')}")
        elif response.status_code == 500:
            print("   ❌ Server Error (500) - Internal Server Error")
        elif response.status_code == 200:
            print("   ✅ Page loads successfully")
        else:
            print(f"   ⚠️  Unexpected status: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
    
    # Test 3: Check if it's a JavaScript error by examining the HTML
    try:
        print("\n3. Testing for JavaScript errors in response")
        response = session.get(f"{base_url}/admin/food-uploads", allow_redirects=True, timeout=10)
        
        if response.status_code == 200:
            content = response.text
            
            # Check for common error indicators
            if "Error loading food uploads page" in content:
                print("   ❌ Error message found in HTML content")
            elif "food_uploads.html" in content or "Food Uploads" in content:
                print("   ✅ Page seems to load correctly")
            else:
                print("   ⚠️  Unexpected content or login page")
                
        else:
            print(f"   Status: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Next Steps:")
    print("1. Check server logs for detailed error messages")
    print("2. Verify the route is properly defined in routes.py")
    print("3. Check for missing imports or template issues")
    print("4. Test with proper admin authentication")

if __name__ == "__main__":
    test_upload_history_error()
