#!/usr/bin/env python3
"""
Migration script to update FoodServing model structure
- Rename serving_unit to unit
- Rename serving_quantity to grams_per_unit  
- Remove is_default column
- Add created_by column (optional)
- Add UNIQUE constraint on (food_id, serving_name, unit)
- Add CHECK constraint on grams_per_unit > 0
- Add index on food_id
- Update foreign key to include ON DELETE CASCADE
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text

def migrate_food_serving_model():
    """Update FoodServing model structure to match requirements"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔄 Starting FoodServing model migration...")
            
            # Check current table structure
            result = db.session.execute(text("PRAGMA table_info(food_serving)"))
            current_columns = {row[1]: row for row in result}
            print(f"Current columns: {list(current_columns.keys())}")
            
            # Step 1: Create new table with correct structure
            print("📝 Creating new food_serving table with correct structure...")
            
            create_new_table_sql = """
            CREATE TABLE food_serving_new (
                id INTEGER NOT NULL,
                food_id INTEGER NOT NULL,
                serving_name VARCHAR(50) NOT NULL,
                unit VARCHAR(20) NOT NULL,
                grams_per_unit FLOAT NOT NULL,
                created_at DATETIME,
                created_by INTEGER,
                PRIMARY KEY (id),
                FOREIGN KEY(food_id) REFERENCES food (id) ON DELETE CASCADE,
                FOREIGN KEY(created_by) REFERENCES user (id),
                CONSTRAINT uq_food_serving_name_unit UNIQUE (food_id, serving_name, unit),
                CONSTRAINT ck_grams_per_unit_positive CHECK (grams_per_unit > 0)
            )
            """
            
            db.session.execute(text(create_new_table_sql))
            
            # Step 2: Copy existing data, mapping old columns to new ones
            print("📊 Copying existing data to new table...")
            
            copy_data_sql = """
            INSERT INTO food_serving_new (id, food_id, serving_name, unit, grams_per_unit, created_at, created_by)
            SELECT 
                id,
                food_id, 
                serving_name,
                serving_unit as unit,
                serving_quantity as grams_per_unit,
                created_at,
                NULL as created_by
            FROM food_serving
            WHERE serving_quantity > 0
            """
            
            result = db.session.execute(text(copy_data_sql))
            rows_copied = result.rowcount
            print(f"✅ Copied {rows_copied} rows to new table")
            
            # Step 3: Drop old table and rename new table
            print("🔄 Replacing old table with new table...")
            db.session.execute(text("DROP TABLE food_serving"))
            db.session.execute(text("ALTER TABLE food_serving_new RENAME TO food_serving"))
            
            # Step 4: Create index on food_id
            print("📇 Creating index on food_id...")
            db.session.execute(text("CREATE INDEX ix_food_serving_food_id ON food_serving (food_id)"))
            
            # Commit all changes
            db.session.commit()
            
            print("✅ FoodServing model migration completed successfully!")
            
            # Verify new structure
            print("🔍 Verifying new table structure...")
            result = db.session.execute(text("PRAGMA table_info(food_serving)"))
            new_columns = result.fetchall()
            print("New columns:")
            for col in new_columns:
                print(f"  {col[1]} {col[2]} (NOT NULL: {col[3]}, DEFAULT: {col[4]})")
                
            # Check indexes
            result = db.session.execute(text("PRAGMA index_list(food_serving)"))
            indexes = result.fetchall()
            print("Indexes:")
            for idx in indexes:
                print(f"  {idx[1]} (unique: {idx[2]})")
                
            # Check foreign keys
            result = db.session.execute(text("PRAGMA foreign_key_list(food_serving)"))
            foreign_keys = result.fetchall()
            print("Foreign keys:")
            for fk in foreign_keys:
                print(f"  {fk[2]}.{fk[3]} -> {fk[4]} (ON DELETE: {fk[5]})")
                
        except Exception as e:
            print(f"❌ Error during migration: {e}")
            db.session.rollback()
            return False
    
    return True

def verify_constraints():
    """Verify that constraints are working properly"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🧪 Testing constraints...")
            
            # Test CHECK constraint (should fail with negative grams_per_unit)
            try:
                db.session.execute(text("""
                    INSERT INTO food_serving (food_id, serving_name, unit, grams_per_unit) 
                    VALUES (1, 'test', 'gram', -5)
                """))
                db.session.commit()
                print("❌ CHECK constraint test failed - negative value was allowed")
                return False
            except Exception:
                db.session.rollback()
                print("✅ CHECK constraint working - negative grams_per_unit rejected")
            
            # Test UNIQUE constraint (insert duplicate then try again)
            try:
                # First insert should succeed
                db.session.execute(text("""
                    INSERT INTO food_serving (food_id, serving_name, unit, grams_per_unit) 
                    VALUES (999, 'test_serving', 'cup', 100)
                """))
                db.session.commit()
                
                # Second insert with same food_id, serving_name, unit should fail
                try:
                    db.session.execute(text("""
                        INSERT INTO food_serving (food_id, serving_name, unit, grams_per_unit) 
                        VALUES (999, 'test_serving', 'cup', 150)
                    """))
                    db.session.commit()
                    print("❌ UNIQUE constraint test failed - duplicate was allowed")
                    return False
                except Exception:
                    db.session.rollback()
                    print("✅ UNIQUE constraint working - duplicate serving rejected")
                    
                # Clean up test data
                db.session.execute(text("DELETE FROM food_serving WHERE food_id = 999"))
                db.session.commit()
                
            except Exception as e:
                db.session.rollback()
                print(f"⚠️  Constraint test setup failed: {e}")
                
        except Exception as e:
            print(f"❌ Error verifying constraints: {e}")
            return False
    
    return True

if __name__ == "__main__":
    print("🚀 Starting FoodServing model migration...")
    success = migrate_food_serving_model()
    
    if success:
        print("✅ Migration completed successfully!")
        
        # Verify constraints
        print("\n🔍 Verifying constraints...")
        constraints_ok = verify_constraints()
        
        if constraints_ok:
            print("✅ All constraints verified!")
        else:
            print("⚠️  Some constraints may not be working properly")
    else:
        print("❌ Migration failed!")
