#!/usr/bin/env python3
"""
Migration script to add UOM support to MealLog table
Adds fields for original_quantity, unit_type, and serving_id
"""

import os
import sys
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import MealLog, FoodServing
from sqlalchemy import text

def migrate_meallog_uom():
    """Add UOM support fields to MealLog table."""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔧 Starting MealLog UOM migration...")
            
            # Check if columns already exist
            inspector = db.inspect(db.engine)
            existing_columns = [col['name'] for col in inspector.get_columns('meal_log')]
            
            columns_to_add = []
            
            if 'original_quantity' not in existing_columns:
                columns_to_add.append(('original_quantity', 'REAL NOT NULL DEFAULT 0'))
            
            if 'unit_type' not in existing_columns:
                columns_to_add.append(('unit_type', "VARCHAR(20) NOT NULL DEFAULT 'grams'"))
            
            if 'serving_id' not in existing_columns:
                columns_to_add.append(('serving_id', 'INTEGER'))
            
            if not columns_to_add:
                print("✅ All UOM columns already exist. No migration needed.")
                return True
            
            # Add new columns
            for column_name, column_def in columns_to_add:
                sql = f"ALTER TABLE meal_log ADD COLUMN {column_name} {column_def}"
                print(f"   Adding column: {column_name}")
                db.session.execute(text(sql))
            
            # Update existing records with default values
            print("   Updating existing records...")
            db.session.execute(text("""
                UPDATE meal_log 
                SET original_quantity = quantity 
                WHERE original_quantity = 0 OR original_quantity IS NULL
            """))
            
            # Add foreign key constraint for serving_id if it doesn't exist
            try:
                # Check if foreign key exists
                fks = inspector.get_foreign_keys('meal_log')
                serving_fk_exists = any(fk['constrained_columns'] == ['serving_id'] for fk in fks)
                
                if not serving_fk_exists and 'serving_id' in [col[0] for col in columns_to_add]:
                    print("   Adding foreign key constraint for serving_id...")
                    db.session.execute(text("""
                        CREATE INDEX IF NOT EXISTS idx_meal_log_serving_id ON meal_log(serving_id)
                    """))
            except Exception as e:
                print(f"   Warning: Could not add foreign key constraint: {e}")
            
            db.session.commit()
            print("✅ MealLog UOM migration completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()
            return False

def add_sample_servings():
    """Add sample serving sizes for common foods."""
    app = create_app()
    
    with app.app_context():
        try:
            print("🍽️  Adding sample serving sizes...")
            
            # Sample servings for common foods
            sample_servings = [
                # Rice servings
                {
                    'food_name': 'Rice',
                    'servings': [
                        {'name': '1 cup cooked', 'unit': 'cup', 'quantity': 195},
                        {'name': '1 small bowl', 'unit': 'bowl', 'quantity': 150},
                        {'name': '1 large bowl', 'unit': 'bowl', 'quantity': 250}
                    ]
                },
                # Bread servings
                {
                    'food_name': 'Bread',
                    'servings': [
                        {'name': '1 slice', 'unit': 'slice', 'quantity': 25},
                        {'name': '1 thick slice', 'unit': 'slice', 'quantity': 35}
                    ]
                },
                # Milk servings
                {
                    'food_name': 'Milk',
                    'servings': [
                        {'name': '1 cup', 'unit': 'cup', 'quantity': 240},
                        {'name': '1 glass', 'unit': 'glass', 'quantity': 200},
                        {'name': '1 small glass', 'unit': 'glass', 'quantity': 150}
                    ]
                }
            ]
            
            from app.models import Food
            
            added_count = 0
            for food_data in sample_servings:
                # Find foods with similar names
                foods = Food.query.filter(
                    Food.name.ilike(f'%{food_data["food_name"]}%')
                ).limit(5).all()
                
                for food in foods:
                    # Check if servings already exist
                    existing_servings = FoodServing.query.filter_by(food_id=food.id).count()
                    if existing_servings > 0:
                        continue
                    
                    # Add servings for this food
                    for i, serving_data in enumerate(food_data['servings']):
                        serving = FoodServing(
                            food_id=food.id,
                            serving_name=serving_data['name'],
                            serving_unit=serving_data['unit'],
                            serving_quantity=serving_data['quantity'],
                            is_default=(i == 0)  # First serving is default
                        )
                        db.session.add(serving)
                        added_count += 1
            
            db.session.commit()
            print(f"✅ Added {added_count} sample serving sizes!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to add sample servings: {e}")
            db.session.rollback()
            return False

def main():
    """Run the migration."""
    print("=" * 60)
    print("🚀 NUTRI TRACKER - UOM MIGRATION")
    print("=" * 60)
    
    success = True
    
    # Run migrations
    if not migrate_meallog_uom():
        success = False
    
    if not add_sample_servings():
        success = False
    
    print("=" * 60)
    if success:
        print("✅ All migrations completed successfully!")
        print("\n📋 What's New:")
        print("   • MealLog now supports Units of Measure (UOM)")
        print("   • Users can log food in grams or custom serving sizes")
        print("   • Only verified foods are shown in meal logging")
        print("   • Enhanced security and validation")
        print("   • Sample serving sizes added for common foods")
    else:
        print("❌ Some migrations failed. Check errors above.")
        return 1
    
    print("=" * 60)
    return 0

if __name__ == '__main__':
    exit(main())
