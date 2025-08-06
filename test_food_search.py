#!/usr/bin/env python3
"""
Test script to check food search functionality
"""

import requests
import sys
import os

def test_food_search():
    """Test the food search API endpoint"""
    
    # Base URL
    base_url = "http://127.0.0.1:5001"
    
    print("🔍 Testing Food Search API...")
    
    # First, try to access the API without authentication
    print("\n1. Testing without authentication:")
    try:
        response = requests.get(f"{base_url}/api/foods/search-verified?q=milk")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test with session (need to login first)
    print("\n2. Testing with authentication:")
    session = requests.Session()
    
    # Try to login
    login_data = {
        'username': 'user',
        'password': 'password123'
    }
    
    try:
        # Login
        login_response = session.post(f"{base_url}/auth/login", data=login_data)
        print(f"   Login Status: {login_response.status_code}")
        
        if login_response.status_code == 200 or login_response.status_code == 302:
            # Now try the API
            api_response = session.get(f"{base_url}/api/foods/search-verified?q=milk")
            print(f"   API Status: {api_response.status_code}")
            print(f"   API Response: {api_response.text[:200]}...")
            
            if api_response.status_code == 200:
                import json
                data = api_response.json()
                print(f"   Found {len(data.get('foods', []))} foods")
                for food in data.get('foods', [])[:3]:
                    print(f"     - {food.get('name')} ({food.get('brand', 'No brand')})")
        else:
            print(f"   Login failed: {login_response.text[:200]}...")
            
    except Exception as e:
        print(f"   Error: {e}")

    # Check verified foods in database
    print("\n3. Checking database for verified foods:")
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from app import create_app, db
        from app.models import Food
        
        app = create_app()
        with app.app_context():
            total_foods = Food.query.count()
            verified_foods = Food.query.filter_by(is_verified=True).count()
            milk_foods = Food.query.filter(Food.name.contains('milk')).filter_by(is_verified=True).count()
            
            print(f"   Total foods: {total_foods}")
            print(f"   Verified foods: {verified_foods}")
            print(f"   Verified foods with 'milk': {milk_foods}")
            
            # Show some verified foods
            sample_foods = Food.query.filter_by(is_verified=True).limit(5).all()
            print(f"   Sample verified foods:")
            for food in sample_foods:
                print(f"     - {food.name} ({food.brand or 'No brand'})")
                
    except Exception as e:
        print(f"   Database Error: {e}")

if __name__ == '__main__':
    test_food_search()
