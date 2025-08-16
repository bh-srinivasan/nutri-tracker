# 🥗 **COMPLETE FOOD MODEL DOCUMENTATION**
## **Nutri Tracker Application - Food System Overview**

---

## **📁 1. FOOD MODEL DEFINITION**

### **File: `app/models.py`**
**Lines: 181-240**

### **🏗️ Database Fields:**

| Field Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `id` | Integer | Primary Key | Auto-increment unique identifier |
| `name` | String(100) | NOT NULL, Indexed | Food name (e.g., "Basmati Rice") |
| `brand` | String(50) | Optional | Brand name (e.g., "Amul", "Nestlé") |
| `category` | String(50) | NOT NULL, Indexed | Food category |
| `calories` | Float | NOT NULL, Default=0 | Calories per 100g |
| `protein` | Float | NOT NULL, Default=0 | Protein in grams per 100g |
| `carbs` | Float | NOT NULL, Default=0 | Carbohydrates in grams per 100g |
| `fat` | Float | NOT NULL, Default=0 | Fat in grams per 100g |
| `fiber` | Float | Default=0 | Fiber in grams per 100g |
| `sugar` | Float | Default=0 | Sugar in grams per 100g |
| `sodium` | Float | Default=0 | Sodium in mg per 100g |
| `description` | Text | Optional | Extended description |
| `serving_size` | Float | Default=100 | Legacy serving size in grams |
| `default_serving_size_grams` | Float | Default=100.0 | Default serving for UI |
| `is_verified` | Boolean | Default=False | Admin verification status |
| `created_at` | DateTime | Auto | Creation timestamp |
| `created_by` | Integer | Foreign Key | User who created (admin) |

### **🔗 Relationships:**
- **One-to-Many**: `meal_logs` → MealLog entries
- **One-to-Many**: `servings` → FoodServing options
- **One-to-Many**: `nutrition_info` → Extended nutrition data

### **📊 Methods:**
- `get_nutrition_per_serving()` - Calculates nutrition per serving size

---

## **📋 2. FOOD CATEGORIES**

### **Available Categories:**
1. **grains** - Grains & Cereals
2. **vegetables** - Vegetables  
3. **fruits** - Fruits
4. **dairy** - Dairy Products
5. **meat** - Meat & Poultry
6. **fish** - Fish & Seafood
7. **legumes** - Legumes & Pulses
8. **nuts** - Nuts & Seeds
9. **beverages** - Beverages
10. **snacks** - Snacks
11. **sweets** - Sweets & Desserts
12. **oils** - Oils & Fats
13. **spices** - Spices & Herbs
14. **processed** - Processed Foods
15. **other** - Other

---

## **🛠️ 3. ADMIN PANEL USAGE**

### **📂 Admin Files & Routes:**

| **File** | **Route** | **Purpose** | **Food Fields Used** |
|----------|-----------|-------------|---------------------|
| **foods.html** | `/admin/foods` | **Main food management page** | All fields, pagination, search |
| **add_food.html** | `/admin/foods/add` | **Add new food** | All input fields |
| **edit_food.html** | `/admin/foods/<id>/edit` | **Edit existing food** | All fields with pre-population |
| **bulk_upload.html** | `/admin/foods/upload` | **CSV bulk upload** | All fields from CSV |
| **bulk_upload_redesigned.html** | `/admin/foods/bulk-upload` | **Enhanced bulk upload** | Enhanced CSV processing |
| **food_uploads.html** | `/admin/food-uploads` | **Upload history** | Upload tracking |
| **export_foods.html** | `/admin/foods/export` | **Export foods to CSV** | All fields for export |

### **🎯 Admin Features:**

#### **A) Food Management (foods.html)**
- **Display**: ID, Name, Brand, Category, Calories, Protein, Status, Created Date
- **Actions**: Edit, Verify/Unverify, Delete
- **Filters**: Search, Category, Status, Brand
- **Sorting**: All columns sortable
- **Pagination**: Configurable page sizes

#### **B) Add Food (add_food.html)**
- **Required**: Name, Category, Calories, Protein, Carbs, Fat
- **Optional**: Brand, Fiber, Sugar, Sodium, Serving Size, Description
- **Validation**: Data ranges, required fields
- **Security**: XSS protection, input sanitization

#### **C) Edit Food (edit_food.html)**
- **All Fields**: Editable with current values
- **Verification**: Admin can toggle is_verified status
- **Validation**: Same as add form
- **Audit**: Change tracking logged

#### **D) Bulk Upload (bulk_upload*.html)**
- **CSV Format**: Supports all food fields
- **Templates**: Downloadable CSV templates
- **Validation**: Row-by-row processing
- **Progress**: Real-time upload progress
- **Error Handling**: Detailed error reporting

