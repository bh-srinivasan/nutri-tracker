# Nutrition Calculation Service Documentation

## Overview

The `app.services.nutrition` module provides pure functions for calculating nutrition values without database dependencies or side effects. This enables unit testing and separation of business logic from data access.

## Module: `app/services/nutrition.py`

### Primary Function: `compute_nutrition()`

```python
def compute_nutrition(
    food, 
    *, 
    grams: Optional[float] = None, 
    serving=None, 
    quantity: Optional[float] = None
) -> Dict[str, float]
```

#### Purpose
Calculates nutrition values for a food based on either direct grams or serving size, using the food's per-100g nutrition data.

#### Parameters
- **`food`**: Food object with per-100g nutrition values (calories, protein, carbs, fat, fiber, sugar, sodium)
- **`grams`** *(Optional[float])*: Direct grams amount to calculate for (takes precedence over serving)
- **`serving`** *(Optional)*: FoodServing object with `grams_per_unit` attribute
- **`quantity`** *(Optional[float])*: Quantity multiplier for the serving (required if serving provided)

#### Return Value
Dictionary with calculated nutrition values:
```python
{
    'calories': float,
    'protein': float,
    'carbs': float,
    'fat': float,
    'fiber': float,
    'sugar': float,
    'sodium': float
}
```

#### Usage Examples

##### Direct Grams Calculation
```python
from app.services.nutrition import compute_nutrition

# Calculate nutrition for 150g of food
nutrition = compute_nutrition(food, grams=150.0)
print(f"Calories: {nutrition['calories']}")
```

##### Serving-Based Calculation
```python
# Calculate nutrition for 2 servings
nutrition = compute_nutrition(food, serving=serving_obj, quantity=2.0)
```

##### Fractional Serving
```python
# Calculate nutrition for half a serving
nutrition = compute_nutrition(food, serving=serving_obj, quantity=0.5)
```

## Features

### ✅ Pure Function
- No side effects or database operations
- Deterministic output for given inputs
- Unit-testable without external dependencies

### ✅ Robust Error Handling
- Validates input parameters
- Handles missing nutrition fields (defaults to 0)
- Provides clear error messages for invalid inputs

### ✅ Flexible Input Methods
- Direct grams specification
- Serving-based calculations with quantity multipliers
- Grams parameter takes precedence when both provided

### ✅ Comprehensive Validation
- Non-negative values required for grams and quantity
- Proper serving object validation
- Clear error messages for missing required parameters

## Validation Rules

### Input Validation
1. **Either `grams` OR (`serving` + `quantity`) must be provided**
2. **`grams` must be non-negative** (≥ 0)
3. **`quantity` must be non-negative** (≥ 0)  
4. **`serving` must have `grams_per_unit` attribute**
5. **If `serving` provided, `quantity` is required**

### Data Handling
1. **Missing nutrition fields default to 0**
2. **None nutrition values default to 0**
3. **Per-100g nutrition values are multiplied by (grams/100) factor**

## Error Cases

### ValueError Exceptions
```python
# Negative grams
compute_nutrition(food, grams=-10.0)
# ValueError: grams must be non-negative

# Negative quantity
compute_nutrition(food, serving=serving, quantity=-1.0)
# ValueError: quantity must be non-negative

# Serving without quantity
compute_nutrition(food, serving=serving)
# ValueError: quantity must be provided when serving is specified

# No calculation parameters
compute_nutrition(food)
# ValueError: Either grams or (serving + quantity) must be provided

# Invalid serving object
compute_nutrition(food, serving=invalid_obj, quantity=1.0)
# ValueError: serving must have grams_per_unit attribute
```

## Helper Function: `validate_nutrition_inputs()`

```python
def validate_nutrition_inputs(
    grams: Optional[float] = None,
    serving=None,
    quantity: Optional[float] = None
) -> float
```

Validates nutrition calculation inputs and returns the effective grams amount. Useful for testing and validation without performing the full calculation.

## Real-World Example

```python
# Using with actual Food and FoodServing models
from app.models import Food, FoodServing
from app.services.nutrition import compute_nutrition

# Get food and serving from database
food = Food.query.get(93)  # Idli small
serving = FoodServing.query.filter_by(food_id=93).first()

# Calculate nutrition for 1.5 servings
nutrition = compute_nutrition(food, serving=serving, quantity=1.5)

# Results for 1.5 × 100g = 150g of Idli small:
# {
#     'calories': 87.0,   # 58 * 1.5
#     'protein': 2.4,     # 1.6 * 1.5  
#     'carbs': 18.0,      # 12.0 * 1.5
#     'fat': 0.6,         # 0.4 * 1.5
#     'fiber': 0.8,       # 0.5 * 1.5
#     'sugar': 0.3,       # 0.2 * 1.5 (Note: None values default to 0)
#     'sodium': 150.0     # 100.0 * 1.5
# }
```

## Testing

### Unit Test Coverage
- ✅ Direct grams calculations
- ✅ Serving-based calculations  
- ✅ Fractional quantities
- ✅ Zero amounts
- ✅ Missing nutrition fields
- ✅ None nutrition values
- ✅ Parameter precedence (grams over serving)
- ✅ All validation error cases
- ✅ Edge cases and boundary conditions

### Test Files
- `test_nutrition_service.py` - Complete unit test suite
- `demo_nutrition_service.py` - Real-world usage demonstration

## Integration

### Usage in Controllers/Routes
```python
from app.services.nutrition import compute_nutrition

@bp.route('/meal_log', methods=['POST'])
def log_meal():
    # Get form data
    food = Food.query.get(form.food_id.data)
    
    if form.unit_type.data == 'grams':
        nutrition = compute_nutrition(food, grams=form.quantity.data)
    else:
        serving = FoodServing.query.get(form.serving_id.data)
        nutrition = compute_nutrition(food, serving=serving, quantity=form.quantity.data)
    
    # Use nutrition values for meal log...
```

### Benefits for Application
1. **Consistent calculations** across all parts of the application
2. **Easy testing** without database setup
3. **Clear separation** of business logic from data access
4. **Reusable** across different contexts (API, forms, background jobs)
5. **Maintainable** with single source of truth for nutrition calculations

## Acceptance Criteria Met

✅ **Pure function** - No database writes or side effects  
✅ **Unit-testable** - Complete test suite without DB dependencies  
✅ **Flexible inputs** - Supports both grams and serving-based calculations  
✅ **Robust handling** - Missing fields default to 0, comprehensive validation  
✅ **Clear API** - Keyword-only parameters, descriptive function signature
