# Edit Meal Background Process Documentation

## Overview
This document provides a detailed technical analysis of what happens when a user clicks the "Edit" button on a meal from today's dashboard in the Nutri Tracker application.

## Complete Edit Meal Flow

### 1. Frontend: Edit Button Click Event
**Location**: `app/templates/dashboard/index.html` (lines 195-220)
```html
<button type="button" class="btn btn-sm btn-outline-primary edit-meal-btn" 
        data-meal-id="{{ meal.id }}" title="Edit this meal">
    <i class="fas fa-edit"></i>
</button>
```

**Key Details**:
- Button has class `edit-meal-btn` for JavaScript targeting
- `data-meal-id` attribute contains the meal ID for processing
- Uses Font Awesome edit icon for visual clarity

### 2. JavaScript Event Delegation
**Location**: `app/static/js/main.js` (lines 500-515)
```javascript
// Event delegation for edit meal buttons
$(document).on('click', '.edit-meal-btn', function(e) {
    e.preventDefault();
    const mealId = $(this).data('meal-id');
    console.log('[Dashboard] Edit meal clicked:', mealId);
    
    if (mealId && window.NutriTracker && window.NutriTracker.dashboard) {
        window.NutriTracker.dashboard.editMeal(mealId);
    } else {
        console.error('[Dashboard] Cannot edit meal - missing dependencies');
    }
});
```

**Process**:
- Uses jQuery event delegation to handle dynamically loaded content
- Extracts meal ID from `data-meal-id` attribute
- Calls the `editMeal` function with the meal ID
- Includes error handling for missing dependencies

### 3. Edit Meal Function Execution
**Location**: `app/static/js/main.js` (lines 555-570)
```javascript
editMeal: function(mealId) {
    console.log('[Dashboard] Editing meal:', mealId);
    
    if (!mealId) {
        console.error('[Dashboard] No meal ID provided for editing');
        return;
    }
    
    // Redirect to log meal page with edit parameter
    const editUrl = `/dashboard/log-meal?edit=${mealId}`;
    console.log('[Dashboard] Redirecting to:', editUrl);
    window.location.href = editUrl;
}
```

**Process**:
- Validates that meal ID is provided
- Constructs edit URL with query parameter: `/dashboard/log-meal?edit={mealId}`
- Performs browser redirect to the log meal page
- Includes comprehensive logging for debugging

### 4. Backend Route Processing
**Location**: `app/dashboard/routes.py` (lines 110-140)
```python
@dashboard_bp.route('/log-meal', methods=['GET', 'POST'])
@login_required
def log_meal():
    """Log a new meal or edit existing meal"""
    form = MealLogForm()
    
    # Check if this is an edit request
    edit_meal_id = request.args.get('edit')
    selected_food = None
    
    if edit_meal_id:
        # Load existing meal for editing
        meal = MealLog.query.filter_by(
            id=edit_meal_id,
            user_id=current_user.id
        ).first()
        
        if meal:
            # Pre-populate form with existing meal data
            form.food_id.data = meal.food_id
            form.quantity.data = meal.original_quantity  # Key: uses original_quantity
            form.meal_type.data = meal.meal_type
            form.date.data = meal.date
            form.unit_type.data = meal.unit_type
            form.serving_id.data = meal.serving_id
            
            # Prepare food data for JavaScript
            selected_food = serialize_food_for_js(meal.food)
```

**Security & Validation**:
- Validates user ownership with `user_id=current_user.id` filter
- Uses `@login_required` decorator for authentication
- Returns 404 if meal not found or doesn't belong to user

### 5. Food Data Serialization
**Location**: `app/dashboard/routes.py` (lines 180-210)
```python
def serialize_food_for_js(food):
    """Serialize food data for JavaScript consumption"""
    return {
        'id': food.id,
        'name': food.name,
        'brand': food.brand,
        'description': food.description,
        'image_url': food.image_url,
        'category': food.category,
        'calories_per_100g': food.calories_per_100g,
        'protein_per_100g': food.protein_per_100g,
        'carbs_per_100g': food.carbs_per_100g,
        'fat_per_100g': food.fat_per_100g,
        'default_serving_size_grams': food.default_serving_size_grams,
        'is_verified': food.is_verified,
        'created_by': food.created_by
    }
```

**Purpose**:
- Converts SQLAlchemy model to JSON-serializable dictionary
- Includes all necessary nutritional and metadata information
- Used for JavaScript pre-population of form fields

### 6. Template Rendering with Pre-selected Data
**Location**: `app/templates/dashboard/log_meal.html` (lines 290-310)
```html
<!-- Pre-fill data using JSON -->
{% if selected_food %}
  <script id="preselected-food-data" type="application/json">
    {{ selected_food | tojson }}
  </script>
{% endif %}

{% if form.meal_type.data %}
  <script id="preselected-meal-type" type="application/json">
    {{ form.meal_type.data | tojson }}
  </script>
{% endif %}

{% if form.quantity.data %}
  <script id="preselected-quantity" type="application/json">
    {{ form.quantity.data|tojson }}
  </script>
{% endif %}
```

**Process**:
- Embeds JSON data directly in HTML using Jinja2 `tojson` filter
- Creates script tags with specific IDs for JavaScript access
- Safely serializes Python data to JSON format
- Includes food data, meal type, and **original quantity**

