#!/usr/bin/env python3

print('=== TESTING FOOD ID 71 DELETE (500 ERROR) ===')

from app import create_app
from bs4 import BeautifulSoup

app = create_app()

with app.test_client() as client:
    with app.app_context():
        print('1. Getting login page...')
        login_page = client.get('/auth/login')
        print(f'   Status: {login_page.status_code}')
        
        # Extract CSRF token
        soup = BeautifulSoup(login_page.data, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})
        
        if csrf_token:
            csrf_value = csrf_token.get('value')
            print('   Found CSRF token')
            
            # Login with correct admin credentials
            print('\n2. Logging in as admin...')
            login_response = client.post('/auth/login', data={
                'username': 'admin',
                'password': 'admin123',
                'csrf_token': csrf_value
            }, follow_redirects=True)
            
            print(f'   Login response status: {login_response.status_code}')
            
            # Check session
            with client.session_transaction() as sess:
                user_id = sess.get('_user_id')
                print(f'   Session user_id: {user_id}')
            
            if user_id:
                print('   ✅ Login successful')
                
                # Test the specific food ID that's causing 500 error
                print('\n3. Testing DELETE /api/admin/foods/71 (the problematic one)...')
                
                try:
                    delete_response = client.delete('/api/admin/foods/71')
                    print(f'   Response status: {delete_response.status_code}')
                    print(f'   Response headers: {dict(delete_response.headers)}')
                    
                    if delete_response.status_code == 500:
                        print('   ❌ 500 Internal Server Error confirmed!')
                        print('   Response body:')
                        response_text = delete_response.get_data(as_text=True)
                        print(f'     {response_text}')
                        
                        # Try to get JSON error
                        try:
                            error_json = delete_response.get_json()
                            print(f'   JSON error: {error_json}')
                        except:
                            print('   No JSON error data')
                            
                    elif delete_response.status_code == 200:
                        success_data = delete_response.get_json()
                        print(f'   ✅ Success: {success_data}')
                        
                    elif delete_response.status_code == 404:
                        error_data = delete_response.get_json()
                        print(f'   ❌ Food not found: {error_data}')
                        
                    else:
                        print(f'   Unexpected status: {delete_response.status_code}')
                        print(f'   Response: {delete_response.get_data(as_text=True)}')
                        
                except Exception as e:
                    print(f'   ❌ Exception during delete: {e}')
                    import traceback
                    traceback.print_exc()
                
                # Also check if food ID 71 exists
                print('\n4. Checking if food ID 71 exists...')
                from app.models import Food
                food_71 = Food.query.get(71)
                if food_71:
                    print(f'   ✅ Food 71 exists: {food_71.name}')
                    
                    # Check if it has meal logs (referential constraint)
                    from app.models import MealLog
                    meal_logs = MealLog.query.filter_by(food_id=71).count()
                    print(f'   Meal logs for food 71: {meal_logs}')
                    
                else:
                    print('   ❌ Food ID 71 does not exist')
                
            else:
                print('   ❌ Login failed')
        else:
            print('   ❌ No CSRF token found')
