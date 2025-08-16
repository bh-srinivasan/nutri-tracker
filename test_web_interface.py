#!/usr/bin/env python3
"""
Test the web interface for the new flexible MealLog system.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, User, Food, FoodServing, MealLog
from datetime import date

def test_web_interface():
    """Test the web routes with the new system."""
    app = create_app()
    
    with app.app_context():
        with app.test_client() as client:
            print("🌐 Testing web interface for flexible MealLog system...")
            
            # Login as admin
            response = client.post('/auth/login', data={
                'username': 'admin',
                'password': 'admin'
            })
            
            if response.status_code != 302:  # Should redirect after successful login
                print(f"❌ Login failed: {response.status_code}")
                return
            
            print("   ✅ Logged in successfully")
            
            # Get test data
            food = Food.query.filter_by(name='Idli small').first()
            serving = FoodServing.query.filter_by(food_id=food.id).first() if food else None
            
            if not food or not serving:
                print("❌ Missing test data")
                return
            
            print(f"   📊 Testing with food: {food.name}")
            print(f"   🥄 Testing with serving: {serving.serving_name} ({serving.grams_per_unit}g)")
            
            # Test 1: Grams-based meal logging
            print("\n🔹 Test 1: Web interface grams-based logging")
            response = client.post('/dashboard/log_meal', data={
                'food_id': food.id,
                'quantity': 150.0,
                'unit_type': 'grams',
                'meal_type': 'dinner',
                'date': date.today().strftime('%Y-%m-%d')
            })
            
            if response.status_code == 302:  # Redirect on success
                print("   ✅ Grams-based meal logged via web interface")
            else:
                print(f"   ❌ Grams-based logging failed: {response.status_code}")
                
            # Test 2: Serving-based meal logging
            print("\n🔹 Test 2: Web interface serving-based logging")
            response = client.post('/dashboard/log_meal', data={
                'food_id': food.id,
                'quantity': 1.5,
                'unit_type': 'serving',
                'serving_id': serving.id,
                'meal_type': 'snack',
                'date': date.today().strftime('%Y-%m-%d')
            })
            
            if response.status_code == 302:  # Redirect on success
                print("   ✅ Serving-based meal logged via web interface")
            else:
                print(f"   ❌ Serving-based logging failed: {response.status_code}")
            
            # Verify the logged meals
            print("\n🔍 Verifying logged meals...")
            recent_meals = MealLog.query.filter_by(food_id=food.id).order_by(MealLog.logged_at.desc()).limit(4).all()
            
            for i, meal in enumerate(recent_meals):
                print(f"   📋 Meal {i+1}: {meal.original_quantity} {meal.unit_type}")
                print(f"      Logged grams: {meal.logged_grams}g")
                print(f"      Calories: {meal.calories}")
                print(f"      Meal type: {meal.meal_type}")
                if meal.serving_id:
                    print(f"      Serving: {meal.serving.serving_name}")
                print()
            
            print("✅ Web interface test completed!")

if __name__ == "__main__":
    test_web_interface()
