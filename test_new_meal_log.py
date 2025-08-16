#!/usr/bin/env python3
"""
Test the new MealLog flexible input system.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, User, Food, FoodServing, MealLog
from app.services.nutrition import compute_nutrition
from datetime import date

def test_meal_logging():
    """Test both grams and serving-based meal logging."""
    app = create_app()
    
    with app.app_context():
        print("🧪 Testing new MealLog flexible input system...")
        
        # Get test data
        user = User.query.filter_by(username='admin').first()
        food = Food.query.filter_by(name='Idli small').first()
        
        if not user or not food:
            print("❌ Missing test data (admin user or Idli small food)")
            return
            
        print(f"   📊 Testing with food: {food.name}")
        print(f"   👤 Testing with user: {user.username}")
        
        # Test 1: Grams-based logging (direct)
        print("\n🔹 Test 1: Grams-based logging (100g)")
        grams_amount = 100.0
        nutrition_result = compute_nutrition(food, grams=grams_amount)
        
        meal_log_grams = MealLog(
            user_id=user.id,
            food_id=food.id,
            quantity=grams_amount,
            original_quantity=grams_amount,
            unit_type='grams',
            serving_id=None,
            meal_type='breakfast',
            date=date.today(),
            logged_grams=grams_amount,  # Direct grams
            calories=nutrition_result['calories'],
            protein=nutrition_result['protein'],
            carbs=nutrition_result['carbs'],
            fat=nutrition_result['fat'],
            fiber=nutrition_result['fiber'],
            sugar=nutrition_result['sugar'],
            sodium=nutrition_result['sodium']
        )
        
        db.session.add(meal_log_grams)
        print(f"   ✅ Created grams-based MealLog: {grams_amount}g, {nutrition_result['calories']} cal")
        
        # Test 2: Serving-based logging
        serving = FoodServing.query.filter_by(food_id=food.id).first()
        if serving:
            print(f"\n🔹 Test 2: Serving-based logging (2x {serving.serving_name})")
            serving_quantity = 2.0
            logged_grams = serving_quantity * serving.grams_per_unit
            nutrition_result = compute_nutrition(food, serving=serving, quantity=serving_quantity)
            
            meal_log_serving = MealLog(
                user_id=user.id,
                food_id=food.id,
                quantity=serving_quantity,
                original_quantity=serving_quantity,
                unit_type='serving',
                serving_id=serving.id,
                meal_type='lunch',
                date=date.today(),
                logged_grams=logged_grams,  # Computed from serving
                calories=nutrition_result['calories'],
                protein=nutrition_result['protein'],
                carbs=nutrition_result['carbs'],
                fat=nutrition_result['fat'],
                fiber=nutrition_result['fiber'],
                sugar=nutrition_result['sugar'],
                sodium=nutrition_result['sodium']
            )
            
            db.session.add(meal_log_serving)
            print(f"   ✅ Created serving-based MealLog: {logged_grams}g, {nutrition_result['calories']} cal")
        else:
            print(f"\n⚠️  No servings found for {food.name}")
        
        # Commit changes
        db.session.commit()
        print("\n✅ Test meals logged successfully!")
        
        # Verify backward compatibility
        print("\n🔄 Testing backward compatibility...")
        recent_meals = MealLog.query.filter_by(user_id=user.id).order_by(MealLog.logged_at.desc()).limit(2).all()
        
        for meal in recent_meals:
            print(f"   📋 Meal: {meal.food.name}")
            print(f"      Original quantity: {meal.original_quantity} {meal.unit_type}")
            print(f"      Logged grams: {meal.logged_grams}g")
            print(f"      Calories: {meal.calories}")
            if meal.serving_id:
                print(f"      Serving: {meal.serving.serving_name}")

if __name__ == "__main__":
    test_meal_logging()
