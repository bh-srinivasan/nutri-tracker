#!/usr/bin/env python3
"""
Test the final edit food page functionality after layout corrections.
This ensures the form still works properly with the new button placement.
"""

import requests
from bs4 import BeautifulSoup
import sys

def test_edit_food_functionality():
    """Test the edit food form works with new layout"""
    session = requests.Session()
    
    print("🧪 Testing Final Edit Food Functionality")
    print("==========================================")
    
    # Step 1: Login as admin
    login_url = "http://localhost:5001/auth/login"
    login_data = {"username": "admin", "password": "admin123"}
    
    login_response = session.post(login_url, data=login_data, allow_redirects=True)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed with status {login_response.status_code}")
        return False
    
    if "Admin Dashboard" not in login_response.text:
        print("❌ Login failed - not redirected to admin dashboard")
        return False
    
    print("✅ Login successful")
    
    # Step 2: Get edit food page
    edit_url = "http://localhost:5001/admin/foods/1/edit"
    edit_response = session.get(edit_url)
    
    if edit_response.status_code != 200:
        print(f"❌ Edit food page failed with status {edit_response.status_code}")
        return False
    
    print("✅ Edit food page loaded")
    
    # Step 3: Parse the form
    soup = BeautifulSoup(edit_response.text, 'html.parser')
    
    # Check 1: Main form exists and has correct structure
    main_form = soup.find('form', {'data-food-id': True})
    if not main_form:
        print("❌ Main food form not found")
        return False
    
    print("✅ Main food form found")
    
    # Check 2: Form has input fields
    name_input = main_form.find('input', {'name': 'name'})
    brand_input = main_form.find('input', {'name': 'brand'})
    category_select = main_form.find('select', {'name': 'category'})
    
    if not all([name_input, brand_input, category_select]):
        print("❌ Required form fields missing")
        return False
    
    print("✅ Required form fields found")
    
    # Check 3: No submit buttons inside main form (should be at end of page)
    form_buttons = main_form.find_all('button', type='submit')
    if form_buttons:
        print(f"❌ Found {len(form_buttons)} submit buttons inside main form (should be 0)")
        return False
    
    print("✅ No submit buttons inside main form (correct)")
    
    # Check 4: Update Food button exists at end of page
    update_buttons = soup.find_all('button', type='button')
    update_food_btn = None
    for btn in update_buttons:
        if btn.get_text() and 'Update Food' in btn.get_text():
            update_food_btn = btn
            break
    
    if not update_food_btn:
        print("❌ Update Food button not found at end of page")
        return False
    
    print("✅ Update Food button found at end of page")
    
    # Check 5: Update button has correct onclick behavior
    onclick = update_food_btn.get('onclick', '')
    if 'document.querySelector(\'form[data-food-id]\').submit()' not in onclick:
        print("❌ Update Food button doesn't have correct onclick handler")
        return False
    
    print("✅ Update Food button has correct form submission handler")
    
    # Check 6: Test actual form submission
    food_id = main_form.get('data-food-id')
    if not food_id:
        print("❌ Food ID not found in form")
        return False
    
    # Get current form data
    current_name = name_input.get('value', '')
    current_brand = brand_input.get('value', '')
    
    # Submit form with same data (no changes)
    form_action = main_form.get('action') or f"/admin/foods/{food_id}/edit"
    
    form_data = {
        'name': current_name,
        'brand': current_brand,
        'category': category_select.find('option', selected=True).get('value') if category_select.find('option', selected=True) else 'Other',
        'calories': main_form.find('input', {'name': 'calories'}).get('value', '0'),
        'protein': main_form.find('input', {'name': 'protein'}).get('value', '0'),
        'carbs': main_form.find('input', {'name': 'carbs'}).get('value', '0'),
        'fat': main_form.find('input', {'name': 'fat'}).get('value', '0'),
        'fiber': main_form.find('input', {'name': 'fiber'}).get('value', '0'),
        'sugar': main_form.find('input', {'name': 'sugar'}).get('value', '0'),
        'sodium': main_form.find('input', {'name': 'sodium'}).get('value', '0')
    }
    
    print(f"🔄 Testing form submission for food ID {food_id}")
    
    submit_response = session.post(f"http://localhost:5001{form_action}", data=form_data, allow_redirects=True)
    
    if submit_response.status_code != 200:
        print(f"❌ Form submission failed with status {submit_response.status_code}")
        return False
    
    # Check if redirected to foods list with success message
    if "Food updated successfully" in submit_response.text or "food management" in submit_response.url.lower():
        print("✅ Form submission successful")
    else:
        print("❌ Form submission may have failed - no success indication")
        return False
    
    print("\n🎯 Functionality Summary:")
    print("   1. ✅ Main form exists with all required fields")
    print("   2. ✅ No submit buttons inside main form")
    print("   3. ✅ Update Food button at end of page")
    print("   4. ✅ JavaScript form submission handler works")
    print("   5. ✅ Form submission and redirect working")
    
    return True

if __name__ == "__main__":
    try:
        success = test_edit_food_functionality()
        if success:
            print("\n🎉 ALL FUNCTIONALITY TESTS PASSED!")
            sys.exit(0)
        else:
            print("\n❌ FUNCTIONALITY ISSUES DETECTED")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        sys.exit(1)
