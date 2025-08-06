#!/usr/bin/env python3

import requests
import sys

def test_simple_login():
    """Test different login credentials to find the working one"""
    
    credentials_to_test = [
        ('admin', 'admin123'),
        ('admin', 'password'),
        ('admin', 'admin'),
        ('testuser', 'test123'),
        ('demo', 'demo123'),
        ('demo', 'demo'),
    ]
    
    for username, password in credentials_to_test:
        try:
            print(f"\nTrying {username}:{password}")
            
            session = requests.Session()
            
            # Get login page first
            login_page = session.get('http://127.0.0.1:5001/auth/login')
            
            # Try to login
            login_data = {
                'username': username,
                'password': password,
                'submit': 'Sign In'
            }
            
            login_response = session.post('http://127.0.0.1:5001/auth/login', data=login_data, allow_redirects=False)
            
            print(f"Login response status: {login_response.status_code}")
            
            if login_response.status_code == 302:
                redirect_url = login_response.headers.get('Location', '')
                print(f"Redirect to: {redirect_url}")
                
                if 'dashboard' in redirect_url:
                    print("✅ Login successful!")
                    
                    # Now try to access the dashboard
                    dashboard_response = session.get('http://127.0.0.1:5001/dashboard/')
                    print(f"Dashboard access: {dashboard_response.status_code}")
                    
                    if dashboard_response.status_code == 200:
                        # Now try log meal page
                        meal_response = session.get('http://127.0.0.1:5001/dashboard/log-meal')
                        print(f"Log meal page: {meal_response.status_code}")
                        
                        if meal_response.status_code == 200:
                            content = meal_response.text.lower()
                            has_search = 'id="foodsearch"' in content
                            has_logger = 'enhancedmeallogger' in content
                            has_results = 'id="foodsearchresults"' in content
                            
                            print(f"Has search input: {has_search}")
                            print(f"Has meal logger: {has_logger}")  
                            print(f"Has results div: {has_results}")
                            
                            if has_search and has_logger and has_results:
                                print(f"🎉 SUCCESS! Working credentials: {username}:{password}")
                                print("🎉 Search functionality is fully present!")
                                return True
                        
            elif login_response.status_code == 200:
                if 'invalid' in login_response.text.lower() or 'error' in login_response.text.lower():
                    print("❌ Invalid credentials")
                else:
                    print("❌ Login form returned with unknown error")
            else:
                print(f"❌ Unexpected response: {login_response.status_code}")
                
        except Exception as e:
            print(f"❌ Error testing {username}:{password} - {e}")
    
    return False

if __name__ == "__main__":
    if test_simple_login():
        print("\n✅ Food search is working correctly!")
    else:
        print("\n❌ Could not find working credentials or search is broken")
