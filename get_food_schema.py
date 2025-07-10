#!/usr/bin/env python3
"""
Database Schema Information for Foods Table
Generate complete field details for the foods table
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Food
import sqlite3

def get_food_table_schema():
    """Get detailed schema information for the food table."""
    print("🗄️ NUTRI TRACKER - FOODS TABLE DATABASE SCHEMA")
    print("=" * 80)
    
    app = create_app()
    with app.app_context():
        # Get SQLAlchemy model information
        print("\n📋 FOOD MODEL FIELDS (from SQLAlchemy):")
        print("-" * 50)
        
        for column in Food.__table__.columns:
            nullable = "NULL" if column.nullable else "NOT NULL"
            default = f", DEFAULT: {column.default}" if column.default else ""
            primary_key = " [PRIMARY KEY]" if column.primary_key else ""
            foreign_key = ""
            if column.foreign_keys:
                fk = list(column.foreign_keys)[0]
                foreign_key = f" [FOREIGN KEY -> {fk.column}]"
            
            print(f"• {column.name:<15} | {str(column.type):<20} | {nullable:<8}{default}{primary_key}{foreign_key}")
        
        # Get actual database schema
        print(f"\n🔍 ACTUAL DATABASE SCHEMA:")
        print("-" * 50)
        
        try:
            # Connect to SQLite database
            db_path = "instance/nutri_tracker.db"
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Get table info
                cursor.execute("PRAGMA table_info(food)")
                columns = cursor.fetchall()
                
                print("Field Name       | Type          | Not Null | Default   | Primary Key")
                print("-" * 70)
                for col in columns:
                    cid, name, type_name, notnull, default, pk = col
                    not_null = "YES" if notnull else "NO"
                    default_val = default if default is not None else "NULL"
                    is_pk = "YES" if pk else "NO"
                    print(f"{name:<15} | {type_name:<12} | {not_null:<8} | {default_val:<9} | {is_pk}")
                
                # Get indexes
                print(f"\n📊 INDEXES:")
                print("-" * 30)
                cursor.execute("PRAGMA index_list(food)")
                indexes = cursor.fetchall()
                
                for idx in indexes:
                    seq, name, unique, origin, partial = idx
                    unique_str = "UNIQUE" if unique else "NON-UNIQUE"
                    print(f"• {name} ({unique_str})")
                    
                    # Get index columns
                    cursor.execute(f"PRAGMA index_info({name})")
                    idx_cols = cursor.fetchall()
                    for idx_col in idx_cols:
                        seqno, cid, col_name = idx_col
                        print(f"  - Column: {col_name}")
                
                conn.close()
            else:
                print("Database file not found. Using SQLAlchemy model definition only.")
                
        except Exception as e:
            print(f"Error accessing database: {e}")

def generate_detailed_schema():
    """Generate comprehensive schema documentation."""
    
    schema_doc = """
# 🗄️ FOODS TABLE - DATABASE SCHEMA SPECIFICATION

## 📋 Table Overview
**Table Name:** `food`  
**Purpose:** Store nutrition information for food items in the Nutri Tracker application  
**Engine:** SQLite  
**Character Set:** UTF-8  

## 🔧 Field Specifications

| Field Name    | Data Type     | Length | Nullable | Default | Constraints | Description |
|---------------|---------------|--------|----------|---------|-------------|-------------|
| `id`          | INTEGER       | -      | NO       | -       | PRIMARY KEY, AUTO INCREMENT | Unique identifier for each food item |
| `name`        | VARCHAR       | 100    | NO       | -       | INDEX | Food item name (e.g., "Basmati Rice", "Amul Butter") |
| `brand`       | VARCHAR       | 50     | YES      | NULL    | - | Brand name for commercial products (e.g., "Amul", "Nestlé") |
| `category`    | VARCHAR       | 50     | NO       | -       | INDEX | Food category (e.g., "Grains", "Dairy", "Vegetables") |
| `calories`    | REAL/FLOAT    | -      | NO       | 0       | - | Calories per 100g |
| `protein`     | REAL/FLOAT    | -      | NO       | 0       | - | Protein content per 100g (in grams) |
| `carbs`       | REAL/FLOAT    | -      | NO       | 0       | - | Carbohydrate content per 100g (in grams) |
| `fat`         | REAL/FLOAT    | -      | NO       | 0       | - | Fat content per 100g (in grams) |
| `fiber`       | REAL/FLOAT    | -      | YES      | 0       | - | Fiber content per 100g (in grams) |
| `sugar`       | REAL/FLOAT    | -      | YES      | 0       | - | Sugar content per 100g (in grams) |
| `sodium`      | REAL/FLOAT    | -      | YES      | 0       | - | Sodium content per 100g (in milligrams) |
| `serving_size`| REAL/FLOAT    | -      | YES      | 100     | - | Standard serving size (in grams) |
| `is_verified` | BOOLEAN       | -      | YES      | 0/FALSE | - | Whether the food data has been verified |
| `created_at`  | DATETIME      | -      | YES      | CURRENT_TIMESTAMP | - | When the food item was added |
| `created_by`  | INTEGER       | -      | YES      | NULL    | FOREIGN KEY (user.id) | ID of user who added this food item |

