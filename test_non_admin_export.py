#!/usr/bin/env python3
"""
Comprehensive test script for export functionality with non-admin user
Tests the complete flow: login -> reports page -> CSV export
"""

import requests
import time
import csv
import io
from requests.exceptions import ConnectionError, RequestException

class NutriTrackerTester:
    def __init__(self, base_url="http://127.0.0.1:5001"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_server_connection(self):
        """Test if server is running and accessible"""
        print("🔍 Testing server connection...")
        try:
            response = self.session.get(f"{self.base_url}/")
            print(f"✅ Server accessible - Status: {response.status_code}")
            return True
        except ConnectionError:
            print("❌ Server not accessible - Make sure Flask server is running on port 5001")
            return False
        except Exception as e:
            print(f"❌ Server connection error: {e}")
            return False
    
    def register_test_user(self):
        """Register a test non-admin user"""
        print("\n📝 Creating test user...")
        
        # First check if we can access register page
        try:
            register_page = self.session.get(f"{self.base_url}/auth/register")
            if register_page.status_code != 200:
                print(f"⚠️  Register page status: {register_page.status_code}")
                return False
                
            # Register test user
            register_data = {
                'username': 'testuser',
                'email': 'test@example.com',
                'password': 'testpass123',
                'confirm_password': 'testpass123',
                'first_name': 'Test',
                'last_name': 'User'
            }
            
            register_response = self.session.post(f"{self.base_url}/auth/register", data=register_data)
            
            if register_response.status_code == 200:
                # Check if registration was successful (might redirect or show success message)
                if "welcome" in register_response.text.lower() or "login" in register_response.text.lower():
                    print("✅ Test user created successfully")
                    return True
                else:
                    print("⚠️  User might already exist or registration failed")
                    return True  # Continue anyway, user might already exist
            else:
                print(f"⚠️  Registration status: {register_response.status_code}")
                return True  # Continue anyway
                
        except Exception as e:
            print(f"⚠️  Registration error (continuing anyway): {e}")
            return True  # Continue anyway, user might already exist
    
    def login_as_non_admin(self):
        """Login as non-admin test user"""
        print("\n🔑 Logging in as non-admin user...")
        
        try:
            # Get login page
            login_page = self.session.get(f"{self.base_url}/auth/login")
            if login_page.status_code != 200:
                print(f"❌ Cannot access login page - Status: {login_page.status_code}")
                return False
            
            print("✅ Login page accessible")
            
            # Attempt login
            login_data = {
                'username': 'testuser',
                'password': 'testpass123'
            }
            
            login_response = self.session.post(f"{self.base_url}/auth/login", data=login_data, allow_redirects=False)
            
            print(f"📊 Login response status: {login_response.status_code}")
            
            # Check if login was successful (should redirect)
            if login_response.status_code == 302:
                redirect_location = login_response.headers.get('Location', '')
                print(f"✅ Login successful - Redirected to: {redirect_location}")
                
                # Follow redirect to dashboard
                dashboard_response = self.session.get(f"{self.base_url}{redirect_location}")
                if dashboard_response.status_code == 200:
                    print("✅ Dashboard accessible after login")
                    return True
                else:
                    print(f"⚠️  Dashboard access issue - Status: {dashboard_response.status_code}")
                    return False
            else:
                print(f"❌ Login failed - Status: {login_response.status_code}")
                # Try to see what went wrong
                if "invalid" in login_response.text.lower():
                    print("   Reason: Invalid credentials")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def test_reports_page_access(self):
        """Test access to reports page"""
        print("\n📊 Testing reports page access...")
        
        try:
            reports_response = self.session.get(f"{self.base_url}/dashboard/reports")
            
            print(f"📈 Reports page status: {reports_response.status_code}")
            
            if reports_response.status_code == 200:
                print("✅ Reports page accessible")
                
                # Check if export buttons are present
                if "export-data" in reports_response.text.lower():
                    print("✅ Export buttons found on reports page")
                    return True
                else:
                    print("⚠️  Export buttons not found on reports page")
                    return False
            else:
                print(f"❌ Cannot access reports page - Status: {reports_response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Reports page error: {e}")
            return False
    
    def test_csv_export(self, period="7"):
        """Test CSV export functionality"""
        print(f"\n📤 Testing CSV export (period: {period} days)...")
        
        try:
            export_url = f"{self.base_url}/dashboard/export-data"
            params = {'format': 'csv', 'period': period}
            
            export_response = self.session.get(export_url, params=params)
            
            print(f"📊 Export response status: {export_response.status_code}")
            print(f"📋 Content-Type: {export_response.headers.get('Content-Type', 'Not set')}")
            print(f"📏 Content-Length: {len(export_response.content)} bytes")
            
            if export_response.status_code == 200:
                # Check if it's actually CSV content
                content_type = export_response.headers.get('Content-Type', '')
                
                if 'csv' in content_type:
                    print("✅ CSV export successful!")
                    
                    # Try to parse CSV to verify it's valid
                    try:
                        csv_content = export_response.text
                        csv_reader = csv.reader(io.StringIO(csv_content))
                        rows = list(csv_reader)
                        
                        print(f"📊 CSV has {len(rows)} rows")
                        
                        if len(rows) > 0:
                            headers = rows[0]
                            print(f"📋 CSV headers: {headers}")
                            
                            if len(rows) > 1:
                                print(f"📝 Sample data row: {rows[1]}")
                            else:
                                print("📝 No data rows (empty export)")
                        
                        return True
                        
                    except csv.Error as e:
                        print(f"❌ Invalid CSV format: {e}")
                        print(f"📄 Response content preview: {export_response.text[:200]}...")
                        return False
                        
                else:
                    print(f"❌ Unexpected content type: {content_type}")
                    print(f"📄 Response content preview: {export_response.text[:200]}...")
                    return False
            else:
                print(f"❌ Export failed - Status: {export_response.status_code}")
                print(f"📄 Error content: {export_response.text[:500]}...")
                return False
                
        except Exception as e:
            print(f"❌ CSV export error: {e}")
            return False
    
    def test_multiple_periods(self):
        """Test export with different periods"""
        print("\n🔄 Testing multiple export periods...")
        
        periods = ['7', '30', '90']
        results = {}
        
        for period in periods:
            print(f"\n   📅 Testing {period}-day export...")
            success = self.test_csv_export(period)
            results[period] = success
            
            if success:
                print(f"   ✅ {period}-day export: SUCCESS")
            else:
                print(f"   ❌ {period}-day export: FAILED")
            
            time.sleep(1)  # Brief pause between tests
        
        return results
    
    def run_complete_test(self):
        """Run the complete test suite"""
        print("🚀 Starting comprehensive export functionality test...")
        print("="*60)
        
        # Test 1: Server connection
        if not self.test_server_connection():
            return False
        
        # Test 2: Register test user (optional, might fail if user exists)
        self.register_test_user()
        
        # Test 3: Login as non-admin user
        if not self.login_as_non_admin():
            return False
        
        # Test 4: Access reports page
        if not self.test_reports_page_access():
            return False
        
        # Test 5: Test CSV exports
        export_results = self.test_multiple_periods()
        
        # Summary
        print("\n" + "="*60)
        print("📋 TEST SUMMARY:")
        print("="*60)
        
        successful_exports = sum(1 for success in export_results.values() if success)
        total_exports = len(export_results)
        
        print(f"✅ Server Connection: OK")
        print(f"✅ User Login: OK")
        print(f"✅ Reports Page Access: OK")
        print(f"📊 CSV Exports: {successful_exports}/{total_exports} successful")
        
        for period, success in export_results.items():
            status = "✅ OK" if success else "❌ FAILED"
            print(f"   - {period} days: {status}")
        
        overall_success = successful_exports == total_exports
        
        if overall_success:
            print("\n🎉 ALL TESTS PASSED!")
            print("   The export functionality is working correctly for non-admin users.")
        else:
            print("\n⚠️  SOME TESTS FAILED!")
            print("   Check the detailed output above for specific issues.")
        
        return overall_success

def main():
    """Main test execution"""
    tester = NutriTrackerTester()
    
    try:
        success = tester.run_complete_test()
        
        if success:
            print("\n✅ Export functionality verified successfully!")
        else:
            print("\n❌ Export functionality has issues!")
            
        return success
        
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        return False
    except Exception as e:
        print(f"\n💥 Unexpected error during testing: {e}")
        return False

if __name__ == "__main__":
    main()
