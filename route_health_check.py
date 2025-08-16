#!/usr/bin/env python3
"""
Quick diagnostic script to check route health.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.abspath('.'))

def check_route_health():
    print("=== Food Servings Upload Route Health Check ===")
    
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            # Test 1: Check if route is registered
            print("\n1. Checking route registration...")
            routes = []
            for rule in app.url_map.iter_rules():
                if 'food-servings' in rule.rule:
                    routes.append(f"{rule.rule} -> {rule.endpoint} ({list(rule.methods)})")
            
            if routes:
                print("✅ Food servings routes found:")
                for route in routes:
                    print(f"   {route}")
            else:
                print("❌ No food servings routes found!")
                
            # Test 2: Check model import
            print("\n2. Checking model availability...")
            from app.models import ServingUploadJob, ServingUploadJobItem
            job_count = ServingUploadJob.query.count()
            print(f"✅ ServingUploadJob accessible: {job_count} jobs in database")
            
            # Test 3: Check template existence
            print("\n3. Checking template files...")
            import os
            template_files = [
                'app/templates/admin/food_servings_uploads.html',
                'app/templates/admin/_food_servings_upload_form.html',
                'app/templates/admin/_food_servings_upload_history.html'
            ]
            
            for template in template_files:
                if os.path.exists(template):
                    print(f"✅ {template} exists")
                else:
                    print(f"❌ {template} missing")
            
            # Test 4: Check route function
            print("\n4. Testing route function...")
            with app.test_request_context('/admin/food-servings/uploads'):
                try:
                    from flask import url_for
                    url = url_for('admin.food_servings_uploads')
                    print(f"✅ URL generation works: {url}")
                except Exception as e:
                    print(f"❌ URL generation failed: {e}")
            
            # Test 5: Simulate the route logic
            print("\n5. Testing route logic components...")
            try:
                # Test pagination
                from sqlalchemy import desc
                jobs = ServingUploadJob.query.order_by(desc(ServingUploadJob.created_at)).limit(10).all()
                print(f"✅ Job query works: {len(jobs)} jobs found")
                
                # Test CSRF generation in request context
                with app.test_request_context():
                    from flask_wtf.csrf import generate_csrf
                    csrf = generate_csrf()
                    print(f"✅ CSRF generation works: {csrf[:20]}...")
                    
            except Exception as e:
                print(f"❌ Route logic error: {e}")
                import traceback
                traceback.print_exc()
                
            print("\n=== Health Check Complete ===")
            print("If all tests pass, the route should work correctly.")
            print("If you're still seeing errors, try:")
            print("1. Clear browser cache and reload")
            print("2. Log out and log back in")
            print("3. Access the URL directly: http://127.0.0.1:5001/admin/food-servings/uploads")
    
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_route_health()
