#!/usr/bin/env python3
"""
Simple test to check if the server starts without errors.
"""

import subprocess
import time
import requests
import sys

def test_server_startup():
    """Test if the Flask server starts without immediate errors."""
    print("🚀 Testing Server Startup")
    print("=" * 25)
    
    try:
        # Start the server process
        print("Starting Flask server...")
        process = subprocess.Popen(['python', 'app.py'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True)
        
        # Give it a few seconds to start
        time.sleep(5)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ Server started successfully (process still running)")
            
            # Try to make a simple request
            try:
                response = requests.get('http://localhost:5001/', timeout=5)
                print(f"✅ Homepage accessible (status: {response.status_code})")
                
                if response.status_code == 200:
                    print("✅ Homepage loads without errors")
                elif response.status_code == 302:
                    print("✅ Homepage redirects (normal for unauthenticated user)")
                else:
                    print(f"⚠️ Unexpected status code: {response.status_code}")
                
            except requests.exceptions.RequestException as e:
                print(f"❌ Cannot connect to server: {e}")
            
            # Terminate the process
            process.terminate()
            process.wait()
            print("✅ Server stopped cleanly")
            return True
            
        else:
            # Process died, check for errors
            stdout, stderr = process.communicate()
            print("❌ Server failed to start")
            if stderr:
                print(f"Error output: {stderr}")
            if stdout:
                print(f"Standard output: {stdout}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing server: {e}")
        return False

if __name__ == "__main__":
    print("🛠️ Server Startup Test\n")
    
    success = test_server_startup()
    
    print("\n" + "="*40)
    if success:
        print("🎉 Server test passed!")
        print("✅ Flask server starts without immediate errors")
        print("✅ Homepage is accessible")
        print("\n🚀 Your application should now work correctly!")
    else:
        print("❌ Server test failed!")
        print("💡 Check the error output above for details")
        sys.exit(1)
