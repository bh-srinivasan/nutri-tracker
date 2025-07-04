#!/usr/bin/env python3
"""
Start the Nutri Tracker Flask server
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import create_app
    
    print("🚀 Starting Nutri Tracker Server...")
    print("=" * 40)
    
    app = create_app()
    
    print("✅ Flask app created successfully")
    print("🌐 Server will be available at: http://localhost:5001")
    print("🔧 Running in debug mode")
    print("📱 Press Ctrl+C to stop the server")
    print("=" * 40)
    
    # Start the server
    app.run(debug=True, port=5001, host='0.0.0.0')
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("💡 Make sure you're in the correct directory and virtual environment is activated")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error starting server: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
