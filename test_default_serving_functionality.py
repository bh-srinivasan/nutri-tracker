#!/usr/bin/env python3
"""
Test setting and using default_serving_id functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_default_serving_functionality():
    """Test that we can set and use default_serving_id"""
    
    try:
        print("🧪 Testing default_serving functionality...")
        
        from app import create_app, db
        from app.models import Food, FoodServing
        
        app = create_app()
        
        with app.app_context():
            # Find a food that has servings
            food_with_servings = db.session.query(Food).join(
                FoodServing, Food.id == FoodServing.food_id
            ).first()
            
            if not food_with_servings:
                print("❌ No foods with servings found for testing")
                return False
                
            print(f"📋 Testing with: {food_with_servings.name}")
            
            # Get available servings
            available_servings = FoodServing.query.filter_by(food_id=food_with_servings.id).all()
            print(f"   Available servings: {len(available_servings)}")
            
            for serving in available_servings:
                print(f"   - {serving.serving_name}: {serving.grams_per_unit}g ({serving.unit})")
                
            # Test 1: Initially no default serving
            print("\\n1️⃣ Testing initial state...")
            print(f"   Default serving ID: {food_with_servings.default_serving_id}")
            print(f"   Default serving: {food_with_servings.default_serving}")
            assert food_with_servings.default_serving is None, "Should initially be None"
            print("   ✅ Initial state correct (None)")
            
            # Test 2: Set a default serving
            print("\\n2️⃣ Setting default serving...")
            test_serving = available_servings[0]
            food_with_servings.default_serving_id = test_serving.id
            db.session.commit()
            
            print(f"   Set default_serving_id to: {test_serving.id}")
            print(f"   Serving: {test_serving.serving_name} ({test_serving.grams_per_unit}g)")
            
            # Test 3: Reload and verify relationship works
            print("\\n3️⃣ Testing relationship after setting...")
            db.session.refresh(food_with_servings)
            
            default_serving = food_with_servings.default_serving
            print(f"   Default serving ID: {food_with_servings.default_serving_id}")
            print(f"   Default serving object: {default_serving}")
            
            if default_serving:
                print(f"   Default serving name: {default_serving.serving_name}")
                print(f"   Default serving grams: {default_serving.grams_per_unit}")
                assert default_serving.id == test_serving.id, "Should match the set serving"
                print("   ✅ Relationship working correctly!")
            else:
                print("   ❌ Default serving is None when it should not be")
                return False
                
            # Test 4: Clear default serving
            print("\\n4️⃣ Clearing default serving...")
            food_with_servings.default_serving_id = None
            db.session.commit()
            
            db.session.refresh(food_with_servings)
            print(f"   Default serving ID: {food_with_servings.default_serving_id}")
            print(f"   Default serving: {food_with_servings.default_serving}")
            assert food_with_servings.default_serving is None, "Should be None again"
            print("   ✅ Clearing works correctly!")
            
            # Test 5: Test with multiple foods
            print("\\n5️⃣ Testing with multiple foods...")
            foods = Food.query.limit(3).all()
            for food in foods:
                default_serving = food.default_serving  # Should not cause errors
                servings_count = food.servings.count()
                print(f"   {food.name}: default={default_serving}, servings={servings_count}")
                
            print("   ✅ Multiple food access works!")
            
        print("\\n🎉 ALL FUNCTIONALITY TESTS PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_default_serving_functionality()
    
    if success:
        print("\\n✅ FUNCTIONALITY TEST PASSED!")
        print("🎯 default_serving_id feature is working correctly!")
    else:
        print("\\n❌ FUNCTIONALITY TEST FAILED!")
