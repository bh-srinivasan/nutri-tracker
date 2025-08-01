#!/usr/bin/env python3
"""
Quick test script to verify UOM implementation
"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Food, FoodServing, MealLog

def test_uom_implementation():
    """Test the UOM implementation."""
    app = create_app()
    
    with app.app_context():
        try:
            print("🧪 Testing UOM Implementation...")
            
            # Test 1: Check if database tables exist
            print("\n1️⃣  Checking database tables...")
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            required_tables = ['food', 'food_serving', 'meal_log']
            for table in required_tables:
                if table in tables:
                    print(f"   ✅ Table '{table}' exists")
                else:
                    print(f"   ❌ Table '{table}' missing")
            
            # Test 2: Check MealLog columns
            print("\n2️⃣  Checking MealLog columns...")
            meal_log_columns = [col['name'] for col in inspector.get_columns('meal_log')]
            
            required_columns = ['original_quantity', 'unit_type', 'serving_id']
            for col in required_columns:
                if col in meal_log_columns:
                    print(f"   ✅ Column '{col}' exists in meal_log")
                else:
                    print(f"   ❌ Column '{col}' missing in meal_log")
            
            # Test 3: Check for verified foods
            print("\n3️⃣  Checking verified foods...")
            verified_foods = Food.query.filter_by(is_verified=True).count()
            print(f"   📊 Verified foods in database: {verified_foods}")
            
            # Test 4: Check food servings
            print("\n4️⃣  Checking food servings...")
            total_servings = FoodServing.query.count()
            print(f"   📊 Total food servings: {total_servings}")
            
            # Test 5: Sample some foods with servings
            print("\n5️⃣  Sample foods with servings...")
            foods_with_servings = db.session.query(Food).join(FoodServing).filter(Food.is_verified == True).limit(3).all()
            for food in foods_with_servings:
                servings = FoodServing.query.filter_by(food_id=food.id).count()
                print(f"   🍽️  {food.name}: {servings} serving sizes")
            
            print("\n✅ UOM Implementation Test Complete!")
            return True
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Run the test."""
    print("=" * 60)
    print("🚀 NUTRI TRACKER - UOM IMPLEMENTATION TEST")
    print("=" * 60)
    
    if test_uom_implementation():
        print("\n🎯 Next steps:")
        print("   1. Start the Flask application")
        print("   2. Navigate to 'Log Meal'")
        print("   3. Test food search and UOM selection")
        print("   4. Verify meal logging with different serving sizes")
    else:
        print("❌ Implementation test failed. Check the errors above.")
        return 1
    
    print("=" * 60)
    return 0

if __name__ == '__main__':
    exit(main())
