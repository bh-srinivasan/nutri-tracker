#!/usr/bin/env python3
"""
Test script to specifically verify pagination fixes in admin users and foods pages.
"""
import requests
from bs4 import BeautifulSoup


def extract_csrf_token(html_content):
    """Extract CSRF token from HTML form."""
    soup = BeautifulSoup(html_content, 'html.parser')
    csrf_input = soup.find('input', {'name': 'csrf_token'})
    if csrf_input:
        return csrf_input.get('value')
    return None


def login_as_admin(session, base_url):
    """Login as admin and return success status."""
    # Get login page
    login_url = f"{base_url}/auth/login"
    response = session.get(login_url)
    
    if response.status_code != 200:
        return False
    
    # Extract CSRF token
    csrf_token = extract_csrf_token(response.text)
    if not csrf_token:
        return False
    
    # Try login
    login_data = {
        'username': 'admin',
        'password': 'admin123',
        'csrf_token': csrf_token
    }
    
    response = session.post(login_url, data=login_data, allow_redirects=False)
    return response.status_code == 302


def test_pagination_in_html(html_content, page_name):
    """Test if pagination is properly rendered in HTML."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Check for pagination elements
    pagination_nav = soup.find('nav', {'aria-label': f'{page_name} pagination'})
    pagination_ul = soup.find('ul', {'class': 'pagination'})
    
    # Check for error messages that might indicate pagination issues
    error_messages = soup.find_all('div', {'class': 'alert-danger'})
    pagination_errors = [msg for msg in error_messages if 'pagination' in msg.get_text().lower()]
    
    return {
        'has_pagination_nav': pagination_nav is not None,
        'has_pagination_ul': pagination_ul is not None,
        'pagination_errors': len(pagination_errors),
        'error_messages': [msg.get_text().strip() for msg in pagination_errors]
    }


def main():
    """Test pagination fixes."""
    base_url = "http://127.0.0.1:5001"
    
    # Test server connectivity
    try:
        response = requests.get(base_url, timeout=5)
        print(f"✓ Server is running (status: {response.status_code})")
    except Exception as e:
        print(f"✗ Cannot connect to server: {e}")
        return False
    
    # Create session and login
    session = requests.Session()
    
    if not login_as_admin(session, base_url):
        print("✗ Failed to login as admin")
        return False
    
    print("✓ Admin login successful")
    
    # Test admin users page
    print("\n=== Testing Admin Users Page Pagination ===")
    users_response = session.get(f"{base_url}/admin/users")
    
    if users_response.status_code == 200:
        print("✓ Users page loads successfully")
        pagination_test = test_pagination_in_html(users_response.text, "Users")
        
        if pagination_test['pagination_errors'] > 0:
            print(f"✗ Found {pagination_test['pagination_errors']} pagination errors:")
            for error in pagination_test['error_messages']:
                print(f"   - {error}")
        else:
            print("✓ No pagination errors found")
        
        print(f"✓ Pagination navigation present: {pagination_test['has_pagination_nav']}")
        print(f"✓ Pagination controls present: {pagination_test['has_pagination_ul']}")
    else:
        print(f"✗ Users page failed to load (status: {users_response.status_code})")
    
    # Test admin foods page
    print("\n=== Testing Admin Foods Page Pagination ===")
    foods_response = session.get(f"{base_url}/admin/foods")
    
    if foods_response.status_code == 200:
        print("✓ Foods page loads successfully")
        pagination_test = test_pagination_in_html(foods_response.text, "Foods")
        
        if pagination_test['pagination_errors'] > 0:
            print(f"✗ Found {pagination_test['pagination_errors']} pagination errors:")
            for error in pagination_test['error_messages']:
                print(f"   - {error}")
        else:
            print("✓ No pagination errors found")
        
        print(f"✓ Pagination navigation present: {pagination_test['has_pagination_nav']}")
        print(f"✓ Pagination controls present: {pagination_test['has_pagination_ul']}")
    else:
        print(f"✗ Foods page failed to load (status: {foods_response.status_code})")
    
    # Test with search parameters to trigger different pagination scenarios
    print("\n=== Testing Pagination with Search ===")
    users_search_response = session.get(f"{base_url}/admin/users?search=admin&page=1")
    foods_search_response = session.get(f"{base_url}/admin/foods?search=rice&page=1")
    
    print(f"✓ Users search with pagination: {users_search_response.status_code == 200}")
    print(f"✓ Foods search with pagination: {foods_search_response.status_code == 200}")
    
    print("\n=== Pagination Fix Tests Complete ===")
    return True


if __name__ == "__main__":
    main()
