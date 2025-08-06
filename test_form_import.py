#!/usr/bin/env python3
"""
Simple test to render the nutrition goals form and check the HTML output
"""

import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_form_rendering():
    """Test the form rendering outside of Flask context"""
    
    print("🧪 TESTING FORM RENDERING")
    print("=" * 30)
    
    try:
        from app.dashboard.forms import NutritionGoalForm
        print("✅ Successfully imported NutritionGoalForm")
        
        # Create form instance
        form = NutritionGoalForm()
        print("✅ Successfully created form instance")
        
        # Check form fields
        print(f"📋 Form fields available:")
        for field_name, field in form._fields.items():
            print(f"   - {field_name}: {type(field).__name__}")
        
        # Check target_duration field specifically
        if hasattr(form, 'target_duration'):
            print(f"✅ target_duration field found: {type(form.target_duration).__name__}")
            print(f"   - Choices: {form.target_duration.choices}")
        else:
            print("❌ target_duration field NOT found")
        
        # Check target_date field specifically  
        if hasattr(form, 'target_date'):
            print(f"✅ target_date field found: {type(form.target_date).__name__}")
        else:
            print("❌ target_date field NOT found")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_app_structure():
    """Check the app structure"""
    
    print("\n🔍 CHECKING APP STRUCTURE")
    print("=" * 30)
    
    files_to_check = [
        'app/__init__.py',
        'app/dashboard/__init__.py', 
        'app/dashboard/forms.py',
        'app/dashboard/routes.py',
        'app/templates/dashboard/nutrition_goals.html'
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} NOT FOUND")

def simple_test():
    """Run a simple test"""
    
    print("🚀 NUTRITION GOALS FORM TEST")
    print("=" * 40)
    
    check_app_structure()
    success = test_form_rendering()
    
    print("\n" + "=" * 40)
    if success:
        print("✅ FORM TEST COMPLETED")
        print("📋 Form can be imported and instantiated correctly")
    else:
        print("❌ FORM TEST FAILED")
        print("💡 There may be an import or configuration issue")
    
    print("\n💡 NEXT STEPS:")
    print("1. Test the standalone HTML file (test_target_date.html)")
    print("2. Compare with the Flask app behavior")
    print("3. Check browser console for JavaScript errors")
    print("4. Verify form rendering in Flask app")
    
    return success

if __name__ == "__main__":
    simple_test()
