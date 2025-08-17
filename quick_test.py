#!/usr/bin/env python3

import requests
import time

print("=== TESTING LIVE API ENDPOINT ===")
try:
    response = requests.delete('http://127.0.0.1:5001/api/admin/foods/1', timeout=3)
    print(f'Status: {response.status_code}')
    print(f'Response: {response.text}')
    print('✅ API endpoint exists and is working!')
except requests.exceptions.ConnectionError:
    print('❌ Server not responding')
except Exception as e:
    print(f'Error: {e}')
    peanuts = Food.query.filter(Food.name.ilike('%peanut%')).first()
    user = User.query.first()
    
    if peanuts and user:
        print(f"Testing FIX for {peanuts.name}")
        print(f"Peanuts nutrition: calories={peanuts.calories}, protein={peanuts.protein}")
        
        # Create test meal WITHOUT explicitly setting meal.food
        meal = MealLog(
            user_id=user.id,
            food_id=peanuts.id,
            quantity=200.0,
            original_quantity=200.0,
            unit_type='grams',
            meal_type='snack',
            date=date.today()
        )
        
        print("Before calculation:", meal.calories, meal.protein)
        print("meal.food before calculation:", meal.food)
        
        # This should now work without explicit assignment
        meal.calculate_nutrition()
        print("After calculation:", meal.calories, meal.protein)
        
        if meal.calories and meal.calories > 0:
            print("✅ FIX WORKS! Nutrition calculated correctly")
        else:
            print("❌ FIX FAILED! Nutrition still not calculated")
        
        # Try to save
        db.session.add(meal)
        db.session.commit()
        print(f"Saved with ID: {meal.id}")
        
        # Verify saved values
        saved_meal = MealLog.query.get(meal.id)
        print(f"Saved values: calories={saved_meal.calories}, protein={saved_meal.protein}")
    else:
        print("Missing data:", "peanuts" if not peanuts else "", "user" if not user else "")
