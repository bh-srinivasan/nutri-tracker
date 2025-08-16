#!/usr/bin/env python3
"""Direct test of FoodServing model attributes."""

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, Food, FoodServing

def test_food_serving_model():
    """Test FoodServing model attributes"""
    app = create_app()
    
    with app.app_context():
        # Test food 93
        food = Food.query.get(93)
        if food:
            print(f"✅ Food found: {food.name}")
            print(f"   Category: {food.category}")
            print(f"   Default serving ID: {food.default_serving_id}")
            
            # Test servings
            servings = FoodServing.query.filter_by(food_id=93).all()
            print(f"   Servings count: {len(servings)}")
            
            for s in servings:
                print(f"   Serving ID {s.id}:")
                print(f"   - Name: {s.serving_name}")
                print(f"   - Unit: {s.unit}")
                print(f"   - Grams per unit: {s.grams_per_unit}")
                
                # Test the actual attributes that were causing issues
                try:
                    unit_value = s.unit  # This should work
                    print(f"   - ✅ s.unit = {unit_value}")
                except AttributeError as e:
                    print(f"   - ❌ s.unit failed: {e}")
                    
                try:
                    grams_value = s.grams_per_unit  # This should work
                    print(f"   - ✅ s.grams_per_unit = {grams_value}")
                except AttributeError as e:
                    print(f"   - ❌ s.grams_per_unit failed: {e}")
                
                print()
                
        else:
            print("❌ Food 93 not found")

if __name__ == "__main__":
    test_food_serving_model()
