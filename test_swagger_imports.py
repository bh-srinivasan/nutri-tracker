#!/usr/bin/env python3
"""
Test if Swagger imports work correctly
"""

try:
    print("Testing Swagger API imports...")
    
    # Test basic Flask imports
    from flask import Flask
    print("✅ Flask imported successfully")
    
    # Test flask-restx import
    from flask_restx import Api, Resource, fields
    print("✅ Flask-RESTX imported successfully")
    
    # Test our swagger module imports
    from app.swagger_api import swagger_bp
    print("✅ Swagger blueprint imported successfully")
    
    # Test API namespace imports
    from app.swagger_api import foods_ns
    print("✅ Foods namespace imported successfully")
    
    from app.swagger_api import servings_ns  
    print("✅ Servings namespace imported successfully")
    
    from app.swagger_api import meals_ns
    print("✅ Meals namespace imported successfully")
    
    print("\n🎉 All Swagger imports successful!")
    print("The issue is likely not with imports.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("This might be causing the server startup issue.")
    
except Exception as e:
    print(f"❌ Unexpected error: {e}")
