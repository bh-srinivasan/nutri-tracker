import requests
import json

# Create a session to maintain cookies
session = requests.Session()

print('Testing with admin login...')
login_data = {
    'username': 'admin',
    'password': 'admin123'
}

# Login
login_response = session.post('http://localhost:5001/auth/login', data=login_data, allow_redirects=False)
print(f'Login status: {login_response.status_code}')

if login_response.status_code == 302:
    print('Login successful, now accessing log meal page...')
    log_meal_response = session.get('http://localhost:5001/dashboard/log-meal')
    print(f'Log meal page status: {log_meal_response.status_code}')
    
    print('Checking for key elements:')
    print(f'- foodSearch element: {"foodSearch" in log_meal_response.text}')
    print(f'- EnhancedMealLogger: {"EnhancedMealLogger" in log_meal_response.text}')
    print(f'- Search results div: {"foodSearchResults" in log_meal_response.text}')
    
    # Show first 1000 chars to see what we're getting
    print('First 1000 chars of response:')
    print(log_meal_response.text[:1000])
    
    # Test the search API with authenticated session
    search_response = session.get('http://localhost:5001/api/foods/search-verified?q=milk')
    print(f'Search API status: {search_response.status_code}')
    
    if search_response.status_code == 200:
        data = search_response.json()
        print(f'Search results: {len(data)} foods found')
        if data:
            print(f'First result: {data[0]["name"]} - {data[0]["calories_per_100g"]} cal/100g')
else:
    print('Login failed')
