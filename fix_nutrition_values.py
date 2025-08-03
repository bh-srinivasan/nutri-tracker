#!/usr/bin/env python3
"""
Script to fix existing meal logs that don't have nutrition values calculated
"""

from app import create_app
from app.models import MealLog, db

app = create_app()

with app.app_context():
    # Get all meal logs with missing nutrition values
    broken_logs = MealLog.query.filter(MealLog.calories.is_(None)).all()
    
    print(f"Found {len(broken_logs)} meal logs with missing nutrition values")
    
    for log in broken_logs:
        if log.food:
            print(f"Fixing MealLog ID {log.id} - {log.food.name}")
            log.calculate_nutrition()
            print(f"  Set calories to: {log.calories}")
            print(f"  Set protein to: {log.protein}")
        else:
            print(f"Skipping MealLog ID {log.id} - no food associated")
    
    # Commit the changes
    try:
        db.session.commit()
        print(f"\n✅ Successfully updated {len(broken_logs)} meal logs!")
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Error updating meal logs: {e}")
        
    # Verify the fix
    print("\nVerifying fix...")
    fixed_logs = MealLog.query.filter(MealLog.calories.is_not(None)).all()
    print(f"Meal logs with nutrition values: {len(fixed_logs)}")
