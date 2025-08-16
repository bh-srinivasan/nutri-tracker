#!/usr/bin/env python3
"""Test the /api/foods/<id>/servings endpoint."""

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, Food, FoodServing

def test_servings_endpoint_data():
    """Test data that servings endpoint should return"""
    app = create_app()
    
    with app.app_context():
        # Test food 93
        food = Food.query.get(93)
        if food:
            print(f"✅ Food found: {food.name}")
            
            # Test servings query like the API does
            servings = FoodServing.query.filter_by(food_id=93).all()
            print(f"   Servings count: {len(servings)}")
            
            # Test the exact JSON structure that should be returned
            servings_data = [{
                'id': s.id if s.id else None,
                'unit_type': s.unit,
                'size_in_grams': s.grams_per_unit,
                'description': s.serving_name
            } for s in servings]
            
            print("   Expected API response structure:")
            import json
            for serving in servings_data:
                print(f"     {json.dumps(serving, indent=6)}")
                
        else:
            print("❌ Food 93 not found")

if __name__ == "__main__":
    test_servings_endpoint_data()
