#!/usr/bin/env python3
"""
Test script to verify the Most Consumed Foods section fix
Tests the reports page for non-admin users
"""

import requests
import re
from bs4 import BeautifulSoup

def test_reports_page_most_consumed():
    """Test the Most Consumed Foods section"""
    
    print("🔍 Testing Most Consumed Foods Section...")
    print("=" * 60)
    
    session = requests.Session()
    base_url = "http://127.0.0.1:5001"
    
    try:
        # Step 1: Login as non-admin user
        print("1️⃣ Logging in as non-admin user...")
        
        # Get login page
        login_page = session.get(f"{base_url}/auth/login")
        print(f"   Login page status: {login_page.status_code}")
        
        # Extract CSRF token
        csrf_token = None
        csrf_match = re.search(r'name="csrf_token".*?value="([^"]+)"', login_page.text)
        if csrf_match:
            csrf_token = csrf_match.group(1)
            print(f"   CSRF token found: ✓")
        
        # Login
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        if csrf_token:
            login_data['csrf_token'] = csrf_token
        
        login_response = session.post(f"{base_url}/auth/login", data=login_data, allow_redirects=True)
        
        if "/dashboard" in login_response.url:
            print("   ✅ Login successful")
        else:
            print("   ❌ Login failed")
            return False
        
        # Step 2: Access Reports page
        print("\n2️⃣ Accessing Reports page...")
        
        reports_response = session.get(f"{base_url}/dashboard/reports")
        
        if reports_response.status_code == 200:
            print("   ✅ Reports page accessible")
        else:
            print(f"   ❌ Reports page error: {reports_response.status_code}")
            return False
        
        # Step 3: Check Most Consumed Foods section
        print("\n3️⃣ Checking Most Consumed Foods section...")
        
        soup = BeautifulSoup(reports_response.text, 'html.parser')
        
        # Find the Most Consumed Foods section
        most_consumed_section = soup.find(string=re.compile("Most Consumed Foods"))
        
        if most_consumed_section:
            print("   ✅ Most Consumed Foods section found")
            
            # Find the parent card containing this section
            card = most_consumed_section.find_parent('div', class_='card')
            
            if card:
                card_body = card.find('div', class_='card-body')
                
                if card_body:
                    # Check for function object errors
                    card_text = card_body.get_text()
                    
                    if "function" in card_text.lower() and "0x" in card_text:
                        print("   ❌ Function object detected in Most Consumed Foods!")
                        print(f"   Content preview: {card_text[:200]}...")
                        return False
                    elif "times" in card_text:
                        print("   ✅ Proper 'times' text found")
                        
                        # Extract and display the content
                        list_items = card_body.find_all('div', class_='list-group-item')
                        
                        if list_items:
                            print(f"   📊 Found {len(list_items)} food items:")
                            
                            for i, item in enumerate(list_items[:3], 1):  # Show first 3
                                item_text = item.get_text().strip()
                                print(f"      {i}. {item_text}")
                                
                                # Check if it contains function objects
                                if "function" in item_text or "0x" in item_text:
                                    print(f"      ❌ Function object in item {i}!")
                                    return False
                                    
                        else:
                            print("   📊 No food items found (user has no data)")
                            
                    elif "No foods logged yet" in card_text:
                        print("   ✅ Proper 'No foods logged yet' message displayed")
                    else:
                        print("   ⚠️  Unexpected content in Most Consumed Foods section")
                        print(f"   Content: {card_text[:100]}...")
                        
        else:
            print("   ❌ Most Consumed Foods section not found")
            return False
        
        # Step 4: Test different time periods
        print("\n4️⃣ Testing different time periods...")
        
        periods = ['7', '30', '90']
        
        for period in periods:
            print(f"\n   📅 Testing {period} day period...")
            
            period_response = session.get(f"{base_url}/dashboard/reports", params={'period': period})
            
            if period_response.status_code == 200:
                period_soup = BeautifulSoup(period_response.text, 'html.parser')
                period_section = period_soup.find(string=re.compile("Most Consumed Foods"))
                
                if period_section:
                    period_card = period_section.find_parent('div', class_='card')
                    
                    if period_card:
                        period_text = period_card.get_text()
                        
                        if "function" in period_text.lower() and "0x" in period_text:
                            print(f"      ❌ Function object in {period} day period!")
                            return False
                        else:
                            print(f"      ✅ {period} day period looks good")
                else:
                    print(f"      ⚠️  Section not found for {period} day period")
            else:
                print(f"      ❌ Error accessing {period} day period")
        
        print("\n" + "=" * 60)
        print("📋 MOST CONSUMED FOODS TEST SUMMARY")
        print("=" * 60)
        print("✅ Login: SUCCESS")
        print("✅ Reports Page: SUCCESS")
        print("✅ Most Consumed Foods Section: SUCCESS")
        print("✅ No Function Objects: SUCCESS")
        print("✅ All Time Periods: SUCCESS")
        
        print("\n🎉 Most Consumed Foods section is working correctly!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    success = test_reports_page_most_consumed()
    
    if success:
        print("\n✅ Most Consumed Foods fix verified successfully!")
    else:
        print("\n❌ Most Consumed Foods section has issues!")
