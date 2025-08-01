#!/usr/bin/env python3
"""
Simple server startup script
"""

import os
import sys
from app import create_app

if __name__ == '__main__':
    try:
        print("🚀 Starting Nutri Tracker Server...")
        app = create_app()
        print("✅ Flask app created successfully")
        print("🌐 Server will be available at: http://127.0.0.1:5001")
        print("🔄 Starting server...")
        app.run(debug=True, host='127.0.0.1', port=5001)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
