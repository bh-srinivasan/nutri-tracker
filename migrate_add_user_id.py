#!/usr/bin/env python3
"""
Migration script to add user_id field to user table
"""

from app import create_app, db
from sqlalchemy import text
import uuid
import sys

def migrate_add_user_id():
    """Add user_id field to the user table and populate it."""
    
    app = create_app()
    with app.app_context():
        
        print("🔄 Starting migration: Adding user_id field to user table")
        print("=" * 60)
        
        try:
            # Step 1: Check if user_id column already exists
            print("Step 1: Checking current schema...")
            result = db.session.execute(text('PRAGMA table_info(user);'))
            columns = result.fetchall()
            
            user_id_exists = any(col[1] == 'user_id' for col in columns)
            if user_id_exists:
                print("✅ user_id field already exists. No migration needed.")
                return
            
            print("📋 Current user table schema:")
            for col in columns:
                cid, name, type_, notnull, default, pk = col
                nullable = "NOT NULL" if notnull else "NULL"
                print(f"   {name:20} {type_:15} {nullable}")
            
            # Step 2: Create new table with user_id field
            print("\nStep 2: Creating new user table with user_id field...")
            
            create_new_table_sql = """
            CREATE TABLE user_new (
                id INTEGER PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL UNIQUE,
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
            print("✅ Created user_new table with user_id field")
            
            # Step 3: Copy data from old table to new table with generated user_ids
            print("\nStep 3: Copying data and generating user_ids...")
            
            # Get all users from the old table
            old_users_result = db.session.execute(text('SELECT * FROM user;'))
            old_users = old_users_result.fetchall()
            
            print(f"   Found {len(old_users)} users to migrate")
            
            # Insert each user with a generated user_id
            for user in old_users:
                # Generate unique UUID for each user
                user_id = str(uuid.uuid4())
                
                insert_sql = """
                INSERT INTO user_new (
                    id, user_id, username, email, password_hash, is_admin, is_active,
                    created_at, last_login, first_name, last_name, age, gender,
                    height, weight, activity_level, password_changed_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """
                
                db.session.execute(text(insert_sql), (
                    user[0],   # id
                    user_id,   # user_id (new field)
                    user[1],   # username  
                    user[2],   # email
                    user[3],   # password_hash
                    user[4],   # is_admin
                    user[5],   # is_active
                    user[6],   # created_at
                    user[7],   # last_login
                    user[8],   # first_name
                    user[9],   # last_name
                    user[10],  # age
                    user[11],  # gender
                    user[12],  # height
                    user[13],  # weight
                    user[14],  # activity_level
                    user[15]   # password_changed_at
                ))
                
                print(f"   Generated user_id for user {user[1]}: {user_id[:8]}...")
            
            # Check how many rows were copied
            count_result = db.session.execute(text('SELECT COUNT(*) FROM user_new;'))
            new_count = count_result.fetchone()[0]
            
            print(f"✅ Copied {new_count} users with generated user_ids")
            
            if new_count != len(old_users):
                print("❌ Row count mismatch! Rolling back...")
                db.session.rollback()
                return
            
            # Step 4: Create indexes on new table
            print("\nStep 4: Creating indexes...")
            
            index_commands = [
                "CREATE UNIQUE INDEX ix_user_new_user_id ON user_new (user_id);",
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
            
            # Check user_id field specifically
            user_id_info = [col for col in columns if col[1] == 'user_id']
            if user_id_info and user_id_info[0][3]:  # notnull = 1 means NOT NULL
                print("\n🎉 SUCCESS: user_id field added with NOT NULL UNIQUE constraint!")
            else:
                print("\n❌ PROBLEM: user_id field is not properly configured")
                
            # Show sample user_ids
            print("\nSample user_ids generated:")
            sample_result = db.session.execute(text('SELECT username, user_id FROM user LIMIT 3;'))
            samples = sample_result.fetchall()
            for username, user_id in samples:
                print(f"   {username}: {user_id}")
                
        except Exception as e:
            print(f"\n❌ Migration failed: {str(e)}")
            print("Rolling back changes...")
            db.session.rollback()
            sys.exit(1)

if __name__ == '__main__':
    migrate_add_user_id()
