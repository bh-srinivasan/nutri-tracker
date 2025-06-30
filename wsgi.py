#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
    # Add the project directory to Python path
    sys.path.insert(0, os.path.dirname(__file__))
    
    from app import create_app
    
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
