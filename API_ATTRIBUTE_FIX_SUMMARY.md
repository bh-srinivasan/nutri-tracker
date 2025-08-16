# API Attribute Mapping Fix Summary

## Issues Found and Fixed

### Problem
The API routes in `app/api/routes.py` were trying to access incorrect attribute names on the `FoodServing` model:

1. **Line 96**: `s.unit_type` → Should be `s.unit`
2. **Line 143**: `s.serving_unit` → Should be `s.unit` 
3. **Line 143**: `s.serving_quantity` → Should be `s.grams_per_unit`

### Root Cause
The `FoodServing` model has these actual attributes:
- `unit` (not `unit_type` or `serving_unit`)
- `grams_per_unit` (not `serving_quantity`)
- `serving_name` (correct)
- `id` (correct)

### Fixes Applied

#### 1. Debug endpoint fix (`/api/foods/<id>/debug`)
```python
# Before (line 96):
debug_info['servings'] = [s.unit_type for s in servings]

# After:
debug_info['servings'] = [s.unit for s in servings]
```

#### 2. Servings endpoint fix (`/api/foods/<id>/servings`)
```python
# Before (lines 142-147):
'servings': [{
    'id': s.id if s.id else None,
    'unit_type': s.serving_unit,
    'size_in_grams': s.serving_quantity,
    'description': s.serving_name
} for s in servings]

# After:
'servings': [{
    'id': s.id if s.id else None,
    'unit_type': s.unit,
    'size_in_grams': s.grams_per_unit,
    'description': s.serving_name
} for s in servings]
```

### Validation Results

#### Model Attributes (✅ Working):
- `FoodServing.unit` = "gram"
- `FoodServing.grams_per_unit` = 100.0
- `FoodServing.serving_name` = "100 g"

#### Expected API Response:
```json
{
  "id": 125,
  "unit_type": "gram",
  "size_in_grams": 100.0,
  "description": "100 g"
}
```

### Files Modified
- `app/api/routes.py` (2 fixes for attribute name mismatches)

### Status
✅ **RESOLVED** - API endpoints should now work correctly with the FoodServing model
