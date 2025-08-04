#!/usr/bin/env python3
"""
Test to verify the nutrition calculation fix works for dashboard totals
"""

from app import create_app
from app.models import *
from datetime import date

app = create_app()

with app.app_context():
    print("🧪 TESTING NUTRITION CALCULATION FIX")
    print("=" * 50)
    
    # Check today's totals BEFORE adding new meal
    today_logs_before = MealLog.query.filter_by(date=date.today()).all()
    total_calories_before = sum(log.calories or 0 for log in today_logs_before)
    total_protein_before = sum(log.protein or 0 for log in today_logs_before)
    
    print(f"📊 BEFORE adding 200g peanuts:")
    print(f"   Meal logs today: {len(today_logs_before)}")
    print(f"   Total calories: {total_calories_before}")
    print(f"   Total protein: {total_protein_before}g")
    
    # Add a 200g peanuts meal (exactly like user would do)
    user = User.query.first()
    peanuts = Food.query.filter(Food.name.ilike('%peanut%')).first()
    
    # Simulate the dashboard route behavior
    meal_log = MealLog(
        user_id=user.id,
        food_id=peanuts.id,
        quantity=200.0,
        original_quantity=200.0,
        unit_type='grams',
        serving_id=None,
        meal_type='snack',
        date=date.today()
    )
    
    # Calculate nutrition (the fix should work here)
    meal_log.calculate_nutrition()
    
    print(f"\n🥜 Adding 200g peanuts:")
    print(f"   Calculated calories: {meal_log.calories}")
    print(f"   Calculated protein: {meal_log.protein}g")
    
    # Save to database
    db.session.add(meal_log)
    db.session.commit()
    
    # Check today's totals AFTER adding new meal
    today_logs_after = MealLog.query.filter_by(date=date.today()).all()
    total_calories_after = sum(log.calories or 0 for log in today_logs_after)
    total_protein_after = sum(log.protein or 0 for log in today_logs_after)
    
    print(f"\n📊 AFTER adding 200g peanuts:")
    print(f"   Meal logs today: {len(today_logs_after)}")
    print(f"   Total calories: {total_calories_after}")
    print(f"   Total protein: {total_protein_after}g")
    
    # Calculate the difference
    calories_added = total_calories_after - total_calories_before
    protein_added = total_protein_after - total_protein_before
    
    print(f"\n📈 CHANGE:")
    print(f"   Calories added: {calories_added}")
    print(f"   Protein added: {protein_added}g")
    
    # Verify the fix
    expected_calories = 1134.0  # 200g of peanuts
    expected_protein = 51.6     # 200g of peanuts
    
    if abs(calories_added - expected_calories) < 0.1:
        print("✅ CALORIES: Dashboard will show correct total!")
    else:
        print(f"❌ CALORIES: Expected {expected_calories}, got {calories_added}")
    
    if abs(protein_added - expected_protein) < 0.1:
        print("✅ PROTEIN: Dashboard will show correct total!")
    else:
        print(f"❌ PROTEIN: Expected {expected_protein}, got {protein_added}")
    
    print(f"\n🎯 CONCLUSION:")
    if (abs(calories_added - expected_calories) < 0.1 and 
        abs(protein_added - expected_protein) < 0.1):
        print("✅ FIX SUCCESSFUL! Dashboard nutrition will update correctly!")
        print("✅ 200g peanuts will now show proper calories and protein!")
    else:
        print("❌ FIX FAILED! Issue still exists!")
    
    print(f"\n📋 Today's meal breakdown:")
    for i, log in enumerate(today_logs_after, 1):
        food_name = log.food.name if log.food else "Unknown"
        print(f"   {i}. {food_name}: {log.quantity}g → {log.calories or 0}cal, {log.protein or 0}g protein")