#### **E) Export (export_foods.html)**
- **Format**: CSV with all fields
- **Filters**: Same filters as main page
- **Async**: Background processing for large datasets

### **📊 Admin Dashboard Integration:**
- **Statistics**: Total foods, verified foods count
- **Recent Items**: Last 5 added foods
- **Quick Actions**: Links to manage foods

---

## **👤 4. USER DASHBOARD USAGE**

### **📂 User Files & Routes:**

| **File** | **Route** | **Purpose** | **Food Fields Used** |
|----------|-----------|-------------|---------------------|
| **log_meal.html** | `/dashboard/log-meal` | **Log meals** | Name, brand, nutrition per 100g |
| **search_foods.html** | `/dashboard/search-foods` | **Search food database** | Name, brand, category, nutrition |
| **index.html** | `/dashboard/` | **Recent meals display** | Name, brand, image_url |
| **history.html** | `/dashboard/history` | **Meal history** | Name, brand, nutrition calculated |
| **reports.html** | `/dashboard/reports` | **Nutrition reports** | Top foods, nutrition totals |

### **🎯 User Features:**

#### **A) Meal Logging (log_meal.html)**
- **Search**: Only verified foods (`is_verified=True`)
- **Display**: Name, brand, calories, protein, carbs, fat per 100g
- **Selection**: Click to select food for logging
- **Units**: Grams or serving sizes
- **Real-time**: Nutrition preview based on quantity

#### **B) Food Search (search_foods.html)**
- **Filters**: Name, category, verified status
- **Display**: Name, brand, category, basic nutrition
- **Results**: Paginated search results
- **Details**: Expandable nutrition information

#### **C) Dashboard Overview (index.html)**
- **Recent Meals**: Last logged foods with images
- **Display**: Food name, brand (if available)
- **Visual**: Food images when available
- **Quick Actions**: Links to log more meals

#### **D) History & Reports (history.html, reports.html)**
- **History**: Complete meal log with food details
- **Top Foods**: Most frequently consumed items
- **Nutrition**: Calculated totals from food nutrition data
- **Trends**: Daily/weekly/monthly consumption patterns

---

## **🔌 5. API ENDPOINTS**

### **📂 File: `app/api/routes.py`**

| **Endpoint** | **Method** | **Purpose** | **Food Fields** |
|--------------|------------|-------------|-----------------|
| `/api/foods/search` | GET | **General food search** | All fields |
| `/api/foods/search-verified` | GET | **Verified foods only** | All fields (verified=True) |
| `/api/foods/<id>/debug` | GET | **Food debugging** | Full food details |
| `/api/admin/foods` | POST | **Add food (admin)** | All fields |
| `/api/admin/foods/<id>` | PUT/DELETE | **Update/Delete food** | All fields |
| `/api/admin/foods/<id>/toggle-status` | POST | **Toggle verification** | is_verified field |

### **🔄 API Response Format:**
```json
{
  "id": 1,
  "name": "Basmati Rice (cooked)",
  "brand": null,
  "category": "grains",
  "calories": 121,
  "protein": 2.9,
  "carbs": 25.0,
  "fat": 0.4,
  "fiber": 0.6,
  "sugar": 0.0,
  "sodium": 1.0,
  "is_verified": true,
  "serving_size": 100,
  "description": "Cooked basmati rice..."
}
```

---

## **🔐 6. SECURITY & VALIDATION**

### **🛡️ Admin Security:**
- **Input Sanitization**: XSS protection, dangerous character removal
- **Validation Ranges**: Calories (0-1000), Protein (0-100), etc.
- **Duplicate Prevention**: Name + brand uniqueness checks
- **Audit Logging**: All changes tracked with user ID and timestamp
- **Transaction Safety**: Database rollback on errors

### **✅ Validation Rules:**
- **Required**: Name, Category, Calories, Protein, Carbs, Fat
- **Optional**: Brand, Fiber, Sugar, Sodium, Description, Serving Size
- **Ranges**: Nutritional values within realistic bounds
- **Text Limits**: Name (100 chars), Brand (50 chars), Category (50 chars)

### **🔒 User Restrictions:**
- **Read-Only**: Users can only view and search foods
- **Verified Only**: Meal logging restricted to verified foods
- **No Modification**: Users cannot add/edit/delete foods

---

## **📈 7. RELATED MODELS**

### **A) FoodNutrition (Extended Nutrition)**
- **Purpose**: Detailed micronutrient information
- **Fields**: Calcium, Iron, Vitamin C, Vitamin D per base unit
- **Usage**: Future enhancement for detailed nutrition tracking

