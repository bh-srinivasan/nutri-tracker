import sqlite3

# Connect to the database
conn = sqlite3.connect('instance/nutri_tracker.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("=== DATABASE TABLES ===")
for table in tables:
    print(f"Table: {table[0]}")

print("\n=== USER TABLE SCHEMA ===")
cursor.execute("PRAGMA table_info(user);")
columns = cursor.fetchall()
for col in columns:
    print(f"  {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULLABLE'}")

print("\n=== FOOD TABLE SCHEMA ===")
cursor.execute("PRAGMA table_info(food);")
columns = cursor.fetchall()
for col in columns:
    print(f"  {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULLABLE'}")

# Check if there are any users and foods
cursor.execute("SELECT COUNT(*) FROM user;")
user_count = cursor.fetchone()[0]
print(f"\n=== DATA COUNTS ===")
print(f"Users: {user_count}")

cursor.execute("SELECT COUNT(*) FROM food;")
food_count = cursor.fetchone()[0]
print(f"Foods: {food_count}")

conn.close()
