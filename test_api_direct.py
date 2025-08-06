#!/usr/bin/env python3
"""Test the fixed API endpoint by directly accessing the route."""

from app import create_app
from app.models import User, Food
from flask_login import login_user

app = create_app()

with app.test_client() as client:
    with app.app_context():
        # Get a non-admin user
        user = User.query.filter_by(username='demo').first()
        
        if not user:
            print("❌ Demo user not found")
            exit(1)
            
        print(f"🔐 Testing with user: {user.username} (admin: {user.is_admin})")
        
        # Login the user
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True
            
        # Test the API endpoint
        response = client.get('/api/foods/1/servings')
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.get_json()
            print("✅ API call successful!")
            print(f"Response: {data}")
        else:
            print(f"❌ API call failed with status {response.status_code}")
            print(f"Response: {response.get_data(as_text=True)}")
