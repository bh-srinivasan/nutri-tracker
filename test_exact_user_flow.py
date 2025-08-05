#!/usr/bin/env python3
"""
Manual test simulating the exact user flow that was reported
"""

import requests
import re

def test_exact_user_flow():
    """Test the exact flow: non-admin user clicks Set Goals from Quick Actions"""
    
    print("🧪 Testing Exact User Flow: Non-admin clicks 'Set Goals'")
    print("=" * 60)
    
    session = requests.Session()
    base_url = "http://127.0.0.1:5001"
    
    try:
        # Step 1: Login as non-admin user (testuser)
        print("1️⃣ Logging in as non-admin user (testuser)...")
        
        login_page = session.get(f"{base_url}/auth/login")
        csrf_match = re.search(r'name="csrf_token".*?value="([^"]+)"', login_page.text)
        csrf_token = csrf_match.group(1) if csrf_match else None
        
        login_data = {'username': 'testuser', 'password': 'testpass123'}
        if csrf_token:
            login_data['csrf_token'] = csrf_token
        
        login_response = session.post(f"{base_url}/auth/login", data=login_data, allow_redirects=True)
        
        if "/dashboard" in login_response.url:
            print("   ✅ Login successful")
        else:
            print("   ❌ Login failed")
            return False
        
        # Step 2: Access dashboard and look for Quick Actions
        print("\n2️⃣ Checking dashboard for Quick Actions...")
        
        dashboard_response = session.get(f"{base_url}/dashboard")
        
        if dashboard_response.status_code == 200:
            print("   ✅ Dashboard accessible")
            
            # Check for Set Goals link
            if 'nutrition-goals' in dashboard_response.text:
                print("   ✅ 'Set Goals' link found in dashboard")
            else:
                print("   ⚠️ 'Set Goals' link not found (but this might be normal)")
        else:
            print(f"   ❌ Dashboard error: {dashboard_response.status_code}")
            return False
        
        # Step 3: Click on "Set Goals" (the exact action reported to fail)
        print("\n3️⃣ Clicking on 'Set Goals' (simulating user action)...")
        
        goals_response = session.get(f"{base_url}/dashboard/nutrition-goals")
        
        print(f"   Status Code: {goals_response.status_code}")
        
        if goals_response.status_code == 200:
            print("   ✅ Goals page loaded successfully!")
            
            # Check for specific errors mentioned in the traceback
            error_checks = [
                ('start_date', "start_date attribute error"),
                ('end_date', "end_date attribute error"), 
                ('UndefinedError', "UndefinedError"),
                ('has no attribute', "Attribute error"),
                ('Internal Server Error', "500 error"),
                ('line 23', "Template line 23 error")
            ]
            
            errors_found = []
            content = goals_response.text
            
            for pattern, description in error_checks:
                if pattern in content:
                    errors_found.append(description)
            
            if errors_found:
                print(f"   ❌ Errors found: {', '.join(errors_found)}")
                return False
            else:
                print("   ✅ No template errors detected")
            
            # Check that form loads properly
            if '<form method="POST">' in content:
                print("   ✅ Form found")
                
                # Check for required fields
                required_fields = ['weight', 'height', 'age', 'gender', 'activity_level', 'target_calories']
                missing_fields = []
                
                for field in required_fields:
                    if f'name="{field}"' not in content:
                        missing_fields.append(field)
                
                if missing_fields:
                    print(f"   ❌ Missing fields: {missing_fields}")
                    return False
                else:
                    print("   ✅ All required form fields present")
            else:
                print("   ❌ Form not found")
                return False
        
        elif goals_response.status_code == 500:
            print("   ❌ 500 Internal Server Error!")
            print("   Server Error Content:")
            error_content = goals_response.text
            
            # Extract specific error from werkzeug debugger
            if 'UndefinedError' in error_content:
                error_match = re.search(r'UndefinedError: (.+?)(?:\n|<)', error_content)
                if error_match:
                    print(f"   Specific Error: {error_match.group(1)}")
            
            # Look for line numbers
            line_match = re.search(r'line (\d+)', error_content)
            if line_match:
                print(f"   Error on line: {line_match.group(1)}")
            
            return False
        else:
            print(f"   ❌ Unexpected status code: {goals_response.status_code}")
            return False
        
        # Step 4: Test form submission (if we got this far)
        print("\n4️⃣ Testing form submission...")
        
        # Extract CSRF token from goals page
        csrf_match = re.search(r'name="csrf_token".*?value="([^"]+)"', goals_response.text)
        csrf_token = csrf_match.group(1) if csrf_match else None
        
        if not csrf_token:
            print("   ❌ CSRF token not found")
            return False
        
        # Submit test data
        form_data = {
            'csrf_token': csrf_token,
            'weight': '70.0',
            'height': '175.0', 
            'age': '30',
            'gender': 'male',
            'activity_level': 'moderate',
            'goal_type': 'maintain',
            'target_calories': '2000',
            'target_protein': '150',
            'target_carbs': '200',
            'target_fat': '65',
            'target_fiber': '25',
            'submit': 'Set Goals'
        }
        
        submit_response = session.post(f"{base_url}/dashboard/nutrition-goals", 
                                     data=form_data, allow_redirects=False)
        
        if submit_response.status_code == 302:
            print("   ✅ Form submission successful (redirected)")
        elif submit_response.status_code == 200:
            print("   ✅ Form submission processed")
        else:
            print(f"   ❌ Form submission failed: {submit_response.status_code}")
            return False
        
        print("\n🎉 USER FLOW TEST COMPLETED SUCCESSFULLY!")
        print("✅ Non-admin user can click 'Set Goals' without errors")
        return True
        
    except Exception as e:
        print(f"\n❌ Exception during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_exact_user_flow()
    
    print("\n" + "=" * 60)
    print("📋 FINAL RESULT")
    print("=" * 60)
    
    if success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ The reported issue has been RESOLVED!")
        print("✅ Non-admin users can now click 'Set Goals' without errors")
    else:
        print("❌ ISSUE NOT RESOLVED!")
        print("🔧 Additional fixes are needed")
    
    print("=" * 60)
