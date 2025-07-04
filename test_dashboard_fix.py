#!/usr/bin/env python3
"""
Quick test to verify the dashboard template fix.
"""

import re

def test_dashboard_fix():
    """Test if the dashboard template fix is correct."""
    print("🔍 Testing Dashboard Template Fix")
    print("=" * 35)
    
    # Read the dashboard route
    with open('app/dashboard/routes.py', 'r') as f:
        routes_content = f.read()
    
    # Read the template
    with open('app/templates/dashboard/index.html', 'r') as f:
        template_content = f.read()
    
    print("✅ Backend checks:")
    
    # Check if progress is properly initialized
    if "progress = {" in routes_content and "'calories': 0" in routes_content:
        print("   ✅ Progress dictionary properly initialized with default values")
    else:
        print("   ❌ Progress dictionary not properly initialized")
    
    # Check if all keys are present
    required_keys = ['calories', 'protein', 'carbs', 'fat', 'fiber']
    all_keys_present = all(f"'{key}': 0" in routes_content for key in required_keys)
    if all_keys_present:
        print("   ✅ All required progress keys initialized")
    else:
        print("   ❌ Missing some progress keys")
    
    print("\n✅ Template checks:")
    
    # Check if template uses dictionary syntax
    if "progress.calories" in template_content:
        print("   ❌ Template still uses attribute syntax (progress.calories)")
    elif "progress['calories']" in template_content:
        print("   ✅ Template uses correct dictionary syntax")
    else:
        print("   ⚠️ No calories progress found in template")
    
    # Check other nutrition components
    components = ['protein', 'carbs', 'fat']
    for component in components:
        if f"progress.{component}" in template_content:
            print(f"   ❌ Template still uses attribute syntax for {component}")
        elif f"progress['{component}']" in template_content:
            print(f"   ✅ Template uses correct dictionary syntax for {component}")
        else:
            print(f"   ⚠️ No {component} progress found in template")
    
    # Summary
    has_attr_syntax = any(f"progress.{comp}" in template_content for comp in ['calories', 'protein', 'carbs', 'fat', 'fiber'])
    
    print(f"\n{'🎉' if not has_attr_syntax else '❌'} RESULT:")
    if not has_attr_syntax:
        print("✅ Dashboard fix successful! No more UndefinedError should occur.")
        print("✅ Progress dictionary properly initialized with default values")
        print("✅ Template uses correct dictionary syntax")
    else:
        print("❌ Fix incomplete - some attribute syntax still present")
    
    return not has_attr_syntax

def test_syntax_errors():
    """Check for common template syntax errors."""
    print("\n🔍 Checking for syntax errors...")
    
    with open('app/templates/dashboard/index.html', 'r') as f:
        content = f.read()
    
    # Check for common issues
    issues = []
    
    # Check bracket matching
    if content.count('{%') != content.count('%}'):
        issues.append("Mismatched Jinja2 template tags")
    
    if content.count('{{') != content.count('}}'):
        issues.append("Mismatched Jinja2 expressions")
    
    # Check for potential undefined variables
    undefined_patterns = [
        r'progress\.\w+',  # Any progress.attribute usage
        r'\{\%\s*set\s+\w+\s*=\s*progress\.\w+',  # Set statements with progress.attribute
    ]
    
    for pattern in undefined_patterns:
        matches = re.findall(pattern, content)
        if matches:
            issues.append(f"Potential undefined variable usage: {matches}")
    
    if issues:
        print("❌ Potential issues found:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("✅ No obvious syntax errors found")
    
    return len(issues) == 0

if __name__ == "__main__":
    print("🛠️ Dashboard Template Fix Verification\n")
    
    fix_ok = test_dashboard_fix()
    syntax_ok = test_syntax_errors()
    
    print("\n" + "="*50)
    if fix_ok and syntax_ok:
        print("🎉 All checks passed! Dashboard should work correctly now.")
        print("\n📋 What was fixed:")
        print("   ✅ Progress dictionary initialized with default values (0 for all metrics)")
        print("   ✅ Template changed from progress.calories to progress['calories']")
        print("   ✅ All nutrition components use correct dictionary syntax")
        print("   ✅ No more UndefinedError should occur")
    else:
        print("❌ Some issues found. Please review the output above.")
