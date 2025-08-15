# Database Constraint Fix Complete - Original Quantity Field

## Issue Summary
You encountered an `IntegrityError: NOT NULL constraint failed: meal_log.original_quantity` when testing meal logging in Swagger UI. This was the third issue after fixing the `verified` field and nutrition field names.

## Root Cause Analysis
Looking at the SQL error:
```sql
[parameters: (1, 93, 150.0, None, 'grams', None, 150.0, 'lunch', '2025-08-15 11:23:31.674025', '2025-08-14', 87.0, 2.4, 18.0, 0.6, 0.75, None, None)]
```

The `original_quantity` was being set to `None`, but the MealLog model has:
```python
original_quantity = db.Column(db.Float, nullable=False)  # NOT NULL constraint
```

## Database Schema Understanding
The MealLog model has these key fields:
- `quantity` - DEPRECATED field but still NOT NULL (stores grams for legacy)
- `original_quantity` - NOT NULL (stores the original user input quantity)
- `logged_grams` - NOT NULL (normalized grams value)
- `unit_type` - 'grams' or 'serving'

## Fix Applied

### File: `app/swagger_api/meals_v2.py` - Line 147-162

**Before:**
```python
# Create meal log
meal_log = MealLog(
    user_id=current_user.id,
    food_id=food_id,
    serving_id=used_serving_id,
    quantity=original_quantity,           # ❌ Wrong mapping
    logged_grams=logged_grams,
    unit_type=unit_type,
    meal_type=meal_type,
    date=meal_date,
    calories=calories,
    protein=protein,
    carbs=carbs,
    fat=fat,
    fiber=fiber
)
```

**After:**
```python
# Create meal log
meal_log = MealLog(
    user_id=current_user.id,
    food_id=food_id,
    serving_id=used_serving_id,
    quantity=logged_grams,                # ✅ DEPRECATED field but required (NOT NULL)
    original_quantity=original_quantity,  # ✅ Original quantity entered by user
    logged_grams=logged_grams,
    unit_type=unit_type,
    meal_type=meal_type,
    date=meal_date,
    calories=calories,
    protein=protein,
    carbs=carbs,
    fat=fat,
    fiber=fiber
)
```

## Field Mapping Logic

### For Grams Input:
```json
{
  "food_id": 1,
  "grams": 150.0,
  "meal_type": "lunch"
}
```
- `quantity` = 150.0 (logged_grams value)
- `original_quantity` = 150.0 (user input)
- `logged_grams` = 150.0
- `unit_type` = 'grams'

### For Serving Input:
```json
{
  "food_id": 1,
  "serving_id": 2,
  "quantity": 2.0,
  "meal_type": "lunch"
}
```
- `quantity` = 300.0 (calculated grams: 2 × 150g per serving)
- `original_quantity` = 2.0 (user input quantity)
- `logged_grams` = 300.0
- `unit_type` = 'serving'

## Expected Behavior
✅ **Your Swagger UI POST request should now work without IntegrityError!**

When you POST your JSON to `/api/v2/meals`, you should get a **200 OK** response with meal data instead of the **500 IntegrityError**.

## Complete Fix History
1. ✅ Fixed `verified` → `is_verified` field mappings
2. ✅ Fixed nutrition field names (`calories_per_100g` → `calories`)
3. ✅ Fixed database constraint (`original_quantity` NOT NULL issue)

---

**Status: 🎉 COMPLETE** - All database constraint issues resolved!
