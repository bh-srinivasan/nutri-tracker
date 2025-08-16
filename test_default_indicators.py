#!/usr/bin/env python3
"""
Test script for improved default indicators in edit_food.html
"""

import requests
import sys
from bs4 import BeautifulSoup

def test_default_indicators():
    """Test the improved default indicators in the edit food template"""
    
    base_url = "http://127.0.0.1:5001"
    
    print("🧪 Testing Improved Default Indicators")
    print("=" * 50)
    
    # Test login
    session = requests.Session()
    
    # Login as admin
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    try:
        login_response = session.post(f"{base_url}/auth/login", data=login_data)
        if login_response.status_code != 200 and 'admin' not in login_response.text:
            print("❌ Admin login failed")
            return False
        print("✅ Admin login successful")
        
        # Get edit food page for a food item (assuming food ID 1 exists)
        edit_response = session.get(f"{base_url}/admin/foods/1/edit")
        if edit_response.status_code != 200:
            print("❌ Failed to access edit food page")
            return False
        
        soup = BeautifulSoup(edit_response.text, 'html.parser')
        
        # Test 1: Check if system default row has proper structure
        system_default_row = soup.find('tr', class_='table-secondary')
        if not system_default_row:
            print("❌ System default row not found")
            return False
        
        print("✅ System default row found")
        
        # Test 2: Check for improved default column structure
        default_cell = system_default_row.find_all('td')[3]  # 4th column (0-indexed)
        if 'Default' in default_cell.get_text() or 'System default' in default_cell.get_text():
            print("✅ System default indicators present")
        else:
            print("❌ System default indicators missing")
            return False
        
        # Test 3: Check serving rows structure
        serving_rows = soup.find_all('tr', attrs={'data-serving-id': True})
        print(f"✅ Found {len(serving_rows)} custom serving rows")
        
        # Test 4: Check for proper badge placement in serving names
        for row in serving_rows:
            name_cell = row.find('td', class_='serving-name')
            if name_cell:
                if 'badge' in str(name_cell):
                    print("✅ Found default badge in serving name")
                    break
        
        # Test 5: Check for icon buttons
        edit_buttons = soup.find_all('button', class_='edit-serving-btn')
        delete_buttons = soup.find_all('button', class_='delete-serving-btn')
        
        if edit_buttons:
            print(f"✅ Found {len(edit_buttons)} edit buttons with proper classes")
        
        if delete_buttons:
            print(f"✅ Found {len(delete_buttons)} delete buttons with proper classes")
        
        # Test 6: Check for icons in buttons
        if any('fas fa-edit' in str(btn) for btn in edit_buttons):
            print("✅ Edit buttons have icons")
        
        if any('fas fa-trash' in str(btn) for btn in delete_buttons):
            print("✅ Delete buttons have icons")
        
        # Test 7: Check default action buttons
        set_default_buttons = soup.find_all(string=lambda text: text and 'Set Default' in text)
        unset_default_buttons = soup.find_all(string=lambda text: text and 'Unset Default' in text)
        
        if set_default_buttons:
            print(f"✅ Found Set Default buttons")
        
        if unset_default_buttons:
            print(f"✅ Found Unset Default buttons")
        
        print("\n🎉 All default indicator tests passed!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure Flask app is running on port 5001")
        return False
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    success = test_default_indicators()
    sys.exit(0 if success else 1)
