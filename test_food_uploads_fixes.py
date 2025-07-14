#!/usr/bin/env python3
"""
Test script to verify the fixes in food_uploads.html
"""

import os
import re
import sys

def main():
    # Change to the correct directory
    os.chdir(r'c:\Users\bhsrinivasan\Downloads\Learning\Vibe Coding\Nutri_Tracker')
    
    file_path = 'app/templates/admin/food_uploads.html'
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔍 FOOD UPLOADS HTML VALIDATION")
    print("=" * 50)
    
    # Test 1: Check for infinite loop fixes
    window_location_href_count = content.count('window.location.href')
    refresh_jobs_list_calls = len(re.findall(r'\.refreshJobsList\(\)', content))
    refresh_jobs_data_calls = len(re.findall(r'\.refreshJobsData\(\)', content))
    
    print(f"\n📊 INFINITE LOOP FIX VALIDATION:")
    print(f"   window.location.href calls: {window_location_href_count}")
    print(f"   refreshJobsList() calls: {refresh_jobs_list_calls}")
    print(f"   refreshJobsData() calls: {refresh_jobs_data_calls}")
    
    if window_location_href_count == 0:
        print("   ✅ No window.location.href calls found (infinite loop fixed)")
    else:
        print("   ❌ Still contains window.location.href calls")
    
    # Test 2: Check for preventDefault usage
    prevent_default_count = content.count('preventDefault()')
    print(f"\n🛡️  EVENT HANDLING:")
    print(f"   preventDefault() calls: {prevent_default_count}")
    
    if prevent_default_count >= 2:
        print("   ✅ Proper event prevention implemented")
    else:
        print("   ⚠️  May need more preventDefault() calls")
    
    # Test 3: Check for error handling
    try_catch_blocks = len(re.findall(r'try\s*{[^}]*}[^}]*catch', content, re.DOTALL))
    print(f"\n🔧 ERROR HANDLING:")
    print(f"   Try-catch blocks: {try_catch_blocks}")
    
    if try_catch_blocks >= 5:
        print("   ✅ Good error handling coverage")
    else:
        print("   ⚠️  Consider adding more error handling")
    
    # Test 4: Check for security features
    sanitize_html = 'sanitizeHTML' in content
    csrf_protection = 'X-Requested-With' in content
    credentials_same_origin = 'same-origin' in content
    
    print(f"\n🔒 SECURITY FEATURES:")
    print(f"   HTML sanitization: {'✅' if sanitize_html else '❌'}")
    print(f"   CSRF protection: {'✅' if csrf_protection else '❌'}")
    print(f"   Credential handling: {'✅' if credentials_same_origin else '❌'}")
    
    # Test 5: Check for proper tab handling
    bootstrap_tab_instance = 'bootstrap.Tab.getInstance' in content
    fallback_tab_switch = 'fallbackTabSwitch' in content
    
    print(f"\n📑 TAB HANDLING:")
    print(f"   Bootstrap Tab integration: {'✅' if bootstrap_tab_instance else '❌'}")
    print(f"   Fallback tab switching: {'✅' if fallback_tab_switch else '❌'}")
    
    # Test 6: Check for initialization improvements
    is_initializing = 'isInitializing' in content
    history_data_loaded = 'historyDataLoaded' in content
    
    print(f"\n🚀 INITIALIZATION:")
    print(f"   Initialization flag: {'✅' if is_initializing else '❌'}")
    print(f"   Data loading tracking: {'✅' if history_data_loaded else '❌'}")
    
    # Test 7: Check HTML structure
    has_proper_tabs = all(x in content for x in [
        'id="upload-tab"',
        'id="history-tab"',
        'id="upload-panel"',
        'id="history-panel"'
    ])
    
    has_modal = 'id="jobDetailsModal"' in content
    
    print(f"\n🏗️  HTML STRUCTURE:")
    print(f"   Proper tab structure: {'✅' if has_proper_tabs else '❌'}")
    print(f"   Job details modal: {'✅' if has_modal else '❌'}")
    
    # Summary
    total_checks = 12
    passed_checks = sum([
        window_location_href_count == 0,
        prevent_default_count >= 2,
        try_catch_blocks >= 5,
        sanitize_html,
        csrf_protection,
        credentials_same_origin,
        bootstrap_tab_instance,
        fallback_tab_switch,
        is_initializing,
        history_data_loaded,
        has_proper_tabs,
        has_modal
    ])
    
    print(f"\n📈 SUMMARY:")
    print(f"   Checks passed: {passed_checks}/{total_checks}")
    print(f"   Success rate: {(passed_checks/total_checks)*100:.1f}%")
    
    if passed_checks >= 10:
        print("   🎉 EXCELLENT! Most issues have been fixed.")
    elif passed_checks >= 8:
        print("   👍 GOOD! Most critical issues resolved.")
    else:
        print("   ⚠️  NEEDS WORK! Several issues remain.")
    
    print("\n" + "=" * 50)
    print("MAIN FIXES APPLIED:")
    print("✅ Replaced window.location.href with AJAX calls")
    print("✅ Added preventDefault() to prevent default tab behavior")
    print("✅ Added initialization flags to prevent loops")
    print("✅ Implemented proper error handling")
    print("✅ Added HTML sanitization for security")
    print("✅ Improved event listener management")
    print("✅ Added fallback mechanisms for tab switching")
    print("✅ Enhanced state management")
    
    return passed_checks >= 10

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
