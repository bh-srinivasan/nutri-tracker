#!/usr/bin/env python3
"""
Debug serving relationship loading
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Food, FoodServing, MealLog, User
from datetime import date

def debug_serving_relationship():
    """Debug why serving relationship is not loading"""
    
    app = create_app()
    
    with app.app_context():
        # Get test data
        test_user = User.query.filter_by(username='admin').first()
        idli = Food.query.filter_by(name='Idli').first()
        small_idli_serving = FoodServing.query.filter_by(
            food_id=idli.id, 
            serving_name='1 small idli'
        ).first()
        
        print(f"🔍 Debug Info:")
        print(f"   User: {test_user.username if test_user else 'None'}")
        print(f"   Food: {idli.name if idli else 'None'} (ID: {idli.id if idli else 'None'})")
        print(f"   Serving: {small_idli_serving.serving_name if small_idli_serving else 'None'} (ID: {small_idli_serving.id if small_idli_serving else 'None'})")
        
        # Create test meal log
        serving_meal = MealLog(
            user_id=test_user.id,
            food_id=idli.id,
            quantity=1.0,
            original_quantity=1.0,
            unit_type='serving',
            serving_id=small_idli_serving.id,
            logged_grams=30.0,
            meal_type='breakfast',
            date=date.today()
        )
        
        print(f"\n📊 MealLog attributes:")
        print(f"   serving_id: {serving_meal.serving_id}")
        print(f"   unit_type: {serving_meal.unit_type}")
        print(f"   hasattr(self, 'serving'): {hasattr(serving_meal, 'serving')}")
        
        # Try to access the serving
        try:
            serving_obj = serving_meal.serving
            print(f"   serving object: {serving_obj}")
            if serving_obj:
                print(f"   serving.serving_name: {serving_obj.serving_name}")
            else:
                print(f"   serving is None - relationship not loaded")
        except Exception as e:
            print(f"   Error accessing serving: {e}")
        
        # Try manual query
        manual_serving = FoodServing.query.get(serving_meal.serving_id)
        print(f"   Manual query result: {manual_serving.serving_name if manual_serving else 'None'}")
        
        # Test the method step by step
        print(f"\n🔬 Method debugging:")
        unit_type = getattr(serving_meal, "unit_type", None)
        serving = getattr(serving_meal, "serving", None)
        print(f"   getattr(self, 'unit_type', None): {unit_type}")
        print(f"   getattr(self, 'serving', None): {serving}")
        print(f"   Condition result: {unit_type == 'serving' and serving}")
        
        # Check if we need to add the meal to session for relationships to work
        db.session.add(serving_meal)
        db.session.flush()  # Don't commit, just flush to get relationships
        
        print(f"\n🔄 After flush:")
        try:
            serving_obj_after = serving_meal.serving
            print(f"   serving object after flush: {serving_obj_after}")
            if serving_obj_after:
                print(f"   serving.serving_name after flush: {serving_obj_after.serving_name}")
        except Exception as e:
            print(f"   Error accessing serving after flush: {e}")
        
        # Test the display method after flush
        display_result = serving_meal.get_display_quantity_and_unit()
        print(f"   Display result after flush: '{display_result}'")
        
        db.session.rollback()  # Clean up

if __name__ == "__main__":
    debug_serving_relationship()
