#!/usr/bin/env python3
"""
Script to populate sample UOM data for demonstration
"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Food, FoodServing

def populate_sample_uom_data():
    """Add comprehensive sample UOM data for testing."""
    app = create_app()
    
    with app.app_context():
        try:
            print("🍽️  Populating sample UOM data...")
            
            # Enhanced sample data with Indian food focus
            sample_data = [
                {
                    'food_info': {
                        'name': 'Basmati Rice',
                        'brand': 'India Gate',
                        'category': 'Grains',
                        'calories': 345,
                        'protein': 7.1,
                        'carbs': 78.2,
                        'fat': 0.9,
                        'is_verified': True,
                        'description': 'Premium basmati rice'
                    },
                    'servings': [
                        {'name': '1 cup cooked', 'unit': 'cup', 'quantity': 195, 'is_default': True},
                        {'name': '1 small bowl', 'unit': 'bowl', 'quantity': 150},
                        {'name': '1 large bowl', 'unit': 'bowl', 'quantity': 250},
                        {'name': '1 serving spoon', 'unit': 'spoon', 'quantity': 30}
                    ]
                },
                {
                    'food_info': {
                        'name': 'Whole Wheat Bread',
                        'brand': 'Britannia',
                        'category': 'Grains',
                        'calories': 265,
                        'protein': 9.6,
                        'carbs': 49.8,
                        'fat': 4.2,
                        'is_verified': True,
                        'description': 'Nutritious whole wheat bread'
                    },
                    'servings': [
                        {'name': '1 slice', 'unit': 'slice', 'quantity': 25, 'is_default': True},
                        {'name': '2 slices', 'unit': 'slices', 'quantity': 50}
                    ]
                },
                {
                    'food_info': {
                        'name': 'Toned Milk',
                        'brand': 'Amul',
                        'category': 'Dairy',
                        'calories': 58,
                        'protein': 3.1,
                        'carbs': 4.8,
                        'fat': 3.0,
                        'is_verified': True,
                        'description': 'Fresh toned milk'
                    },
                    'servings': [
                        {'name': '1 cup', 'unit': 'cup', 'quantity': 240, 'is_default': True},
                        {'name': '1 glass', 'unit': 'glass', 'quantity': 200},
                        {'name': '1 small glass', 'unit': 'glass', 'quantity': 150}
                    ]
                },
                {
                    'food_info': {
                        'name': 'Small Idli',
                        'brand': None,
                        'category': 'Traditional',
                        'calories': 39,
                        'protein': 1.7,
                        'carbs': 8.1,
                        'fat': 0.1,
                        'is_verified': True,
                        'description': 'Traditional steamed rice cake'
                    },
                    'servings': [
                        {'name': '1 piece', 'unit': 'piece', 'quantity': 30, 'is_default': True},
                        {'name': '2 pieces', 'unit': 'pieces', 'quantity': 60},
                        {'name': '3 pieces', 'unit': 'pieces', 'quantity': 90},
                        {'name': '1 plate (4 pieces)', 'unit': 'plate', 'quantity': 120}
                    ]
                },
                {
                    'food_info': {
                        'name': 'Banana',
                        'brand': None,
                        'category': 'Fruits',
                        'calories': 89,
                        'protein': 1.1,
                        'carbs': 22.8,
                        'fat': 0.3,
                        'is_verified': True,
                        'description': 'Fresh banana fruit'
                    },
                    'servings': [
                        {'name': '1 medium', 'unit': 'piece', 'quantity': 118, 'is_default': True},
                        {'name': '1 small', 'unit': 'piece', 'quantity': 90},
                        {'name': '1 large', 'unit': 'piece', 'quantity': 140}
                    ]
                },
                {
                    'food_info': {
                        'name': 'Paneer',
                        'brand': 'Amul',
                        'category': 'Dairy',
                        'calories': 265,
                        'protein': 18.3,
                        'carbs': 1.2,
                        'fat': 20.8,
                        'is_verified': True,
                        'description': 'Fresh cottage cheese'
                    },
                    'servings': [
                        {'name': '1 cube (20g)', 'unit': 'cube', 'quantity': 20, 'is_default': True},
                        {'name': '2 cubes', 'unit': 'cubes', 'quantity': 40},
                        {'name': '1 serving (50g)', 'unit': 'serving', 'quantity': 50}
                    ]
                }
            ]
            
            added_foods = 0
            added_servings = 0
            
            for data in sample_data:
                # Check if food already exists
                existing_food = Food.query.filter_by(
                    name=data['food_info']['name'],
                    brand=data['food_info']['brand']
                ).first()
                
                if not existing_food:
                    # Create new food
                    food = Food(**data['food_info'])
                    db.session.add(food)
                    db.session.flush()  # Get the ID
                    added_foods += 1
                else:
                    food = existing_food
                
                # Add servings if they don't exist
                existing_servings = FoodServing.query.filter_by(food_id=food.id).count()
                if existing_servings == 0:
                    for serving_data in data['servings']:
                        serving = FoodServing(
                            food_id=food.id,
                            **serving_data
                        )
                        db.session.add(serving)
                        added_servings += 1
            
            db.session.commit()
            
            print(f"✅ Added {added_foods} sample foods")
            print(f"✅ Added {added_servings} sample serving sizes")
            
            # Print summary
            total_foods = Food.query.filter_by(is_verified=True).count()
            total_servings = FoodServing.query.count()
            
            print(f"\n📊 Database Summary:")
            print(f"   • Total verified foods: {total_foods}")
            print(f"   • Total serving sizes: {total_servings}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to populate sample data: {e}")
            db.session.rollback()
            return False

def main():
    """Run the sample data population."""
    print("=" * 60)
    print("🚀 NUTRI TRACKER - SAMPLE UOM DATA")
    print("=" * 60)
    
    if populate_sample_uom_data():
        print("\n✅ Sample UOM data populated successfully!")
        print("\n🎯 Ready to test:")
        print("   1. Start the Flask application")
        print("   2. Login to a user account")
        print("   3. Navigate to 'Log Meal'")
        print("   4. Search for foods like 'rice', 'idli', 'banana'")
        print("   5. Test different serving sizes")
    else:
        print("❌ Failed to populate sample data.")
        return 1
    
    print("=" * 60)
    return 0

if __name__ == '__main__':
    exit(main())
