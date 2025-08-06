#!/usr/bin/env python3
"""
Direct test of nutrition goals JavaScript functionality.
"""

import time
import sys
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    """Set up Chrome driver with options."""
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # Comment out to see browser
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def test_javascript_directly(driver, base_url):
    """Test JavaScript functionality directly on the nutrition goals page."""
    print("🧪 Testing JavaScript functionality directly...")
    
    # Navigate directly to the nutrition goals page
    driver.get(f"{base_url}/dashboard/nutrition-goals")
    
    # Wait for page to load
    time.sleep(5)
    
    # Check if we're redirected to login
    current_url = driver.current_url
    if "login" in current_url:
        print("🔐 Need to authenticate first...")
        
        # Try logging in with admin credentials
        try:
            username_field = driver.find_element(By.NAME, "username")
            password_field = driver.find_element(By.NAME, "password")
            
            username_field.send_keys("admin")
            password_field.send_keys("admin123")
            
            submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_button.click()
            
            time.sleep(3)
            
            # Navigate back to nutrition goals
            driver.get(f"{base_url}/dashboard/nutrition-goals")
            time.sleep(3)
            
        except Exception as e:
            print(f"❌ Login failed: {e}")
            return False
    
    # Now test the JavaScript functionality
    print("🎯 Testing duration dropdown functionality...")
    
    # Inject test JavaScript
    test_script = """
    // Test the updateTargetDate function directly
    console.log('=== TESTING NUTRITION GOALS FUNCTIONALITY ===');
    
    let testResults = [];
    
    // Check if elements exist
    const durationSelect = document.getElementById('targetDuration');
    const dateInput = document.getElementById('targetDate');
    
    if (!durationSelect) {
        testResults.push('❌ Duration select element not found');
        return testResults;
    }
    
    if (!dateInput) {
        testResults.push('❌ Date input element not found');
        return testResults;
    }
    
    testResults.push('✅ Found both duration select and date input elements');
    
    // Test each duration option
    const durations = [
        {value: '2_weeks', days: 14, name: '2 weeks'},
        {value: '1_month', days: 30, name: '1 month'},
        {value: '2_months', days: 60, name: '2 months'},
        {value: '3_months', days: 90, name: '3 months'},
        {value: '6_months', days: 180, name: '6 months'},
        {value: '1_year', days: 365, name: '1 year'}
    ];
    
    for (const duration of durations) {
        // Clear date first
        dateInput.value = '';
        
        // Set duration
        durationSelect.value = duration.value;
        
        // Call the update function
        if (typeof updateTargetDate === 'function') {
            updateTargetDate();
            
            // Check the result
            const targetDateValue = dateInput.value;
            
            if (targetDateValue) {
                const targetDate = new Date(targetDateValue);
                const today = new Date();
                const daysDiff = Math.ceil((targetDate - today) / (1000 * 60 * 60 * 24));
                
                if (Math.abs(daysDiff - duration.days) <= 2) {
                    testResults.push(`✅ ${duration.name}: Correctly set to ${targetDateValue} (${daysDiff} days)`);
                } else {
                    testResults.push(`❌ ${duration.name}: Expected ~${duration.days} days, got ${daysDiff} days`);
                }
            } else {
                testResults.push(`❌ ${duration.name}: No date was set`);
            }
        } else {
            testResults.push('❌ updateTargetDate function not found');
            break;
        }
    }
    
    return testResults;
    """
    
    try:
        # Execute the test script
        results = driver.execute_script(test_script)
        
        print("\n📊 JavaScript Test Results:")
        for result in results:
            print(f"  {result}")
        
        # Check browser console for errors
        try:
            logs = driver.get_log('browser')
            js_errors = [log for log in logs if log['level'] == 'SEVERE']
            
            if js_errors:
                print(f"\n⚠️  JavaScript Errors Found:")
                for error in js_errors[-5:]:  # Show last 5 errors
                    print(f"  - {error['message']}")
            else:
                print(f"\n✅ No severe JavaScript errors found")
                
        except Exception as e:
            print(f"\n⚠️  Could not check console logs: {e}")
        
        # Count successful tests
        success_count = len([r for r in results if r.startswith('✅') and 'Correctly set' in r])
        total_duration_tests = 6  # Number of duration options
        
        return success_count >= total_duration_tests
        
    except Exception as e:
        print(f"❌ Error executing JavaScript test: {e}")
        return False

def test_html_elements(driver):
    """Test if the HTML elements are properly set up."""
    print("\n🔍 Testing HTML element setup...")
    
    try:
        # Check for required elements
        elements_to_check = [
            "targetDuration",
            "targetDate", 
            "clearDateBtn",
            "pastDateError",
            "dateAutoFillMessage",
            "dateCustomMessage",
            "dateClearedMessage",
            "dateResetOption",
            "autoFillText",
            "customText"
        ]
        
        missing_elements = []
        found_elements = []
        
        for element_id in elements_to_check:
            try:
                element = driver.find_element(By.ID, element_id)
                found_elements.append(element_id)
            except:
                missing_elements.append(element_id)
        
        print(f"✅ Found elements: {len(found_elements)}/{len(elements_to_check)}")
        
        if missing_elements:
            print(f"❌ Missing elements: {missing_elements}")
        
        return len(missing_elements) == 0
        
    except Exception as e:
        print(f"❌ Error checking HTML elements: {e}")
        return False

def main():
    """Main test function."""
    base_url = "http://127.0.0.1:5001"
    driver = None
    
    try:
        print("🚀 Starting direct JavaScript test for nutrition goals...")
        print(f"🌐 Testing application at: {base_url}")
        
        # Setup driver
        driver = setup_driver()
        
        # Test HTML elements
        html_test_passed = test_html_elements(driver)
        
        # Test JavaScript functionality
        js_test_passed = test_javascript_directly(driver, base_url)
        
        # Keep browser open for manual verification
        print(f"\n🔍 Manual verification: The browser will stay open for 30 seconds...")
        print(f"   You can manually test the duration dropdown in the browser window.")
        time.sleep(30)
        
        # Final summary
        print(f"\n🏁 Test Results Summary:")
        print(f"✅ HTML Elements: {'PASSED' if html_test_passed else 'FAILED'}")
        print(f"✅ JavaScript Functionality: {'PASSED' if js_test_passed else 'FAILED'}")
        
        overall_success = html_test_passed and js_test_passed
        
        if overall_success:
            print(f"\n🎉 TESTS PASSED! The nutrition goals functionality appears to be working.")
        else:
            print(f"\n❌ TESTS FAILED. There are issues with the implementation.")
            
        return overall_success
        
    except Exception as e:
        print(f"❌ Critical error during testing: {e}")
        return False
        
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
