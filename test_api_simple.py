#!/usr/bin/env python3
"""
Simple test for API endpoints while server is running
"""
import requests
import time

def test_endpoints():
    print("🔍 Testing Swagger UI and API v2 endpoints...")
    
    base_url = "http://127.0.0.1:5001"
    
    endpoints = [
        {"name": "Swagger UI", "url": f"{base_url}/api/docs/"},
        {"name": "API v2 Food Search", "url": f"{base_url}/api/v2/foods/search?q=test"}
    ]
    
    for endpoint in endpoints:
        try:
            print(f"\n🌐 Testing: {endpoint['name']}")
            print(f"   URL: {endpoint['url']}")
            
            response = requests.get(endpoint['url'], timeout=5)
            print(f"   ✅ Status: {response.status_code}")
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                print(f"   📄 Content-Type: {content_type}")
                
                if 'html' in content_type:
                    print(f"   📏 HTML Length: {len(response.text)} chars")
                    if 'swagger' in response.text.lower():
                        print("   🎉 Swagger UI detected!")
                        
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Connection failed")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n🏁 Test completed!")

if __name__ == "__main__":
    test_endpoints()
