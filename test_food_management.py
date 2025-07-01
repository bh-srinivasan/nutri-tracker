#!/usr/bin/env python3
"""
Test script to verify pagination and sorting fixes in admin food management.
"""
import requests
from bs4 import BeautifulSoup
import re


def extract_csrf_token(html_content):
    """Extract CSRF token from HTML form."""
    soup = BeautifulSoup(html_content, 'html.parser')
    csrf_input = soup.find('input', {'name': 'csrf_token'})
    if csrf_input:
        return csrf_input.get('value')
    return None


def login_as_admin(session, base_url):
    """Login as admin and return success status."""
    login_url = f"{base_url}/auth/login"
    response = session.get(login_url)
    
    if response.status_code != 200:
        return False
    
    csrf_token = extract_csrf_token(response.text)
    if not csrf_token:
        return False
    
    login_data = {
        'username': 'admin',
        'password': 'admin123',
        'csrf_token': csrf_token
    }
    
    response = session.post(login_url, data=login_data, allow_redirects=False)
    return response.status_code == 302


def test_pagination_urls(html_content):
    """Test if pagination URLs are correctly generated without duplicate 'page' parameters."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all pagination links
    pagination_links = soup.find_all('a', {'class': 'page-link'})
    
    issues = []
    valid_links = 0
    
    for link in pagination_links:
        href = link.get('href', '')
        if href:
            # Count how many times 'page=' appears in the URL
            page_count = href.count('page=')
            if page_count > 1:
                issues.append(f"Duplicate 'page' parameter in URL: {href}")
            elif page_count == 1:
                valid_links += 1
    
    return {
        'valid_links': valid_links,
        'issues': issues,
        'total_pagination_links': len(pagination_links)
    }


def test_food_sorting(html_content):
    """Test if foods are sorted in ascending order."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all table rows with food data
    food_rows = soup.find_all('tr')[1:]  # Skip header row
    
    if not food_rows:
        return {'status': 'no_data', 'ids': []}
    
    # Extract food IDs from the first column
    food_ids = []
    for row in food_rows:
        cells = row.find_all('td')
        if cells:
            id_cell = cells[0].get_text().strip()
            try:
                food_id = int(id_cell)
                food_ids.append(food_id)
            except ValueError:
                continue
    
    # Check if IDs are in ascending order
    is_ascending = food_ids == sorted(food_ids)
    
    return {
        'status': 'success',
        'ids': food_ids,
        'is_ascending': is_ascending,
        'first_few': food_ids[:5] if len(food_ids) >= 5 else food_ids
    }


def main():
    """Test pagination and sorting fixes."""
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
    
    # Test admin foods page pagination URLs
    print("\n=== Testing Food Management Pagination URLs ===")
    foods_response = session.get(f"{base_url}/admin/foods")
    
    if foods_response.status_code == 200:
        print("✓ Foods page loads successfully")
        
        # Test pagination URL generation
        pagination_test = test_pagination_urls(foods_response.text)
        
        if pagination_test['issues']:
            print(f"✗ Found {len(pagination_test['issues'])} pagination URL issues:")
            for issue in pagination_test['issues']:
                print(f"   - {issue}")
        else:
            print("✓ No duplicate 'page' parameter issues found")
        
        print(f"✓ Found {pagination_test['valid_links']} valid pagination links")
        print(f"✓ Total pagination links: {pagination_test['total_pagination_links']}")
        
        # Test food sorting
        sorting_test = test_food_sorting(foods_response.text)
        
        if sorting_test['status'] == 'no_data':
            print("⚠ No food data found to test sorting")
        else:
            if sorting_test['is_ascending']:
                print("✓ Foods are sorted in ascending order")
                print(f"✓ First few IDs: {sorting_test['first_few']}")
            else:
                print("✗ Foods are NOT sorted in ascending order")
                print(f"✗ Current order: {sorting_test['first_few']}")
    else:
        print(f"✗ Foods page failed to load (status: {foods_response.status_code})")
    
    # Test pagination navigation by trying to access page 2
    print("\n=== Testing Pagination Navigation ===")
    page2_response = session.get(f"{base_url}/admin/foods?page=2")
    
    if page2_response.status_code == 200:
        print("✓ Page 2 loads successfully")
        
        # Check if pagination URLs on page 2 are also correct
        page2_pagination_test = test_pagination_urls(page2_response.text)
        
        if page2_pagination_test['issues']:
            print(f"✗ Found issues on page 2: {len(page2_pagination_test['issues'])}")
        else:
            print("✓ Page 2 pagination URLs are correct")
    else:
        print(f"⚠ Page 2 not accessible (status: {page2_response.status_code}) - might be normal if there's only one page")
    
    # Test with search and pagination
    print("\n=== Testing Search + Pagination ===")
    search_response = session.get(f"{base_url}/admin/foods?search=rice&page=1")
    
    if search_response.status_code == 200:
        print("✓ Search with pagination works")
        
        search_pagination_test = test_pagination_urls(search_response.text)
        
        if search_pagination_test['issues']:
            print(f"✗ Found pagination issues in search results")
        else:
            print("✓ Search result pagination URLs are correct")
    else:
        print(f"✗ Search with pagination failed (status: {search_response.status_code})")
    
    print("\n=== Food Management Tests Complete ===")
    return True


if __name__ == "__main__":
    main()
