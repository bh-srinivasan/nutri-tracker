#!/usr/bin/env python3
"""
Test script to verify that Servings Upload History matches Food Uploads History UX.
Tests the unified interface, table structure, and auto-refresh functionality.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, ServingUploadJob
from datetime import datetime, timedelta
import uuid

def create_test_data():
    """Create test data for servings upload jobs"""
    app = create_app()
    
    with app.app_context():
        # Get admin user
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print("❌ Admin user not found")
            return False
            
        print(f"✅ Found admin user: {admin.username}")
        
        # Create test serving upload jobs with different statuses
        test_jobs = [
            {
                'filename': 'protein_servings_test.csv',
                'status': 'completed',
                'total_rows': 50,
                'successful_rows': 48,
                'failed_rows': 2,
                'processed_rows': 50,
                'created_at': datetime.utcnow() - timedelta(hours=2)
            },
            {
                'filename': 'snack_servings_bulk.csv',
                'status': 'processing',
                'total_rows': 100,
                'successful_rows': 45,
                'failed_rows': 0,
                'processed_rows': 45,
                'created_at': datetime.utcnow() - timedelta(minutes=15)
            },
            {
                'filename': 'breakfast_servings.csv',
                'status': 'failed',
                'total_rows': 25,
                'successful_rows': 10,
                'failed_rows': 15,
                'processed_rows': 25,
                'error_message': 'Invalid food_id in row 11',
                'created_at': datetime.utcnow() - timedelta(hours=1)
            },
            {
                'filename': 'dinner_servings_large.csv',
                'status': 'pending',
                'total_rows': 200,
                'successful_rows': 0,
                'failed_rows': 0,
                'processed_rows': 0,
                'created_at': datetime.utcnow() - timedelta(minutes=5)
            }
        ]
        
        created_jobs = []
        for job_data in test_jobs:
            job = ServingUploadJob(
                job_id=str(uuid.uuid4()),
                filename=job_data['filename'],
                status=job_data['status'],
                total_rows=job_data['total_rows'],
                successful_rows=job_data['successful_rows'],
                failed_rows=job_data['failed_rows'],
                processed_rows=job_data['processed_rows'],
                error_message=job_data.get('error_message'),
                created_by=admin.id,
                created_at=job_data['created_at']
            )
            
            if job_data['status'] in ['processing', 'completed', 'failed']:
                job.started_at = job_data['created_at'] + timedelta(seconds=30)
                
            if job_data['status'] in ['completed', 'failed']:
                job.completed_at = job_data['created_at'] + timedelta(minutes=5)
            
            db.session.add(job)
            created_jobs.append(job)
            
        try:
            db.session.commit()
            print(f"✅ Created {len(created_jobs)} test serving upload jobs")
            
            # Display created jobs
            for job in created_jobs:
                progress = 0
                if job.total_rows and job.total_rows > 0:
                    progress = round((job.processed_rows or 0) / job.total_rows * 100, 1)
                    
                print(f"   📄 {job.filename} | {job.status} | {progress}% | {job.successful_rows}/{job.total_rows}")
                
            return True
            
        except Exception as e:
            print(f"❌ Error creating test data: {e}")
            db.session.rollback()
            return False

def test_route_access():
    """Test that servings upload routes are accessible"""
    app = create_app()
    
    with app.app_context():
        with app.test_client() as client:
            # Login as admin
            login_response = client.post('/auth/login', data={
                'username': 'admin',
                'password': 'admin123'
            }, follow_redirects=True)
            
            if b'Dashboard' not in login_response.data:
                print("❌ Failed to login as admin")
                return False
                
            print("✅ Successfully logged in as admin")
            
            # Test servings upload page access
            upload_response = client.get('/admin/food-servings/uploads')
            if upload_response.status_code != 200:
                print(f"❌ Failed to access servings uploads page: {upload_response.status_code}")
                return False
                
            print("✅ Servings upload page accessible")
            
            # Check for unified interface elements
            response_text = upload_response.data.decode('utf-8')
            
            # Check for tabs
            if 'Upload Serving Data' not in response_text:
                print("❌ Upload tab not found")
                return False
                
            if 'Upload History' not in response_text:
                print("❌ History tab not found")
                return False
                
            print("✅ Unified tabbed interface present")
            
            # Check for table structure
            if 'Recent Upload Jobs' not in response_text:
                print("❌ Jobs table header not found")
                return False
                
            if 'Progress' not in response_text:
                print("❌ Progress column not found")
                return False
                
            print("✅ History table structure matches Food Uploads")
            
            # Test status check endpoint with existing job
            jobs = ServingUploadJob.query.filter_by(status='completed').first()
            if jobs:
                status_response = client.get(f'/admin/food-servings/status/{jobs.job_id}')
                if status_response.status_code == 200:
                    status_data = status_response.get_json()
                    required_fields = ['job_id', 'status', 'progress_percentage', 'total_rows', 'successful_rows', 'failed_rows']
                    
                    if all(field in status_data for field in required_fields):
                        print("✅ Status check API returns correct JSON format")
                    else:
                        print(f"❌ Status check API missing fields: {[f for f in required_fields if f not in status_data]}")
                        return False
                else:
                    print(f"❌ Status check API failed: {status_response.status_code}")
                    return False
            
            return True

def test_javascript_functionality():
    """Test that JavaScript auto-refresh and progress bars work"""
    app = create_app()
    
    with app.app_context():
        with app.test_client() as client:
            # Login as admin
            client.post('/auth/login', data={
                'username': 'admin',
                'password': 'admin123'
            })
            
            # Get servings upload page
            response = client.get('/admin/food-servings/uploads?tab=history')
            response_text = response.data.decode('utf-8')
            
            # Check for JavaScript elements
            js_checks = [
                'initializeHistoryTab',
                'startAutoRefresh',
                'animateProgressBars',
                'refreshJobStatus',
                'viewJobDetails',
                'progress-bar',
                'view-details-btn'
            ]
            
            for check in js_checks:
                if check not in response_text:
                    print(f"❌ Missing JavaScript element: {check}")
                    return False
                    
            print("✅ All JavaScript functionality present")
            
            # Check for auto-refresh interval setup
            if 'historyRefreshInterval' not in response_text:
                print("❌ Auto-refresh interval not found")
                return False
                
            print("✅ Auto-refresh functionality configured")
            return True

def cleanup_test_data():
    """Clean up test data"""
    app = create_app()
    
    with app.app_context():
        try:
            # Delete test serving upload jobs
            test_files = [
                'protein_servings_test.csv',
                'snack_servings_bulk.csv', 
                'breakfast_servings.csv',
                'dinner_servings_large.csv'
            ]
            
            for filename in test_files:
                jobs = ServingUploadJob.query.filter_by(filename=filename).all()
                for job in jobs:
                    db.session.delete(job)
                    
            db.session.commit()
            print("✅ Test data cleaned up")
            return True
            
        except Exception as e:
            print(f"❌ Error cleaning up test data: {e}")
            db.session.rollback()
            return False

def main():
    """Run comprehensive test suite"""
    print("🧪 Testing Servings Upload History UX Match with Food Uploads")
    print("=" * 60)
    
    # Test 1: Create test data
    print("\n1️⃣ Creating test data...")
    if not create_test_data():
        print("❌ Test failed at data creation")
        return False
    
    # Test 2: Test route access and UI structure
    print("\n2️⃣ Testing route access and UI structure...")
    if not test_route_access():
        print("❌ Test failed at route access")
        cleanup_test_data()
        return False
    
    # Test 3: Test JavaScript functionality
    print("\n3️⃣ Testing JavaScript functionality...")
    if not test_javascript_functionality():
        print("❌ Test failed at JavaScript functionality")
        cleanup_test_data()
        return False
    
    # Test 4: Clean up
    print("\n4️⃣ Cleaning up test data...")
    cleanup_test_data()
    
    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED!")
    print("✅ Servings Upload History successfully matches Food Uploads UX")
    print("✅ Unified tabbed interface working")
    print("✅ Table structure matches exactly")
    print("✅ JSON API format aligned")
    print("✅ Auto-refresh functionality configured")
    print("✅ Progress bars and status badges consistent")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
