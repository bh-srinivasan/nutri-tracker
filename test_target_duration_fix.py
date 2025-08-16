#!/usr/bin/env python3
"""
Test script to verify the target duration fix for custom dates.
This will open the nutrition goals page and test the target date functionality.
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import subprocess
import threading

def start_flask_server():
    """Start the Flask server in a separate thread"""
    subprocess.run(['python', 'run_server.py'], cwd='.')

def test_custom_target_date():
    """Test that setting a custom target date changes duration to 'custom'"""
    
    # Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    driver = None
    server_thread = None
    
    try:
        # Start Flask server in background
        print("🚀 Starting Flask server...")
        server_thread = threading.Thread(target=start_flask_server, daemon=True)
        server_thread.start()
        time.sleep(3)  # Give server time to start
        
        # Initialize Chrome driver
        print("🌐 Starting Chrome driver...")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("http://localhost:5000")
        
        # Login as regular user
        print("🔐 Logging in as regular user...")
        try:
            # Check if we're on login page
            login_link = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Login"))
            )
            login_link.click()
        except TimeoutException:
            print("Already logged in or login link not found")
        
        # Try to login
        try:
            username_field = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            password_field = driver.find_element(By.ID, "password")
            
            username_field.send_keys("user1")
            password_field.send_keys("password123")
            
            login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            time.sleep(2)
        except TimeoutException:
            print("Login form not found - might already be logged in")
        
        # Navigate to nutrition goals page
        print("📊 Navigating to nutrition goals page...")
        driver.get("http://localhost:5000/dashboard/nutrition_goals")
        
        # Wait for page to load
        wait = WebDriverWait(driver, 10)
        
        # Find the target date input
        print("🎯 Testing target date functionality...")
        target_date_input = wait.until(
            EC.presence_of_element_located((By.ID, "target_date"))
        )
        
        # Find the duration select
        duration_select = driver.find_element(By.ID, "target_duration")
        
        # Get current date + 45 days (should not match any predefined duration)
        from datetime import datetime, timedelta
        future_date = datetime.now() + timedelta(days=45)
        formatted_date = future_date.strftime('%Y-%m-%d')
        
        print(f"📅 Setting target date to: {formatted_date}")
        
        # Clear and set the target date
        target_date_input.clear()
        target_date_input.send_keys(formatted_date)
        
        # Trigger the change event
        driver.execute_script("document.getElementById('target_date').dispatchEvent(new Event('change'));")
        
        # Wait a moment for the JavaScript to process
        time.sleep(1)
        
        # Check the duration dropdown value
        duration_value = duration_select.get_attribute('value')
        
        print(f"✅ Duration dropdown value after setting custom date: '{duration_value}'")
        
        # Verify that duration is set to 'custom' and not empty string
        if duration_value == 'custom':
            print("✅ SUCCESS: Duration correctly set to 'custom' for custom target date!")
            return True
        elif duration_value == '':
            print("❌ FAILURE: Duration is empty string instead of 'custom'")
            return False
        else:
            print(f"❌ UNEXPECTED: Duration is '{duration_value}' instead of 'custom'")
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False
        
    finally:
        if driver:
            driver.quit()
            print("🔚 Browser closed")

if __name__ == "__main__":
    print("🧪 Testing target duration fix for custom dates...")
    success = test_custom_target_date()
    
    if success:
        print("\n🎉 Test PASSED: Custom target date correctly sets duration to 'custom'")
    else:
        print("\n💥 Test FAILED: Issue with target duration setting")
    
    exit(0 if success else 1)
