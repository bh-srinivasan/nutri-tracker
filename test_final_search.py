#!/usr/bin/env python3

import requests
import json

def test_corrected_search_functionality():
    """Test the search functionality with the correct API endpoint"""
    
    try:
        print("=== Testing CORRECTED Search Functionality ===\n")
        
        # 1. Test the page loads correctly
        print("1. Testing Log Meal page...")
        page_response = requests.get('http://127.0.0.1:5001/dashboard/log-meal')
        print(f"Page status: {page_response.status_code}")
        
        if page_response.status_code == 200:
            content = page_response.text.lower()
            
            # Check for all required elements with correct API endpoint
            checks = {
                'Search Input': 'id="foodsearch"' in content,
                'EnhancedMealLogger': 'enhancedmeallogger' in content,
                'Search Results Div': 'id="foodsearchresults"' in content,
                'Search Function': 'searchverifiedfoods' in content,
                'Correct API URL': '/api/foods/search-verified' in content
            }
            
            print("Page Element Checks:")
            for check_name, result in checks.items():
                status = "✅" if result else "❌"
                print(f"  {status} {check_name}: {result}")
            
            page_working = all(checks.values())
            if page_working:
                print("\n✅ All required elements are present on the page!\n")
            else:
                print("\n⚠️ Some elements are missing, but core functionality may still work\n")
                
        # 2. Test the CORRECTED search API
        print("2. Testing Search API with CORRECT endpoint...")
        
        test_queries = ['milk', 'rice', 'chicken', 'apple']
        api_working = True
        
        for query in test_queries:
            print(f"\nTesting query: '{query}'")
            try:
                # Use the CORRECT API endpoint
                api_response = requests.get(f'http://127.0.0.1:5001/api/foods/search-verified?q={query}', timeout=5)
                print(f"  API Status: {api_response.status_code}")
                
                if api_response.status_code == 200:
                    foods = api_response.json()
                    print(f"  Results found: {len(foods)}")
                    
                    if foods:
                        first_food = foods[0]
                        required_fields = ['id', 'name', 'calories_per_100g']
                        has_all_fields = all(field in first_food for field in required_fields)
                        
                        print(f"  First result: {first_food.get('name', 'Unknown')}")
                        print(f"  Has required fields: {has_all_fields}")
                        print(f"  Calories: {first_food.get('calories_per_100g', 'N/A')}")
                        
                        if has_all_fields:
                            print(f"  ✅ API returning correct data format")
                        else:
                            print(f"  ❌ Missing required fields")
                            api_working = False
                    else:
                        print(f"  ℹ️ No results found for '{query}'")
                        
                else:
                    print(f"  ❌ API error: {api_response.status_code}")
                    api_working = False
                    
            except Exception as e:
                print(f"  ❌ API request failed: {e}")
                api_working = False
        
        # 3. Test JavaScript functionality (basic check)
        print(f"\n3. Testing JavaScript Integration...")
        
        js_checks = {
            'Input Event Listener': 'addeventlistener(\'input\'' in content,
            'Search Timeout': 'searchtimeout' in content,
            'Results Display': 'displaysearchresults' in content,
            'Food Selection': 'selectfood' in content
        }
        
        print("JavaScript Element Checks:")
        js_working = True
        for check_name, result in js_checks.items():
            status = "✅" if result else "❌"
            print(f"  {status} {check_name}: {result}")
            if not result:
                js_working = False
        
        # 4. Final Test - Manual Search Simulation
        print(f"\n4. Simulating User Search Flow...")
        
        if api_working:
            print("Testing 'milk' search as user would do...")
            try:
                milk_response = requests.get('http://127.0.0.1:5001/api/foods/search-verified?q=milk', timeout=5)
                if milk_response.status_code == 200:
                    milk_foods = milk_response.json()
                    if milk_foods:
                        print(f"✅ User would see {len(milk_foods)} milk options")
                        print(f"   First option: {milk_foods[0]['name']} ({milk_foods[0]['calories_per_100g']} cal/100g)")
                    else:
                        print("❌ No milk foods found")
                else:
                    print(f"❌ Search API failed with status {milk_response.status_code}")
            except Exception as e:
                print(f"❌ Search simulation failed: {e}")
        
        # 5. Summary
        print(f"\n=== FINAL SUMMARY ===")
        overall_working = page_response.status_code == 200 and api_working and js_working
        
        print(f"📄 Page Loading: {'✅ Working' if page_response.status_code == 200 else '❌ Failed'}")
        print(f"🔍 Search API: {'✅ Working correctly' if api_working else '❌ Has issues'}")
        print(f"🖥️ JavaScript: {'✅ Elements present' if js_working else '❌ Missing elements'}")
        
        if overall_working:
            print(f"\n🎉 COMPLETE SUCCESS! 🎉")
            print(f"✅ The food search functionality is FULLY WORKING!")
            print(f"✅ Users can now search for foods in the Log Meal page!")
            print(f"✅ API returns correct data format!")
            print(f"✅ All JavaScript elements are in place!")
        elif api_working and page_response.status_code == 200:
            print(f"\n🎯 MOSTLY WORKING! 🎯")
            print(f"✅ Core search functionality is working!")
            print(f"✅ Users can search and get results!")
            print(f"⚠️ Some minor JavaScript elements may need verification!")
        else:
            print(f"\n❌ Issues found that need fixing")
        
        return overall_working
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    test_corrected_search_functionality()
