#!/usr/bin/env python3
"""
Migration script to add target_weight field to nutrition_goal table
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text

def migrate_add_target_weight():
    """Add target_weight column to nutrition_goal table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if target_weight column already exists
            result = db.session.execute(text("PRAGMA table_info(nutrition_goal)"))
            columns = [row[1] for row in result]
            
            if 'target_weight' not in columns:
                print("Adding target_weight column to nutrition_goal table...")
                
                # Add the target_weight column
                db.session.execute(text(
                    "ALTER TABLE nutrition_goal ADD COLUMN target_weight FLOAT"
                ))
                db.session.commit()
                
                print("✅ Successfully added target_weight column!")
            else:
                print("✅ target_weight column already exists!")
                
        except Exception as e:
            print(f"❌ Error during migration: {e}")
            db.session.rollback()
            return False
    
    return True

if __name__ == "__main__":
    print("🔄 Starting migration to add target_weight field...")
    success = migrate_add_target_weight()
    
    if success:
        print("✅ Migration completed successfully!")
    else:
        print("❌ Migration failed!")
        exit(1)
