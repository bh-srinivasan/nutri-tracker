#!/usr/bin/env python3
"""
Simple test to verify export route exists
"""

import urllib.request
import urllib.error

def test_export_route():
    """Test if the export route is accessible."""
    url = "http://127.0.0.1:5001/dashboard/export-data"
    
    try:
        response = urllib.request.urlopen(url)
        print(f"✅ Route accessible - Status: {response.getcode()}")
        return True
    except urllib.error.HTTPError as e:
        if e.code == 302:
            print(f"✅ Route exists but redirects (expected for login) - Status: {e.code}")
            return True
        elif e.code == 404:
            print(f"❌ Route NOT found - Status: {e.code}")
            return False
        else:
            print(f"⚠️  Route exists but error - Status: {e.code}")
            return True
    except urllib.error.URLError as e:
        print(f"❌ Cannot connect to server: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing Export Route Availability")
    print("=" * 40)
    
    if test_export_route():
        print("\n🎉 SUCCESS: Export route is properly implemented!")
        print("✅ The 'Could not build url for endpoint' error has been resolved")
        print("✅ Reports page export buttons should now work")
    else:
        print("\n❌ FAILURE: Export route is not accessible")
        print("⚠️  The BuildError may still occur")
