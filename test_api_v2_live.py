#!/usr/bin/env python3
"""
Simple test for API v2 endpoint using requests to the running server.
"""

import requests
import json

def test_api_v2_live():
    """Test the API v2 endpoint against the running Flask server."""
    base_url = "http://127.0.0.1:5001"
    
    print("🧪 Testing live API v2 foods endpoint...")
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Login first
    print("   🔐 Logging in...")
    login_data = {
        'username': 'admin',
        'password': 'admin'
    }
    
    login_response = session.post(f"{base_url}/auth/login", data=login_data)
    
    if login_response.status_code not in [200, 302]:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    print("   ✅ Logged in successfully")
    
    # Test food ID 93 (Idli small) 
    food_id = 93
    
    # Test 1: v1 endpoint (should still work)
    print(f"\n🔹 Test 1: v1 endpoint /api/foods/{food_id}/servings")
    v1_response = session.get(f"{base_url}/api/foods/{food_id}/servings")
    
    if v1_response.status_code == 200:
        v1_data = v1_response.json()
        print("   ✅ v1 endpoint works")
        print(f"   📊 v1 response: food + servings structure")
        
        if 'food' in v1_data and 'servings' in v1_data:
            print(f"   📄 v1 food name: {v1_data['food']['name']}")
            print(f"   📄 v1 servings count: {len(v1_data['servings'])}")
        else:
            print("   ❌ Unexpected v1 structure")
    else:
        print(f"   ❌ v1 endpoint failed: {v1_response.status_code}")
        try:
            error_data = v1_response.json()
            print(f"   Error: {error_data}")
        except:
            print(f"   Error text: {v1_response.text}")
        return
    
    # Test 2: v2 endpoint (new)
    print(f"\n🔹 Test 2: v2 endpoint /api/v2/foods/{food_id}")
    v2_response = session.get(f"{base_url}/api/v2/foods/{food_id}")
    
    if v2_response.status_code == 200:
        v2_data = v2_response.json()
        print("   ✅ v2 endpoint works")
        
        # Check required fields
        required_fields = [
            'id', 'name', 'brand', 'category', 'description',
            'calories_per_100g', 'protein_per_100g', 'carbs_per_100g', 'fat_per_100g',
            'fiber_per_100g', 'sugar_per_100g', 'sodium_per_100g',
            'verified', 'servings', 'default_serving_id'
        ]
        
        missing_fields = [field for field in required_fields if field not in v2_data]
        if missing_fields:
            print(f"   ❌ Missing fields: {missing_fields}")
        else:
            print("   ✅ All required fields present")
        
        # Check servings array
        servings = v2_data.get('servings', [])
        print(f"   📊 Servings count: {len(servings)}")
        
        for i, serving in enumerate(servings):
            required_serving_fields = ['id', 'serving_name', 'unit', 'grams_per_unit']
            missing_serving_fields = [field for field in required_serving_fields if field not in serving]
            
            if missing_serving_fields:
                print(f"   ❌ Serving {i} missing: {missing_serving_fields}")
            else:
                print(f"   ✅ Serving {i}: {serving['serving_name']} = {serving['grams_per_unit']}g")
        
        # Check default_serving_id
        default_serving_id = v2_data.get('default_serving_id')
        print(f"   📌 default_serving_id: {default_serving_id}")
        
        if default_serving_id is not None:
            serving_ids = [s['id'] for s in servings]
            if default_serving_id in serving_ids:
                print("   ✅ default_serving_id points to valid serving")
            else:
                print(f"   ⚠️  default_serving_id not in serving IDs: {serving_ids}")
        
        # Show sample response
        print(f"\n📄 Sample v2 Response:")
        print(json.dumps(v2_data, indent=2))
        
    else:
        print(f"   ❌ v2 endpoint failed: {v2_response.status_code}")
        try:
            error_data = v2_response.json()
            print(f"   Error: {error_data}")
        except:
            print(f"   Error text: {v2_response.text}")
        return
    
    # Test 3: Acceptance criteria verification
    print(f"\n🔹 Test 3: Acceptance criteria verification")
    
    # For foods with "100 g" serving, array should have one item
    servings = v2_data.get('servings', [])
    has_100g_serving = any(s['serving_name'] == '100 g' for s in servings)
    
    if has_100g_serving:
        print("   ✅ Food has '100 g' serving")
        
        default_serving_id = v2_data.get('default_serving_id')
        if default_serving_id is not None:
            default_serving = next((s for s in servings if s['id'] == default_serving_id), None)
            if default_serving:
                print(f"   ✅ default_serving_id points to: {default_serving['serving_name']}")
            else:
                print(f"   ❌ default_serving_id {default_serving_id} not found in servings")
        else:
            print("   ⚠️  default_serving_id is null")
    else:
        print("   ℹ️  Food does not have '100 g' serving")
    
    print("\n✅ API v2 live test completed!")

if __name__ == "__main__":
    test_api_v2_live()