## 🔑 Keys and Constraints

### Primary Key
- **Field:** `id`
- **Type:** AUTO INCREMENT INTEGER
- **Purpose:** Unique identifier for each food record

### Foreign Keys
- **Field:** `created_by`
- **References:** `user(id)`
- **Action:** SET NULL ON DELETE (if user is deleted, food remains but creator is nulled)

### Indexes
- **name_idx:** INDEX on `name` field (for fast food name searches)
- **category_idx:** INDEX on `category` field (for category filtering)

### Unique Constraints
- None (allows duplicate food names for different brands/variations)

## 📊 Data Types and Ranges

### Nutritional Values (per 100g basis)
- **calories:** 0.0 - 900.0 (typical range for most foods)
- **protein:** 0.0 - 100.0 grams
- **carbs:** 0.0 - 100.0 grams  
- **fat:** 0.0 - 100.0 grams
- **fiber:** 0.0 - 50.0 grams
- **sugar:** 0.0 - 100.0 grams
- **sodium:** 0.0 - 5000.0 milligrams

### String Lengths
- **name:** Up to 100 characters (sufficient for food names like "Organic Whole Wheat Bread")
- **brand:** Up to 50 characters (sufficient for brand names like "Amul", "Tata", "Nestlé")
- **category:** Up to 50 characters (sufficient for categories like "Dairy Products", "Breakfast Cereals")

## 🎯 Usage Examples

### Sample Food Records

```sql
-- Indian Staple Food
INSERT INTO food (name, brand, category, calories, protein, carbs, fat, fiber, serving_size, is_verified) 
VALUES ('Basmati Rice', NULL, 'Grains', 350, 7.5, 78, 0.5, 1.0, 100, 1);

-- Branded Product
INSERT INTO food (name, brand, category, calories, protein, carbs, fat, sodium, serving_size, is_verified)
VALUES ('Butter', 'Amul', 'Dairy', 717, 0.9, 0.1, 81, 643, 10, 1);

-- Vegetable
INSERT INTO food (name, brand, category, calories, protein, carbs, fat, fiber, serving_size, is_verified)
VALUES ('Spinach', NULL, 'Vegetables', 23, 2.9, 3.6, 0.4, 2.2, 100, 1);
```

## 🔍 Search and Query Patterns

### Common Queries
```sql
-- Search by food name
SELECT * FROM food WHERE name LIKE '%rice%';

-- Filter by category
SELECT * FROM food WHERE category = 'Dairy';

-- Search by brand
SELECT * FROM food WHERE brand = 'Amul';

-- Get high-protein foods
SELECT * FROM food WHERE protein > 20 ORDER BY protein DESC;

-- Get low-calorie foods
SELECT * FROM food WHERE calories < 100 ORDER BY calories ASC;
```

## 📈 Performance Considerations

### Indexed Fields
- `name` - For fast text searches
- `category` - For category filtering
- Primary key `id` - Automatic clustering

### Query Optimization
- Use indexes for WHERE clauses on name and category
- Consider adding composite indexes for common query combinations
- Limit results for large datasets using LIMIT clause

## 🔒 Data Integrity Rules

### Required Fields
- `name` - Cannot be empty (food must have a name)
- `category` - Cannot be empty (food must be categorized)
- `calories`, `protein`, `carbs`, `fat` - Cannot be NULL (must have basic nutrition data)

### Optional Fields
- `brand` - NULL for generic/unbranded foods
- `fiber`, `sugar`, `sodium` - Can be NULL if unknown
- `created_by` - Can be NULL for system-imported foods

### Business Logic
- All nutritional values are per 100g basis for consistency
- `serving_size` defaults to 100g but can be customized
- `is_verified` flag for data quality control

---

**Database Schema Version:** 1.0  
**Last Updated:** July 6, 2025  
**Compatible with:** SQLite 3.x, PostgreSQL 12+, MySQL 8.0+
"""
    
    return schema_doc

def main():
    """Generate complete food table schema information."""
    get_food_table_schema()
    
    # Save detailed documentation
    schema_doc = generate_detailed_schema()
    with open("FOODS_TABLE_SCHEMA.md", "w", encoding="utf-8") as f:
        f.write(schema_doc)
    
    print(f"\n📄 Detailed schema documentation saved to: FOODS_TABLE_SCHEMA.md")
    print(f"\n✅ Food table schema analysis complete!")

if __name__ == "__main__":
    main()