### **B) FoodServing (Serving Sizes)**
- **Purpose**: Standard serving size definitions
- **Fields**: Serving name, unit, quantity in grams
- **Usage**: UOM support for meal logging

### **C) MealLog (Food Consumption)**
- **Purpose**: User meal entries
- **Relationship**: Many-to-One with Food
- **Fields**: Quantity, unit type, calculated nutrition
- **Usage**: Tracking what users eat

---

## **🎨 8. UI/UX PATTERNS**

### **📱 Bootstrap Components:**
- **Tables**: Responsive food listings with sorting
- **Forms**: Multi-column layouts for nutrition fields
- **Modals**: Add/edit food pop-ups
- **Cards**: Food display cards with images
- **Badges**: Category and verification status indicators
- **Pagination**: Navigation for large food lists

### **🔍 Search Patterns:**
- **Real-time**: AJAX search with live results
- **Filters**: Multiple filter combinations
- **Typeahead**: Auto-complete food name suggestions
- **Results**: Preview with basic nutrition info

### **📊 Data Display:**
- **Nutrition Cards**: Color-coded macronutrient display
- **Progress Bars**: Visual nutrition goal tracking
- **Charts**: Food consumption trends
- **Images**: Food photos when available

---

## **💾 9. DATABASE RELATIONSHIPS**

```
Food (1) ←→ (Many) MealLog
Food (1) ←→ (Many) FoodServing  
Food (1) ←→ (Many) FoodNutrition
User (1) ←→ (Many) Food (created_by)
```

### **🔗 Cascading Deletes:**
- **MealLog**: Protected (prevent food deletion if meals exist)
- **FoodServing**: Cascade (delete servings with food)
- **FoodNutrition**: Cascade (delete nutrition data with food)

---

## **🚀 10. IMPLEMENTATION DETAILS**

### **📋 Form Definitions (app/admin/forms.py):**

```python
class FoodForm(FlaskForm):
    """Form for adding/editing food items."""
    name = StringField('Food Name', validators=[
        DataRequired(), 
        Length(min=2, max=100)
    ])
    brand = StringField('Brand', validators=[
        Optional(), 
        Length(max=50)
    ])
    category = SelectField('Category', choices=[
        ('', 'Select Category'),
        ('grains', 'Grains & Cereals'),
        ('vegetables', 'Vegetables'),
        # ... more categories
    ], validators=[DataRequired()])
    
    # Nutritional information per 100g
    calories = FloatField('Calories (per 100g)', validators=[
        DataRequired(), 
        NumberRange(min=0, max=1000)
    ])
    protein = FloatField('Protein (g per 100g)', validators=[
        DataRequired(), 
        NumberRange(min=0, max=100)
    ])
    # ... more nutrition fields
    
    is_verified = BooleanField('Verified Food Item', default=True)
    submit = SubmitField('Save Food Item')
```

### **🗂️ Admin Route Structure (app/admin/routes.py):**

```python
@bp.route('/foods')
@login_required
@admin_required
def foods():
    """Main food management page with filtering and pagination."""
    # Implements search, category filter, status filter
    # Supports sorting by all columns
    # Paginated results with configurable page size

@bp.route('/foods/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_food():
    """Add new food item with validation."""
    # Form validation and security checks
    # Duplicate prevention
    # Audit logging

@bp.route('/foods/<int:food_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_food(food_id):
    """Edit existing food with comprehensive security."""
    # Enhanced validation and sanitization
    # Change tracking for audit
    # Transaction safety
```

### **🔍 User Dashboard Integration (app/dashboard/routes.py):**

```python
@bp.route('/log-meal', methods=['GET', 'POST'])
@login_required
def log_meal():
    """Meal logging with verified foods only."""
    # Only shows verified foods (is_verified=True)
    # UOM support (grams, servings)
    # Real-time nutrition calculation

def serialize_food_for_js(food: Food) -> dict:
    """Serialize food data for JavaScript consumption."""
    return {
        "id": food.id,
        "name": food.name,
        "brand": food.brand,
        "calories_per_100g": food.calories or 0,
        "protein_per_100g": food.protein or 0,
        "carbs_per_100g": food.carbs or 0,
        "fat_per_100g": food.fat or 0,
        # ... more fields
    }
```

### **🌐 API Implementation (app/api/routes.py):**

```python
@bp.route('/foods/search-verified')
def search_verified_foods():
    """API endpoint for searching only verified foods."""
    query = request.args.get('q', '').strip()
    
    verified_foods = Food.query.filter(
        Food.is_verified == True,
        Food.name.ilike(f'%{query}%')
    ).limit(20).all()
    
    return jsonify([{
        'id': f.id,
        'name': f.name,
        'brand': f.brand,
        'calories': f.calories,
        'protein': f.protein,
        'carbs': f.carbs,
        'fat': f.fat
    } for f in verified_foods])
```

