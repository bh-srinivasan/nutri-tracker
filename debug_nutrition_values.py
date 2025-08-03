#!/usr/bin/env python3
"""
Test script to check nutrition values in MealLog entries
"""

from app import create_app
from app.models import MealLog, Food
from datetime import date

app = create_app()

with app.app_context():
    # Get today's meal logs
    today_logs = MealLog.query.filter_by(date=date.today()).all()
    
    print(f"Today's meal logs: {len(today_logs)}")
    
    for log in today_logs:
        print(f"\nMeal Log ID: {log.id}")
        print(f"Food: {log.food.name if log.food else 'None'}")
        print(f"Quantity: {log.quantity}")
        print(f"Original Quantity: {log.original_quantity}")
        print(f"Unit Type: {log.unit_type}")
        print(f"Stored Calories: {log.calories}")
        print(f"Stored Protein: {log.protein}")
        print(f"Stored Carbs: {log.carbs}")
        print(f"Stored Fat: {log.fat}")
        print(f"Stored Fiber: {log.fiber}")
        
        if log.food:
            print(f"Food's base calories per 100g: {log.food.calories}")
            print(f"Food's base protein per 100g: {log.food.protein}")
            
            # Calculate what the values should be
            factor = log.quantity / 100
            expected_calories = log.food.calories * factor
            expected_protein = log.food.protein * factor
            
            print(f"Expected calories: {expected_calories}")
            print(f"Expected protein: {expected_protein}")
            
            # Check if they match
            if log.calories != expected_calories:
                print(f"❌ MISMATCH in calories!")
            else:
                print(f"✅ Calories match")
                
            if log.protein != expected_protein:
                print(f"❌ MISMATCH in protein!")
            else:
                print(f"✅ Protein matches")
