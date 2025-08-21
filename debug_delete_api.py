#!/usr/bin/env python3
"""
Test the admin food delete API endpoint to see the actual response
"""

from app import create_app
import json

def test_delete_api():
    """Test the delete API endpoint directly"""
    
    print("=== TESTING DELETE API ENDPOINT ===\n")
    
    app = create_app()
    
    with app.test_client() as client:
        with app.app_context():
            from app.models import User, Food, MealLog
            
            # Login as admin first
            print("1. Logging in as admin...")
            login_response = client.post('/auth/login', data={
                'username': 'admin',
                'password': 'admin'
            })
            
            print(f"   Login status: {login_response.status_code}")
            if login_response.status_code != 200:
                print("   ❌ Login failed - cannot test API")
                return
            
            # Get a food to test with
            print("\n2. Finding a test food...")
            test_food = Food.query.outerjoin(MealLog).filter(MealLog.id == None).first()
            
            if not test_food:
                print("   ❌ No available food for testing")
                return
                
            print(f"   ✅ Test food: {test_food.name} (ID: {test_food.id})")
            
            # Test the DELETE endpoint
            print(f"\n3. Testing DELETE /api/admin/foods/{test_food.id}")
            delete_response = client.delete(f'/api/admin/foods/{test_food.id}')
            
            print(f"   Response status: {delete_response.status_code}")
            print(f"   Response headers: {dict(delete_response.headers)}")
            
            # Try to get response data
            try:
                if delete_response.content_type and 'application/json' in delete_response.content_type:
                    response_data = delete_response.get_json()
                    print(f"   Response JSON: {json.dumps(response_data, indent=2)}")
                else:
                    response_text = delete_response.get_data(as_text=True)
                    print(f"   Response text: {response_text}")
            except Exception as e:
                print(f"   Could not parse response: {e}")
                print(f"   Raw response: {delete_response.get_data()}")
            
            # Check if the API route actually exists
            print(f"\n4. Checking available routes...")
            routes = []
            for rule in app.url_map.iter_rules():
                if '/api/' in rule.rule and 'admin' in rule.rule and 'foods' in rule.rule:
                    routes.append(f"{rule.rule} - {list(rule.methods)} - {rule.endpoint}")
            
            if routes:
                print("   Available API admin/foods routes:")
                for route in routes:
                    print(f"     {route}")
            else:
                print("   ❌ No API admin/foods routes found!")

if __name__ == "__main__":
    test_delete_api()
