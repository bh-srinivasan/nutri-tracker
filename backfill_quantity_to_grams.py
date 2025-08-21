#!/usr/bin/env python3
"""
Data backfill script to ensure legacy quantity field stores grams.
This is a one-time migration to fix the serving display bug.
"""

import sys
import os

# Add the app directory to the path so we can import the models
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import MealLog

def backfill_quantity_field():
    """Update all MealLog rows to store grams in the legacy quantity field."""
    app = create_app()
    
    with app.app_context():
        print("🔄 Starting quantity field backfill...")
        
        # Count total rows to update
        total_rows = MealLog.query.count()
        print(f"📊 Found {total_rows} meal log entries to process")
        
        if total_rows == 0:
            print("✅ No meal logs found. Nothing to update.")
            return
        
        updated_count = 0
        batch_size = 1000
        
        # Process in batches to avoid memory issues
        for offset in range(0, total_rows, batch_size):
            meal_logs = MealLog.query.offset(offset).limit(batch_size).all()
            
            for meal_log in meal_logs:
                # Update quantity to match logged_grams (the actual weight)
                old_quantity = meal_log.quantity
                meal_log.quantity = meal_log.logged_grams
                updated_count += 1
                
                # Optional: Log significant changes for verification
                if abs(old_quantity - meal_log.logged_grams) > 0.1:
                    print(f"  📝 Updated MealLog {meal_log.id}: {old_quantity:.1f} → {meal_log.logged_grams:.1f}g")
            
            # Commit batch
            try:
                db.session.commit()
                print(f"✅ Processed batch {offset//batch_size + 1}/{(total_rows-1)//batch_size + 1}")
            except Exception as e:
                print(f"❌ Error committing batch: {e}")
                db.session.rollback()
                return False
        
        print(f"🎉 Successfully updated {updated_count} meal log entries")
        print("✅ Legacy quantity field now stores grams for all entries")
        return True

if __name__ == "__main__":
    print("🚀 Nutri Tracker - Quantity Field Backfill")
    print("=" * 50)
    
    success = backfill_quantity_field()
    
    if success:
        print("\n✅ Backfill completed successfully!")
        print("💡 The serving display bug fix is now complete.")
    else:
        print("\n❌ Backfill failed. Please check the error messages above.")
        sys.exit(1)