---

## **🎯 11. BUSINESS LOGIC**

### **📊 Nutrition Calculations:**
- **Per 100g Basis**: All nutrition stored per 100g for consistency
- **Serving Conversion**: Real-time calculation based on user input
- **Precision**: Float values for accurate calculations
- **Validation**: Realistic ranges prevent data entry errors

### **🔐 Verification Workflow:**
1. **Admin Creates/Imports**: Foods start as unverified
2. **Review Process**: Admin reviews nutrition accuracy
3. **Verification**: Admin marks as verified (is_verified=True)
4. **User Access**: Only verified foods appear in meal logging
5. **Quality Control**: Prevents inaccurate data from reaching users

### **📈 Data Integrity:**
- **Duplicate Prevention**: Name + brand combination checks
- **Referential Integrity**: Foreign key constraints
- **Audit Trail**: All changes logged with timestamps
- **Backup Safety**: Export functionality for data preservation

---

## **🛠️ 12. MAINTENANCE & MONITORING**

### **📊 Admin Dashboard Metrics:**
- **Total Foods**: Count of all food items
- **Verified Foods**: Count of admin-approved items
- **Recent Additions**: Last 5 foods added
- **Category Distribution**: Foods per category breakdown

### **🔧 Bulk Operations:**
- **CSV Import**: Batch food creation with validation
- **CSV Export**: Complete database export
- **Bulk Verification**: Mass approval workflows
- **Data Cleanup**: Remove duplicates and invalid entries

### **📱 Performance Optimization:**
- **Database Indexing**: name and category fields indexed
- **Pagination**: Large datasets split across pages
- **Caching**: API responses cached where appropriate
- **Lazy Loading**: Related data loaded on demand

---

## **🔮 13. FUTURE ENHANCEMENTS**

### **🌟 Planned Features:**
- **Image Upload**: Food photography with storage
- **Barcode Integration**: UPC/EAN code scanning
- **Nutrition API**: Integration with USDA database
- **User Contributions**: Community-driven food database
- **Multi-language**: Internationalization support

### **📊 Advanced Analytics:**
- **Popular Foods**: Most searched/logged items
- **Nutrition Trends**: Category consumption patterns
- **Data Quality**: Verification rate metrics
- **User Behavior**: Search and logging analytics

---

## **📚 14. DEVELOPER RESOURCES**

### **🔧 Database Schema:**
```sql
-- Food table structure
CREATE TABLE food (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    brand VARCHAR(50),
    category VARCHAR(50) NOT NULL,
    calories FLOAT NOT NULL DEFAULT 0,
    protein FLOAT NOT NULL DEFAULT 0,
    carbs FLOAT NOT NULL DEFAULT 0,
    fat FLOAT NOT NULL DEFAULT 0,
    fiber FLOAT DEFAULT 0,
    sugar FLOAT DEFAULT 0,
    sodium FLOAT DEFAULT 0,
    description TEXT,
    serving_size FLOAT DEFAULT 100,
    default_serving_size_grams FLOAT DEFAULT 100.0,
    is_verified BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    FOREIGN KEY (created_by) REFERENCES user (id)
);

-- Indexes for performance
CREATE INDEX ix_food_name ON food (name);
CREATE INDEX ix_food_category ON food (category);
```

### **🧪 Testing Coverage:**
- **Unit Tests**: Model validation and methods
- **Integration Tests**: API endpoint functionality
- **UI Tests**: Form submission and validation
- **Security Tests**: Input sanitization and XSS prevention

### **📖 API Documentation:**
- **OpenAPI Specification**: Complete API documentation
- **Rate Limiting**: API usage quotas
- **Authentication**: Token-based API access
- **Versioning**: API version management

---

## **📞 15. SUPPORT & TROUBLESHOOTING**

### **🐛 Common Issues:**
1. **Save Errors**: Check validation rules and data ranges
2. **Search Problems**: Verify database indexes
3. **Permission Errors**: Confirm admin role assignments
4. **Upload Failures**: Validate CSV format and file size

### **🔍 Debugging Tools:**
- **Admin Debug**: Food detail debug endpoint
- **Logging**: Comprehensive application logs
- **Validation**: Real-time form error display
- **Database**: SQL query logging for troubleshooting

### **📧 Contact Information:**
- **Technical Issues**: Check application logs first
- **Data Problems**: Use admin food management tools
- **Feature Requests**: Document in project requirements
- **Security Concerns**: Report through proper channels

---

**Last Updated**: August 13, 2025  
**Version**: 1.0  
**Maintainer**: Nutri Tracker Development Team
