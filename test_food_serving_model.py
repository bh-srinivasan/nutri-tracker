#!/usr/bin/env python3
"""
Test the updated FoodServing model
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import FoodServing, Food, User

def test_food_serving_model():
    """Test the updated FoodServing model"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🧪 Testing FoodServing model...")
            
            # Test 1: Model is importable
            print("✅ FoodServing model imported successfully")
            
            # Test 2: Check if model appears in metadata
            table_names = db.metadata.tables.keys()
            print(f"📋 Available tables: {list(table_names)}")
            
            if 'food_serving' in table_names:
                print("✅ FoodServing table found in metadata")
            else:
                print("❌ FoodServing table not found in metadata")
                return False
                
            # Test 3: Query existing records
            servings = FoodServing.query.limit(5).all()
            print(f"📊 Found {len(servings)} existing servings")
            
            for serving in servings:
                print(f"   {serving.id}: {serving.serving_name} ({serving.unit}) = {serving.grams_per_unit}g")
                
            # Test 4: Create a new serving (if we have foods)
            food = Food.query.first()
            if food:
                print(f"🍎 Testing with food: {food.name}")
                
                # Try to create a new serving
                new_serving = FoodServing(
                    food_id=food.id,
                    serving_name="1 test portion",
                    unit="portion",
                    grams_per_unit=150.0
                )
                
                db.session.add(new_serving)
                db.session.commit()
                
                print(f"✅ Created new serving: {new_serving}")
                
                # Clean up
                db.session.delete(new_serving)
                db.session.commit()
                print("🧹 Cleaned up test serving")
                
            # Test 5: Test relationships
            if servings:
                test_serving = servings[0]
                print(f"🔗 Testing relationships for serving: {test_serving.serving_name}")
                print(f"   Related food: {test_serving.food.name if test_serving.food else 'None'}")
                print(f"   Creator: {test_serving.creator.username if test_serving.creator else 'None'}")
                
            print("✅ All tests passed!")
            return True
            
        except Exception as e:
            print(f"❌ Error testing model: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    print("🚀 Testing updated FoodServing model...")
    success = test_food_serving_model()
    
    if success:
        print("✅ FoodServing model is working correctly!")
    else:
        print("❌ FoodServing model test failed!")
