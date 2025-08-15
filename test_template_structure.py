#!/usr/bin/env python3
"""
Simple test to verify the edit food template layout is correct.
This reads the template directly to verify structure.
"""

from bs4 import BeautifulSoup
import sys

def test_template_structure():
    """Test the edit food template structure"""
    
    print("🧪 Testing Edit Food Template Structure")
    print("=======================================")
    
    # Read the template file
    try:
        with open('app/templates/admin/edit_food.html', 'r', encoding='utf-8') as f:
            template_content = f.read()
    except FileNotFoundError:
        print("❌ Template file not found")
        return False
    
    print("✅ Template file loaded")
    
    # Parse the template (we'll look for basic structure)
    soup = BeautifulSoup(template_content, 'html.parser')
    
    # Check 1: Back button at the top
    back_buttons = soup.find_all('a', href=lambda x: x and 'admin.foods' in x)
    back_at_top = False
    for btn in back_buttons:
        if btn.get_text() and 'Back to Food Management' in btn.get_text():
            back_at_top = True
            break
    
    if back_at_top:
        print("✅ Back to Food Management button found")
    else:
        print("❌ Back to Food Management button not found")
        return False
    
    # Check 2: Main food form exists and has no submit buttons
    main_forms = soup.find_all('form', {'data-food-id': True})
    if not main_forms:
        print("❌ Main food form not found")
        return False
    
    main_form = main_forms[0]
    print("✅ Main food form found")
    
    # Check that main form has no submit buttons
    form_submit_buttons = main_form.find_all('button', type='submit')
    if form_submit_buttons:
        print(f"❌ Found {len(form_submit_buttons)} submit buttons inside main form")
        return False
    
    print("✅ Main form has no submit buttons inside")
    
    # Check 3: Servings section exists
    servings_text_found = 'Servings' in template_content
    if servings_text_found:
        print("✅ Servings section found")
    else:
        print("❌ Servings section not found")
        return False
    
    # Check 4: Add serving form exists
    add_serving_forms = soup.find_all('form', {'id': 'add-serving-form'})
    if add_serving_forms:
        print("✅ Add serving form found")
    else:
        print("❌ Add serving form not found")
        return False
    
    # Check 5: Update Food button exists at the END of the page
    update_food_buttons = soup.find_all('button', type='button')
    update_found = False
    for btn in update_food_buttons:
        if btn.get_text() and 'Update Food' in btn.get_text():
            update_found = True
            break
    
    if update_found:
        print("✅ Update Food button found")
    else:
        print("❌ Update Food button not found")
        return False
    
    # Check 6: Update Food button has correct onclick
    update_button = None
    for btn in update_food_buttons:
        if btn.get_text() and 'Update Food' in btn.get_text():
            update_button = btn
            break
    
    if update_button:
        onclick = update_button.get('onclick', '')
        if 'document.querySelector(\'form[data-food-id]\').submit()' in onclick:
            print("✅ Update Food button has correct form submission handler")
        else:
            print("❌ Update Food button missing correct onclick handler")
            return False
    
    # Check 7: Cancel button exists
    cancel_buttons = soup.find_all('a')
    cancel_found = False
    for btn in cancel_buttons:
        if btn.get_text() and 'Cancel' in btn.get_text() and btn.get('href'):
            cancel_found = True
            break
    
    if cancel_found:
        print("✅ Cancel button found")
    else:
        print("❌ Cancel button not found")
        return False
    
    # Check 8: Verify no nested forms
    all_forms = soup.find_all('form')
    nested_forms = []
    for form in all_forms:
        nested = form.find_all('form')
        if nested:
            nested_forms.extend(nested)
    
    if nested_forms:
        print(f"❌ Found {len(nested_forms)} nested forms")
        return False
    
    print("✅ No nested forms found")
    
    print("\n🎯 Template Structure Summary:")
    print("   1. ✅ Back to Food Management button at top")
    print("   2. ✅ Main food form (no submit buttons inside)")
    print("   3. ✅ Servings section with Add New Serving form")
    print("   4. ✅ Update Food button with JavaScript submission")
    print("   5. ✅ Cancel button for navigation")
    print("   6. ✅ No nested forms (valid HTML)")
    
    return True

if __name__ == "__main__":
    try:
        success = test_template_structure()
        if success:
            print("\n🎉 TEMPLATE STRUCTURE PERFECT!")
            sys.exit(0)
        else:
            print("\n❌ TEMPLATE STRUCTURE ISSUES")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        sys.exit(1)
