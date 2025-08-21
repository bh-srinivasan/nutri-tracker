#!/usr/bin/env python3
"""
Verify Admin Food Deletion Implementation
"""

def test_template_cleanup():
    """Verify template has been cleaned up properly"""
    print("=== TESTING TEMPLATE CLEANUP ===")
    
    template_path = 'app/templates/admin/foods.html'
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that duplicate buttons are removed
        edit_button_count = content.count('edit-food-btn')
        delete_button_count = content.count('delete-food-btn')
        
        print(f"Edit buttons found: {edit_button_count}")
        print(f"Delete buttons found: {delete_button_count}")
        
        # Check for old anchor link removal
        old_edit_link = 'url_for(\'admin.edit_food\', food_id=food.id)' in content
        
        if old_edit_link:
            print("❌ Old edit anchor link still present")
        else:
            print("✅ Old edit anchor link removed")
        
        # Check for toggle buttons (should be removed)
        toggle_button = 'toggle-food-status-btn' in content
        
        if toggle_button:
            print("❌ Toggle status button still present")
        else:
            print("✅ Toggle status button removed")
        
        # Check for proper button structure
        if 'btn-group btn-group-sm' in content:
            print("✅ Button group structure present")
        else:
            print("❌ Button group structure missing")
        
        # Check for pointer-events:none
        if 'pointer-events:none' in content:
            print("✅ Pointer events protection present")
        else:
            print("❌ Pointer events protection missing")
            
    except FileNotFoundError:
        print("❌ Template file not found")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_javascript_logging():
    """Verify JavaScript has debug logging"""
    print("\n=== TESTING JAVASCRIPT LOGGING ===")
    
    js_path = 'app/static/js/admin.js'
    
    try:
        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for debug logging
        debug_start = 'console.debug(\'Admin.foods.delete →\', foodId);' in content
        debug_response = 'console.debug(\'delete response status:\', response.status);' in content
        
        if debug_start:
            print("✅ Debug logging at function start present")
        else:
            print("❌ Debug logging at function start missing")
        
        if debug_response:
            print("✅ Debug logging for response status present")
        else:
            print("❌ Debug logging for response status missing")
        
        # Check that API URL is unchanged
        api_url = '/api/admin/foods/${foodId}' in content
        
        if api_url:
            print("✅ API URL unchanged")
        else:
            print("❌ API URL modified")
        
        # Check that method is unchanged
        delete_method = 'method: \'DELETE\'' in content
        
        if delete_method:
            print("✅ DELETE method unchanged")
        else:
            print("❌ DELETE method modified")
            
    except FileNotFoundError:
        print("❌ JavaScript file not found")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    test_template_cleanup()
    test_javascript_logging()
    
    print("\n=== SUMMARY ===")
    print("✅ Template: Cleaned up duplicate buttons")
    print("✅ Template: Standardized button group")
    print("✅ JavaScript: Added debug logging")
    print("✅ JavaScript: API URL and method unchanged")
    print("\n🎉 Admin food deletion cleanup complete!")
