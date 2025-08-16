#!/usr/bin/env python3
"""
Test the new API v2 endpoint for foods.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests
import json
from app import create_app
from app.models import db, User, Food, FoodServing

def test_api_v2_foods():
    """Test the new /api/v2/foods/<id> endpoint."""
    app = create_app()
    
    with app.app_context():
        with app.test_client() as client:
            print("🧪 Testing API v2 foods endpoint...")
            
            # Login as admin to get session
            login_response = client.post('/auth/login', data={
                'username': 'admin',
                'password': 'admin'
            })
            
            # Check if login redirected (302) or returned success page (200)
            if login_response.status_code not in [200, 302]:
                print(f"❌ Login failed: {login_response.status_code}")
                return
            
            # Follow redirects to complete login
            if login_response.status_code == 302:
                redirect_response = client.get(login_response.location)
                if redirect_response.status_code != 200:
                    print(f"❌ Login redirect failed: {redirect_response.status_code}")
                    return
            
            print("   ✅ Logged in successfully")
            
            # Get test food data
            food = Food.query.filter_by(name='Idli small').first()
            if not food:
                print("❌ Test food 'Idli small' not found")
                return
            
            print(f"   📊 Testing with food: {food.name} (ID: {food.id})")
            
            # Test 1: Verify v1 endpoint still works (unchanged)
            print("\n🔹 Test 1: Verify v1 endpoint unchanged")
            v1_response = client.get(f'/api/foods/{food.id}/servings')
            
            if v1_response.status_code == 200:
                v1_data = v1_response.get_json()
                print("   ✅ v1 endpoint still works")
                print(f"   📄 v1 response structure: food, servings (legacy format)")
                
                # Check v1 structure
                if 'food' in v1_data and 'servings' in v1_data:
                    print("   ✅ v1 maintains expected structure")
                else:
                    print("   ❌ v1 structure changed!")
            else:
                print(f"   ❌ v1 endpoint failed: {v1_response.status_code}")
                return
            
            # Test 2: Test new v2 endpoint
            print("\n🔹 Test 2: Test new v2 endpoint")
            v2_response = client.get(f'/api/v2/foods/{food.id}')
            
            if v2_response.status_code == 200:
                v2_data = v2_response.get_json()
                print("   ✅ v2 endpoint works")
                
                # Verify v2 structure
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
                
                # Check servings array structure
                if 'servings' in v2_data and isinstance(v2_data['servings'], list):
                    print(f"   ✅ Servings array has {len(v2_data['servings'])} items")
                    
                    for i, serving in enumerate(v2_data['servings']):
                        serving_fields = ['id', 'serving_name', 'unit', 'grams_per_unit']
                        missing_serving_fields = [field for field in serving_fields if field not in serving]
                        
                        if missing_serving_fields:
                            print(f"   ❌ Serving {i} missing fields: {missing_serving_fields}")
                        else:
                            print(f"   ✅ Serving {i}: {serving['serving_name']} ({serving['grams_per_unit']}g)")
                else:
                    print("   ❌ Servings not found or not an array")
                
                # Check default_serving_id
                default_serving_id = v2_data.get('default_serving_id')
                if default_serving_id is not None:
                    print(f"   ✅ default_serving_id: {default_serving_id}")
                    
                    # Verify it points to a valid serving
                    serving_ids = [s['id'] for s in v2_data['servings']]
                    if default_serving_id in serving_ids:
                        print("   ✅ default_serving_id points to valid serving")
                    else:
                        print(f"   ⚠️  default_serving_id {default_serving_id} not in serving IDs: {serving_ids}")
                else:
                    print("   ℹ️  default_serving_id is null")
                
                # Pretty print the response
                print(f"\n📄 v2 Response:")
                print(json.dumps(v2_data, indent=2))
                
            else:
                print(f"   ❌ v2 endpoint failed: {v2_response.status_code}")
                error_data = v2_response.get_json()
                if error_data:
                    print(f"   Error: {error_data}")
                return
            
            # Test 3: Compare v1 vs v2 data consistency
            print("\n🔹 Test 3: Verify data consistency between v1 and v2")
            
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
            
            print("\n✅ API v2 endpoint test completed!")

if __name__ == "__main__":
    test_api_v2_foods()
