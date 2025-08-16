#!/usr/bin/env python3
"""
Simple verification of Goals menu item implementation
"""

def simple_verification():
    """Simple check for Goals menu implementation"""
    
    print("🔍 Checking Goals menu item implementation...")
    
    try:
        # Read base template
        with open('app/templates/base.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check key components
        checks = [
            ("Goals URL", "url_for('dashboard.nutrition_goals')" in content),
            ("Target icon", "fa-target" in content),
            ("Goals text", ">Goals<" in content),
            ("Non-admin section", "{% else %}" in content and "Dashboard" in content)
        ]
        
        all_passed = True
        for check_name, result in checks:
            status = "✅" if result else "❌"
            print(f"   {status} {check_name}: {'PASS' if result else 'FAIL'}")
            if not result:
                all_passed = False
        
        # Count menu items in non-admin section
        lines = content.split('\n')
        in_non_admin = False
        menu_items = []
        
        for line in lines:
            if "{% else %}" in line:
                in_non_admin = True
            elif "{% endif %}" in line and in_non_admin:
                break
            elif in_non_admin and "<i class=\"fas fa-" in line and "me-1\"></i>" in line:
                # Extract menu item name
                import re
                match = re.search(r'<i class="fas fa-[^"]*"></i>([^<]*)', line)
                if match:
                    menu_items.append(match.group(1).strip())
        
        print(f"\n📋 Found menu items: {menu_items}")
        
        expected_items = ["Dashboard", "Goals", "Log Meal", "History", "Reports"]
        if menu_items == expected_items:
            print("✅ Menu order is correct!")
        else:
            print("❌ Menu order issues detected")
            all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = simple_verification()
    
    if success:
        print("\n🎉 SUCCESS: Goals menu item properly implemented!")
        print("📝 Implementation details:")
        print("   • Goals menu item added between Dashboard and Log Meal")
        print("   • Uses target icon (fas fa-target)")
        print("   • Links to dashboard.nutrition_goals route")
        print("   • Visible only for non-admin users")
    else:
        print("\n💥 ISSUES DETECTED in Goals menu implementation")
    
    exit(0 if success else 1)
