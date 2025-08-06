#!/usr/bin/env python3
"""Test the new nutrition API endpoint."""

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
            
        print(f"🔐 Testing nutrition endpoint with user: {user.username}")
        
        # Login the user
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True
            
        # Test the nutrition API endpoint
        response = client.get('/api/foods/1/nutrition')
        print(f"Nutrition endpoint - Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.get_json()
            print("✅ Nutrition API call successful!")
            print(f"Food: {data['name']}")
            print(f"Calories: {data['calories_per_100g']}")
            print(f"Protein: {data['protein_per_100g']}g")
        else:
            print(f"❌ Nutrition API call failed")
            print(f"Response: {response.get_data(as_text=True)}")
            
        # Also test the servings endpoint
        response2 = client.get('/api/foods/1/servings')
        print(f"\nServings endpoint - Status Code: {response2.status_code}")
        
        if response2.status_code == 200:
            print("✅ Servings API call successful!")
        else:
            print(f"❌ Servings API call failed")
            print(f"Response: {response2.get_data(as_text=True)}")
