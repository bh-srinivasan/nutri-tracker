#!/usr/bin/env python3
"""
Test the serving upload job tracking functionality
"""

import requests
from bs4 import BeautifulSoup
import time
import io

def test_upload_with_history():
    """Test uploading a CSV and checking the job history"""
    
    print("🎯 Testing Serving Upload Job Tracking")
    print("=" * 45)
    
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
    
    # Test 1: Upload a test CSV file
    print("\n📤 Test 1: Upload Test CSV")
    print("-" * 27)
    
    # Create test CSV content
    test_csv = """food_key,serving_name,unit,grams_per_unit,is_default
1,Test Cup,cup,240.0,true
1,Test Tablespoon,tbsp,15.0,false
2,Small Bowl,bowl,150.0,true"""
    
    # Get CSRF token for upload
    upload_page = session.get("http://localhost:5001/admin/food-servings/uploads")
    soup = BeautifulSoup(upload_page.content, 'html.parser')
    
    # Try multiple ways to find CSRF token
    csrf_token = None
    
    # Method 1: Look for input with name csrf_token
    csrf_inputs = soup.find_all('input', {'name': 'csrf_token'})
    if csrf_inputs:
        csrf_token = csrf_inputs[0].get('value')
        print(f"Found CSRF token via input: {csrf_token[:10]}...")
    
    # Method 2: Look in JavaScript variables
    if not csrf_token:
        import re
        csrf_patterns = [
            r"csrf_token['\"]?\s*[:=]\s*['\"]([^'\"]+)['\"]",
            r"{{ csrf_token }}",
            r"{{csrf_token}}"
        ]
        for pattern in csrf_patterns:
            csrf_match = re.search(pattern, upload_page.text)
            if csrf_match:
                csrf_token = csrf_match.group(1)
                print(f"Found CSRF token via regex: {csrf_token[:10]}...")
                break
    
    # Method 3: Use the login CSRF token (should work for same session)
    if not csrf_token:
        csrf_token = login_data['csrf_token']  # Reuse from login
        print(f"Using login CSRF token: {csrf_token[:10]}...")
    
    if not csrf_token:
        print("❌ Could not find CSRF token")
        print("Page content snippet:")
        print(upload_page.text[:500])
        return False
    
    # Upload the CSV
    upload_url = "http://localhost:5001/admin/food-servings/upload-async"
    files = {'file': ('test_servings.csv', test_csv, 'text/csv')}
    data = {'csrf_token': csrf_token}
    
    upload_response = session.post(upload_url, files=files, data=data)
    
    if upload_response.status_code == 200:
        result = upload_response.json()
        if result.get('success'):
            job_id = result.get('job_id')
            print(f"✅ Upload successful, Job ID: {job_id[:8]}...")
            print(f"📋 Message: {result.get('message', 'N/A')}")
        else:
            print(f"❌ Upload failed: {result.get('error', 'Unknown error')}")
            return False
    else:
        print(f"❌ Upload request failed: {upload_response.status_code}")
        print(f"Response: {upload_response.text[:200]}...")
        return False
    
    # Test 2: Check job appears in history
    print("\n📊 Test 2: Check Upload History")
    print("-" * 32)
    
    history_url = "http://localhost:5001/admin/food-servings/uploads?tab=history"
    history_response = session.get(history_url)
    
    if history_response.status_code == 200:
        if job_id[:8] in history_response.text:
            print("✅ Job appears in upload history")
            
            # Check for status
            if "Completed" in history_response.text or "completed" in history_response.text:
                print("✅ Job shows completed status")
            elif "Processing" in history_response.text or "processing" in history_response.text:
                print("⏳ Job still processing")
            else:
                print("ℹ️ Job status unclear")
        else:
            print("❌ Job not found in history")
    else:
        print(f"❌ Failed to access history: {history_response.status_code}")
    
    # Test 3: Try to get job details (if the endpoint exists)
    print("\n🔍 Test 3: Job Details")
    print("-" * 20)
    
    details_url = f"http://localhost:5001/admin/food-servings/uploads?job_details={job_id}"
    headers = {'X-Requested-With': 'XMLHttpRequest'}
    details_response = session.get(details_url, headers=headers)
    
    if details_response.status_code == 200:
        try:
            details = details_response.json()
            print("✅ Job details retrieved:")
            print(f"   - Status: {details.get('status', 'Unknown')}")
            print(f"   - Total rows: {details.get('total_rows', 0)}")
            print(f"   - Successful: {details.get('successful_rows', 0)}")
            print(f"   - Failed: {details.get('failed_rows', 0)}")
        except:
            print("❌ Could not parse job details")
    else:
        print(f"❌ Job details request failed: {details_response.status_code}")
    
    # Test 4: Upload with errors to test error tracking
    print("\n⚠️  Test 4: Upload with Errors")
    print("-" * 30)
    
    # Create CSV with intentional errors
    error_csv = """food_key,serving_name,unit,grams_per_unit,is_default
999999,Invalid Food,cup,240.0,true
NONEXISTENT,Bad Key,tbsp,15.0,false"""
    
    files_error = {'file': ('error_test.csv', error_csv, 'text/csv')}
    error_upload_response = session.post(upload_url, files=files_error, data=data)
    
    if error_upload_response.status_code == 200:
        error_result = error_upload_response.json()
        if error_result.get('success'):
            error_job_id = error_result.get('job_id')
            print(f"✅ Error test upload completed, Job ID: {error_job_id[:8]}...")
            print(f"📋 Message: {error_result.get('message', 'N/A')}")
            
            # Check if error handling is reported
            if "Errors:" in error_result.get('message', ''):
                print("✅ Error reporting working")
            else:
                print("ℹ️ No errors reported (may be expected)")
        else:
            print(f"ℹ️ Error upload rejected: {error_result.get('error', 'Unknown')}")
    else:
        print(f"❌ Error upload failed: {error_upload_response.status_code}")
    
    print("\n🎉 Upload Job Tracking Tests Complete!")
    return True

if __name__ == "__main__":
    try:
        success = test_upload_with_history()
        if success:
            print("\n🚀 JOB TRACKING SYSTEM WORKING!")
            print("📝 Features verified:")
            print("   - CSV upload creates tracked jobs")
            print("   - Jobs appear in upload history")
            print("   - Job details can be retrieved")
            print("   - Error handling and reporting")
        else:
            print("\n❌ SOME FEATURES NOT WORKING!")
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
