#!/usr/bin/env python3

from app import create_app
from app.models import *
from datetime import date

app = create_app()

with app.app_context():
    print("=== DEBUGGING NUTRITION CALCULATION ===")
    
    # Find a peanuts food item
    peanuts = Food.query.filter(Food.name.ilike('%peanut%')).first()
    if peanuts:
        print(f"Found: {peanuts.name}")
        print(f"Calories per 100g: {peanuts.calories}")
        print(f"Protein per 100g: {peanuts.protein}")
        
        # Test calculation
        quantity = 200.0
        factor = quantity / 100
        expected_calories = peanuts.calories * factor if peanuts.calories else None
        expected_protein = peanuts.protein * factor if peanuts.protein else None
        
        print(f"\nFor {quantity}g:")
        print(f"Factor: {factor}")
        print(f"Expected calories: {expected_calories}")
        print(f"Expected protein: {expected_protein}")
    else:
        print("No peanuts found")
    
    # Check recent meal logs
    print("\n=== RECENT MEAL LOGS ===")
    recent_logs = MealLog.query.order_by(MealLog.id.desc()).limit(5).all()
    
    for log in recent_logs:
        print(f"\nLog ID: {log.id}")
        print(f"Food: {log.food.name if log.food else 'None'}")
        print(f"Quantity: {log.quantity}")
        print(f"Stored calories: {log.calories}")
        print(f"Stored protein: {log.protein}")
        
        if log.food and log.food.calories:
            expected_cal = (log.quantity / 100) * log.food.calories
            print(f"Expected calories: {expected_cal}")
            if log.calories != expected_cal:
                print("❌ MISMATCH!")
            else:
                print("✅ MATCH")
    
    print("\n=== TODAY'S TOTALS ===")
    today_logs = MealLog.query.filter_by(date=date.today()).all()
    total_cal = sum(log.calories or 0 for log in today_logs)
    total_protein = sum(log.protein or 0 for log in today_logs)
    
    print(f"Today's logs: {len(today_logs)}")
    print(f"Total calories: {total_cal}")
    print(f"Total protein: {total_protein}")
