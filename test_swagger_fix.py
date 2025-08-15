#!/usr/bin/env python3
"""
Quick test script to verify the Swagger API meal logging fix.
This script will test both meal logging and food search endpoints.
"""

import requests
import json

# Test configuration
BASE_URL = "http://127.0.0.1:5001"
LOGIN_URL = f"{BASE_URL}/auth/login"
FOODS_API_URL = f"{BASE_URL}/api/v2/foods/search"
MEALS_API_URL = f"{BASE_URL}/api/v2/meals"

def test_swagger_api_fix():
    """Test the Swagger API endpoints after fixing the verified field issue."""
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    print("🧪 Testing Swagger API Fix...")
    print("=" * 50)
    
    # Step 1: Login to get authenticated session
    print("Step 1: Logging in as admin...")
    login_data = {
        'username': 'admin',
        'password': 'admin123',
        'remember_me': False
    }
    
    try:
        # First get the login page to get any CSRF tokens if needed
        login_page = session.get(LOGIN_URL)
        print(f"✅ Login page accessible: {login_page.status_code}")
        
        # Post login credentials
        response = session.post(LOGIN_URL, data=login_data, allow_redirects=False)
        print(f"✅ Login attempt: {response.status_code}")
        
        if response.status_code in [200, 302]:
            print("✅ Login successful!")
        else:
            print(f"❌ Login failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return False
    
    # Step 2: Test food search API
    print("\nStep 2: Testing food search API...")
    try:
        search_params = {'q': 'rice', 'page': 1, 'per_page': 5}
        foods_response = session.get(FOODS_API_URL, params=search_params)
        print(f"✅ Food search response: {foods_response.status_code}")
        
        if foods_response.status_code == 200:
            foods_data = foods_response.json()
            print(f"✅ Found {len(foods_data.get('foods', []))} foods")
            if foods_data.get('foods'):
                first_food = foods_data['foods'][0]
                print(f"✅ First food: {first_food.get('name')} (ID: {first_food.get('id')})")
                food_id = first_food.get('id')
            else:
                print("⚠️  No foods found, will use ID 1 for meal test")
                food_id = 1
        else:
            print(f"❌ Food search failed: {foods_response.text}")
            food_id = 1  # Fallback
            
    except Exception as e:
        print(f"❌ Food search error: {str(e)}")
        food_id = 1  # Fallback
    
    # Step 3: Test meal logging API
    print("\nStep 3: Testing meal logging API...")
    try:
        meal_data = {
            "food_id": food_id,
            "grams": 150.0,
            "meal_type": "lunch",
            "date": "2025-08-14"
        }
        
        meals_response = session.post(
            MEALS_API_URL, 
            headers={'Content-Type': 'application/json'},
            data=json.dumps(meal_data)
        )
        print(f"✅ Meal logging response: {meals_response.status_code}")
        
        if meals_response.status_code == 200:
            meal_result = meals_response.json()
            print(f"✅ Meal logged successfully!")
            print(f"   Meal ID: {meal_result.get('meal_log', {}).get('id')}")
            print(f"   Calories: {meal_result.get('meal_log', {}).get('calculated_nutrition', {}).get('calories')}")
        elif meals_response.status_code == 404:
            print(f"⚠️  Food not found (probably no verified foods in database)")
            print(f"   Response: {meals_response.text}")
        else:
            print(f"❌ Meal logging failed: {meals_response.status_code}")
            print(f"   Response: {meals_response.text}")
            
    except Exception as e:
        print(f"❌ Meal logging error: {str(e)}")
    
    # Step 4: Test Swagger UI accessibility
    print("\nStep 4: Testing Swagger UI accessibility...")
    try:
        swagger_url = f"{BASE_URL}/api/docs/"
        swagger_response = session.get(swagger_url)
        print(f"✅ Swagger UI response: {swagger_response.status_code}")
        
        if swagger_response.status_code == 200:
            if "Swagger UI" in swagger_response.text or "swagger" in swagger_response.text.lower():
                print("✅ Swagger UI is accessible and working!")
            else:
                print("⚠️  Swagger UI accessible but content unclear")
        else:
            print(f"❌ Swagger UI failed: {swagger_response.text}")
            
    except Exception as e:
        print(f"❌ Swagger UI error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎉 Test completed! Check results above.")
    print("💡 Now you can test the actual request body in Swagger UI at:")
    print(f"   {BASE_URL}/api/docs/")
    print("\n📝 Try this JSON in the Swagger UI:")
    print(json.dumps(meal_data, indent=2))

if __name__ == "__main__":
    test_swagger_api_fix()
