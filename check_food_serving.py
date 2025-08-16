#!/usr/bin/env python3
"""
Check current food_serving table structure
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text

def check_food_serving_table():
    """Check current food_serving table structure"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if food_serving table exists
            result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='food_serving'"))
            table_exists = result.fetchone() is not None
            print(f'food_serving table exists: {table_exists}')
            
            if table_exists:
                result = db.session.execute(text('PRAGMA table_info(food_serving)'))
                columns = result.fetchall()
                print('Current columns:')
                for col in columns:
                    print(f'  {col[1]} {col[2]} (NOT NULL: {col[3]}, DEFAULT: {col[4]})')
                    
                # Check indexes
                result = db.session.execute(text("PRAGMA index_list(food_serving)"))
                indexes = result.fetchall()
                print('Current indexes:')
                for idx in indexes:
                    print(f'  {idx[1]} (unique: {idx[2]})')
                    
                # Check constraints
                result = db.session.execute(text("SELECT sql FROM sqlite_master WHERE type='table' AND name='food_serving'"))
                table_sql = result.fetchone()
                if table_sql:
                    print('Table creation SQL:')
                    print(table_sql[0])
            else:
                print('Table does not exist - will need to create it')
                
        except Exception as e:
            print(f"Error checking table: {e}")

if __name__ == "__main__":
    check_food_serving_table()
