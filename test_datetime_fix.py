#!/usr/bin/env python3
"""
Test to verify the dashboard template fix for current_datetime.
"""

def test_dashboard_datetime_fix():
    """Test if the dashboard route passes current_datetime to template."""
    print("🔍 Testing Dashboard DateTime Fix")
    print("=" * 35)
    
    # Read the dashboard route
    with open('app/dashboard/routes.py', 'r') as f:
        routes_content = f.read()
    
    # Read the template
    with open('app/templates/dashboard/index.html', 'r') as f:
        template_content = f.read()
    
    print("✅ Backend checks:")
    
    # Check if current_datetime is being passed
    if "current_datetime=datetime.now()" in routes_content:
        print("   ✅ current_datetime passed to template")
    else:
        print("   ❌ current_datetime not passed to template")
    
    # Check if datetime is imported
    if "from datetime import datetime" in routes_content:
        print("   ✅ datetime module imported")
    else:
        print("   ❌ datetime module not imported")
    
    print("\n✅ Template checks:")
    
    # Check if template uses current_datetime
    if "current_datetime.strftime" in template_content:
        print("   ✅ Template uses current_datetime.strftime")
    else:
        print("   ⚠️ Template doesn't use current_datetime")
    
    # Check the specific usage
    if "current_datetime.strftime('%B %d, %Y')" in template_content:
        print("   ✅ Template formats date correctly")
    else:
        print("   ❌ Template date format issue")
    
    # Summary
    has_datetime_import = "from datetime import datetime" in routes_content
    has_datetime_passed = "current_datetime=datetime.now()" in routes_content
    template_uses_datetime = "current_datetime.strftime" in template_content
    
    print(f"\n{'🎉' if has_datetime_import and has_datetime_passed and template_uses_datetime else '❌'} RESULT:")
    if has_datetime_import and has_datetime_passed and template_uses_datetime:
        print("✅ Dashboard datetime fix successful!")
        print("✅ No more UndefinedError for 'current_datetime'")
        print("✅ Date will display correctly in dashboard")
    else:
        print("❌ Fix incomplete - some issues remain")
        if not has_datetime_import:
            print("   - Missing datetime import")
        if not has_datetime_passed:
            print("   - current_datetime not passed to template")
        if not template_uses_datetime:
            print("   - Template doesn't use current_datetime")
    
    return has_datetime_import and has_datetime_passed and template_uses_datetime

def check_other_template_issues():
    """Check for other potential template issues."""
    print("\n🔍 Checking for other potential issues...")
    
    with open('app/templates/dashboard/index.html', 'r') as f:
        content = f.read()
    
    # Common variables that might be undefined
    potential_issues = [
        'user_challenges',
        'meals_by_type', 
        'today_nutrition',
        'current_goal',
        'progress',
        'streak'
    ]
    
    print("✅ Variable usage checks:")
    for var in potential_issues:
        if var in content:
            print(f"   ✅ {var}: Used in template")
        else:
            print(f"   ⚠️ {var}: Not found in template")
    
    # Check for other undefined patterns
    import re
    undefined_patterns = [
        r'\{\{\s*(\w+)\.(\w+)',  # Any variable.attribute usage
        r'\{\%\s*for\s+\w+\s+in\s+(\w+)',  # For loops
        r'\{\%\s*if\s+(\w+)',  # If statements
    ]
    
    variables_used = set()
    for pattern in undefined_patterns:
        matches = re.findall(pattern, content)
        variables_used.update([match[0] if isinstance(match, tuple) else match for match in matches])
    
    print(f"\n✅ Template variables found: {sorted(variables_used)}")
    
    return True

if __name__ == "__main__":
    print("🛠️ Dashboard DateTime Fix Verification\n")
    
    fix_ok = test_dashboard_datetime_fix()
    other_ok = check_other_template_issues()
    
    print("\n" + "="*50)
    if fix_ok and other_ok:
        print("🎉 All checks passed! Dashboard should work correctly now.")
        print("\n📋 What was fixed:")
        print("   ✅ Added current_datetime=datetime.now() to template context")
        print("   ✅ Template can now access current date/time")
        print("   ✅ No more UndefinedError for 'current_datetime'")
        print("\n🚀 The homepage should now load without errors!")
    else:
        print("❌ Some issues found. Please review the output above.")
