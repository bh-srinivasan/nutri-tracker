"""
Direct test of the food_uploads route to identify the specific error
"""
from app import create_app, db
from app.models import User, BulkUploadJob
from flask import url_for
import traceback

def test_food_uploads_route_directly():
    """Test the food_uploads route directly to see the exact error."""
    
    app = create_app()
    with app.app_context():
        with app.test_client() as client:
            # Get admin user
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                print("❌ No admin user found")
                return
            
            print(f"✅ Admin user found: {admin.username}")
            
            # Login as admin
            with client.session_transaction() as sess:
                sess['_user_id'] = str(admin.id)
                sess['_fresh'] = True
            
            print("✅ Simulated admin login")
            
            try:
                # Test the base route
                print("🧪 Testing /admin/food-uploads")
                response = client.get('/admin/food-uploads')
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("   ✅ Base route works")
                elif response.status_code == 302:
                    print(f"   🔄 Redirects to: {response.location}")
                else:
                    print(f"   ❌ Error: {response.status_code}")
                    print(f"   Data: {response.get_data(as_text=True)[:200]}...")
                
                # Test with tab=history parameter
                print("🧪 Testing /admin/food-uploads?tab=history")
                response = client.get('/admin/food-uploads?tab=history')
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("   ✅ History tab works")
                elif response.status_code == 302:
                    print(f"   🔄 Redirects to: {response.location}")
                else:
                    print(f"   ❌ Error: {response.status_code}")
                    print(f"   Data: {response.get_data(as_text=True)[:200]}...")
                    
            except Exception as e:
                print(f"❌ Exception occurred: {e}")
                print("📍 Full traceback:")
                traceback.print_exc()

if __name__ == "__main__":
    test_food_uploads_route_directly()
