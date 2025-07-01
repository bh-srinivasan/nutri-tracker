#!/usr/bin/env python3
"""
Test script to verify admin routes are working properly.
"""
import requests
import sys
from requests.exceptions import ConnectionError, RequestException


def test_route(session, url, name, expected_redirect=False):
    """Test a single route."""
    try:
        response = session.get(url, allow_redirects=False)
        
        if expected_redirect:
            if response.status_code in [302, 301]:
                print(f"✓ {name}: Redirects properly (status: {response.status_code})")
                return True
            else:
                print(f"✗ {name}: Expected redirect but got status {response.status_code}")
                return False
        else:
            if response.status_code == 200:
                print(f"✓ {name}: OK (status: {response.status_code})")
                return True
            elif response.status_code in [302, 301]:
                print(f"⚠ {name}: Redirects (status: {response.status_code}) - likely needs authentication")
                return True  # This is expected for protected routes when not logged in
            else:
                print(f"✗ {name}: Error (status: {response.status_code})")
                return False
                
    except Exception as e:
        print(f"✗ {name}: Exception - {str(e)}")
        return False


def main():
    """Test admin routes."""
    base_url = "http://127.0.0.1:5001"
    
    # Test if server is running
    try:
        response = requests.get(base_url, timeout=5)
        print(f"✓ Server is running (status: {response.status_code})")
    except ConnectionError:
        print("✗ Cannot connect to server. Is it running on port 5001?")
        return False
    except Exception as e:
        print(f"✗ Error connecting to server: {e}")
        return False
    
    # Create session for testing
    session = requests.Session()
    
    print("\n=== Testing Public Routes ===")
    routes = [
        ("/", "Home page"),
        ("/auth/login", "Login page"),
        ("/auth/register", "Register page"),
    ]
    
    for route, name in routes:
        test_route(session, f"{base_url}{route}", name)
    
    print("\n=== Testing Admin Routes (should redirect to login) ===")
    admin_routes = [
        ("/admin/", "Admin dashboard"),
        ("/admin/users", "Manage users"),
        ("/admin/foods", "Manage foods"),
        ("/admin/foods/bulk-upload", "Bulk upload"),
        ("/admin/change-password", "Admin change password"),
    ]
    
    for route, name in admin_routes:
        test_route(session, f"{base_url}{route}", name, expected_redirect=True)
    
    print("\n=== Testing Dashboard Routes (should redirect to login) ===")
    dashboard_routes = [
        ("/dashboard/", "User dashboard"),
        ("/dashboard/log-meal", "Log meal"),
        ("/dashboard/history", "Meal history"),
        ("/dashboard/nutrition-goals", "Nutrition goals"),
        ("/dashboard/challenges", "Challenges"),
        ("/dashboard/reports", "Reports"),
    ]
    
    for route, name in dashboard_routes:
        test_route(session, f"{base_url}{route}", name, expected_redirect=True)
    
    print("\n=== Route Testing Complete ===")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
