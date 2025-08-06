#!/usr/bin/env python3

import requests
import sys

def test_log_meal_page():
    """Test the log meal page and search functionality"""
    
    try:
        # Test the page that should have search functionality
        print("Testing Log Meal page...")
        
        # Try both possible URLs
        urls_to_test = [
            'http://127.0.0.1:5001/dashboard/log_meal',
            'http://127.0.0.1:5001/dashboard/log-meal'
        ]
        
        for url in urls_to_test:
            print(f"\nTesting: {url}")
            try:
                response = requests.get(url, timeout=10, allow_redirects=True)
                print(f"Status: {response.status_code}")
                print(f"Final URL: {response.url}")
                print(f"Content length: {len(response.text)}")
                
                if response.status_code == 200:
                    # Check for search functionality
                    content = response.text.lower()
                    has_search = 'foodsearch' in content or 'food-search' in content
                    has_meal_logger = 'enhancedmeallogger' in content or 'meallogger' in content
                    has_form = '<form' in content
                    page_title = 'log meal' in content
                    
                    print(f"Has search input: {has_search}")
                    print(f"Has MealLogger: {has_meal_logger}")
                    print(f"Has form: {has_form}")
                    print(f"Page title check: {page_title}")
                    
                    if has_search and has_meal_logger:
                        print("✅ This page has the search functionality!")
                        return url
                    else:
                        print("❌ Missing search functionality")
                else:
                    print(f"❌ Page returned status {response.status_code}")
                    if 'login' in response.url.lower():
                        print("🔐 Page requires authentication")
                        
            except Exception as e:
                print(f"❌ Error accessing {url}: {e}")
        
        return None
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return None

if __name__ == "__main__":
    working_url = test_log_meal_page()
    if working_url:
        print(f"\n✅ Found working search page at: {working_url}")
    else:
        print("\n❌ No working search page found")
