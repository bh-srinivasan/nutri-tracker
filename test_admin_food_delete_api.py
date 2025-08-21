#!/usr/bin/env python3
"""
Test Admin Food Delete API Implementation
"""

def test_api_endpoint_exists():
    """Test if the new API endpoint exists"""
    print("=== TESTING ADMIN FOOD DELETE API ===")
    
    try:
        from app import create_app
        from app.models import Food, User, MealLog
        import json
        
        app = create_app()
        
        with app.test_client() as client:
            with app.app_context():
                # Test 1: Unauthenticated request
                print("1. Testing unauthenticated request...")
                response = client.delete('/api/admin/foods/1')
                print(f"   Status: {response.status_code}")
                if response.status_code == 401:
                    data = response.get_json()
                    print(f"   Response: {data}")
                    print("   ✅ Correctly rejects unauthenticated requests")
                else:
                    print("   ❌ Should return 401 for unauthenticated requests")
                
                # Test 2: Create admin user and login
                print("\n2. Testing with admin user...")
                
                # Create or get admin user
                admin_user = User.query.filter_by(username='admin').first()
                if not admin_user:
                    admin_user = User(
                        username='admin',
                        user_id='admin',
                        email='admin@test.com',
                        first_name='Admin',
                        last_name='User',
                        is_admin=True,
                        is_active=True
                    )
                    admin_user.set_password('admin')
                    from app import db
                    db.session.add(admin_user)
                    db.session.commit()
                
                # Login as admin
                with client.session_transaction() as sess:
                    sess['_user_id'] = str(admin_user.id)
                    sess['_fresh'] = True
                
                # Test 3: Non-existent food
                print("   Testing non-existent food...")
                response = client.delete('/api/admin/foods/99999')
                print(f"   Status: {response.status_code}")
                if response.status_code == 404:
                    data = response.get_json()
                    print(f"   Response: {data}")
                    print("   ✅ Correctly returns 404 for non-existent food")
                else:
                    print("   ❌ Should return 404 for non-existent food")
                
                # Test 4: Check if we have a food to test with
                print("\n   Testing with existing food...")
                food = Food.query.first()
                if food:
                    print(f"   Found food: {food.name} (ID: {food.id})")
                    
                    # Check if food has meal logs
                    meal_count = MealLog.query.filter_by(food_id=food.id).count()
                    print(f"   Meal logs referencing this food: {meal_count}")
                    
                    if meal_count > 0:
                        print("   Testing deletion of food with meal logs...")
                        response = client.delete(f'/api/admin/foods/{food.id}')
                        print(f"   Status: {response.status_code}")
                        if response.status_code == 409:
                            data = response.get_json()
                            print(f"   Response: {data}")
                            print("   ✅ Correctly blocks deletion of food with meal logs")
                        else:
                            print("   ❌ Should return 409 for food with meal logs")
                    else:
                        print("   Food has no meal logs, could be deleted")
                        print("   (Not actually deleting to preserve data)")
                else:
                    print("   No foods found in database")
                
                # Test 5: Non-admin user
                print("\n3. Testing with non-admin user...")
                
                # Create or get regular user
                regular_user = User.query.filter_by(username='testuser').first()
                if not regular_user:
                    regular_user = User(
                        username='testuser',
                        user_id='testuser',
                        email='test@test.com',
                        first_name='Test',
                        last_name='User',
                        is_admin=False,
                        is_active=True
                    )
                    regular_user.set_password('password123')
                    from app import db
                    db.session.add(regular_user)
                    db.session.commit()
                
                # Login as regular user
                with client.session_transaction() as sess:
                    sess['_user_id'] = str(regular_user.id)
                    sess['_fresh'] = True
                
                response = client.delete('/api/admin/foods/1')
                print(f"   Status: {response.status_code}")
                if response.status_code == 403:
                    data = response.get_json()
                    print(f"   Response: {data}")
                    print("   ✅ Correctly rejects non-admin users")
                else:
                    print("   ❌ Should return 403 for non-admin users")
                
                print("\n=== API ENDPOINT TESTS COMPLETE ===")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_template_buttons():
    """Test if template has correct buttons"""
    print("\n=== TESTING TEMPLATE BUTTONS ===")
    
    try:
        import os
        template_path = 'app/templates/admin/foods.html'
        
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for edit button
            if 'edit-food-btn' in content and 'data-food-id' in content:
                print("✅ Edit button with correct class found")
            else:
                print("❌ Edit button not found or missing data-food-id")
            
            # Check for delete button
            if 'delete-food-btn' in content and 'data-food-id' in content:
                print("✅ Delete button with correct class found")
            else:
                print("❌ Delete button not found or missing data-food-id")
            
            # Check for pointer-events:none
            if 'pointer-events:none' in content:
                print("✅ Icon pointer-events protection found")
            else:
                print("❌ Missing pointer-events:none on icons")
                
        else:
            print("❌ Template file not found")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    test_api_endpoint_exists()
    test_template_buttons()
