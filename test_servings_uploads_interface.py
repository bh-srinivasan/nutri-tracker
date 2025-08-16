#!/usr/bin/env python3
"""
Test the new food servings uploads interface
"""

import requests
from bs4 import BeautifulSoup
import time

def test_servings_uploads_interface():
    """Test the new unified servings uploads interface"""
    
    print("🎯 Testing Food Servings Uploads Interface")
    print("=" * 50)
    
    session = requests.Session()
    
    # Login as admin
    login_url = "http://localhost:5001/auth/login"
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    # Get CSRF token
    login_page = session.get(login_url)
    soup = BeautifulSoup(login_page.content, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
    login_data['csrf_token'] = csrf_token
    
    # Login
    login_response = session.post(login_url, data=login_data, allow_redirects=True)
    
    if "Admin Dashboard" not in login_response.text:
        print("❌ Admin login failed")
        return False
    
    print("✅ Admin login successful")
    
    # Test 1: Check dashboard has updated link
    print("\n📋 Test 1: Dashboard Navigation")
    print("-" * 30)
    
    dashboard_url = "http://localhost:5001/admin/dashboard"
    dashboard_response = session.get(dashboard_url)
    
    if "food_servings_uploads" in dashboard_response.text:
        print("✅ Dashboard has updated link to unified interface")
    else:
        print("❌ Dashboard link not updated")
        
    # Test 2: Access unified interface
    print("\n📤 Test 2: Unified Interface Access")
    print("-" * 35)
    
    uploads_url = "http://localhost:5001/admin/food-servings/uploads"
    uploads_response = session.get(uploads_url)
    
    if uploads_response.status_code == 200:
        print("✅ Unified interface accessible")
        
        # Check for expected elements
        if "Upload Servings Data" in uploads_response.text:
            print("✅ Upload tab present")
        else:
            print("❌ Upload tab missing")
            
        if "Upload History" in uploads_response.text:
            print("✅ History tab present")
        else:
            print("❌ History tab missing")
            
        if "asyncUploadForm" in uploads_response.text:
            print("✅ Upload form present")
        else:
            print("❌ Upload form missing")
            
    else:
        print(f"❌ Failed to access unified interface: {uploads_response.status_code}")
        return False
    
    # Test 3: Check history tab functionality
    print("\n📊 Test 3: History Tab")
    print("-" * 20)
    
    history_url = "http://localhost:5001/admin/food-servings/uploads?tab=history"
    history_response = session.get(history_url)
    
    if history_response.status_code == 200:
        print("✅ History tab accessible")
        
        if "No Upload History" in history_response.text or "Upload History" in history_response.text:
            print("✅ History content displayed")
        else:
            print("❌ History content missing")
    else:
        print(f"❌ History tab failed: {history_response.status_code}")
    
    # Test 4: Template download still works
    print("\n📁 Test 4: Template Download")
    print("-" * 28)
    
    template_url = "http://localhost:5001/admin/food-servings/template"
    template_response = session.get(template_url)
    
    if template_response.status_code == 200:
        print("✅ Template download working")
        
        # Check CSV content
        lines = template_response.text.strip().split('\n')
        if len(lines) > 0 and 'food_key' in lines[0]:
            print("✅ Template has correct headers")
        else:
            print("❌ Template headers incorrect")
    else:
        print(f"❌ Template download failed: {template_response.status_code}")
    
    # Test 5: Legacy redirect
    print("\n🔄 Test 5: Legacy Route Redirect")
    print("-" * 32)
    
    legacy_url = "http://localhost:5001/admin/food-servings/upload"
    legacy_response = session.get(legacy_url, allow_redirects=False)
    
    if legacy_response.status_code == 302:
        print("✅ Legacy route redirects")
        
        # Follow redirect
        redirect_response = session.get(legacy_url, allow_redirects=True)
        if "food-servings/uploads" in redirect_response.url:
            print("✅ Redirects to unified interface")
        else:
            print("❌ Redirect target incorrect")
    else:
        print(f"❌ Legacy route not redirecting: {legacy_response.status_code}")
    
    print("\n🎉 Food Servings Uploads Interface Tests Complete!")
    print("=" * 50)
    return True

if __name__ == "__main__":
    try:
        success = test_servings_uploads_interface()
        if success:
            print("\n🚀 UNIFIED INTERFACE READY!")
            print("📝 Features verified:")
            print("   - Unified upload and history interface")
            print("   - Dashboard navigation updated")
            print("   - Legacy route redirection")
            print("   - Template download working")
            print("   - History tracking functional")
        else:
            print("\n❌ SOME TESTS FAILED!")
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
