#!/usr/bin/env python3
"""
Migration script to add default_serving_size_grams to Food model.

This migration adds a default serving size in grams for each food item,
which will be used as the baseline for portion calculations.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Food, FoodServing
from sqlalchemy import text

def migrate_default_serving_size():
    """Add default_serving_size_grams column to Food table and populate it."""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔧 Starting default serving size migration...")
            
            # Step 1: Add the new column if it doesn't exist
            print("📝 Adding default_serving_size_grams column...")
            with db.engine.connect() as conn:
                # Check if column already exists
                result = conn.execute(text("PRAGMA table_info(food)")).fetchall()
                column_exists = any(row[1] == 'default_serving_size_grams' for row in result)
                
                if not column_exists:
                    conn.execute(text('''
                        ALTER TABLE food 
                        ADD COLUMN default_serving_size_grams FLOAT DEFAULT 100.0
                    '''))
                    conn.commit()
                    print("   ✅ Column added successfully")
                else:
                    print("   ℹ️ Column already exists, skipping creation")
            
            # Step 2: Update existing foods with appropriate default serving sizes
            print("📊 Setting default serving sizes for existing foods...")
            
            # Category-based default serving sizes (in grams)
            category_defaults = {
                'Dairy': 250,        # 1 cup of milk/yogurt
                'Grains': 50,        # 1/2 cup cooked rice/bread slice
                'Vegetables': 100,   # Standard vegetable serving
                'Fruits': 150,       # Medium fruit
                'Proteins': 100,     # Standard protein portion
                'Legumes': 50,       # 1/2 cup cooked legumes
                'Nuts': 30,          # Small handful
                'Beverages': 250,    # 1 cup
                'Snacks': 30,        # Standard snack portion
                'Oils': 15,          # 1 tablespoon
                'Spices': 5,         # 1 teaspoon
                'Condiments': 15,    # 1 tablespoon
            }
            
            # Update foods based on category
            foods_updated = 0
            with db.engine.connect() as conn:
                for category, default_size in category_defaults.items():
                    result = conn.execute(text('''
                        UPDATE food 
                        SET default_serving_size_grams = :default_size 
                        WHERE category = :category
                    '''), {"default_size": default_size, "category": category})
                    foods_updated += result.rowcount
                    print(f"   ✅ Updated {result.rowcount} foods in {category} category (default: {default_size}g)")
                conn.commit()
            
            # Step 3: For foods with existing default servings, use those
            print("🎯 Using existing default servings where available...")
            
            default_servings = db.session.query(FoodServing).filter_by(is_default=True).all()
            with db.engine.connect() as conn:
                for serving in default_servings:
                    conn.execute(text('''
                        UPDATE food 
                        SET default_serving_size_grams = :serving_quantity 
                        WHERE id = :food_id
                    '''), {"serving_quantity": serving.serving_quantity, "food_id": serving.food_id})
                    print(f"   ✅ Set {serving.food.name} default to {serving.serving_quantity}g ({serving.serving_name})")
                
                # Step 4: Set remaining foods to 100g default
                remaining_result = conn.execute(text('''
                    UPDATE food 
                    SET default_serving_size_grams = 100.0 
                    WHERE default_serving_size_grams IS NULL
                '''))
                conn.commit()
            
            if remaining_result.rowcount > 0:
                print(f"   ✅ Set {remaining_result.rowcount} remaining foods to 100g default")
            
            # Step 5: Verify the migration
            total_foods = db.session.query(Food).count()
            with db.engine.connect() as conn:
                foods_with_default = conn.execute(text('''
                    SELECT COUNT(*) as count FROM food 
                    WHERE default_serving_size_grams IS NOT NULL
                ''')).fetchone().count
            
            print(f"📈 Migration verification:")
            print(f"   Total foods: {total_foods}")
            print(f"   Foods with default serving size: {foods_with_default}")
            
            if foods_with_default == total_foods:
                print("✅ Migration completed successfully!")
                db.session.commit()
            else:
                print("❌ Migration incomplete - rolling back")
                db.session.rollback()
                return False
                
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()
            return False
    
    return True

if __name__ == '__main__':
    if migrate_default_serving_size():
        print("🎉 Default serving size migration completed successfully!")
    else:
        print("💥 Migration failed!")
        sys.exit(1)
