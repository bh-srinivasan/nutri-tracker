#!/usr/bin/env python3
"""
Database migration to add password_changed_at column to user table.
"""

import sqlite3
from datetime import datetime

def migrate_database():
    """Add password_changed_at column to user table."""
    print("🔄 Adding password_changed_at column to user table...")
    
    try:
        # Connect to database
        conn = sqlite3.connect('instance/nutri_tracker.db')
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(user)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'password_changed_at' not in columns:
            # Add the new column with NULL as default (SQLite limitation)
            cursor.execute("""
                ALTER TABLE user 
                ADD COLUMN password_changed_at DATETIME
            """)
            
            # Update existing users with current timestamp
            current_time = datetime.utcnow().isoformat()
            cursor.execute("""
                UPDATE user 
                SET password_changed_at = ? 
                WHERE password_changed_at IS NULL
            """, (current_time,))
            
            conn.commit()
            print("✅ Successfully added password_changed_at column")
        else:
            print("✅ password_changed_at column already exists")
        
        # Verify the change
        cursor.execute("PRAGMA table_info(user)")
        columns = cursor.fetchall()
        print(f"✅ User table now has {len(columns)} columns:")
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error migrating database: {e}")
        return False

if __name__ == "__main__":
    success = migrate_database()
    if success:
        print("\n🎉 Database migration completed successfully!")
        print("You can now start the Flask server.")
    else:
        print("\n💥 Database migration failed!")
