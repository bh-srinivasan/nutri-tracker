#!/usr/bin/env python3
"""
Simple diagnostic script to check the nutrition goals template
"""

import re

def check_template_content():
    """Check the template content for issues"""
    
    print("🔍 CHECKING NUTRITION GOALS TEMPLATE")
    print("=" * 50)
    
    try:
        with open("app/templates/dashboard/nutrition_goals.html", 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("✅ Template file loaded successfully")
        print(f"📄 File size: {len(content)} characters")
        
        # Check 1: Form field rendering
        print("\n1. 🔍 Checking form field rendering:")
        
        # Look for target_duration field
        duration_matches = re.findall(r'form\.target_duration[^}]*', content)
        print(f"   - target_duration references: {len(duration_matches)}")
        for match in duration_matches:
            print(f"     → {match}")
        
        # Look for target_date field  
        date_matches = re.findall(r'form\.target_date[^}]*', content)
        print(f"   - target_date references: {len(date_matches)}")
        for match in date_matches:
            print(f"     → {match}")
        
        # Check 2: onchange attributes
        print("\n2. 🔍 Checking onchange attributes:")
        onchange_matches = re.findall(r'onchange="[^"]*"', content)
        print(f"   - onchange attributes found: {len(onchange_matches)}")
        for match in onchange_matches:
            print(f"     → {match}")
        
        # Check 3: JavaScript function
        print("\n3. 🔍 Checking JavaScript function:")
        if "function updateTargetDate()" in content:
            print("   ✅ updateTargetDate function found")
        else:
            print("   ❌ updateTargetDate function NOT found")
        
        # Check 4: Duration mapping
        print("\n4. 🔍 Checking duration mapping:")
        if "durationToDays = {" in content:
            print("   ✅ durationToDays mapping found")
            
            # Extract the mapping
            mapping_match = re.search(r'durationToDays = \{([^}]+)\}', content, re.DOTALL)
            if mapping_match:
                print("   📋 Duration mapping:")
                mapping_content = mapping_match.group(1)
                for line in mapping_content.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('//'):
                        print(f"     → {line}")
        else:
            print("   ❌ durationToDays mapping NOT found")
        
        # Check 5: Script structure
        print("\n5. 🔍 Checking script structure:")
        script_sections = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
        print(f"   - Script sections found: {len(script_sections)}")
        
        # Check for common issues
        print("\n6. 🔍 Checking for common issues:")
        
        # Check for duplicate functions
        update_function_count = content.count("function updateTargetDate()")
        print(f"   - updateTargetDate function definitions: {update_function_count}")
        if update_function_count > 1:
            print("   ⚠️  WARNING: Multiple updateTargetDate function definitions found!")
        
        # Check for duplicate event listeners
        dom_content_loaded_count = content.count("addEventListener('DOMContentLoaded'")
        print(f"   - DOMContentLoaded listeners: {dom_content_loaded_count}")
        if dom_content_loaded_count > 1:
            print("   ⚠️  WARNING: Multiple DOMContentLoaded listeners found!")
        
        # Check for syntax errors
        if "getElementById('target_duration')" in content:
            print("   ✅ getElementById('target_duration') found")
        else:
            print("   ❌ getElementById('target_duration') NOT found")
        
        if "getElementById('target_date')" in content:
            print("   ✅ getElementById('target_date') found")
        else:
            print("   ❌ getElementById('target_date') NOT found")
        
        return True
        
    except FileNotFoundError:
        print("❌ Template file not found")
        return False
    except Exception as e:
        print(f"❌ Error reading template: {e}")
        return False

def check_forms_py():
    """Check the forms.py file"""
    
    print("\n🔍 CHECKING FORMS.PY")
    print("=" * 30)
    
    try:
        with open("app/dashboard/forms.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("✅ Forms file loaded successfully")
        
        # Check for NutritionGoalForm
        if "class NutritionGoalForm" in content:
            print("✅ NutritionGoalForm class found")
            
            # Check for target_duration field
            if "target_duration = SelectField" in content:
                print("✅ target_duration field found")
                
                # Extract choices
                choices_match = re.search(r'target_duration = SelectField[^,]*choices=\[([^\]]+)\]', content, re.DOTALL)
                if choices_match:
                    print("📋 Duration choices:")
                    choices_content = choices_match.group(1)
                    for line in choices_content.split('\n'):
                        line = line.strip()
                        if line and line.startswith('('):
                            print(f"   → {line}")
            else:
                print("❌ target_duration field NOT found")
            
            # Check for target_date field
            if "target_date = DateField" in content:
                print("✅ target_date field found")
            else:
                print("❌ target_date field NOT found")
                
        else:
            print("❌ NutritionGoalForm class NOT found")
        
        return True
        
    except FileNotFoundError:
        print("❌ Forms file not found")
        return False
    except Exception as e:
        print(f"❌ Error reading forms file: {e}")
        return False

def main():
    """Main function"""
    print("🚀 NUTRITION GOALS DIAGNOSTIC TOOL")
    print("=" * 50)
    
    template_ok = check_template_content()
    forms_ok = check_forms_py()
    
    print("\n" + "=" * 50)
    if template_ok and forms_ok:
        print("🔍 DIAGNOSTIC COMPLETED")
        print("📋 Check the analysis above for any issues")
    else:
        print("❌ DIAGNOSTIC FAILED")
        print("Please check the errors above")
    print("=" * 50)

if __name__ == "__main__":
    main()
