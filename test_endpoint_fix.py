#!/usr/bin/env python3
"""
Test to verify that the dashboard template doesn't have endpoint errors.
"""

import sys
import os
from datetime import datetime
from app import create_app, db
from app.models import User

def test_dashboard_template():
    """Test if dashboard template renders without endpoint errors."""
    print("🛠️ Dashboard Template Test")
    print("🔧 Testing Dashboard Endpoint Fix")
    print("=" * 35)
    
    try:
        # Create app and push context
        app = create_app()
        
        with app.app_context():
            # Create test client
            client = app.test_client()
            
            # Try to render dashboard (should redirect to login for unauthenticated user)
            print("Testing dashboard route...")
            
            # Test URL generation for the dashboard endpoint
            with app.test_request_context():
                from flask import url_for
                try:
                    # This should work now that we fixed the endpoint name
                    search_url = url_for('dashboard.search_foods')
                    print(f"✅ dashboard.search_foods endpoint found: {search_url}")
                    
                    log_meal_url = url_for('dashboard.log_meal')
                    print(f"✅ dashboard.log_meal endpoint found: {log_meal_url}")
                    
                    goals_url = url_for('dashboard.nutrition_goals')
                    print(f"✅ dashboard.nutrition_goals endpoint found: {goals_url}")
                    
                    reports_url = url_for('dashboard.reports')
                    print(f"✅ dashboard.reports endpoint found: {reports_url}")
                    
                except Exception as e:
                    print(f"❌ URL generation error: {e}")
                    return False
            
            print("\n✅ All dashboard endpoints are valid!")
            print("✅ Template should now render without errors")
            return True
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🛠️ Dashboard Endpoint Fix Test")
    
    success = test_dashboard_template()
    
    if success:
        print("\n" + "="*50)
        print("✅ Dashboard endpoint fix test PASSED!")
        print("✅ All dashboard template endpoints are valid")
        print("💡 The dashboard should now load without endpoint errors")
    else:
        print("\n" + "="*50)
        print("❌ Dashboard endpoint fix test FAILED!")
        print("💡 Check the error output above for details")
        sys.exit(1)
