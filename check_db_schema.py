#!/usr/bin/env python3
"""
Check the database schema for the user table
"""

from app import create_app, db
from sqlalchemy import text

app = create_app()
with app.app_context():
    # Check the user table schema
    result = db.session.execute(text('PRAGMA table_info(user);'))
    columns = result.fetchall()
    
    print("📋 User table schema:")
    print("=" * 50)
    for col in columns:
        cid, name, type_, notnull, default, pk = col
        nullable = "NOT NULL" if notnull else "NULL"
        print(f"{name:20} {type_:15} {nullable:10} (PK: {bool(pk)})")
    
    # Check if email field allows NULL
    email_info = [col for col in columns if col[1] == 'email']
    if email_info:
        email_notnull = email_info[0][3]
        if email_notnull:
            print("\n❌ PROBLEM FOUND: email field has NOT NULL constraint")
            print("   This is why we get: sqlite3.IntegrityError: NOT NULL constraint failed: user.email")
        else:
            print("\n✅ Email field allows NULL values")
    else:
        print("\n❌ Email field not found in table")
