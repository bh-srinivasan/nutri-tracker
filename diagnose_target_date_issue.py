#!/usr/bin/env python3
"""
Diagnostic script to check the actual HTML output of the nutrition goals page
"""

import requests
from bs4 import BeautifulSoup
import re

def diagnose_nutrition_goals_page():
    """Diagnose the nutrition goals page HTML output"""
    
    print("🔍 DIAGNOSING NUTRITION GOALS PAGE HTML OUTPUT")
    print("=" * 60)
    
    try:
        # Check if app is running
        print("1. 🌐 Testing app accessibility...")
        response = requests.get("http://127.0.0.1:5001", timeout=5)
        print(f"   ✅ App is running. Status: {response.status_code}")
        
        # Try to get the nutrition goals page (will likely redirect to login)
        print("2. 🎯 Accessing nutrition goals page...")
        goals_response = requests.get("http://127.0.0.1:5001/dashboard/nutrition-goals", timeout=5)
        print(f"   📍 Response status: {goals_response.status_code}")
        print(f"   📍 Final URL: {goals_response.url}")
        
        # Parse the HTML
        soup = BeautifulSoup(goals_response.text, 'html.parser')
        
        # Check if it's a login page
        if "login" in goals_response.url.lower() or "sign in" in soup.get_text().lower():
            print("   🔐 Redirected to login page (expected)")
            
            # Let's try to access the template file directly and analyze it
            print("3. 📄 Analyzing template file directly...")
            
            with open("app/templates/dashboard/nutrition_goals.html", 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            print("   📋 Template analysis:")
            
            # Check for form fields
            duration_field_matches = re.findall(r'form\.target_duration[^}]*', template_content)
            date_field_matches = re.findall(r'form\.target_date[^}]*', template_content)
            
            print(f"   - Target duration field references: {len(duration_field_matches)}")
            for match in duration_field_matches:
                print(f"     → {match}")
            
            print(f"   - Target date field references: {len(date_field_matches)}")
            for match in date_field_matches:
                print(f"     → {match}")
            
            # Check for onchange attributes
            onchange_matches = re.findall(r'onchange="[^"]*"', template_content)
            print(f"   - onchange attributes found: {len(onchange_matches)}")
            for match in onchange_matches:
                print(f"     → {match}")
            
            # Check for the updateTargetDate function
            function_matches = re.findall(r'function updateTargetDate\(\)[^}]*\{[^}]*\}', template_content, re.DOTALL)
            print(f"   - updateTargetDate function definitions: {len(function_matches)}")
            
            # Check for JavaScript errors in template
            script_sections = re.findall(r'<script[^>]*>(.*?)</script>', template_content, re.DOTALL)
            print(f"   - Script sections found: {len(script_sections)}")
            
            return True
            
        else:
            print("   ✅ Successfully accessed nutrition goals page")
            
            # Analyze the actual rendered HTML
            print("3. 📄 Analyzing rendered HTML...")
            
            # Look for target_duration select element
            duration_select = soup.find('select', {'id': 'target_duration'})
            if duration_select:
                print("   ✅ target_duration select element found")
                print(f"      - Has onchange: {'onchange' in duration_select.attrs}")
                if 'onchange' in duration_select.attrs:
                    print(f"      - onchange value: {duration_select['onchange']}")
                
                # Check options
                options = duration_select.find_all('option')
                print(f"      - Options count: {len(options)}")
                for opt in options:
                    print(f"        → {opt.get('value', 'no-value')}: {opt.get_text().strip()}")
            else:
                print("   ❌ target_duration select element NOT found")
            
            # Look for target_date input element
            date_input = soup.find('input', {'id': 'target_date'})
            if date_input:
                print("   ✅ target_date input element found")
                print(f"      - Type: {date_input.get('type', 'not-specified')}")
                print(f"      - Has onchange: {'onchange' in date_input.attrs}")
            else:
                print("   ❌ target_date input element NOT found")
            
            # Look for JavaScript
            scripts = soup.find_all('script')
            print(f"   - Script tags found: {len(scripts)}")
            
            js_content = ""
            for script in scripts:
                if script.string:
                    js_content += script.string
            
            if "updateTargetDate" in js_content:
                print("   ✅ updateTargetDate function found in JavaScript")
            else:
                print("   ❌ updateTargetDate function NOT found in JavaScript")
            
            if "durationToDays" in js_content:
                print("   ✅ durationToDays mapping found in JavaScript")
            else:
                print("   ❌ durationToDays mapping NOT found in JavaScript")
            
            return True
            
    except Exception as e:
        print(f"❌ Diagnosis failed: {e}")
        return False

def check_form_class():
    """Check the form class definition"""
    print("\n4. 🔍 Checking form class definition...")
    
    try:
        with open("app/dashboard/forms.py", 'r', encoding='utf-8') as f:
            forms_content = f.read()
        
        # Look for NutritionGoalForm
        if "class NutritionGoalForm" in forms_content:
            print("   ✅ NutritionGoalForm class found")
            
            # Extract the target_duration field definition
            target_duration_match = re.search(r'target_duration\s*=\s*SelectField[^)]*\)', forms_content, re.DOTALL)
            if target_duration_match:
                print("   ✅ target_duration field found:")
                print(f"      → {target_duration_match.group()}")
            else:
                print("   ❌ target_duration field NOT found")
            
            # Extract the target_date field definition
            target_date_match = re.search(r'target_date\s*=\s*DateField[^)]*\)', forms_content, re.DOTALL)
            if target_date_match:
                print("   ✅ target_date field found:")
                print(f"      → {target_date_match.group()}")
            else:
                print("   ❌ target_date field NOT found")
                
        else:
            print("   ❌ NutritionGoalForm class NOT found")
            
    except Exception as e:
        print(f"   ❌ Error reading forms.py: {e}")

def main():
    """Main function"""
    print("🚀 COMPREHENSIVE NUTRITION GOALS DIAGNOSIS")
    print("=" * 60)
    
    success = diagnose_nutrition_goals_page()
    check_form_class()
    
    print("\n" + "=" * 60)
    if success:
        print("🔍 DIAGNOSIS COMPLETED - Check results above")
    else:
        print("❌ DIAGNOSIS FAILED - Please check errors above")
    print("=" * 60)

if __name__ == "__main__":
    main()
