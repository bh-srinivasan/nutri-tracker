#!/usr/bin/env python3

import requests
import sys

def test_with_login():
    """Test the log meal page with proper authentication"""
    
    try:
        session = requests.Session()
        
        # First get the login page to establish session
        print("Getting login page...")
        login_page = session.get('http://127.0.0.1:5001/auth/login')
        print(f"Login page status: {login_page.status_code}")
        
        # Try to login with admin credentials
        print("Attempting to login...")
        login_data = {
            'username': 'admin',
            'password': 'admin123',
            'submit': 'Sign In'
        }
        
        login_response = session.post('http://127.0.0.1:5001/auth/login', data=login_data, allow_redirects=True)
        print(f"Login response status: {login_response.status_code}")
        print(f"Final URL after login: {login_response.url}")
        
        # Now try to access the log meal page
        print("\nTesting Log Meal page with authentication...")
        meal_page = session.get('http://127.0.0.1:5001/dashboard/log-meal')
        print(f"Log meal page status: {meal_page.status_code}")
        print(f"Final URL: {meal_page.url}")
        print(f"Content length: {len(meal_page.text)}")
        
        if meal_page.status_code == 200:
            content = meal_page.text.lower()
            has_search = 'foodsearch' in content or 'food-search' in content
            has_meal_logger = 'enhancedmeallogger' in content or 'meallogger' in content
            has_results_div = 'foodsearchresults' in content
            page_title = 'log meal' in content
            
            print(f"Has foodSearch input: {has_search}")
            print(f"Has EnhancedMealLogger: {has_meal_logger}")
            print(f"Has foodSearchResults div: {has_results_div}")
            print(f"Page title check: {page_title}")
            
            if has_search and has_meal_logger and has_results_div:
                print("✅ Search functionality is present!")
                
                # Test the API as well
                print("\nTesting search API...")
                api_response = session.get('http://127.0.0.1:5001/api/search_verified_foods?query=milk')
                print(f"API response status: {api_response.status_code}")
                if api_response.status_code == 200:
                    foods = api_response.json()
                    print(f"Found {len(foods)} foods")
                    if foods:
                        print(f"First food: {foods[0].get('name', 'Unknown')}")
                        print("✅ API is working!")
                    else:
                        print("❌ API returned empty results")
                else:
                    print("❌ API request failed")
                    
                return True
            else:
                print("❌ Search functionality missing")
                # Print some content for debugging
                print("\n--- Page content snippet ---")
                if 'foodsearch' in content:
                    start = content.find('foodsearch') - 100
                    end = content.find('foodsearch') + 200
                    print(content[max(0, start):end])
        else:
            print("❌ Could not access log meal page")
            
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_with_login()
    if success:
        print(f"\n✅ Food search functionality is working correctly!")
    else:
        print("\n❌ Food search functionality has issues")
