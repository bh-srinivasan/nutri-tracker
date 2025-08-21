#!/usr/bin/env python3
"""
Test to verify the delete button setup for admin foods page.
"""

import os
from pathlib import Path

def check_admin_foods_delete_setup():
    """Check the current setup for admin foods delete functionality"""
    
    print("=== ADMIN FOODS DELETE BUTTON ANALYSIS ===\n")
    
    # Check template file
    template_file = Path('app/templates/admin/foods.html')
    if template_file.exists():
        content = template_file.read_text(encoding='utf-8')
        
        print("1. TEMPLATE FILE: app/templates/admin/foods.html")
        print("   ✅ File exists")
        
        # Check for delete button
        if 'delete-food-btn' in content:
            print("   ✅ delete-food-btn class found")
            
            # Count delete buttons
            import re
            delete_btn_matches = re.findall(r'class="[^"]*delete-food-btn[^"]*"', content)
            print(f"   ✅ Found {len(delete_btn_matches)} delete button(s)")
            
            # Check data attribute
            if 'data-food-id' in content:
                print("   ✅ data-food-id attribute found")
            else:
                print("   ❌ data-food-id attribute missing")
                
        else:
            print("   ❌ delete-food-btn class not found")
            
    else:
        print("   ❌ Template file not found")
    
    print()
    
    # Check JavaScript file
    js_file = Path('app/static/js/admin.js')
    if js_file.exists():
        content = js_file.read_text(encoding='utf-8')
        
        print("2. JAVASCRIPT FILE: app/static/js/admin.js")
        print("   ✅ File exists")
        
        # Check for event handler
        if ".closest('.delete-food-btn')" in content:
            print("   ✅ Event handler for delete-food-btn found")
        else:
            print("   ❌ Event handler for delete-food-btn missing")
            
        # Check for delete function
        if "Admin.foods.delete" in content:
            print("   ✅ Admin.foods.delete function call found")
        else:
            print("   ❌ Admin.foods.delete function call missing")
            
        # Check for delete function definition
        if "delete: async function(foodId)" in content:
            print("   ✅ delete function definition found")
        else:
            print("   ❌ delete function definition missing")
            
    else:
        print("   ❌ JavaScript file not found")
    
    print()
    
    # Check API file
    api_file = Path('app/api/routes.py')
    if api_file.exists():
        content = api_file.read_text(encoding='utf-8')
        
        print("3. API FILE: app/api/routes.py")
        print("   ✅ File exists")
        
        # Check for DELETE endpoint
        if "'/admin/foods/<int:food_id>', methods=['DELETE']" in content:
            print("   ✅ DELETE endpoint route found")
        else:
            print("   ❌ DELETE endpoint route missing")
            
        # Check for function
        if "def delete_food_admin_api(food_id):" in content:
            print("   ✅ delete_food_admin_api function found")
        else:
            print("   ❌ delete_food_admin_api function missing")
            
    else:
        print("   ❌ API file not found")
    
    print()
    
    print("=== SUMMARY ===")
    print("The delete button for admin foods is in:")
    print("📁 Template: app/templates/admin/foods.html")
    print("📁 JavaScript: app/static/js/admin.js") 
    print("📁 API: app/api/routes.py")
    print()
    print("This is the 'Manage Foods' page in the admin section.")
    print("The delete button has class 'delete-food-btn' and data-food-id attribute.")

if __name__ == "__main__":
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    check_admin_foods_delete_setup()
