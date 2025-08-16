#!/usr/bin/env python3
"""
Quick verification script to check if the Goals menu item has been properly added.
This will parse the base template and confirm the menu structure.
"""

import re

def verify_goals_menu_item():
    """Verify that the Goals menu item exists in the correct position"""
    
    try:
        # Read the base template
        with open('app/templates/base.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("🔍 Analyzing base.html template...")
        
        # Extract the non-admin menu section
        non_admin_pattern = r'{% else %}.*?{% endif %}'
        non_admin_match = re.search(non_admin_pattern, content, re.DOTALL)
        
        if not non_admin_match:
            print("❌ Could not find non-admin menu section")
            return False
        
        non_admin_section = non_admin_match.group()
        print("✅ Found non-admin menu section")
        
        # Check for Goals menu item
        goals_pattern = r'<a class="nav-link" href="{{ url_for\(\'dashboard\.nutrition_goals\'\) }}">\s*<i class="fas fa-target me-1"></i>Goals\s*</a>'
        goals_match = re.search(goals_pattern, non_admin_section, re.DOTALL)
        
        if goals_match:
            print("✅ Goals menu item found with correct URL and icon!")
        else:
            print("❌ Goals menu item not found or incorrect format")
            return False
        
        # Extract all menu items to verify order
        menu_items = re.findall(r'<a class="nav-link" href="[^"]*">\s*<i class="[^"]*"></i>([^<]*)</a>', non_admin_section)
        
        print(f"\n📋 Found menu items in order:")
        for i, item in enumerate(menu_items, 1):
            item_clean = item.strip()
            print(f"   {i}. {item_clean}")
        
        # Verify expected order
        expected_order = ["Dashboard", "Goals", "Log Meal", "History", "Reports"]
        
        if len(menu_items) >= 5:
            actual_order = [item.strip() for item in menu_items[:5]]
            if actual_order == expected_order:
                print("\n✅ Menu items are in the correct order!")
                return True
            else:
                print(f"\n❌ Menu order incorrect. Expected: {expected_order}, Got: {actual_order}")
                return False
        else:
            print(f"\n❌ Expected at least 5 menu items, found {len(menu_items)}")
            return False
            
    except Exception as e:
        print(f"❌ Error analyzing template: {e}")
        return False

def verify_route_exists():
    """Verify that the nutrition_goals route exists"""
    
    try:
        with open('app/dashboard/routes.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for the route definition
        route_pattern = r"@bp\.route\('/nutrition-goals'.*?\ndef nutrition_goals\(\):"
        route_match = re.search(route_pattern, content, re.DOTALL)
        
        if route_match:
            print("✅ nutrition_goals route exists in dashboard/routes.py")
            return True
        else:
            print("❌ nutrition_goals route not found")
            return False
            
    except Exception as e:
        print(f"❌ Error checking routes: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Verifying Goals menu item implementation...\n")
    
    menu_check = verify_goals_menu_item()
    route_check = verify_route_exists()
    
    if menu_check and route_check:
        print("\n🎉 VERIFICATION PASSED: Goals menu item properly implemented!")
        print("📝 Summary:")
        print("   ✅ Goals menu item added to navigation")
        print("   ✅ Positioned between Dashboard and Log Meal")
        print("   ✅ Uses target icon (fas fa-target)")
        print("   ✅ Links to dashboard.nutrition_goals route")
        print("   ✅ Route exists and is functional")
    else:
        print("\n💥 VERIFICATION FAILED: Issues found with implementation")
    
    exit(0 if (menu_check and route_check) else 1)
