#!/usr/bin/env python3
"""
Migration script to make email field nullable in user table
"""

from app import create_app, db
from sqlalchemy import text
import sys

def migrate_email_nullable():
    """Migrate the user table to make email field nullable."""
    
    app = create_app()
    with app.app_context():
        
        print("🔄 Starting migration: Making user.email nullable")
        print("=" * 60)
        
        try:
            # Step 1: Check current schema
            print("Step 1: Checking current schema...")
            result = db.session.execute(text('PRAGMA table_info(user);'))
            columns = result.fetchall()
            
            email_info = [col for col in columns if col[1] == 'email']
            if email_info and not email_info[0][3]:  # notnull = 0 means nullable
                print("✅ Email field is already nullable. No migration needed.")
                return
            
            print("📋 Current user table schema:")
            for col in columns:
                cid, name, type_, notnull, default, pk = col
                nullable = "NOT NULL" if notnull else "NULL"
                print(f"   {name:20} {type_:15} {nullable}")
            
            # Step 2: Create new table with correct schema
            print("\nStep 2: Creating new user table with nullable email...")
            
            create_new_table_sql = """
            CREATE TABLE user_new (
                id INTEGER PRIMARY KEY,
                username VARCHAR(80) NOT NULL UNIQUE,
                email VARCHAR(120) NULL,
                password_hash VARCHAR(255) NOT NULL,
                is_admin BOOLEAN DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME,
                last_login DATETIME,
                first_name VARCHAR(50),
                last_name VARCHAR(50),
                age INTEGER,
                gender VARCHAR(10),
                height FLOAT,
                weight FLOAT,
                activity_level VARCHAR(20),
                password_changed_at DATETIME
            );
            """
            
            db.session.execute(text(create_new_table_sql))
            print("✅ Created user_new table with nullable email")
            
            # Step 3: Copy data from old table to new table
            print("\nStep 3: Copying data from old table...")
            
            copy_data_sql = """
            INSERT INTO user_new (
                id, username, email, password_hash, is_admin, is_active,
                created_at, last_login, first_name, last_name, age, gender,
                height, weight, activity_level, password_changed_at
            )
            SELECT 
                id, username, email, password_hash, is_admin, is_active,
                created_at, last_login, first_name, last_name, age, gender,
                height, weight, activity_level, password_changed_at
            FROM user;
            """
            
            db.session.execute(text(copy_data_sql))
            
            # Check how many rows were copied
            count_result = db.session.execute(text('SELECT COUNT(*) FROM user_new;'))
            new_count = count_result.fetchone()[0]
            
            count_result_old = db.session.execute(text('SELECT COUNT(*) FROM user;'))
            old_count = count_result_old.fetchone()[0]
            
            print(f"✅ Copied {new_count} rows (original table had {old_count} rows)")
            
            if new_count != old_count:
                print("❌ Row count mismatch! Rolling back...")
                db.session.rollback()
                return
            
            # Step 4: Create indexes on new table
            print("\nStep 4: Creating indexes...")
            
            index_commands = [
                "CREATE UNIQUE INDEX ix_user_new_username ON user_new (username);",
                "CREATE INDEX ix_user_new_email ON user_new (email);"
            ]
            
            for cmd in index_commands:
                db.session.execute(text(cmd))
            
            print("✅ Created indexes")
            
            # Step 5: Drop old table and rename new table
            print("\nStep 5: Replacing old table...")
            
            db.session.execute(text('DROP TABLE user;'))
            db.session.execute(text('ALTER TABLE user_new RENAME TO user;'))
            
            print("✅ Old table dropped and new table renamed")
            
            # Step 6: Commit the transaction
            print("\nStep 6: Committing changes...")
            db.session.commit()
            
            print("✅ Migration completed successfully!")
            
            # Step 7: Verify the new schema
            print("\nStep 7: Verifying new schema...")
            result = db.session.execute(text('PRAGMA table_info(user);'))
            columns = result.fetchall()
            
            print("📋 New user table schema:")
            for col in columns:
                cid, name, type_, notnull, default, pk = col
                nullable = "NOT NULL" if notnull else "NULL"
                print(f"   {name:20} {type_:15} {nullable}")
            
            # Check email field specifically
            email_info = [col for col in columns if col[1] == 'email']
            if email_info and not email_info[0][3]:  # notnull = 0 means nullable
                print("\n🎉 SUCCESS: Email field is now nullable!")
            else:
                print("\n❌ PROBLEM: Email field is still NOT NULL")
                
        except Exception as e:
            print(f"\n❌ Migration failed: {str(e)}")
            print("Rolling back changes...")
            db.session.rollback()
            sys.exit(1)

if __name__ == '__main__':
    migrate_email_nullable()
