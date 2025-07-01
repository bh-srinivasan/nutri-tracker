#!/usr/bin/env python3
"""
Comprehensive test script to verify admin functionality with authentication.
"""
import requests
import sys
from bs4 import BeautifulSoup


def extract_csrf_token(html_content):
    """Extract CSRF token from HTML form."""
    soup = BeautifulSoup(html_content, 'html.parser')
    csrf_input = soup.find('input', {'name': 'csrf_token'})
    if csrf_input:
        return csrf_input.get('value')
    return None


def login_as_admin(session, base_url):
    """Attempt to login as admin."""
    print("=== Testing Admin Login ===")
    
    # Get login page
    login_url = f"{base_url}/auth/login"
    response = session.get(login_url)
    
    if response.status_code != 200:
        print(f"✗ Failed to get login page (status: {response.status_code})")
        return False
    
    # Extract CSRF token
    csrf_token = extract_csrf_token(response.text)
    if not csrf_token:
        print("✗ Could not find CSRF token in login form")
        return False
    
    # Try login with admin credentials
    login_data = {
        'username': 'admin',
        'password': 'admin123',
        'csrf_token': csrf_token
    }
    
    response = session.post(login_url, data=login_data, allow_redirects=False)
    
    if response.status_code == 302:
        print("✓ Login successful (redirected)")
        return True
    else:
        print(f"⚠ Login attempt returned status {response.status_code}")
        print("This might be expected if admin user doesn't exist or password is different")
        return False


def test_admin_pages(session, base_url):
    """Test admin pages after login."""
    print("\n=== Testing Admin Pages (Authenticated) ===")
    
    admin_routes = [
        ("/admin/", "Admin dashboard"),
        ("/admin/users", "Manage users"),
        ("/admin/foods", "Manage foods"),
        ("/admin/foods/add", "Add food"),
        ("/admin/foods/bulk-upload", "Bulk upload"),
    ]
    
    success_count = 0
    for route, name in admin_routes:
        try:
            response = session.get(f"{base_url}{route}")
            if response.status_code == 200:
                print(f"✓ {name}: OK (status: {response.status_code})")
                success_count += 1
            elif response.status_code in [302, 301]:
                print(f"⚠ {name}: Redirected (status: {response.status_code})")
            else:
                print(f"✗ {name}: Error (status: {response.status_code})")
        except Exception as e:
            print(f"✗ {name}: Exception - {str(e)}")
    
    return success_count


def test_food_search_api(session, base_url):
    """Test the food search API endpoint."""
    print("\n=== Testing Food Search API ===")
    
    try:
        search_url = f"{base_url}/api/foods/search"
        response = session.get(search_url, params={'q': 'rice'})
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✓ Food search API works (found {len(data)} results)")
                return True
            except:
                print("✗ Food search API returned invalid JSON")
                return False
        else:
            print(f"✗ Food search API failed (status: {response.status_code})")
            return False
    except Exception as e:
        print(f"✗ Food search API exception: {str(e)}")
        return False


def main():
    """Main test function."""
    base_url = "http://127.0.0.1:5001"
    
    # Test if server is running
    try:
        response = requests.get(base_url, timeout=5)
        print(f"✓ Server is running (status: {response.status_code})")
    except Exception as e:
        print(f"✗ Cannot connect to server: {e}")
        return False
    
    # Create session for testing
    session = requests.Session()
    
    # Test login
    login_success = login_as_admin(session, base_url)
    
    # Test admin pages
    if login_success:
        success_count = test_admin_pages(session, base_url)
        test_food_search_api(session, base_url)
        
        print(f"\n=== Summary ===")
        print(f"Successfully accessed {success_count} admin pages")
    else:
        print("\n⚠ Could not test admin functionality due to login failure")
        print("This is expected if admin user hasn't been created yet")
    
    # Test public routes regardless
    print("\n=== Testing Public API Routes ===")
    
    # Test some public endpoints
    public_routes = [
        ("/api/foods/search?q=rice", "Food search (public)"),
    ]
    
    for route, name in public_routes:
        try:
            response = session.get(f"{base_url}{route}")
            if response.status_code == 200:
                print(f"✓ {name}: OK")
            else:
                print(f"⚠ {name}: Status {response.status_code}")
        except Exception as e:
            print(f"✗ {name}: Exception - {str(e)}")
    
    print("\n=== All Tests Complete ===")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
