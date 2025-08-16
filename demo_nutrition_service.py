#!/usr/bin/env python3
"""Demonstration of the nutrition calculation service with real data."""

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, Food, FoodServing
from app.services.nutrition import compute_nutrition

def demo_nutrition_calculation():
    """Demonstrate nutrition calculation with real food data."""
    app = create_app()
    
    with app.app_context():
        # Get a food item (e.g., food ID 93 - Idli small)
        food = Food.query.get(93)
        if not food:
            print("❌ Food 93 not found")
            return
            
        print(f"🍚 Food: {food.name}")
        print(f"   Per 100g nutrition:")
        print(f"   - Calories: {food.calories}")
        print(f"   - Protein: {food.protein}g")
        print(f"   - Carbs: {food.carbs}g")
        print(f"   - Fat: {food.fat}g")
        print(f"   - Fiber: {food.fiber}g")
        print()
        
        # Get the food's serving
        serving = FoodServing.query.filter_by(food_id=food.id).first()
        if serving:
            print(f"📏 Available serving: {serving.serving_name} ({serving.grams_per_unit}g)")
        print()
        
        # Test 1: Direct grams calculation
        print("🔢 Test 1: Direct grams calculation")
        nutrition_150g = compute_nutrition(food, grams=150.0)
        print(f"   For 150g of {food.name}:")
        for nutrient, value in nutrition_150g.items():
            print(f"   - {nutrient.capitalize()}: {value:.1f}")
        print()
        
        # Test 2: Serving-based calculation
        if serving:
            print("🍽️ Test 2: Serving-based calculation")
            nutrition_2_servings = compute_nutrition(food, serving=serving, quantity=2.0)
            print(f"   For 2 servings of {food.name} (2 × {serving.grams_per_unit}g = {2 * serving.grams_per_unit}g):")
            for nutrient, value in nutrition_2_servings.items():
                print(f"   - {nutrient.capitalize()}: {value:.1f}")
            print()
        
        # Test 3: Fractional serving
        if serving:
            print("🥄 Test 3: Fractional serving calculation")
            nutrition_half_serving = compute_nutrition(food, serving=serving, quantity=0.5)
            print(f"   For 0.5 serving of {food.name} (0.5 × {serving.grams_per_unit}g = {0.5 * serving.grams_per_unit}g):")
            for nutrient, value in nutrition_half_serving.items():
                print(f"   - {nutrient.capitalize()}: {value:.1f}")
            print()
        
        # Test 4: Zero amount
        print("🚫 Test 4: Zero amount calculation")
        nutrition_zero = compute_nutrition(food, grams=0.0)
        print(f"   For 0g of {food.name}:")
        for nutrient, value in nutrition_zero.items():
            print(f"   - {nutrient.capitalize()}: {value:.1f}")
        print()
        
        print("✅ All nutrition calculations completed successfully!")

if __name__ == "__main__":
    demo_nutrition_calculation()
