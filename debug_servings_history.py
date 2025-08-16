#!/usr/bin/env python3
"""
Debug the serving uploads history display issue
"""

import requests
from bs4 import BeautifulSoup

def debug_servings_history():
    """Debug why servings history isn't showing"""
    
    print("🔍 Debugging Servings Upload History")
    print("=" * 40)
    
    session = requests.Session()
    
    # Login as admin
    login_url = "http://localhost:5001/auth/login"
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    # Get CSRF token
    login_page = session.get(login_url)
    soup = BeautifulSoup(login_page.content, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
    login_data['csrf_token'] = csrf_token
    
    # Login
    login_response = session.post(login_url, data=login_data, allow_redirects=True)
    
    if "Admin Dashboard" not in login_response.text:
        print("❌ Admin login failed")
        return False
    
    print("✅ Admin login successful")
    
    # Test 1: Check upload interface (upload tab)
    print("\n📋 Test 1: Upload Tab")
    print("-" * 20)
    
    upload_url = "http://localhost:5001/admin/food-servings/uploads"
    upload_response = session.get(upload_url)
    
    print(f"Status: {upload_response.status_code}")
    if upload_response.status_code == 200:
        print("✅ Upload interface accessible")
        if "Upload Servings Data" in upload_response.text:
            print("✅ Upload tab content present")
    else:
        print(f"❌ Upload interface failed: {upload_response.status_code}")
        return False
    
    # Test 2: Check history tab directly
    print("\n📊 Test 2: History Tab Direct Access")
    print("-" * 35)
    
    history_url = "http://localhost:5001/admin/food-servings/uploads?tab=history"
    history_response = session.get(history_url)
    
    print(f"Status: {history_response.status_code}")
    if history_response.status_code == 200:
        print("✅ History tab accessible")
        
        # Check for key elements
        soup = BeautifulSoup(history_response.content, 'html.parser')
        
        # Check if active tab is set correctly
        history_tab = soup.find('button', {'id': 'history-tab'})
        if history_tab and 'active' in history_tab.get('class', []):
            print("✅ History tab is active")
        else:
            print("❌ History tab not active")
        
        # Check for job table or no jobs message
        if "No Upload History" in history_response.text:
            print("❌ Shows 'No Upload History' message")
        elif "Upload History" in history_response.text and "table" in history_response.text.lower():
            print("✅ History table structure present")
        else:
            print("⚠️ Unclear history content state")
            
        # Check for specific job content
        if "test_servings.csv" in history_response.text or "error_test.csv" in history_response.text:
            print("✅ Job files found in history")
        else:
            print("❌ No job files found in history content")
            
        # Print relevant part of the response for debugging
        print("\n--- History Panel Content (first 500 chars) ---")
        history_panel_start = history_response.text.find('id="history-panel"')
        if history_panel_start != -1:
            content_sample = history_response.text[history_panel_start:history_panel_start + 500]
            print(content_sample)
        else:
            print("History panel not found in response")
    else:
        print(f"❌ History tab failed: {history_response.status_code}")
    
    # Test 3: Check what the route is actually querying
    print("\n🔍 Test 3: Direct Database Query Simulation")
    print("-" * 44)
    
    # This would be done server-side, but let's check the response content
    if "jobs.items" in history_response.text or "{% for job in jobs.items %}" in history_response.text:
        print("✅ Template expects jobs.items (pagination)")
    else:
        print("⚠️ Template pagination structure unclear")
    
    return True

if __name__ == "__main__":
    try:
        debug_servings_history()
    except Exception as e:
        print(f"\n💥 Debug failed with error: {e}")
        import traceback
        traceback.print_exc()
