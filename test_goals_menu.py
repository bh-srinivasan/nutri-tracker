#!/usr/bin/env python3
"""
Test script to verify the Goals menu item has been added to the navigation.
This will test that the menu item appears and links to the correct page.
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import subprocess
import threading

def start_flask_server():
    """Start the Flask server in a separate thread"""
    subprocess.run(['python', 'run_server.py'], cwd='.')

def test_goals_menu_item():
    """Test that the Goals menu item appears and works correctly"""
    
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
        
        # Navigate to dashboard to ensure we're in the main app
        print("📊 Navigating to dashboard...")
        driver.get("http://localhost:5000/dashboard")
        
        # Wait for page to load
        wait = WebDriverWait(driver, 10)
        
        # Check if Goals menu item exists
        print("🎯 Looking for Goals menu item...")
        try:
            goals_menu_item = wait.until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/dashboard/nutrition-goals') and contains(text(), 'Goals')]"))
            )
            print("✅ Goals menu item found in navigation!")
            
            # Check the icon
            icon = goals_menu_item.find_element(By.TAG_NAME, "i")
            if "fa-target" in icon.get_attribute("class"):
                print("✅ Correct target icon found!")
            else:
                print(f"❌ Wrong icon found: {icon.get_attribute('class')}")
            
            # Test clicking the menu item
            print("🖱️ Clicking Goals menu item...")
            goals_menu_item.click()
            
            # Wait for navigation to goals page
            time.sleep(2)
            
            # Check if we're on the nutrition goals page
            current_url = driver.current_url
            if "/nutrition-goals" in current_url:
                print("✅ Successfully navigated to nutrition goals page!")
                
                # Check for page title or content to confirm we're on the right page
                try:
                    page_heading = driver.find_element(By.XPATH, "//h1[contains(text(), 'Nutrition Goals')]")
                    print("✅ Nutrition Goals page heading found!")
                    return True
                except:
                    print("❌ Could not find nutrition goals page heading")
                    return False
            else:
                print(f"❌ Wrong page reached: {current_url}")
                return False
                
        except TimeoutException:
            print("❌ Goals menu item not found in navigation")
            
            # Debug: Print all menu items found
            try:
                menu_items = driver.find_elements(By.CSS_SELECTOR, ".navbar-nav .nav-link")
                print(f"📋 Found {len(menu_items)} menu items:")
                for item in menu_items:
                    print(f"   - {item.text} -> {item.get_attribute('href')}")
            except:
                print("Could not retrieve menu items for debugging")
            
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False
        
    finally:
        if driver:
            driver.quit()
            print("🔚 Browser closed")

if __name__ == "__main__":
    print("🧪 Testing Goals menu item addition...")
    success = test_goals_menu_item()
    
    if success:
        print("\n🎉 Test PASSED: Goals menu item working correctly!")
    else:
        print("\n💥 Test FAILED: Issue with Goals menu item")
    
    exit(0 if success else 1)
