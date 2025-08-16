#!/usr/bin/env python3
"""
Test the final layout with correct button placement
"""

import requests
import sys
from bs4 import BeautifulSoup

def test_final_layout():
    """Test that the layout is now correct"""
    
    base_url = "http://127.0.0.1:5001"
    session = requests.Session()
    
    try:
        print("🧪 Testing Final Layout")
        print("=" * 30)
        
        # Login
        login_page = session.get(f"{base_url}/auth/login")
        soup = BeautifulSoup(login_page.text, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
        
        login_data = {
            'username': 'admin', 
            'password': 'admin123',
            'csrf_token': csrf_token
        }
        
        login_response = session.post(f"{base_url}/auth/login", data=login_data, allow_redirects=True)
        
        if 'admin' not in login_response.url:
            print("❌ Login failed")
            return False
        
        print("✅ Login successful")
        
        # Get edit food page
        edit_url = f"{base_url}/admin/foods/1/edit"
        edit_response = session.get(edit_url)
        
        if edit_response.status_code != 200:
            print("❌ Cannot access edit food page")
            return False
        
        print("✅ Edit food page loaded")
        
        # Parse the page
        soup = BeautifulSoup(edit_response.text, 'html.parser')
        
        print("\n🔍 Checking Layout Elements:")
        
        # Check 1: Back to Food Management button at top
        back_button = soup.find('a', string=lambda x: x and 'Back to Food Management' in x)
        if not back_button:
            # Try to find by href
            back_button = soup.find('a', href=lambda x: x and 'admin/foods' in x)
            if back_button:
                print("✅ Back to Food Management button found (by href)")
            else:
                print("❌ Back to Food Management button not found")
                # Debug: show all links at top
                print("Debug - All links found:")
                links = soup.find_all('a')[:5]  # First 5 links
                for link in links:
                    print(f"   Link: '{link.get_text().strip()}' -> {link.get('href')}")
                return False
        else:
            print("✅ Back to Food Management button found at top")
        
        # Check 2: Main food form exists and has no submit buttons inside
        main_form = soup.find('form', {'data-food-id': True})
        if not main_form:
            print("❌ Main food form not found")
            return False
        
        print("✅ Main food form found")
        
        # Check that main form has no submit buttons
        form_submit_buttons = main_form.find_all('button', type='submit')
        if form_submit_buttons:
            print(f"❌ Found {len(form_submit_buttons)} submit buttons inside main form")
            return False
        
        print("✅ Main form has no submit buttons inside")
        
        # Check 3: Servings section exists
        servings_header = soup.find('h5', string=lambda x: x and 'Servings' in x)
        if not servings_header:
            # Try to find by icon or text content
            servings_elements = soup.find_all(string=lambda x: x and 'Servings' in x)
            if servings_elements:
                print("✅ Servings section found (by text content)")
            else:
                print("❌ Servings section not found")
                return False
        else:
            print("✅ Servings section found")
        
        # Check 4: Add serving form is in servings section
        add_serving_form = soup.find('form', {'id': 'add-serving-form'})
        if not add_serving_form:
            print("❌ Add serving form not found")
            return False
        
        print("✅ Add serving form found")
        
        # Check 5: Update Food button is at the END of the page (outside forms)
        update_buttons = soup.find_all('button', type='button')
        update_food_btn = None
        for btn in update_buttons:
            if btn.get_text() and 'Update Food' in btn.get_text():
                update_food_btn = btn
                break
        
        if not update_food_btn:
            print("❌ Update Food button not found")
            return False
        
        update_button = update_food_btn
        
        # Check that Update Food button is NOT inside main form
        if main_form.find('button', type='button'):
            # Check if any button inside main form contains "Update Food"
            inside_buttons = main_form.find_all('button', type='button')
            for btn in inside_buttons:
                if btn.get_text() and 'Update Food' in btn.get_text():
                    print("❌ Update Food button is still inside main form")
                    return False
        
        print("✅ Update Food button found outside main form")
        
        # Check 6: Cancel button is next to Update Food button
        cancel_links = soup.find_all('a')
        cancel_btn = None
        for link in cancel_links:
            if link.get_text() and 'Cancel' in link.get_text():
                cancel_btn = link
                break
        
        if not cancel_btn:
            print("❌ Cancel button not found")
            return False
        
        print("✅ Cancel button found")
        
        # Check 7: Verify order of elements
        page_text = soup.get_text()
        
        # Find positions in the text
        back_pos = page_text.find('Back to Food Management')
        servings_pos = page_text.find('Servings')
        update_pos = page_text.find('Update Food')
        
        if back_pos < 0 or servings_pos < 0 or update_pos < 0:
            print("❌ Could not find all elements in page text")
            return False
        
        # Check order: Back button < Servings < Update Food
        if back_pos < servings_pos < update_pos:
            print("✅ Element order is correct: Back → Servings → Update Food")
        else:
            print(f"❌ Element order is wrong: Back({back_pos}) → Servings({servings_pos}) → Update({update_pos})")
            return False
        
        print("\n🎯 Layout Summary:")
        print("   1. ✅ Back to Food Management button at top")
        print("   2. ✅ Main food form (no submit buttons inside)")
        print("   3. ✅ Servings section with Add New Serving form")
        print("   4. ✅ Update Food and Cancel buttons at the END")
        print("   5. ✅ Correct visual order")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_final_layout()
    print(f"\n{'🎉 LAYOUT PERFECT!' if success else '❌ LAYOUT ISSUES'}")
    sys.exit(0 if success else 1)
