#!/usr/bin/env python3
"""
Debug user ID mismatch in serving upload jobs
"""

import requests
from bs4 import BeautifulSoup

def debug_user_mismatch():
    """Debug if there's a user ID mismatch"""
    
    print("🔍 Debugging User ID Mismatch")
    print("=" * 35)
    
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
    
    # Test with a simple debug route - let me create a debug endpoint
    print("\n🔍 Creating debug request...")
    
    # Let's check what the route is actually getting
    history_url = "http://localhost:5001/admin/food-servings/uploads?tab=history&debug=1"
    history_response = session.get(history_url)
    
    print(f"Status: {history_response.status_code}")
    
    # Look for debug information or error messages in the response
    if "Error" in history_response.text or "error" in history_response.text:
        print("⚠️ Error detected in response")
        
    # Check if we can see any job information at all
    if "ServingUploadJob" in history_response.text:
        print("✅ ServingUploadJob mentioned in response")
    else:
        print("❌ No ServingUploadJob found in response")
    
    # Check if pagination object exists
    if "jobs.items" in history_response.text:
        print("✅ jobs.items found in template")
    elif "jobs" in history_response.text:
        print("⚠️ 'jobs' found but not 'jobs.items'")
    else:
        print("❌ No 'jobs' variable found in template")

if __name__ == "__main__":
    debug_user_mismatch()

# Let me also run a direct database check
print("\n" + "="*50)
print("🗄️ DIRECT DATABASE CHECK")
print("="*50)

try:
    # Import and check directly
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    from app import create_app
    from app.models import ServingUploadJob, User
    from flask_login import current_user
    
    app = create_app()
    with app.app_context():
        print("=== All Serving Upload Jobs ===")
        all_jobs = ServingUploadJob.query.all()
        print(f"Total jobs in database: {len(all_jobs)}")
        
        for job in all_jobs:
            print(f"Job ID: {job.job_id[:8]}... | Status: {job.status} | Created by User ID: {job.created_by} | Filename: {job.filename}")
        
        print("\n=== All Admin Users ===")
        all_admins = User.query.filter_by(is_admin=True).all()
        for admin in all_admins:
            print(f"Admin User ID: {admin.id} | Username: {admin.username}")
            
        print("\n=== Jobs for Each Admin ===")
        for admin in all_admins:
            admin_jobs = ServingUploadJob.query.filter_by(created_by=admin.id).all()
            print(f"Admin {admin.username} (ID: {admin.id}) has {len(admin_jobs)} jobs")
            for job in admin_jobs:
                print(f"  - {job.filename} ({job.status})")

except Exception as e:
    print(f"❌ Database check failed: {e}")
    import traceback
    traceback.print_exc()
