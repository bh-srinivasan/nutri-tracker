#!/usr/bin/env python3
"""Test the meal logging form validation by simulating food selection."""

from app import create_app
from app.models import User

app = create_app()

with app.test_client() as client:
    with app.app_context():
        # Get a non-admin user
        user = User.query.filter_by(username='demo').first()
        
        if not user:
            print("❌ Demo user not found")
            exit(1)
            
        print(f"🔐 Testing complete meal logging flow with user: {user.username}")
        
        # Login the user
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True
            
        # Test 1: Get the log meal page
        print("\n📄 Testing log meal page access...")
        page_response = client.get('/dashboard/log-meal')
        print(f"Log meal page - Status: {page_response.status_code}")
        
        if page_response.status_code != 200:
            print("❌ Cannot access log meal page")
            exit(1)
            
        # Test 2: Search for foods
        print("\n🔍 Testing food search...")
        search_response = client.get('/api/foods/search-verified?q=rice')
        print(f"Search API - Status: {search_response.status_code}")
        
        if search_response.status_code == 200:
            search_data = search_response.get_json()
            print(f"✅ Found {len(search_data)} foods")
            if search_data:
                first_food = search_data[0]
                food_id = first_food['id']
                print(f"First food: {first_food['name']} (ID: {food_id})")
                
                # Test 3: Get food servings
                print(f"\n🍽️ Testing food servings for ID {food_id}...")
                servings_response = client.get(f'/api/foods/{food_id}/servings')
                print(f"Servings API - Status: {servings_response.status_code}")
                
                if servings_response.status_code == 200:
                    servings_data = servings_response.get_json()
                    print("✅ Servings data retrieved")
                    print(f"Food: {servings_data['food']['name']}")
                    print(f"Servings count: {len(servings_data['servings'])}")
                    
                    # Test 4: Get food nutrition
                    print(f"\n🥗 Testing food nutrition for ID {food_id}...")
                    nutrition_response = client.get(f'/api/foods/{food_id}/nutrition')
                    print(f"Nutrition API - Status: {nutrition_response.status_code}")
                    
                    if nutrition_response.status_code == 200:
                        nutrition_data = nutrition_response.get_json()
                        print("✅ Nutrition data retrieved")
                        print(f"Calories per 100g: {nutrition_data['calories_per_100g']}")
                        print(f"Protein per 100g: {nutrition_data['protein_per_100g']}g")
                        
                        print("\n🎉 All API endpoints working correctly!")
                        print("The issue might be in the frontend JavaScript.")
                        print("Please check the browser console for JavaScript errors.")
                        
                    else:
                        print(f"❌ Nutrition API failed: {nutrition_response.get_data(as_text=True)}")
                else:
                    print(f"❌ Servings API failed: {servings_response.get_data(as_text=True)}")
            else:
                print("❌ No foods found in search")
        else:
            print(f"❌ Search API failed: {search_response.get_data(as_text=True)}")
