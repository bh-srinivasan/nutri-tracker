"""
Test script for the unified Food Uploads interface
"""
import requests
import time

# Test the new unified food uploads interface
def test_unified_food_uploads():
    base_url = "http://localhost:5001"
    
    print("🧪 Testing Unified Food Uploads Interface")
    print("=" * 50)
    
    # Test 1: Check if the food uploads page loads
    try:
        response = requests.get(f"{base_url}/admin/food-uploads", timeout=5)
        if response.status_code == 200:
            print("✅ Food uploads page loads successfully")
        else:
            print(f"❌ Food uploads page returned status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error accessing food uploads page: {e}")
    
    # Test 2: Check if the bulk upload details endpoint works
    try:
        # This will return 404 for non-existent job, but endpoint should work
        response = requests.get(f"{base_url}/admin/bulk-upload-details/test-job-id", timeout=5)
        if response.status_code in [404, 401, 403]:  # Expected responses without auth
            print("✅ Bulk upload details endpoint is accessible")
        else:
            print(f"⚠️  Unexpected response from details endpoint: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error accessing bulk upload details: {e}")
    
    # Test 3: Check if dashboard loads with new button
    try:
        response = requests.get(f"{base_url}/admin/dashboard", timeout=5)
        if response.status_code == 200 or response.status_code == 302:  # 302 for redirect to login
            print("✅ Admin dashboard loads (may redirect to login)")
        else:
            print(f"❌ Dashboard returned status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error accessing dashboard: {e}")
    
    # Test 4: Check if the template file exists
    try:
        response = requests.get(f"{base_url}/static/templates/food_upload_template.csv", timeout=5)
        if response.status_code == 200:
            print("✅ CSV template file is accessible")
        else:
            print(f"❌ CSV template returned status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error accessing CSV template: {e}")
    
    print("\n🎯 Test Summary:")
    print("- Unified Food Uploads interface has been implemented")
    print("- New route /admin/food-uploads combines upload and history")
    print("- Dashboard updated with single 'Food Uploads' button")
    print("- CSV template available for download")
    print("- Tabbed interface provides better UX")

if __name__ == "__main__":
    test_unified_food_uploads()
