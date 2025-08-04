#!/usr/bin/env python3
"""
Debug script to test the specific 200g peanuts issue
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import MealLog, Food, User, db
from datetime import date

app = create_app()

with app.app_context():
    # Create a test context with a user
    test_user = User.query.first()
    if not test_user:
        print("❌ No users found in database")
        exit(1)
    
    print(f"👤 Using test user: {test_user.username}")
    
    # Find peanuts
    peanuts = Food.query.filter(Food.name.ilike('%peanut%')).first()
    if not peanuts:
        print("❌ Peanuts not found")
        exit(1)
    
    print(f"🥜 Testing with: {peanuts.name}")
    print(f"📊 Peanuts nutrition per 100g:")
    print(f"   Calories: {peanuts.calories}")
    print(f"   Protein: {peanuts.protein}")
    print(f"   Default serving: {peanuts.default_serving_size_grams}g")
    
    # Test the exact scenario: 200g of peanuts
    test_quantity = 200.0
    original_quantity = 200.0
    
    print(f"\n🧪 Creating MealLog for {test_quantity}g peanuts...")
    
    # Create the meal log exactly like the dashboard route does
    meal_log = MealLog(
        user_id=test_user.id,
        food_id=peanuts.id,
        quantity=test_quantity,  # normalized quantity in grams
        original_quantity=original_quantity,
        unit_type='grams',
        serving_id=None,
        meal_type='snack',
        date=date.today()
    )
    
    print(f"📝 Before calculate_nutrition():")
    print(f"   meal_log.quantity: {meal_log.quantity}")
    print(f"   meal_log.calories: {meal_log.calories}")
    print(f"   meal_log.protein: {meal_log.protein}")
    
    # Call calculate_nutrition
    meal_log.calculate_nutrition()
    
    print(f"📝 After calculate_nutrition():")
    print(f"   meal_log.calories: {meal_log.calories}")
    print(f"   meal_log.protein: {meal_log.protein}")
    print(f"   meal_log.carbs: {meal_log.carbs}")
    print(f"   meal_log.fat: {meal_log.fat}")
    print(f"   meal_log.fiber: {meal_log.fiber}")
    
    # Manual verification
    expected_factor = test_quantity / 100  # Should be 2.0
    expected_calories = peanuts.calories * expected_factor
    expected_protein = peanuts.protein * expected_factor
    
    print(f"\n🔍 Manual verification:")
    print(f"   Factor: {expected_factor}")
    print(f"   Expected calories: {expected_calories}")
    print(f"   Expected protein: {expected_protein}")
    print(f"   Actual calories: {meal_log.calories}")
    print(f"   Actual protein: {meal_log.protein}")
    
    # Check if values match
    calories_match = abs(meal_log.calories - expected_calories) < 0.01 if meal_log.calories else False
    protein_match = abs(meal_log.protein - expected_protein) < 0.01 if meal_log.protein else False
    
    print(f"\n✅ Results:")
    print(f"   Calories match: {calories_match}")
    print(f"   Protein match: {protein_match}")
    
    if not calories_match or not protein_match:
        print("❌ Issue found with nutrition calculation!")
    else:
        print("✅ Nutrition calculation is working correctly")
    
    # Test saving to database
    print(f"\n💾 Testing database save...")
    try:
        db.session.add(meal_log)
        db.session.commit()
        print("✅ Successfully saved to database")
        
        # Retrieve and verify
        saved_log = MealLog.query.get(meal_log.id)
        print(f"🔍 Retrieved from database:")
        print(f"   ID: {saved_log.id}")
        print(f"   Calories: {saved_log.calories}")
        print(f"   Protein: {saved_log.protein}")
        
    except Exception as e:
        print(f"❌ Database save failed: {e}")
        db.session.rollback()
    
    # Check today's totals
    print(f"\n📊 Today's nutrition totals:")
    today_logs = MealLog.query.filter_by(
        user_id=test_user.id,
        date=date.today()
    ).all()
    
    total_calories = sum(log.calories or 0 for log in today_logs)
    total_protein = sum(log.protein or 0 for log in today_logs)
    
    print(f"   Meal logs: {len(today_logs)}")
    print(f"   Total calories: {total_calories}")
    print(f"   Total protein: {total_protein}")
    
    for log in today_logs:
        print(f"   - {log.food.name if log.food else 'Unknown'}: {log.calories}cal, {log.protein}g protein")
