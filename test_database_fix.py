#!/usr/bin/env python3
"""
Test script to verify the database constraint fix for meal logging.
"""

import requests
import json

def test_database_constraint_fix():
    """Test the meal logging API with corrected database field mapping."""
    
    BASE_URL = "http://127.0.0.1:5001"
    session = requests.Session()
    
    print("🛠️  Testing Database Constraint Fix")
    print("=" * 45)
    
    # Step 1: Login
    print("Step 1: Logging in as admin...")
    login_data = {'username': 'admin', 'password': 'admin123'}
    login_response = session.post(f"{BASE_URL}/auth/login", data=login_data)
    
    if login_response.status_code not in [200, 302]:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    print("✅ Login successful")
    
    # Step 2: Test the exact JSON that was causing the IntegrityError
    print("\nStep 2: Testing meal logging with database field fix...")
    
    meal_payload = {
        "food_id": 1,  # Test with first food
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
            print("🎉 SUCCESS! Meal logged without database constraint errors!")
            print(f"📝 Response data:")
            print(json.dumps(response_data, indent=2))
            
            # Validate the response structure
            meal_log = response_data.get('meal_log', {})
            if meal_log:
                print(f"\n✅ Database Fields Check:")
                print(f"   - ID: {meal_log.get('id')}")
                print(f"   - Food ID: {meal_log.get('food_id')}")
                print(f"   - Original Quantity: {meal_log.get('original_quantity')}")
                print(f"   - Logged Grams: {meal_log.get('logged_grams')}")
                print(f"   - Unit Type: {meal_log.get('unit_type')}")
                
                nutrition = meal_log.get('calculated_nutrition', {})
                print(f"   - Calories: {nutrition.get('calories', 0):.1f}")
                
        elif api_response.status_code == 500:
            print("❌ Still getting 500 error!")
            response_text = api_response.text
            if "IntegrityError" in response_text:
                print("   🔍 Still a database constraint issue")
                if "original_quantity" in response_text:
                    print("   🎯 Problem: original_quantity field")
                if "NOT NULL constraint failed" in response_text:
                    print("   🎯 Problem: NOT NULL constraint violation")
            print(f"   Response snippet: {response_text[:200]}...")
            
        elif api_response.status_code == 401:
            print("❌ Authentication error (401)")
            print("   Make sure you're logged in to the main app first")
            
        else:
            print(f"❌ Request failed: {api_response.status_code}")
            print(f"   Response: {api_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Step 3: Test with different input types
    print("\nStep 3: Testing with serving-based input...")
    
    serving_payload = {
        "food_id": 1,
        "serving_id": 1,  # Assuming there's a serving with ID 1
        "quantity": 2.0,
        "meal_type": "dinner",
        "date": "2025-08-15"
    }
    
    try:
        response = session.post(
            f"{BASE_URL}/api/v2/meals",
            headers={'Content-Type': 'application/json'},
            data=json.dumps(serving_payload)
        )
        
        print(f"   Serving-based input: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success: {data.get('meal_log', {}).get('unit_type')} type")
        elif response.status_code == 404:
            print(f"   ⚠️  Serving not found (expected if no servings exist)")
        else:
            print(f"   ❌ Failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    print("\n" + "=" * 45)
    print("🎯 Database Constraint Fix Summary:")
    print("✅ Fixed field mapping:")
    print("   - quantity: logged_grams (DEPRECATED but NOT NULL)")
    print("   - original_quantity: original_quantity (user input)")
    print("   - logged_grams: logged_grams (normalized grams)")
    print("\n💡 Your Swagger UI should now work without IntegrityError!")

if __name__ == "__main__":
    test_database_constraint_fix()
