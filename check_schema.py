#!/usr/bin/env python3
"""
Check database schema for food_serving table
"""

from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    # Check table creation SQL
    result = db.session.execute(text("SELECT sql FROM sqlite_master WHERE type='table' AND name='food_serving'")).fetchone()
    print("Table creation SQL:")
    print(result[0] if result else "Not found")
    
    # Check indexes
    result = db.session.execute(text("PRAGMA index_list(food_serving)")).fetchall()
    print("\nIndexes:")
    for row in result:
        print(f"  {row}")
        
    # Check constraints by trying to create a duplicate
    print("\nTesting UNIQUE constraint:")
    try:
        # Insert a test record
        db.session.execute(text("INSERT INTO food_serving (food_id, serving_name, unit, grams_per_unit, created_by) VALUES (999, 'test', 'test', 100, 1)"))
        db.session.commit()
        print("  First insert successful")
        
        # Try to insert duplicate
        db.session.execute(text("INSERT INTO food_serving (food_id, serving_name, unit, grams_per_unit, created_by) VALUES (999, 'test', 'test', 200, 1)"))
        db.session.commit()
        print("  ✗ Duplicate insert allowed - UNIQUE constraint not working")
        
        # Clean up
        db.session.execute(text("DELETE FROM food_serving WHERE food_id = 999"))
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        print(f"  ✓ Duplicate insert rejected: {str(e)}")
        
        # Clean up first record
        try:
            db.session.execute(text("DELETE FROM food_serving WHERE food_id = 999"))
            db.session.commit()
        except:
            pass
    
    print("\nTesting CHECK constraint for grams_per_unit:")
    try:
        db.session.execute(text("INSERT INTO food_serving (food_id, serving_name, unit, grams_per_unit, created_by) VALUES (999, 'invalid', 'test', 0, 1)"))
        db.session.commit()
        print("  ✗ Invalid grams allowed - CHECK constraint not working")
        db.session.execute(text("DELETE FROM food_serving WHERE food_id = 999"))
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"  ✓ Invalid grams rejected: {str(e)}")
