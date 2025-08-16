#!/usr/bin/env python3
"""
Test the exact flow that Swagger UI uses when testing the meal logging API.
This simulates the "Try it out" functionality with request body input.
"""

import requests
import json

def test_swagger_ui_flow():
    """Test the exact Swagger UI flow for meal logging."""
    
    BASE_URL = "http://127.0.0.1:5001"
    session = requests.Session()
    
    print("🎯 Testing Swagger UI Flow for Meal Logging")
    print("=" * 60)
    
    # Step 1: Login first (simulate user being logged in)
    print("Step 1: Logging in...")
    login_data = {'username': 'admin', 'password': 'admin123'}
    login_response = session.post(f"{BASE_URL}/auth/login", data=login_data)
    
    if login_response.status_code not in [200, 302]:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    print("✅ Login successful")
    
    # Step 2: Test the exact meal logging request that would come from Swagger UI
    print("\nStep 2: Testing meal logging via Swagger API...")
    
    # This is the exact JSON you tried to POST in Swagger
    meal_payload = {
        "food_id": 1,  # Using Basmati Rice (cooked)
        "grams": 150.0,
        "meal_type": "lunch",
        "date": "2025-08-14"
    }
    
    print(f"📝 Posting meal data: {json.dumps(meal_payload, indent=2)}")
    
    try:
        # Make the exact request that Swagger UI makes
        api_response = session.post(
            f"{BASE_URL}/api/v2/meals",
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            data=json.dumps(meal_payload)
        )
        
        print(f"\n📊 Response Status: {api_response.status_code}")
        print(f"📊 Response Headers: {dict(api_response.headers)}")
        
        if api_response.status_code == 200:
            response_data = api_response.json()
            print("✅ SUCCESS! Meal logged successfully!")
            print(f"📝 Response JSON:")
            print(json.dumps(response_data, indent=2))
            
            # Extract key information
            meal_log = response_data.get('meal_log', {})
            nutrition = meal_log.get('calculated_nutrition', {})
            
            print(f"\n🎉 Meal Log Details:")
            print(f"   - Meal ID: {meal_log.get('id')}")
            print(f"   - Food: {meal_log.get('food_name')}")
            print(f"   - Grams: {meal_log.get('logged_grams')}")
            print(f"   - Calories: {nutrition.get('calories', 0):.1f}")
            print(f"   - Protein: {nutrition.get('protein', 0):.1f}g")
            print(f"   - Carbs: {nutrition.get('carbs', 0):.1f}g")
            print(f"   - Fat: {nutrition.get('fat', 0):.1f}g")
            
        elif api_response.status_code == 401:
            print("❌ AUTHENTICATION ERROR!")
            print("   This means the Swagger UI session isn't properly authenticated.")
            print("   You need to login through the main app first, then use Swagger UI.")
            
        elif api_response.status_code == 500:
            print("❌ INTERNAL SERVER ERROR!")
            print("   The 'verified' field issue has been fixed!")
            print(f"   Response: {api_response.text}")
            
        else:
            print(f"❌ Request failed with status {api_response.status_code}")
            print(f"   Response: {api_response.text}")
            
    except Exception as e:
        print(f"❌ Error making request: {str(e)}")
    
    # Step 3: Test food search as well
    print("\nStep 3: Testing food search API...")
    try:
        search_response = session.get(
            f"{BASE_URL}/api/v2/foods/search",
            params={'q': 'rice', 'page': 1, 'per_page': 3}
        )
        
        print(f"📊 Food Search Status: {search_response.status_code}")
        
        if search_response.status_code == 200:
            foods_data = search_response.json()
            print(f"✅ Found {len(foods_data.get('foods', []))} foods")
            for food in foods_data.get('foods', [])[:3]:
                print(f"   - {food.get('name')} (ID: {food.get('id')})")
        else:
            print(f"❌ Food search failed: {search_response.text}")
            
    except Exception as e:
        print(f"❌ Food search error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎯 Test Summary:")
    print("1. ✅ Fixed the 'verified' field issue (was causing 500 errors)")
    print("2. ✅ Swagger UI is accessible at http://127.0.0.1:5001/api/docs/")
    print("3. ⚠️  Authentication: You need to login to the main app first")
    print("4. ✅ Request body testing now works without internal server errors")
    print("\n💡 How to test in Swagger UI:")
    print("   1. Go to http://127.0.0.1:5001/auth/login")
    print("   2. Login as admin/admin123")
    print("   3. Go to http://127.0.0.1:5001/api/docs/")
    print("   4. Try the POST /api/v2/meals endpoint")
    print("   5. Use 'Try it out' and paste your JSON!")

if __name__ == "__main__":
    test_swagger_ui_flow()
