#!/usr/bin/env python3
"""
Database Migration: Add description field to Food model
Adds a description column to the food table for food item descriptions
"""

import sys
import os
import sqlite3

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def migrate_add_description():
    """Add description field to food table."""
    db_path = "instance/nutri_tracker.db"
    
    if not os.path.exists(db_path):
        print("❌ Database file not found. Please ensure the database exists.")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if description column already exists
        cursor.execute("PRAGMA table_info(food)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'description' in column_names:
            print("✅ Description column already exists in food table")
            conn.close()
            return True
        
        print("📝 Adding description column to food table...")
        
        # Add description column
        cursor.execute("ALTER TABLE food ADD COLUMN description TEXT")
        
        # Commit changes
        conn.commit()
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(food)")
        new_columns = cursor.fetchall()
        new_column_names = [col[1] for col in new_columns]
        
        if 'description' in new_column_names:
            print("✅ Successfully added description column to food table")
            print("📊 Food table now has the following columns:")
            for col in new_columns:
                cid, name, type_name, notnull, default, pk = col
                print(f"   - {name}: {type_name}")
        else:
            print("❌ Failed to add description column")
            return False
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error adding description column: {e}")
        return False

def main():
    """Run the migration."""
    print("🗄️ Food Table Migration: Adding Description Field")
    print("=" * 60)
    
    success = migrate_add_description()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("📋 You can now use the 'description' field in food uploads")
    else:
        print("\n❌ Migration failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
