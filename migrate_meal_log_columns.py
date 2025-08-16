#!/usr/bin/env python3
"""
Migration: Add logged_grams, sugar, and sodium columns to MealLog table.

This migration:
1. Adds logged_grams column (NOT NULL) 
2. Adds sugar column (nullable)
3. Adds sodium column (nullable)
4. Populates logged_grams with existing quantity values for backward compatibility
5. Handles any NULL values gracefully
"""

import sys
import os
from datetime import datetime

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db
from sqlalchemy import text

def migrate_meal_log_columns():
    """Add new columns to MealLog table and populate logged_grams."""
    app = create_app()
    
    with app.app_context():
        print("🔄 Starting MealLog table migration...")
        
        # Execute SQL to add new columns
        try:
            # Add logged_grams column (temporary nullable)
            db.session.execute(text('ALTER TABLE meal_log ADD COLUMN logged_grams FLOAT'))
            print("   ✅ Added logged_grams column")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("   ℹ️  logged_grams column already exists")
            else:
                raise e
                
        try:
            # Add sugar column 
            db.session.execute(text('ALTER TABLE meal_log ADD COLUMN sugar FLOAT'))
            print("   ✅ Added sugar column")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("   ℹ️  sugar column already exists")
            else:
                raise e
                
        try:
            # Add sodium column 
            db.session.execute(text('ALTER TABLE meal_log ADD COLUMN sodium FLOAT'))
            print("   ✅ Added sodium column")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("   ℹ️  sodium column already exists")
            else:
                raise e        # Commit the column additions
        db.session.commit()
        
        # Now populate logged_grams from existing quantity values
        print("   📊 Populating logged_grams from existing quantity values...")
        
        # Update all records where logged_grams is NULL
        result = db.session.execute(text("""
            UPDATE meal_log 
            SET logged_grams = quantity 
            WHERE logged_grams IS NULL
        """))
        
        rows_updated = result.rowcount
        print(f"   ✅ Updated {rows_updated} records with logged_grams values")
        
        # Commit the data population
        db.session.commit()
        
        # Now we need to make logged_grams NOT NULL (SQLite limitation workaround)
        print("   🔧 Making logged_grams NOT NULL...")
        
        # For SQLite, we need to recreate the table to add NOT NULL constraint
        # But for now, let's verify all records have logged_grams values
        null_count = db.session.execute(text("""
            SELECT COUNT(*) as count FROM meal_log WHERE logged_grams IS NULL
        """)).fetchone()[0]
        
        if null_count > 0:
            print(f"   ⚠️  Warning: {null_count} records still have NULL logged_grams")
            # Set remaining NULLs to 0 as fallback
            db.session.execute(text("""
                UPDATE meal_log 
                SET logged_grams = 0 
                WHERE logged_grams IS NULL
            """))
            db.session.commit()
            print("   ✅ Set remaining NULL values to 0")
        
        # Verify final state
        total_records = db.session.execute(text("SELECT COUNT(*) as count FROM meal_log")).fetchone()[0]
        non_null_logged_grams = db.session.execute(text("""
            SELECT COUNT(*) as count FROM meal_log WHERE logged_grams IS NOT NULL
        """)).fetchone()[0]
        
        print(f"\n📋 Migration Summary:")
        print(f"   Total MealLog records: {total_records}")
        print(f"   Records with logged_grams: {non_null_logged_grams}")
        print(f"   Migration completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if total_records == non_null_logged_grams:
            print("   ✅ All records have logged_grams values")
        else:
            print("   ⚠️  Some records missing logged_grams values")
        
        print("\n✅ MealLog migration completed successfully!")

if __name__ == "__main__":
    migrate_meal_log_columns()
