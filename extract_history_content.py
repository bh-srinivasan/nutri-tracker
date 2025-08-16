#!/usr/bin/env python3
"""
Extract exact content from servings history tab
"""

import requests
from bs4 import BeautifulSoup

def extract_history_content():
    """Extract and display the exact history content"""
    
    print("🔍 Extracting Servings History Content")
    print("=" * 45)
    
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
    
    # Get history tab content
    history_url = "http://localhost:5001/admin/food-servings/uploads?tab=history"
    history_response = session.get(history_url)
    
    if history_response.status_code != 200:
        print(f"❌ Failed to get history: {history_response.status_code}")
        return False
    
    soup = BeautifulSoup(history_response.content, 'html.parser')
    
    # Find the history panel
    history_panel = soup.find('div', {'id': 'history-panel'})
    
    if not history_panel:
        print("❌ History panel not found")
        return False
    
    print("✅ History panel found")
    
    # Check for jobs table
    jobs_table = history_panel.find('table')
    if jobs_table:
        print("✅ Jobs table found")
        
        # Extract table rows
        tbody = jobs_table.find('tbody')
        if tbody:
            rows = tbody.find_all('tr')
            print(f"📊 Found {len(rows)} job rows")
            
            for i, row in enumerate(rows, 1):
                cells = row.find_all('td')
                if len(cells) >= 4:
                    status = cells[0].get_text(strip=True)
                    filename = cells[1].get_text(strip=True)
                    progress = cells[2].get_text(strip=True)
                    results = cells[3].get_text(strip=True)
                    created = cells[4].get_text(strip=True) if len(cells) > 4 else 'N/A'
                    
                    print(f"\n📋 Job {i}:")
                    print(f"   Status: {status}")
                    print(f"   Filename: {filename}")
                    print(f"   Progress: {progress}")
                    print(f"   Results: {results}")
                    print(f"   Created: {created}")
        else:
            print("❌ Table body not found")
    else:
        # Check for "No Upload History" message
        if "No Upload History" in history_panel.get_text():
            print("❌ Shows 'No Upload History' message")
            print("\n--- Panel Text Content ---")
            print(history_panel.get_text(strip=True)[:500])
        else:
            print("⚠️ No table found, but no 'No History' message either")
            print("\n--- Panel Text Content ---")
            print(history_panel.get_text(strip=True)[:500])
    
    return True

if __name__ == "__main__":
    try:
        extract_history_content()
    except Exception as e:
        print(f"\n💥 Extraction failed with error: {e}")
        import traceback
        traceback.print_exc()
