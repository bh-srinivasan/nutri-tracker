#!/usr/bin/env python3
"""
Test script to verify the nutrition calculation fix in Swagger API.
"""

import requests
import json

def test_meal_logging_fix():
    """Test the meal logging API with corrected nutrition field names."""
    
    BASE_URL = "http://127.0.0.1:5001"
    session = requests.Session()
    
    print("🔧 Testing Meal Logging Fix (Nutrition Fields)")
    print("=" * 55)
    
    # Step 1: Login
    print("Step 1: Logging in as admin...")
    login_data = {'username': 'admin', 'password': 'admin123'}
    login_response = session.post(f"{BASE_URL}/auth/login", data=login_data)
    
    if login_response.status_code not in [200, 302]:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    print("✅ Login successful")
    
    # Step 2: Test meal logging with the exact JSON from your error
    print("\nStep 2: Testing meal logging with nutrition calculation...")
    
    meal_payload = {
        "food_id": 1,  # Basmati Rice (cooked)
        "grams": 150.0,
        "meal_type": "lunch",
        "date": "2025-08-14"
    }
    
    print(f"📝 Testing with payload: {json.dumps(meal_payload, indent=2)}")
    
    try:
        api_response = session.post(
            f"{BASE_URL}/api/v2/meals",
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            data=json.dumps(meal_payload)
        )
        
        print(f"\n📊 Response Status: {api_response.status_code}")
        
        if api_response.status_code == 200:
            response_data = api_response.json()
            print("🎉 SUCCESS! Meal logged with proper nutrition calculation!")
            print(f"📝 Response:")
            print(json.dumps(response_data, indent=2))
            
            # Extract and display nutrition info
            meal_log = response_data.get('meal_log', {})
            nutrition = meal_log.get('calculated_nutrition', {})
            
            print(f"\n✅ Nutrition Calculation Results:")
            print(f"   🍽️  Food: {meal_log.get('food_name')}")
            print(f"   ⚖️  Grams: {meal_log.get('logged_grams')}")
            print(f"   🔥 Calories: {nutrition.get('calories', 0):.1f}")
            print(f"   🥩 Protein: {nutrition.get('protein', 0):.1f}g")
            print(f"   🍞 Carbs: {nutrition.get('carbs', 0):.1f}g")
            print(f"   🧈 Fat: {nutrition.get('fat', 0):.1f}g")
            print(f"   🌾 Fiber: {nutrition.get('fiber', 0):.1f}g")
            
        elif api_response.status_code == 500:
            print("❌ Still getting 500 error!")
            print("   Check if there are more field name issues")
            print(f"   Response: {api_response.text[:500]}...")
            
        elif api_response.status_code == 401:
            print("❌ Authentication error (401)")
            print("   Make sure you're logged in to the main app first")
            
        else:
            print(f"❌ Request failed: {api_response.status_code}")
            print(f"   Response: {api_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Step 3: Test with different meal types
    print("\nStep 3: Testing other meal types...")
    
    test_cases = [
        {"food_id": 2, "grams": 100.0, "meal_type": "breakfast", "date": "2025-08-15"},
        {"food_id": 3, "grams": 75.0, "meal_type": "dinner", "date": "2025-08-15"}
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n   Test {i}: {test_case['meal_type']} - {test_case['grams']}g")
        try:
            response = session.post(
                f"{BASE_URL}/api/v2/meals",
                headers={'Content-Type': 'application/json'},
                data=json.dumps(test_case)
            )
            
            if response.status_code == 200:
                data = response.json()
                nutrition = data.get('meal_log', {}).get('calculated_nutrition', {})
                print(f"   ✅ Success: {nutrition.get('calories', 0):.1f} calories")
            else:
                print(f"   ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print("\n" + "=" * 55)
    print("🎯 Fix Summary:")
    print("✅ Fixed nutrition field names from:")
    print("   - food.calories_per_100g → food.calories")
    print("   - food.protein_per_100g → food.protein")
    print("   - food.carbs_per_100g → food.carbs")
    print("   - food.fat_per_100g → food.fat")
    print("   - food.fiber_per_100g → food.fiber")
    print("\n💡 Your Swagger UI should now work properly!")
    print("   Try the same JSON again in the Swagger interface.")

if __name__ == "__main__":
    test_meal_logging_fix()
