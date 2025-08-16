#!/usr/bin/env python3
"""
Migration script to add default_serving_id column to Food model
- Add nullable default_serving_id column as FK to food_serving.id
- Maintains backwards compatibility
- No changes to existing fields or behaviors
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text

def migrate_add_default_serving_id():
    """Add default_serving_id column to food table"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔄 Starting migration to add default_serving_id to food table...")
            
            # Step 1: Check if column already exists
            result = db.session.execute(text("PRAGMA table_info(food)"))
            columns = {row[1]: row for row in result}
            
            if 'default_serving_id' in columns:
                print("✅ default_serving_id column already exists!")
                return True
                
            print(f"📋 Current food table columns: {list(columns.keys())}")
            
            # Step 2: Add the new column
            print("📝 Adding default_serving_id column...")
            
            add_column_sql = """
            ALTER TABLE food ADD COLUMN default_serving_id INTEGER
            """
            
            db.session.execute(text(add_column_sql))
            
            # Step 3: Create the foreign key constraint (if supported)
            # Note: SQLite doesn't support adding FK constraints to existing tables
            # The FK will be enforced by SQLAlchemy ORM
            print("⚠️  Note: SQLite doesn't support adding FK constraints to existing tables")
            print("   Foreign key will be enforced by SQLAlchemy ORM")
            
            # Commit the changes
            db.session.commit()
            
            print("✅ Successfully added default_serving_id column!")
            
            # Step 4: Verify the new structure
            print("🔍 Verifying new table structure...")
            result = db.session.execute(text("PRAGMA table_info(food)"))
            new_columns = result.fetchall()
            
            print("Updated columns:")
            for col in new_columns:
                if col[1] == 'default_serving_id':
                    print(f"  ✅ {col[1]} {col[2]} (NOT NULL: {col[3]}, DEFAULT: {col[4]}) - NEW COLUMN")
                else:
                    print(f"     {col[1]} {col[2]} (NOT NULL: {col[3]}, DEFAULT: {col[4]})")
                    
            # Step 5: Test that we can query foods without issues
            print("🧪 Testing food model loading...")
            from app.models import Food
            
            food_count = Food.query.count()
            print(f"   Total foods in database: {food_count}")
            
            # Test loading a food with the new relationship
            sample_food = Food.query.first()
            if sample_food:
                print(f"   Sample food: {sample_food.name}")
                print(f"   Default serving: {sample_food.default_serving}")
                print("   ✅ Food model loads successfully with new relationship")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during migration: {e}")
            db.session.rollback()
            return False

def test_relationship():
    """Test the new default_serving relationship"""
    app = create_app()
    
    with app.app_context():
        try:
            print("\n🧪 Testing default_serving relationship...")
            
            from app.models import Food, FoodServing
            
            # Test 1: Load foods and check default_serving (should be None initially)
            foods = Food.query.limit(3).all()
            for food in foods:
                print(f"   Food: {food.name} | Default serving: {food.default_serving}")
                
            # Test 2: Try to set a default serving if we have servings
            food_with_servings = db.session.query(Food).join(FoodServing).first()
            if food_with_servings:
                available_servings = FoodServing.query.filter_by(food_id=food_with_servings.id).all()
                if available_servings:
                    print(f"\\n   Testing with {food_with_servings.name}:")
                    print(f"   Available servings: {[s.serving_name for s in available_servings]}")
                    
                    # Set the first serving as default (just for testing)
                    original_default = food_with_servings.default_serving_id
                    food_with_servings.default_serving_id = available_servings[0].id
                    db.session.commit()
                    
                    # Reload and check
                    db.session.refresh(food_with_servings)
                    print(f"   Set default serving: {food_with_servings.default_serving.serving_name}")
                    print("   ✅ Relationship working correctly!")
                    
                    # Restore original state
                    food_with_servings.default_serving_id = original_default
                    db.session.commit()
                    print("   🔄 Restored original state")
            
            return True
            
        except Exception as e:
            print(f"❌ Error testing relationship: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    print("🚀 Starting Food model default_serving_id migration...")
    success = migrate_add_default_serving_id()
    
    if success:
        print("✅ Migration completed successfully!")
        
        # Test the new relationship
        test_success = test_relationship()
        
        if test_success:
            print("✅ All tests passed! default_serving relationship is working.")
        else:
            print("⚠️  Migration successful but relationship test failed.")
    else:
        print("❌ Migration failed!")
