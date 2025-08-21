#!/usr/bin/env python3
"""
Test the serving display bug fix
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Food, FoodServing, MealLog, User
from datetime import date

def test_serving_display_fix():
    """Test that serving display shows correct quantities"""
    
    app = create_app()
    
    with app.app_context():
        # Get or create test user
        test_user = User.query.filter_by(username='admin').first()
        if not test_user:
            print("❌ No admin user found")
            return False
            
        # Get or create Idli food
        idli = Food.query.filter_by(name='Idli').first()
        if not idli:
            print("❌ No Idli food found")
            return False
            
        # Get small idli serving
        small_idli_serving = FoodServing.query.filter_by(
            food_id=idli.id, 
            serving_name='1 small idli'
        ).first()
        
        if not small_idli_serving:
            print("❌ No '1 small idli' serving found")
            return False
            
        print(f"🧪 Testing with Idli (ID: {idli.id}) and serving (ID: {small_idli_serving.id})")
        print(f"   Serving: {small_idli_serving.serving_name} = {small_idli_serving.grams_per_unit}g")
        
        # Test 1: Serving-based meal log
        serving_meal = MealLog(
            user_id=test_user.id,
            food_id=idli.id,
            quantity=1.0,  # This is deprecated, should not affect display
            original_quantity=1.0,  # User entered 1 piece
            unit_type='serving',
            serving_id=small_idli_serving.id,
            logged_grams=20.0,  # 1 × 20g (correct grams per unit)
            meal_type='breakfast',
            date=date.today()
        )
        
        # Test the display method
        # Need to add to session for relationships to work
        db.session.add(serving_meal)
        db.session.flush()  # Don't commit, just flush to enable relationships
        
        display_result = serving_meal.get_display_quantity_and_unit()
        expected = "1 small idli"  # Should show this, not "1g" or "20g"
        
        print(f"\n📊 SERVING-BASED TEST:")
        print(f"   Original quantity: {serving_meal.original_quantity}")
        print(f"   Deprecated quantity: {serving_meal.quantity}")
        print(f"   Logged grams: {serving_meal.logged_grams}g")
        print(f"   Unit type: {serving_meal.unit_type}")
        print(f"   Display result: '{display_result}'")
        print(f"   Expected: '{expected}'")
        
        test1_pass = display_result == expected
        print(f"   ✅ PASS" if test1_pass else f"   ❌ FAIL")
        
        # Test 2: Grams-based meal log
        grams_meal = MealLog(
            user_id=test_user.id,
            food_id=idli.id,
            quantity=150.0,  # This is deprecated
            original_quantity=150.0,  # User entered 150g
            unit_type='grams',
            serving_id=None,
            logged_grams=150.0,
            meal_type='lunch',
            date=date.today()
        )
        
        db.session.add(grams_meal)
        db.session.flush()
        
        display_result2 = grams_meal.get_display_quantity_and_unit()
        expected2 = "150 g"
        
        print(f"\n📊 GRAMS-BASED TEST:")
        print(f"   Original quantity: {grams_meal.original_quantity}")
        print(f"   Logged grams: {grams_meal.logged_grams}g")
        print(f"   Unit type: {grams_meal.unit_type}")
        print(f"   Display result: '{display_result2}'")
        print(f"   Expected: '{expected2}'")
        
        test2_pass = display_result2 == expected2
        print(f"   ✅ PASS" if test2_pass else f"   ❌ FAIL")
        
        # Test 3: Fallback test (missing serving)
        fallback_meal = MealLog(
            user_id=test_user.id,
            food_id=idli.id,
            quantity=1.0,  # Deprecated
            original_quantity=1.0,
            unit_type='serving',
            serving_id=None,  # Missing serving
            logged_grams=20.0,  # Use correct grams
            meal_type='dinner',
            date=date.today()
        )
        
        db.session.add(fallback_meal)
        db.session.flush()
        
        display_result3 = fallback_meal.get_display_quantity_and_unit()
        expected3 = "20 g"  # Should fallback to logged_grams
        
        print(f"\n📊 FALLBACK TEST (missing serving):")
        print(f"   Original quantity: {fallback_meal.original_quantity}")
        print(f"   Logged grams: {fallback_meal.logged_grams}g")
        print(f"   Unit type: {fallback_meal.unit_type}")
        print(f"   Serving ID: {fallback_meal.serving_id}")
        print(f"   Display result: '{display_result3}'")
        print(f"   Expected: '{expected3}'")
        
        test3_pass = display_result3 == expected3
        print(f"   ✅ PASS" if test3_pass else f"   ❌ FAIL")
        
        # Test 4: Integer formatting test
        integer_meal = MealLog(
            user_id=test_user.id,
            food_id=idli.id,
            quantity=2.0,
            original_quantity=2.0,  # Should display as "2" not "2.0"
            unit_type='serving',
            serving_id=small_idli_serving.id,
            logged_grams=40.0,  # 2 × 20g
            meal_type='snack',
            date=date.today()
        )
        
        db.session.add(integer_meal)
        db.session.flush()
        
        display_result4 = integer_meal.get_display_quantity_and_unit()
        expected4 = "2 small idli"  # Should show "2" not "2.0"
        
        print(f"\n📊 INTEGER FORMATTING TEST:")
        print(f"   Original quantity: {integer_meal.original_quantity}")
        print(f"   Display result: '{display_result4}'")
        print(f"   Expected: '{expected4}'")
        
        test4_pass = display_result4 == expected4
        print(f"   ✅ PASS" if test4_pass else f"   ❌ FAIL")
        
        # Summary
        all_pass = test1_pass and test2_pass and test3_pass and test4_pass
        print(f"\n🎯 OVERALL RESULT:")
        print(f"   Serving-based display: {'✅' if test1_pass else '❌'}")
        print(f"   Grams-based display: {'✅' if test2_pass else '❌'}")
        print(f"   Fallback display: {'✅' if test3_pass else '❌'}")
        print(f"   Integer formatting: {'✅' if test4_pass else '❌'}")
        print(f"   ALL TESTS: {'✅ PASS' if all_pass else '❌ FAIL'}")
        
        if all_pass:
            print(f"\n🎉 Serving display bug fix is working correctly!")
            print(f"   Templates should now show:")
            print(f"   - '1 small idli' instead of '1g' for serving-based meals")
            print(f"   - '150 g' for grams-based meals")
            print(f"   - Proper fallback to logged grams when serving is missing")
        
        # Clean up test data
        db.session.rollback()  # This removes the test objects from session
        
        return all_pass

if __name__ == "__main__":
    success = test_serving_display_fix()
    sys.exit(0 if success else 1)
