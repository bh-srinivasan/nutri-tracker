#!/usr/bin/env python3
"""
Migration script to add goal timing fields to nutrition_goal table.

This adds:
- goal_date: DateTime field for when the goal was last updated
- target_duration: String field for selected duration (e.g., "1 month", "3 months")
- target_date: Date field for target completion date

Usage:
    python migrate_add_goal_timing_fields.py
"""

import sys
import os
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text

def migrate_goal_timing_fields():
    """Add goal timing fields to nutrition_goal table."""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔄 Starting migration to add goal timing fields...")
            
            # Check current schema
            with db.engine.connect() as conn:
                result = conn.execute(text("PRAGMA table_info(nutrition_goal)"))
                columns = [row[1] for row in result.fetchall()]
                print(f"Current columns in nutrition_goal: {columns}")
                
                # Add goal_date column if it doesn't exist
                if 'goal_date' not in columns:
                    print("Adding goal_date column to nutrition_goal table...")
                    conn.execute(text("ALTER TABLE nutrition_goal ADD COLUMN goal_date DATETIME"))
                    
                    # Update existing records to have goal_date = created_at
                    print("Setting goal_date for existing records...")
                    conn.execute(text("UPDATE nutrition_goal SET goal_date = created_at WHERE goal_date IS NULL"))
                    print("✅ Successfully added goal_date column!")
                else:
                    print("✅ goal_date column already exists!")
                
                # Add target_duration column if it doesn't exist
                if 'target_duration' not in columns:
                    print("Adding target_duration column to nutrition_goal table...")
                    conn.execute(text("ALTER TABLE nutrition_goal ADD COLUMN target_duration VARCHAR(20)"))
                    print("✅ Successfully added target_duration column!")
                else:
                    print("✅ target_duration column already exists!")
                
                # Add target_date column if it doesn't exist
                if 'target_date' not in columns:
                    print("Adding target_date column to nutrition_goal table...")
                    conn.execute(text("ALTER TABLE nutrition_goal ADD COLUMN target_date DATE"))
                    print("✅ Successfully added target_date column!")
                else:
                    print("✅ target_date column already exists!")
                
                conn.commit()
            
            print("✅ Migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            raise

if __name__ == '__main__':
    migrate_goal_timing_fields()
