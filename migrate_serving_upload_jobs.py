#!/usr/bin/env python3
"""
Migration: Add Serving Upload Job tracking tables
"""

import sqlite3
import os
from datetime import datetime

def migrate_serving_upload_jobs():
    """Add serving upload job tracking tables."""
    
    db_path = 'instance/nutri_tracker.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 Adding Serving Upload Job tracking tables...")
        
        # Create serving_upload_job table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS serving_upload_job (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id VARCHAR(36) UNIQUE NOT NULL,
                filename VARCHAR(255) NOT NULL,
                total_rows INTEGER DEFAULT 0,
                processed_rows INTEGER DEFAULT 0,
                successful_rows INTEGER DEFAULT 0,
                failed_rows INTEGER DEFAULT 0,
                status VARCHAR(20) DEFAULT 'pending',
                error_message TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                started_at DATETIME,
                completed_at DATETIME,
                created_by INTEGER NOT NULL,
                FOREIGN KEY (created_by) REFERENCES user (id)
            )
        ''')
        
        # Create index on job_id
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_serving_upload_job_id 
            ON serving_upload_job(job_id)
        ''')
        
        # Create index on created_by
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_serving_upload_job_created_by 
            ON serving_upload_job(created_by)
        ''')
        
        # Create serving_upload_job_item table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS serving_upload_job_item (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER NOT NULL,
                row_number INTEGER NOT NULL,
                food_key VARCHAR(50),
                serving_name VARCHAR(100),
                status VARCHAR(20) DEFAULT 'pending',
                error_message TEXT,
                serving_id INTEGER,
                processed_at DATETIME,
                FOREIGN KEY (job_id) REFERENCES serving_upload_job (id) ON DELETE CASCADE,
                FOREIGN KEY (serving_id) REFERENCES food_serving (id)
            )
        ''')
        
        # Create indexes
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_serving_upload_job_item_job_id 
            ON serving_upload_job_item(job_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_serving_upload_job_item_serving_id 
            ON serving_upload_job_item(serving_id)
        ''')
        
        conn.commit()
        
        print("✅ Serving upload job tables created successfully!")
        
        # Verify tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%serving_upload%'")
        tables = cursor.fetchall()
        
        print("📋 Created tables:")
        for table in tables:
            print(f"   - {table[0]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == "__main__":
    print("🚀 Starting Serving Upload Job Tables Migration")
    print("=" * 50)
    
    success = migrate_serving_upload_jobs()
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("📝 New features available:")
        print("   - Serving upload job tracking")
        print("   - Upload history and progress monitoring")
        print("   - Detailed error reporting for failed uploads")
    else:
        print("\n💥 Migration failed!")
        print("   Check the error messages above for details")
