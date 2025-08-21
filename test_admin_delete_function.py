#!/usr/bin/env python3
"""
Test the admin food delete functionality end-to-end
"""

from app import create_app
import os

def test_admin_food_delete():
    """Test admin food delete functionality"""
    
    print("=== TESTING ADMIN FOOD DELETE FUNCTIONALITY ===\n")
    
    app = create_app()
    
    with app.test_client() as client:
        with app.app_context():
            from app.models import User, Food, MealLog
            
            # Check if admin user exists
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                print("❌ Admin user not found")
                return
            
            print(f"✅ Admin user found: {admin.username}")
            
            # Login as admin
            login_response = client.post('/auth/login', data={
                'username': 'admin',
                'password': 'admin'  # Assuming default admin password
            }, follow_redirects=True)
            
            if login_response.status_code != 200:
                print(f"❌ Admin login failed: {login_response.status_code}")
                return
                
            print("✅ Admin login successful")
            
            # Get a test food to delete (one without meal logs)
            test_food = Food.query.outerjoin(MealLog).filter(MealLog.id == None).first()
            
            if not test_food:
                print("❌ No food available for testing (all foods have meal logs)")
                return
                
            print(f"✅ Test food found: {test_food.name} (ID: {test_food.id})")
            
            # Test the DELETE API endpoint
            delete_response = client.delete(f'/api/admin/foods/{test_food.id}')
            
            print(f"🔧 DELETE API response status: {delete_response.status_code}")
            
            if delete_response.status_code == 200:
                print("✅ Food deleted successfully!")
                
                # Verify food is actually deleted
                deleted_food = Food.query.get(test_food.id)
                if deleted_food is None:
                    print("✅ Food confirmed deleted from database")
                else:
                    print("❌ Food still exists in database")
                    
            elif delete_response.status_code == 409:
                response_data = delete_response.get_json()
                print(f"⚠️  Cannot delete food: {response_data.get('error', 'Unknown error')}")
                
            elif delete_response.status_code == 403:
                print("❌ Access denied - admin permission issue")
                
            elif delete_response.status_code == 404:
                print("❌ Food not found")
                
            else:
                response_text = delete_response.get_data(as_text=True)
                print(f"❌ Unexpected error: {response_text}")
                
    print("\n=== TEST COMPLETE ===")

if __name__ == "__main__":
    test_admin_food_delete()
