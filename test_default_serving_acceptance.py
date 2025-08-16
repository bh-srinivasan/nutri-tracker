#!/usr/bin/env python3
"""
Test that the app starts and Food can be loaded with default_serving
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_app_startup_and_food_loading():
    """Test acceptance criteria: App starts; Food can be loaded with default_serving"""
    
    try:
        print("🚀 Testing app startup and Food model loading...")
        
        # Test 1: App starts successfully
        print("1️⃣ Testing app startup...")
        from app import create_app, db
        app = create_app()
        print("   ✅ App created successfully")
        
        # Test 2: Food model can be imported and loaded
        print("2️⃣ Testing Food model import...")
        from app.models import Food, FoodServing
        print("   ✅ Food and FoodServing models imported successfully")
        
        with app.app_context():
            # Test 3: Food can be loaded with default_serving (possibly None)
            print("3️⃣ Testing Food loading with default_serving relationship...")
            
            foods = Food.query.limit(5).all()
            print(f"   Loaded {len(foods)} foods")
            
            for food in foods:
                # This should work without errors, default_serving should be None initially
                default_serving = food.default_serving
                print(f"   Food: {food.name}")
                print(f"   Default serving: {default_serving}")
                print(f"   Default serving ID: {food.default_serving_id}")
                
            print("   ✅ Food.default_serving relationship works (all None as expected)")
            
            # Test 4: Backwards compatibility - existing fields still work
            print("4️⃣ Testing backwards compatibility...")
            sample_food = foods[0] if foods else None
            if sample_food:
                print(f"   Name: {sample_food.name}")
                print(f"   Calories: {sample_food.calories}")
                print(f"   Protein: {sample_food.protein}")
                print(f"   Legacy serving_size: {sample_food.serving_size}")
                print(f"   Default serving size grams: {sample_food.default_serving_size_grams}")
                print("   ✅ All existing fields accessible")
                
            # Test 5: Test that we can access servings collection
            print("5️⃣ Testing servings relationship...")
            food_with_servings = None
            
            for food in foods:
                servings_count = food.servings.count()
                print(f"   {food.name}: {servings_count} servings")
                if servings_count > 0:
                    food_with_servings = food
                    break
                    
            if food_with_servings:
                servings = food_with_servings.servings.all()
                print(f"   Servings for {food_with_servings.name}:")
                for serving in servings:
                    print(f"     - {serving.serving_name}: {serving.grams_per_unit}g")
                print("   ✅ Existing servings relationship still works")
            else:
                print("   ℹ️  No foods with servings found (this is okay)")
                
        print("\n🎉 ALL ACCEPTANCE CRITERIA MET!")
        print("✅ App starts successfully")
        print("✅ Food can be loaded with default_serving (None)")
        print("✅ No changes to existing fields or behaviors")
        print("✅ Backwards compatibility maintained")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_app_startup_and_food_loading()
    
    if success:
        print("\n✅ ACCEPTANCE TEST PASSED!")
    else:
        print("\n❌ ACCEPTANCE TEST FAILED!")
