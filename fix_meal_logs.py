#!/usr/bin/env python3
"""
Fix existing meal logs by calculating their nutrition values
"""

from app import create_app, db
from app.models import MealLog

def fix_meal_logs():
    """Calculate nutrition values for existing meal logs that are missing them"""
    app = create_app()
    
    with app.app_context():
        print("🔧 Fixing existing meal logs...")
        
        # Get all meal logs with missing nutrition values
        logs_missing_nutrition = MealLog.query.filter(MealLog.calories.is_(None)).all()
        
        print(f"Found {len(logs_missing_nutrition)} meal logs missing nutrition values")
        
        if not logs_missing_nutrition:
            print("✅ All meal logs already have nutrition values calculated")
            return
        
        # Fix each meal log
        fixed_count = 0
        for meal_log in logs_missing_nutrition:
            if meal_log.food:
                print(f"   Fixing log {meal_log.id}: {meal_log.food.name} ({meal_log.quantity}g)")
                meal_log.calculate_nutrition()
                fixed_count += 1
            else:
                print(f"   ⚠️  Log {meal_log.id} has no associated food - skipping")
        
        # Commit changes
        db.session.commit()
        
        print(f"✅ Fixed {fixed_count} meal logs!")
        print("Dashboard should now display correct nutrition values")

if __name__ == "__main__":
    fix_meal_logs()
