#!/usr/bin/env python3
"""
Test the API v2 endpoint using app.test_client() directly.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json
from app import create_app
from app.models import db, User, Food, FoodServing

def test_api_v2_direct():
    """Test the API v2 endpoint using Flask test client."""
    app = create_app()
    
    with app.app_context():
        print("🧪 Testing API v2 foods endpoint directly...")
        
        with app.test_client() as client:
            # Test food ID 93 (Idli small)
            food = Food.query.filter_by(name='Idli small').first()
            if not food:
                print("❌ Test food 'Idli small' not found")
                return
                
            food_id = food.id
            print(f"   📊 Testing with food: {food.name} (ID: {food_id})")
            
            # Create an admin user session by directly setting the session
            with client.session_transaction() as sess:
                # Mock login by setting user_id in session
                user = User.query.filter_by(username='admin').first()
                if user:
                    sess['_user_id'] = str(user.id)
                    sess['_fresh'] = True
            
            # Test 1: v1 endpoint (should still work)
            print(f"\n🔹 Test 1: v1 endpoint /api/foods/{food_id}/servings")
            v1_response = client.get(f'/api/foods/{food_id}/servings')
            
            if v1_response.status_code == 200:
                v1_data = v1_response.get_json()
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
                    error_data = v1_response.get_json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error text: {v1_response.get_data(as_text=True)}")
                return
            
            # Test 2: v2 endpoint (new)
            print(f"\n🔹 Test 2: v2 endpoint /api/v2/foods/{food_id}")
            v2_response = client.get(f'/api/v2/foods/{food_id}')
            
            if v2_response.status_code == 200:
                v2_data = v2_response.get_json()
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
                
                # Test 3: Acceptance criteria verification
                print(f"\n🔹 Test 3: Acceptance criteria verification")
                
                # For foods with "100 g" serving, array should have one item
                has_100g_serving = any(s['serving_name'] == '100 g' for s in servings)
                
                if has_100g_serving:
                    print("   ✅ Food has '100 g' serving")
                    
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
                
                # Show sample response
                print(f"\n📄 Sample v2 Response:")
                print(json.dumps(v2_data, indent=2))
                
            else:
                print(f"   ❌ v2 endpoint failed: {v2_response.status_code}")
                try:
                    error_data = v2_response.get_json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error text: {v2_response.get_data(as_text=True)}")
                return
            
            # Test 4: Compare v1 vs v2 data consistency
            print(f"\n🔹 Test 4: Data consistency between v1 and v2")
            
            v1_food = v1_data['food']
            v2_food = v2_data
            
            # Check basic food fields consistency
            common_fields = ['id', 'name', 'brand', 'category']
            consistent = True
            
            for field in common_fields:
                v1_value = v1_food.get(field)
                v2_value = v2_food.get(field)
                if v1_value != v2_value:
                    print(f"   ❌ Field '{field}' inconsistent: v1={v1_value}, v2={v2_value}")
                    consistent = False
            
            if consistent:
                print("   ✅ Basic food data consistent between v1 and v2")
            
            # Check servings count consistency
            v1_servings_count = len(v1_data['servings'])
            v2_servings_count = len(v2_data['servings'])
            
            if v1_servings_count == v2_servings_count:
                print(f"   ✅ Servings count consistent: {v1_servings_count} servings")
            else:
                print(f"   ❌ Servings count mismatch: v1={v1_servings_count}, v2={v2_servings_count}")
            
            print("\n✅ API v2 direct test completed!")

if __name__ == "__main__":
    test_api_v2_direct()
