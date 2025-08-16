#!/usr/bin/env python3
"""
Verify dashboard navigation and interface linking
"""

import requests
from bs4 import BeautifulSoup

def verify_navigation():
    """Verify that dashboard properly links to the new interface"""
    
    print("🔍 Verifying Dashboard Navigation")
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
    
    # Check dashboard for servings upload links
    dashboard_url = "http://localhost:5001/admin/dashboard"
    dashboard_response = session.get(dashboard_url)
    
    if dashboard_response.status_code != 200:
        print(f"❌ Dashboard access failed: {dashboard_response.status_code}")
        return False
    
    print("✅ Dashboard accessible")
    
    soup = BeautifulSoup(dashboard_response.content, 'html.parser')
    
    # Look for servings upload buttons/links
    servings_links = []
    
    # Check for the new unified interface link
    new_link = soup.find('a', href=lambda x: x and 'food-servings/uploads' in x)
    if new_link:
        servings_links.append(('New Unified Interface', new_link['href'], new_link.get_text(strip=True)))
    
    # Check for any old interface links
    old_link = soup.find('a', href=lambda x: x and 'food-servings/upload' in x and 'uploads' not in x)
    if old_link:
        servings_links.append(('Old Interface', old_link['href'], old_link.get_text(strip=True)))
    
    print(f"\n📋 Found {len(servings_links)} servings upload link(s):")
    for name, href, text in servings_links:
        print(f"   {name}: {href} ('{text}')")
    
    if not servings_links:
        print("❌ No servings upload links found on dashboard")
        
        # Search for any mention of "serving" in the dashboard
        dashboard_text = dashboard_response.text.lower()
        if 'serving' in dashboard_text:
            print("⚠️ 'serving' mentioned in dashboard, but no clear links")
        else:
            print("❌ No mention of 'serving' found in dashboard")
    
    # Test clicking the new interface link if it exists
    if servings_links:
        for name, href, text in servings_links:
            if 'uploads' in href:  # New interface
                print(f"\n🔗 Testing {name} link: {href}")
                
                # Convert relative URL to absolute
                if href.startswith('/'):
                    test_url = f"http://localhost:5001{href}"
                else:
                    test_url = href
                
                test_response = session.get(test_url)
                if test_response.status_code == 200:
                    print(f"✅ {name} accessible")
                    
                    # Check if it shows the history tab
                    if 'Upload History' in test_response.text:
                        print("✅ History tab present")
                    else:
                        print("❌ History tab missing")
                        
                else:
                    print(f"❌ {name} failed: {test_response.status_code}")
    
    return True

if __name__ == "__main__":
    try:
        verify_navigation()
    except Exception as e:
        print(f"\n💥 Verification failed with error: {e}")
        import traceback
        traceback.print_exc()
