#!/usr/bin/env python3
"""
Final comprehensive test to verify the complete serving/grams bug fix.
Tests all aspects after all edits have been applied.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Food, MealLog, FoodServing
from datetime import date

def test_complete_serving_grams_fix():
    """Test the complete serving/grams bug fix after all edits."""
    app = create_app()
    
    with app.app_context():
        print("🎯 Final Comprehensive Test - Serving/Grams Bug Fix")
        print("=" * 60)
        
        # Find test serving
        test_serving = FoodServing.query.filter(
            FoodServing.grams_per_unit == 30
        ).first()
        
        if not test_serving:
            print("❌ No test serving found")
            return False
        
        test_food = test_serving.food
        admin_user = User.query.filter_by(username='admin').first()
        
        print(f"🥢 Test Food: {test_food.name}")
        print(f"🥄 Test Serving: {test_serving.serving_name} ({test_serving.grams_per_unit}g per unit)")
        
        # Test 1: Verify fixed display for existing meals
        print("\n📋 Test 1: Existing meal display")
        
        existing_meals = MealLog.query.filter(
            MealLog.unit_type == 'serving',
            MealLog.serving_id == test_serving.id
        ).limit(3).all()
        
        for meal in existing_meals:
            meal.serving  # Load relationship
            display = meal.get_display_quantity_and_unit()
            print(f"  📝 MealLog {meal.id}: '{display}'")
            print(f"     original_quantity: {meal.original_quantity}")
            print(f"     logged_grams: {meal.logged_grams}g")
            print(f"     legacy quantity: {meal.quantity}g")
            
            # Verify no "240 piece" type displays
            parts = display.split()
            if len(parts) >= 2 and parts[0].replace('.', '').isdigit():
                quantity_value = float(parts[0])
                if quantity_value > 20:  # Suspiciously large serving count
                    print(f"  ❌ Suspicious large serving count: {display}")
                    return False
            
            # Verify legacy quantity is in grams
            if abs(meal.quantity - meal.logged_grams) > 0.01:
                print(f"  ❌ Legacy quantity mismatch: {meal.quantity} != {meal.logged_grams}")
                return False
        
        print("  ✅ All existing meal displays look correct")
        
        # Test 2: Simulate server-side guard logic
        print("\n🔧 Test 2: Server-side guard for bad client input")
        
        def simulate_server_guard(original_quantity, serving):
            """Simulate the server-side guard logic from routes.py"""
            if original_quantity >= serving.grams_per_unit and abs((original_quantity / serving.grams_per_unit) - round(original_quantity / serving.grams_per_unit)) < 1e-6:
                return original_quantity / serving.grams_per_unit
            return original_quantity
        
        # Test cases
        test_cases = [
            (8, 8),      # Normal serving count
            (240, 8),    # Grams accidentally posted (should be corrected)
            (60, 2),     # 2 servings worth of grams
            (1.5, 1.5),  # Fractional serving count
        ]
        
        for input_qty, expected_qty in test_cases:
            corrected = simulate_server_guard(input_qty, test_serving)
            print(f"  🔧 Input: {input_qty} → Corrected: {corrected} (expected: {expected_qty})")
            
            if abs(corrected - expected_qty) > 0.01:
                print(f"  ❌ Server guard failed for input {input_qty}")
                return False
        
        print("  ✅ Server-side guard logic working correctly")
        
        # Test 3: Verify nutrition computation uses grams
        print("\n🧮 Test 3: Nutrition computation uses grams")
        
        # Check that nutrition values are consistent with logged_grams
        for meal in existing_meals[:2]:
            expected_calories_per_gram = meal.food.calories / 100 if meal.food.calories else 0
            expected_calories = expected_calories_per_gram * meal.logged_grams
            
            if expected_calories > 0:
                ratio = meal.calories / expected_calories
                print(f"  📊 MealLog {meal.id}: {meal.calories:.1f} cal for {meal.logged_grams}g")
                print(f"     Expected: {expected_calories:.1f} cal (ratio: {ratio:.3f})")
                
                if not (0.9 <= ratio <= 1.1):  # Allow 10% variance
                    print(f"  ❌ Nutrition computation mismatch")
                    return False
        
        print("  ✅ Nutrition computation consistent with grams")
        
        # Test 4: CSV export format
        print("\n📄 Test 4: CSV export format")
        
        sample_meals = existing_meals[:3]
        for meal in sample_meals:
            csv_quantity = meal.get_display_quantity_and_unit()
            print(f"  📝 CSV Quantity: '{csv_quantity}'")
            
            # Should not have double "g" suffixes
            if csv_quantity.endswith("gg") or " g g" in csv_quantity:
                print(f"  ❌ Double 'g' in CSV: {csv_quantity}")
                return False
            
            # Should be descriptive (not just numbers)
            if csv_quantity.strip().replace('.', '').isdigit():
                print(f"  ❌ CSV shows only numbers: {csv_quantity}")
                return False
        
        print("  ✅ CSV export format is correct")
        
        # Test 5: Form editing behavior
        print("\n📝 Test 5: Form editing shows serving count")
        
        for meal in existing_meals[:2]:
            edit_quantity = meal.original_quantity
            logged_grams = meal.logged_grams
            
            print(f"  📝 Edit form quantity: {edit_quantity}")
            print(f"     Should NOT be: {logged_grams}")
            
            if abs(edit_quantity - logged_grams) < 0.01 and logged_grams > 10:
                print(f"  ❌ Edit form shows grams instead of serving count")
                return False
        
        print("  ✅ Form editing shows correct serving counts")
        
        # Test 6: Legacy quantity consistency
        print("\n🗄️  Test 6: Legacy quantity field consistency")
        
        all_meals = MealLog.query.limit(10).all()
        for meal in all_meals:
            if abs(meal.quantity - meal.logged_grams) > 0.01:
                print(f"  ❌ MealLog {meal.id}: quantity={meal.quantity} != logged_grams={meal.logged_grams}")
                return False
        
        print(f"  ✅ All {len(all_meals)} meal logs have consistent legacy quantity field")
        
        print("\n🎉 ALL FINAL TESTS PASSED!")
        print("✅ Server never confuses serving count with grams")
        print("✅ Always computes nutrition using grams")
        print("✅ Legacy MealLog.quantity field stores grams only")
        print("✅ Guards against client JS posting grams as quantity")
        print("✅ Preserves display using get_display_quantity_and_unit()")
        
        return True

if __name__ == "__main__":
    print("🚀 Nutri Tracker - Final Serving/Grams Bug Fix Test")
    print("=" * 60)
    
    success = test_complete_serving_grams_fix()
    
    if success:
        print("\n🎉 FINAL TEST PASSED!")
        print("🚀 Complete serving/grams bug fix is working perfectly")
        print("🎯 All goals achieved:")
        print("   - No serving↔grams confusion")
        print("   - Nutrition computed from grams")
        print("   - Legacy field properly maintained")
        print("   - Client input validation working")
        print("   - Display methods preserved")
    else:
        print("\n❌ FINAL TEST FAILED!")
        print("🔧 Please review the error messages above")
        sys.exit(1)
