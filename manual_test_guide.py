#!/usr/bin/env python3
"""
Manual test verification for nutrition goals JavaScript functionality.
This script provides instructions for manual testing.
"""

def print_manual_test_instructions():
    """Print comprehensive manual testing instructions."""
    print("🧪 COMPREHENSIVE MANUAL TEST INSTRUCTIONS")
    print("=" * 50)
    
    print("\n1. 🚀 START THE APPLICATION")
    print("   - Ensure Flask app is running: python app.py")
    print("   - Open browser to: http://127.0.0.1:5001")
    
    print("\n2. 🔐 LOGIN/REGISTER")
    print("   - If admin exists: Login with admin/admin123")
    print("   - If no admin: Register a new user account")
    print("   - Any user can test this functionality (not admin-only)")
    
    print("\n3. 🎯 NAVIGATE TO NUTRITION GOALS")
    print("   - Go to Dashboard > Nutrition Goals")
    print("   - OR direct URL: http://127.0.0.1:5001/dashboard/nutrition-goals")
    
    print("\n4. 🔍 INSPECT FORM ELEMENTS")
    print("   - Open browser Developer Tools (F12)")
    print("   - Go to Console tab")
    print("   - Look for any JavaScript errors")
    print("   - Go to Elements tab")
    print("   - Find the duration dropdown: should have id='target_duration'")
    print("   - Find the target date field: should have id='target_date'")
    
    print("\n5. 🧪 TEST DURATION TO DATE FUNCTIONALITY")
    print("   Test each duration option and verify target date updates:")
    print("   ✅ Select '2 weeks' → Target date should be ~14 days from today")
    print("   ✅ Select '1 month' → Target date should be ~30 days from today")
    print("   ✅ Select '2 months' → Target date should be ~60 days from today")
    print("   ✅ Select '3 months' → Target date should be ~90 days from today")
    print("   ✅ Select '6 months' → Target date should be ~180 days from today")
    print("   ✅ Select '1 year' → Target date should be ~365 days from today")
    
    print("\n6. 📝 CHECK CONSOLE OUTPUT")
    print("   In the browser console, you should see debug messages:")
    print("   - 'updateTargetDate function called'")
    print("   - 'Duration selected: [duration_value]'")
    print("   - 'Calculated target date: [date]'")
    print("   - 'Formatted date set: [YYYY-MM-DD]'")
    
    print("\n7. ⚠️  TROUBLESHOOTING")
    print("   If target date is NOT updating:")
    print("   - Check console for errors (red text)")
    print("   - Verify element IDs in Elements tab")
    print("   - Check if JavaScript functions are defined:")
    print("     Type in console: typeof updateTargetDate")
    print("     Should return: 'function'")
    print("   - Check if duration mapping exists:")
    print("     Type in console: durationToDays")
    print("     Should show object with duration mappings")
    
    print("\n8. 🎯 ADDITIONAL TESTS")
    print("   - Test manual date entry (should update duration appropriately)")
    print("   - Test the 'Clear' button (X button next to date field)")
    print("   - Test 'Custom timeframe' option")
    
    print("\n9. ✅ SUCCESS CRITERIA")
    print("   The functionality is working if:")
    print("   ✅ Selecting any duration automatically fills the target date")
    print("   ✅ The calculated date is approximately correct (±2 days)")
    print("   ✅ No JavaScript errors in console")
    print("   ✅ Manual date entry works")
    print("   ✅ Clear button works")
    
    print("\n10. 📊 REPORT RESULTS")
    print("    Please test and report:")
    print("    - Which duration options work correctly")
    print("    - Any JavaScript errors you see")
    print("    - Whether the dates are calculated correctly")
    print("    - Any other issues observed")

def check_javascript_in_template():
    """Check if the JavaScript is properly embedded in the template."""
    template_path = "app/templates/dashboard/nutrition_goals.html"
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("\n🔍 TEMPLATE ANALYSIS")
        print("=" * 30)
        
        # Check for key JavaScript elements
        checks = [
            ("updateTargetDate function", "function updateTargetDate()"),
            ("durationToDays mapping", "durationToDays = {"),
            ("target_duration reference", "getElementById('target_duration')"),
            ("target_date reference", "getElementById('target_date')"),
            ("onchange handler", "onchange=\"updateTargetDate()\""),
            ("addEventListener setup", "addEventListener('change'"),
        ]
        
        for name, pattern in checks:
            if pattern in content:
                print(f"✅ {name}: Found")
            else:
                print(f"❌ {name}: Missing")
        
        # Count function definitions
        function_count = content.count("function ")
        print(f"\n📊 JavaScript functions found: {function_count}")
        
        # Check for common issues
        if "getElementById('targetDuration')" in content:
            print("⚠️  WARNING: Old targetDuration ID found (should be target_duration)")
        
        if "getElementById('targetDate')" in content:
            print("⚠️  WARNING: Old targetDate ID found (should be target_date)")
        
        return True
        
    except FileNotFoundError:
        print(f"❌ Template file not found: {template_path}")
        return False
    except Exception as e:
        print(f"❌ Error reading template: {e}")
        return False

def main():
    """Main function."""
    print("🧪 NUTRITION GOALS FUNCTIONALITY TEST SUITE")
    print("=" * 50)
    
    # Check template
    template_ok = check_javascript_in_template()
    
    if template_ok:
        print("\n✅ Template analysis completed")
    else:
        print("\n❌ Template analysis failed")
    
    # Print manual test instructions
    print_manual_test_instructions()
    
    print("\n" + "=" * 50)
    print("🎯 READY FOR MANUAL TESTING!")
    print("Please follow the instructions above and test the functionality.")
    print("=" * 50)

if __name__ == "__main__":
    main()
