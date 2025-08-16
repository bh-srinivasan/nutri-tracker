#!/usr/bin/env python3
"""
Test script to debug the servings upload route issue.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.abspath('.'))

try:
    print("=== Testing Servings Upload Route Issue ===")
    
    # Test 1: Import the app
    print("\n1. Testing app import...")
    from app import create_app
    app = create_app()
    print("✅ App imported successfully")
    
    # Test 2: Test model imports inside app context
    print("\n2. Testing model imports...")
    with app.app_context():
        try:
            from app.models import ServingUploadJob, ServingUploadJobItem
            print("✅ ServingUploadJob model imported successfully")
            print("✅ ServingUploadJobItem model imported successfully")
            
            # Test 3: Test database table existence
            print("\n3. Testing database table existence...")
            from app import db
            
            # Check if tables exist
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'serving_upload_job' in tables:
                print("✅ serving_upload_job table exists")
            else:
                print("❌ serving_upload_job table missing")
                
            if 'serving_upload_job_item' in tables:
                print("✅ serving_upload_job_item table exists")
            else:
                print("❌ serving_upload_job_item table missing")
            
            # Test 4: Test a simple query
            print("\n4. Testing simple query...")
            job_count = ServingUploadJob.query.count()
            print(f"✅ ServingUploadJob query successful: {job_count} jobs found")
            
            # Test 5: Test flask_wtf import
            print("\n5. Testing flask_wtf import...")
            from flask_wtf.csrf import generate_csrf
            csrf_token = generate_csrf()
            print(f"✅ CSRF token generated: {csrf_token[:20]}...")
            
            print("\n🎉 All tests passed! The route should work properly.")
            
        except Exception as model_error:
            print(f"❌ Model import error: {model_error}")
            import traceback
            traceback.print_exc()
            
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
