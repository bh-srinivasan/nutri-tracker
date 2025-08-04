#!/usr/bin/env python3
"""
Test the exact 200g peanuts scenario by simulating the dashboard route
"""

from app import create_app
from app.models import *
from app.dashboard.forms import MealLogForm
from datetime import date
import tempfile
import os

app = create_app()

with app.app_context():
    print("🧪 TESTING 200G PEANUTS MEAL LOGGING")
    print("=" * 50)
    
    # Get test user
    user = User.query.first()
    if not user:
        print("❌ No users found")
        exit(1)
    print(f"👤 Using user: {user.username}")
    
    # Find peanuts
    peanuts = Food.query.filter(Food.name.ilike('%peanut%')).first()
    if not peanuts:
        print("❌ Peanuts not found")
        exit(1)
    print(f"🥜 Found: {peanuts.name}")
    print(f"📊 Base nutrition per 100g:")
    print(f"   Calories: {peanuts.calories}")
    print(f"   Protein: {peanuts.protein}")
    print(f"   Carbs: {peanuts.carbs}")
    print(f"   Fat: {peanuts.fat}")
    print(f"   Fiber: {peanuts.fiber}")
    
    # Simulate the exact dashboard route logic
    print(f"\n🔄 Simulating dashboard route for 200g peanuts...")
    
    # Step 1: Validate the food
    if not peanuts.is_verified:
        print("❌ Food is not verified")
        exit(1)
    print("✅ Food is verified")
    
    # Step 2: Calculate normalized quantity (exactly like in dashboard route)
    original_quantity = 200.0
    normalized_quantity = original_quantity  # Since we're using grams
    unit_type = 'grams'
    serving_id = None
    meal_type = 'snack'
    
    print(f"📏 Quantity calculation:")
    print(f"   Original quantity: {original_quantity}")
    print(f"   Normalized quantity: {normalized_quantity}")
    print(f"   Unit type: {unit_type}")
    
    # Step 3: Create meal log (exactly like in dashboard route)
    meal_log = MealLog(
        user_id=user.id,
        food_id=peanuts.id,
        quantity=normalized_quantity,  # Always stored in grams
        original_quantity=original_quantity,
        unit_type=unit_type,
        serving_id=serving_id,
        meal_type=meal_type,
        date=date.today()
    )
    
    print(f"\n📝 Created MealLog:")
    print(f"   User ID: {meal_log.user_id}")
    print(f"   Food ID: {meal_log.food_id}")
    print(f"   Quantity: {meal_log.quantity}")
    print(f"   Original quantity: {meal_log.original_quantity}")
    print(f"   Unit type: {meal_log.unit_type}")
    
    # Step 4: Calculate nutrition (exactly like in dashboard route)
    print(f"\n🧮 Before calculate_nutrition():")
    print(f"   meal_log.calories: {meal_log.calories}")
    print(f"   meal_log.protein: {meal_log.protein}")
    
    meal_log.calculate_nutrition()
    
    print(f"🧮 After calculate_nutrition():")
    print(f"   meal_log.calories: {meal_log.calories}")
    print(f"   meal_log.protein: {meal_log.protein}")
    print(f"   meal_log.carbs: {meal_log.carbs}")
    print(f"   meal_log.fat: {meal_log.fat}")
    print(f"   meal_log.fiber: {meal_log.fiber}")
    
    # Step 5: Verify calculation manually
    expected_factor = normalized_quantity / 100  # Should be 2.0
    expected_calories = peanuts.calories * expected_factor if peanuts.calories else None
    expected_protein = peanuts.protein * expected_factor if peanuts.protein else None
    
    print(f"\n🔍 Manual verification:")
    print(f"   Factor: {expected_factor}")
    print(f"   Expected calories: {expected_calories}")
    print(f"   Expected protein: {expected_protein}")
    
    # Check if calculation is correct
    calories_correct = abs(meal_log.calories - expected_calories) < 0.01 if meal_log.calories and expected_calories else False
    protein_correct = abs(meal_log.protein - expected_protein) < 0.01 if meal_log.protein and expected_protein else False
    
    print(f"   Calories calculation correct: {calories_correct}")
    print(f"   Protein calculation correct: {protein_correct}")
    
    if not calories_correct or not protein_correct:
        print("❌ NUTRITION CALCULATION FAILED!")
        if meal_log.calories is None:
            print("   - Calories is None")
        if meal_log.protein is None:
            print("   - Protein is None")
        if peanuts.calories is None:
            print("   - Base calories is None")
        if peanuts.protein is None:
            print("   - Base protein is None")
    else:
        print("✅ NUTRITION CALCULATION CORRECT")
    
    # Step 6: Save to database (exactly like in dashboard route)
    print(f"\n💾 Saving to database...")
    try:
        db.session.add(meal_log)
        db.session.commit()
        print(f"✅ Saved with ID: {meal_log.id}")
        
        # Verify it was saved correctly
        saved_log = MealLog.query.get(meal_log.id)
        print(f"🔍 Retrieved from database:")
        print(f"   Calories: {saved_log.calories}")
        print(f"   Protein: {saved_log.protein}")
        
        if saved_log.calories != meal_log.calories or saved_log.protein != meal_log.protein:
            print("❌ VALUES CHANGED DURING DATABASE SAVE!")
        else:
            print("✅ Values preserved in database")
            
    except Exception as e:
        print(f"❌ Database save failed: {e}")
        db.session.rollback()
        exit(1)
    
    # Step 7: Check today's totals (like dashboard index does)
    print(f"\n📊 Checking today's nutrition totals...")
    today_logs = MealLog.query.filter_by(
        user_id=user.id, 
        date=date.today()
    ).all()
    
    total_calories = sum(log.calories or 0 for log in today_logs)
    total_protein = sum(log.protein or 0 for log in today_logs)
    
    print(f"   Today's meal logs: {len(today_logs)}")
    print(f"   Total calories: {total_calories}")
    print(f"   Total protein: {total_protein}")
    
    print(f"\n📋 Individual meal logs for today:")
    for log in today_logs:
        food_name = log.food.name if log.food else "Unknown"
        print(f"   - {food_name}: {log.quantity}g → {log.calories}cal, {log.protein}g protein")
    
    # Final verification
    if meal_log.calories and meal_log.calories > 0:
        print(f"\n✅ SUCCESS: 200g peanuts logged with {meal_log.calories} calories")
    else:
        print(f"\n❌ FAILURE: 200g peanuts nutrition not calculated properly")
