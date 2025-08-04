#!/usr/bin/env python3
"""
Test script to reproduce the issue with 200g peanuts nutrition calculation
"""

from app import create_app
from app.models import MealLog, Food, db
from datetime import date

app = create_app()

with app.app_context():
    # Find peanuts in the database
    peanuts = Food.query.filter(Food.name.ilike('%peanut%')).first()
    
    if not peanuts:
        print("❌ Peanuts not found in database")
        exit(1)
    
    print(f"🥜 Found food: {peanuts.name}")
    print(f"📊 Base nutrition per 100g:")
    print(f"   Calories: {peanuts.calories}")
    print(f"   Protein: {peanuts.protein}")
    print(f"   Carbs: {peanuts.carbs}")
    print(f"   Fat: {peanuts.fat}")
    print(f"   Fiber: {peanuts.fiber}")
    print(f"   Default serving size: {peanuts.default_serving_size_grams}g")
    
    # Test calculation manually
    test_quantity = 200  # 200 grams
    factor = test_quantity / 100  # Should be 2.0
    
    print(f"\n🧮 Manual calculation for {test_quantity}g:")
    print(f"   Factor: {factor}")
    print(f"   Expected calories: {peanuts.calories * factor}")
    print(f"   Expected protein: {peanuts.protein * factor}")
    
    # Create a test meal log
    test_meal = MealLog(
        user_id=1,  # Assuming user 1 exists
        food_id=peanuts.id,
        quantity=test_quantity,
        original_quantity=test_quantity,
        unit_type='grams',
        serving_id=None,
        meal_type='snack',
        date=date.today()
    )
    
    print(f"\n🧪 Testing calculate_nutrition() method:")
    test_meal.calculate_nutrition()
    
    print(f"   Calculated calories: {test_meal.calories}")
    print(f"   Calculated protein: {test_meal.protein}")
    print(f"   Calculated carbs: {test_meal.carbs}")
    print(f"   Calculated fat: {test_meal.fat}")
    print(f"   Calculated fiber: {test_meal.fiber}")
    
    # Check if calculation is correct
    expected_calories = peanuts.calories * factor
    expected_protein = peanuts.protein * factor
    
    if abs(test_meal.calories - expected_calories) < 0.01:
        print("✅ Calories calculation is correct")
    else:
        print(f"❌ Calories calculation is wrong! Expected: {expected_calories}, Got: {test_meal.calories}")
    
    if abs(test_meal.protein - expected_protein) < 0.01:
        print("✅ Protein calculation is correct")
    else:
        print(f"❌ Protein calculation is wrong! Expected: {expected_protein}, Got: {test_meal.protein}")
    
    # Now check existing meal logs for today
    print(f"\n📅 Checking today's meal logs...")
    today_logs = MealLog.query.filter_by(date=date.today()).all()
    
    total_calories = 0
    total_protein = 0
    
    for log in today_logs:
        print(f"   Meal {log.id}: {log.food.name if log.food else 'Unknown'}")
        print(f"     Quantity: {log.quantity}g (original: {log.original_quantity})")
        print(f"     Stored calories: {log.calories}")
        print(f"     Stored protein: {log.protein}")
        
        if log.calories is not None:
            total_calories += log.calories
        if log.protein is not None:
            total_protein += log.protein
    
    print(f"\n📊 Today's totals:")
    print(f"   Total calories: {total_calories}")
    print(f"   Total protein: {total_protein}")
