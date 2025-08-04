#!/usr/bin/env python3
"""
Simple test script to verify the Most Consumed Foods section fix
Tests the reports page for non-admin users without external dependencies
"""

import requests
import re

def test_most_consumed_foods_simple():
    """Test the Most Consumed Foods section without external dependencies"""
    
    print("🔍 Testing Most Consumed Foods Section Fix...")
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
        
        # Step 3: Check for function object issues
        print("\n3️⃣ Checking for function object issues...")
        
        page_content = reports_response.text
        
        # Check for the problematic function object pattern
        function_pattern = r'<function.*?0x[0-9A-Fa-f]+.*?>'
        function_matches = re.findall(function_pattern, page_content)
        
        if function_matches:
            print(f"   ❌ Found {len(function_matches)} function objects!")
            for i, match in enumerate(function_matches[:3], 1):
                print(f"      {i}. {match}")
            return False
        else:
            print("   ✅ No function objects found")
        
        # Check for the specific pattern that was causing issues
        meth_pattern = r'meth at 0x[0-9A-Fa-f]+.*?times'
        meth_matches = re.findall(meth_pattern, page_content)
        
        if meth_matches:
            print(f"   ❌ Found {len(meth_matches)} 'meth at 0x...' patterns!")
            for i, match in enumerate(meth_matches[:3], 1):
                print(f"      {i}. {match}")
            return False
        else:
            print("   ✅ No 'meth at 0x...' patterns found")
        
        # Check for proper "times" usage
        times_pattern = r'(\d+)\s+times'
        times_matches = re.findall(times_pattern, page_content)
        
        if times_matches:
            print(f"   ✅ Found {len(times_matches)} proper 'times' displays:")
            for i, count in enumerate(times_matches[:5], 1):
                print(f"      {i}. {count} times")
        else:
            print("   📊 No food counts found (user might have no data)")
        
        # Check for "Most Consumed Foods" section
        if "Most Consumed Foods" in page_content:
            print("   ✅ Most Consumed Foods section found")
        else:
            print("   ❌ Most Consumed Foods section not found")
            return False
        
        # Step 4: Test with different periods
        print("\n4️⃣ Testing different time periods...")
        
        periods = ['7', '30', '90']
        all_periods_ok = True
        
        for period in periods:
            print(f"\n   📅 Testing {period} day period...")
            
            period_response = session.get(f"{base_url}/dashboard/reports", params={'period': period})
            
            if period_response.status_code == 200:
                period_content = period_response.text
                
                # Check for function objects in this period
                period_function_matches = re.findall(function_pattern, period_content)
                period_meth_matches = re.findall(meth_pattern, period_content)
                
                if period_function_matches or period_meth_matches:
                    print(f"      ❌ Function objects found in {period} day period!")
                    all_periods_ok = False
                else:
                    print(f"      ✅ {period} day period clean")
            else:
                print(f"      ❌ Error accessing {period} day period")
                all_periods_ok = False
        
        # Final summary
        print("\n" + "=" * 60)
        print("📋 MOST CONSUMED FOODS FIX TEST SUMMARY")
        print("=" * 60)
        
        if all_periods_ok and not function_matches and not meth_matches:
            print("🎉 ALL TESTS PASSED!")
            print("✅ Login: SUCCESS")
            print("✅ Reports Page: SUCCESS") 
            print("✅ No Function Objects: SUCCESS")
            print("✅ All Time Periods: SUCCESS")
            print("✅ Most Consumed Foods Section: FIXED")
            
            print("\n🚀 The fix is working correctly!")
            print("   Non-admin users can now view the Reports page without function object errors.")
            return True
        else:
            print("❌ SOME TESTS FAILED!")
            print("   Function objects are still present in the Most Consumed Foods section.")
            return False
            
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    success = test_most_consumed_foods_simple()
    
    if success:
        print("\n✅ Most Consumed Foods fix verified successfully!")
    else:
        print("\n❌ Most Consumed Foods section still has issues!")