### 7. Client-Side Form Pre-population
**Location**: `app/templates/dashboard/log_meal.html` (Enhanced MealLogger class)
```javascript
handlePreselectedData() {
    const preselectedFoodData = document.getElementById('preselected-food-data');
    if (preselectedFoodData) {
        try {
            const foodData = JSON.parse(preselectedFoodData.textContent);
            this.selectFood(foodData.id);
        } catch (e) {
            console.error('[MealLogger] Error parsing preselected food data:', e);
        }
    }

    const preselectedMealType = document.getElementById('preselected-meal-type');
    if (preselectedMealType) {
        try {
            const mealType = JSON.parse(preselectedMealType.textContent);
            const mealTypeSelect = document.getElementById('meal_type');
            if (mealTypeSelect) {
                mealTypeSelect.value = mealType;
            }
        } catch (e) {
            console.error('[MealLogger] Error parsing preselected meal type:', e);
        }
    }
}
```

### 8. Quantity Pre-fill Implementation
**Location**: `app/static/js/main.js` (NutriTracker system)
```javascript
// Check for preselected quantity and apply it
const preselectedQuantityScript = document.getElementById('preselected-quantity');
if (preselectedQuantityScript) {
    try {
        const preselectedQuantity = JSON.parse(preselectedQuantityScript.textContent);
        
        // Try multiple selectors for quantity input (resilient approach)
        const quantityInput = document.getElementById('quantity') || 
                            document.getElementById('quantityInput') ||
                            document.querySelector('input[name="quantity"]');
                            
        if (quantityInput && preselectedQuantity) {
            quantityInput.value = preselectedQuantity;
            console.log('[NutriTracker] Set preselected quantity:', preselectedQuantity);
            
            // Trigger input event to update nutrition preview
            quantityInput.dispatchEvent(new Event('input', { bubbles: true }));
        }
    } catch (error) {
        console.error('[NutriTracker] Error setting preselected quantity:', error);
    }
}
```

**Key Features**:
- Uses resilient selector approach with multiple fallbacks
- Automatically triggers nutrition preview update
- Includes comprehensive error handling and logging
- Preserves original meal quantity instead of defaulting to 100g

### 9. Dual JavaScript Architecture
The application uses two JavaScript systems working together:

#### Enhanced MealLogger (Template-embedded)
- Handles food search and selection
- Manages serving size dropdowns
- Processes preselected food data
- Updates nutrition previews

#### NutriTracker System (main.js)
- Handles dashboard interactions
- Manages edit meal redirects
- Processes quantity pre-fill
- Provides global meal logging utilities

### 10. Final Form State
After all processing is complete:
- **Food**: Pre-selected and displayed with nutrition info
- **Quantity**: Shows original saved amount (e.g., 400g instead of default 100g)
- **Meal Type**: Pre-selected (breakfast, lunch, dinner, snack)
- **Date**: Set to original meal date
- **Unit Type**: Restored to original selection (grams/serving)
- **Serving ID**: Restored if meal used specific serving size

## Technical Architecture

### Database Schema
```sql
-- MealLog table structure
CREATE TABLE meal_log (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    food_id INTEGER NOT NULL,
    quantity DECIMAL(10,2) NOT NULL,           -- Display quantity
    original_quantity DECIMAL(10,2) NOT NULL,  -- Original entered quantity
    meal_type VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    unit_type VARCHAR(20),
    serving_id INTEGER,
    grams_equivalent DECIMAL(10,2) NOT NULL,
    calories DECIMAL(10,2) NOT NULL,
    protein DECIMAL(10,2) NOT NULL,
    -- Additional nutrition fields...
);
```

### Security Measures
1. **Authentication**: `@login_required` decorator
2. **Authorization**: User ownership validation (`user_id=current_user.id`)
3. **Input Sanitization**: Form validation and CSRF protection
4. **XSS Prevention**: Jinja2 auto-escaping and manual escaping in JavaScript

### Error Handling
1. **Missing Meal**: Returns 404 if meal not found
2. **Unauthorized Access**: Prevents editing other users' meals
3. **JavaScript Errors**: Try-catch blocks with logging
4. **Network Issues**: Graceful degradation with user feedback

## Recent Improvements

### Quantity Prefill Fix
**Problem**: Edit meal was defaulting to 100g instead of showing original quantity

**Solution Implemented**:
1. Updated template to use `id="quantity"` for consistency
2. Added preselected quantity JSON script injection
3. Enhanced JavaScript with resilient selectors
4. Backend now uses `meal.original_quantity` for form population

**Files Modified**:
- `app/templates/dashboard/log_meal.html`: ID alignment and JSON scripts
- `app/static/js/main.js`: Quantity prefill logic with fallback selectors
- `app/dashboard/routes.py`: Form pre-population using original_quantity field

## Performance Considerations

### Frontend Optimizations
- Event delegation prevents memory leaks
- Debounced search prevents excessive API calls
- Lazy loading of nutrition data
- Minimal DOM manipulations

### Backend Optimizations
- Single database query for meal data
- Efficient JSON serialization
- Proper indexing on meal_log table
- Query optimization with selective field loading

## Debugging Information

### Console Logging
The system includes comprehensive console logging:
```javascript
console.log('[Dashboard] Edit meal clicked:', mealId);
console.log('[Dashboard] Redirecting to:', editUrl);
console.log('[NutriTracker] Set preselected quantity:', preselectedQuantity);
console.log('[MealLogger] Preselected food data loaded');
```

### Debug Mode
Enable debug mode by adding `?debug=true` to URL for additional information and alerts.

---

*This documentation reflects the current state of the edit meal functionality as of the latest implementation. The system successfully preserves original meal quantities and provides a seamless editing experience.*
