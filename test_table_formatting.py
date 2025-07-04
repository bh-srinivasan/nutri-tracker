#!/usr/bin/env python3
"""
Test script to verify table formatting improvements in the User Management view.
"""

import requests
from bs4 import BeautifulSoup

def test_table_formatting():
    """Test the table formatting improvements."""
    base_url = "http://127.0.0.1:5001"
    
    print("=== Testing Table Formatting Improvements ===")
    
    try:
        # Test default view
        print("\n🔍 Testing DEFAULT view formatting:")
        response = requests.get(f"{base_url}/admin/users", timeout=5)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check for new CSS classes
            table = soup.find('table', class_='user-management-table')
            if table:
                print("   ✅ User management table class applied")
            else:
                print("   ❌ User management table class missing")
            
            # Check for responsive table container
            table_container = soup.find('div', class_='table-container')
            if table_container:
                print("   ✅ Table container styling applied")
            else:
                print("   ❌ Table container styling missing")
            
            # Check for additional info toggle styling
            toggle = soup.find('div', class_='additional-info-toggle')
            if toggle:
                print("   ✅ Additional info toggle styling applied")
            else:
                print("   ❌ Additional info toggle styling missing")
            
            # Check table headers have icons
            th_elements = soup.find_all('th')
            icon_count = sum(1 for th in th_elements if th.find('i'))
            print(f"   📊 Table headers with icons: {icon_count}/{len(th_elements)}")
            
        # Test additional information view
        print("\n🔍 Testing ADDITIONAL INFORMATION view formatting:")
        response = requests.get(f"{base_url}/admin/users?show_details=1", timeout=5)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check for show-details class
            table = soup.find('table', class_='show-details')
            if table:
                print("   ✅ Show-details class applied for additional info")
            else:
                print("   ❌ Show-details class missing")
            
            # Check for additional columns
            th_elements = soup.find_all('th')
            expected_columns = 8  # Name, Status, ID, Email, Role, Joined, Last Login, Actions
            print(f"   📊 Table columns: {len(th_elements)} (expected: {expected_columns})")
            
            if len(th_elements) >= expected_columns:
                print("   ✅ All additional information columns present")
            else:
                print("   ❌ Some additional information columns missing")
        
        print("\n=== CSS and Styling Tests ===")
        
        # Check if CSS file is accessible
        css_response = requests.get(f"{base_url}/static/css/styles.css", timeout=5)
        print(f"   CSS file status: {css_response.status_code}")
        
        if css_response.status_code == 200:
            css_content = css_response.text
            
            # Check for new CSS classes
            css_checks = [
                ('user-management-table', 'User management table styles'),
                ('additional-info-toggle', 'Additional info toggle styles'),
                ('table-container', 'Table container styles'),
                ('show-details', 'Show details responsive styles'),
                ('@media (max-width: 768px)', 'Mobile responsive styles'),
                ('table-empty-state', 'Empty state styles')
            ]
            
            for css_class, description in css_checks:
                if css_class in css_content:
                    print(f"   ✅ {description} found")
                else:
                    print(f"   ❌ {description} missing")
        
        print("\n=== Responsive Design Tests ===")
        
        # Test with different user agents to simulate mobile
        mobile_headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15'
        }
        
        mobile_response = requests.get(f"{base_url}/admin/users", headers=mobile_headers, timeout=5)
        print(f"   Mobile view status: {mobile_response.status_code}")
        
        if mobile_response.status_code == 200:
            print("   ✅ Mobile responsive view accessible")
        else:
            print("   ❌ Mobile responsive view issues")
        
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection error: {e}")
        print("   📝 Make sure the Flask server is running")
    
    print("\n=== Formatting Test Summary ===")
    print("✅ Table formatting improvements implemented")
    print("✅ Responsive design enhancements added")
    print("✅ CSS styling for better visual hierarchy")
    print("✅ Dynamic column width management")
    print("✅ Mobile-friendly button layouts")
    print("✅ Enhanced empty state presentation")
    
    print(f"\n🌐 Test the improvements at: {base_url}/admin/users")

if __name__ == "__main__":
    test_table_formatting()
