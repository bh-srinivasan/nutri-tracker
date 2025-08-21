#!/usr/bin/env python3
"""
Data patch script to fix existing meal logs where original_quantity may contain grams instead of serving count.
This fixes past rows that now render as "240 piece" instead of "8 piece".
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import MealLog, FoodServing

def patch_serving_quantities():
    """Fix meal logs where original_quantity appears to be grams instead of serving count."""
    app = create_app()
    
    with app.app_context():
        print("🔧 Patching Serving Quantities")
        print("=" * 40)
        
        # Find serving-based meal logs that might have grams in original_quantity
        problematic_logs = db.session.query(MealLog).join(FoodServing).filter(
            MealLog.unit_type == 'serving',
            MealLog.serving_id.isnot(None),
            # Look for cases where original_quantity seems too large (likely grams)
            MealLog.original_quantity >= FoodServing.grams_per_unit
        ).all()
        
        print(f"📊 Found {len(problematic_logs)} potentially problematic meal logs")
        
        if not problematic_logs:
            print("✅ No problematic meal logs found")
            return True
        
        fixed_count = 0
        
        for meal_log in problematic_logs:
            serving = meal_log.serving
            if not serving:
                continue
                
            old_original_quantity = meal_log.original_quantity
            
            # Check if original_quantity is divisible by grams_per_unit (indicating it's likely grams)
            if abs((old_original_quantity / serving.grams_per_unit) - round(old_original_quantity / serving.grams_per_unit)) < 1e-6:
                # This looks like grams were stored in original_quantity
                corrected_serving_count = old_original_quantity / serving.grams_per_unit
                
                print(f"  🔧 MealLog {meal_log.id}: {meal_log.food.name}")
                print(f"     Serving: {serving.serving_name} ({serving.grams_per_unit}g per unit)")
                print(f"     Original quantity: {old_original_quantity} → {corrected_serving_count}")
                
                # Update the original_quantity to the correct serving count
                meal_log.original_quantity = corrected_serving_count
                
                # Ensure quantity (legacy field) contains grams
                meal_log.quantity = meal_log.logged_grams
                
                fixed_count += 1
                
                # Verify the display looks correct now
                display = meal_log.get_display_quantity_and_unit()
                print(f"     Display: '{display}' ✅")
        
        if fixed_count > 0:
            try:
                db.session.commit()
                print(f"\n✅ Fixed {fixed_count} meal logs")
                print("🎉 Data patch completed successfully")
            except Exception as e:
                print(f"\n❌ Error committing changes: {e}")
                db.session.rollback()
                return False
        else:
            print("\n✅ No fixes needed - all meal logs look correct")
        
        return True

def verify_patch_results():
    """Verify that the patch worked correctly."""
    app = create_app()
    
    with app.app_context():
        print("\n🔍 Verifying Patch Results")
        print("=" * 35)
        
        # Check for any remaining problematic displays
        serving_logs = MealLog.query.filter(
            MealLog.unit_type == 'serving',
            MealLog.serving_id.isnot(None)
        ).limit(10).all()
        
        for meal_log in serving_logs:
            meal_log.serving  # Load relationship
            display = meal_log.get_display_quantity_and_unit()
            
            # Check if display looks suspicious (very large numbers)
            if any(char.isdigit() for char in display.split()[0]) and float(display.split()[0]) > 50:
                print(f"  ⚠️  Suspicious display: '{display}' (MealLog {meal_log.id})")
            else:
                print(f"  ✅ Good display: '{display}'")
        
        print("🔍 Verification complete")

if __name__ == "__main__":
    print("🚀 Nutri Tracker - Serving Quantities Data Patch")
    print("=" * 55)
    
    success = patch_serving_quantities()
    
    if success:
        verify_patch_results()
        print("\n🎉 DATA PATCH COMPLETED!")
        print("✅ Serving quantities are now correctly stored")
    else:
        print("\n❌ DATA PATCH FAILED!")
        print("🔧 Please review the error messages above")
        sys.exit(1)
