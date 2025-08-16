"""Nutrition calculation services.

This module provides pure functions for calculating nutrition values
without database dependencies or side effects.
"""

from typing import Dict, Optional, Union


def compute_nutrition(
    food, 
    *, 
    grams: Optional[float] = None, 
    serving=None, 
    quantity: Optional[float] = None
) -> Dict[str, float]:
    """
    Compute nutrition values for a food based on grams or serving size.
    
    This is a pure function that calculates nutrition values from a food's
    per-100g nutrition data without any side effects or database operations.
    
    Args:
        food: Food object with per-100g nutrition values (calories, protein, etc.)
        grams: Direct grams amount to calculate for (takes precedence)
        serving: FoodServing object with grams_per_unit attribute
        quantity: Quantity multiplier for the serving (required if serving provided)
        
    Returns:
        Dict with calculated nutrition values:
        {
            'calories': float,
            'protein': float,
            'carbs': float,
            'fat': float,
            'fiber': float,
            'sugar': float,
            'sodium': float
        }
        
    Raises:
        ValueError: If neither grams nor (serving + quantity) provided
        ValueError: If serving provided without quantity
        ValueError: If grams is negative
        ValueError: If quantity is negative when serving provided
        
    Examples:
        >>> # Direct grams calculation
        >>> nutrition = compute_nutrition(food, grams=150.0)
        
        >>> # Serving-based calculation
        >>> nutrition = compute_nutrition(food, serving=serving_obj, quantity=2.0)
    """
    # Validate input parameters
    if grams is not None:
        if grams < 0:
            raise ValueError("grams must be non-negative")
        effective_grams = grams
    elif serving is not None and quantity is not None:
        if quantity < 0:
            raise ValueError("quantity must be non-negative")
        if not hasattr(serving, 'grams_per_unit'):
            raise ValueError("serving must have grams_per_unit attribute")
        effective_grams = quantity * serving.grams_per_unit
    elif serving is not None and quantity is None:
        raise ValueError("quantity must be provided when serving is specified")
    else:
        raise ValueError("Either grams or (serving + quantity) must be provided")
    
    # Calculate multiplier based on per-100g nutrition values
    multiplier = effective_grams / 100.0
    
    # Extract nutrition values from food, defaulting to 0 for missing fields
    nutrition_fields = ['calories', 'protein', 'carbs', 'fat', 'fiber', 'sugar', 'sodium']
    result = {}
    
    for field in nutrition_fields:
        # Get the value from food object, default to 0 if None or missing
        try:
            raw_value = getattr(food, field, None)
            per_100g_value = raw_value if raw_value is not None else 0.0
        except AttributeError:
            per_100g_value = 0.0
        result[field] = per_100g_value * multiplier
    
    return result


def validate_nutrition_inputs(
    grams: Optional[float] = None,
    serving=None,
    quantity: Optional[float] = None
) -> float:
    """
    Validate nutrition calculation inputs and return effective grams.
    
    Helper function to validate inputs for nutrition calculations.
    Useful for testing and validation without performing the full calculation.
    
    Args:
        grams: Direct grams amount
        serving: FoodServing object
        quantity: Quantity multiplier for serving
        
    Returns:
        float: The effective grams amount that would be used for calculation
        
    Raises:
        ValueError: For invalid input combinations or values
    """
    if grams is not None:
        if grams < 0:
            raise ValueError("grams must be non-negative")
        return grams
    elif serving is not None and quantity is not None:
        if quantity < 0:
            raise ValueError("quantity must be non-negative")
        if not hasattr(serving, 'grams_per_unit'):
            raise ValueError("serving must have grams_per_unit attribute")
        return quantity * serving.grams_per_unit
    elif serving is not None and quantity is None:
        raise ValueError("quantity must be provided when serving is specified")
    else:
        raise ValueError("Either grams or (serving + quantity) must be provided")
