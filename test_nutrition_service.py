"""Unit tests for nutrition calculation services.

These tests validate the pure nutrition calculation functions
without requiring database setup or external dependencies.
"""

import unittest
from unittest.mock import Mock
import sys
import os

# Add the app directory to Python path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.services.nutrition import compute_nutrition, validate_nutrition_inputs


class TestComputeNutrition(unittest.TestCase):
    """Test cases for the compute_nutrition function."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock food object with per-100g nutrition values
        self.mock_food = Mock()
        self.mock_food.calories = 200.0
        self.mock_food.protein = 10.0
        self.mock_food.carbs = 30.0
        self.mock_food.fat = 5.0
        self.mock_food.fiber = 8.0
        self.mock_food.sugar = 2.0
        self.mock_food.sodium = 100.0
        
        # Create a mock serving object
        self.mock_serving = Mock()
        self.mock_serving.grams_per_unit = 150.0
    
    def test_direct_grams_calculation(self):
        """Test nutrition calculation with direct grams input."""
        result = compute_nutrition(self.mock_food, grams=200.0)
        
        expected = {
            'calories': 400.0,  # 200 * 2.0
            'protein': 20.0,    # 10 * 2.0
            'carbs': 60.0,      # 30 * 2.0
            'fat': 10.0,        # 5 * 2.0
            'fiber': 16.0,      # 8 * 2.0
            'sugar': 4.0,       # 2 * 2.0
            'sodium': 200.0     # 100 * 2.0
        }
        
        self.assertEqual(result, expected)
    
    def test_serving_based_calculation(self):
        """Test nutrition calculation with serving and quantity."""
        result = compute_nutrition(
            self.mock_food, 
            serving=self.mock_serving, 
            quantity=2.0
        )
        
        # 2.0 * 150.0 = 300.0 grams, multiplier = 3.0
        expected = {
            'calories': 600.0,  # 200 * 3.0
            'protein': 30.0,    # 10 * 3.0
            'carbs': 90.0,      # 30 * 3.0
            'fat': 15.0,        # 5 * 3.0
            'fiber': 24.0,      # 8 * 3.0
            'sugar': 6.0,       # 2 * 3.0
            'sodium': 300.0     # 100 * 3.0
        }
        
        self.assertEqual(result, expected)
    
    def test_zero_grams(self):
        """Test calculation with zero grams."""
        result = compute_nutrition(self.mock_food, grams=0.0)
        
        expected = {
            'calories': 0.0,
            'protein': 0.0,
            'carbs': 0.0,
            'fat': 0.0,
            'fiber': 0.0,
            'sugar': 0.0,
            'sodium': 0.0
        }
        
        self.assertEqual(result, expected)
    
    def test_missing_nutrition_fields_default_to_zero(self):
        """Test that missing nutrition fields default to zero."""
        # Create food with some missing fields using spec to limit available attributes
        incomplete_food = Mock(spec=['calories', 'protein'])
        incomplete_food.calories = 100.0
        incomplete_food.protein = 5.0
        # carbs, fat, fiber, sugar, sodium are missing and will raise AttributeError
        
        result = compute_nutrition(incomplete_food, grams=100.0)
        
        expected = {
            'calories': 100.0,
            'protein': 5.0,
            'carbs': 0.0,      # Missing, should default to 0
            'fat': 0.0,        # Missing, should default to 0
            'fiber': 0.0,      # Missing, should default to 0
            'sugar': 0.0,      # Missing, should default to 0
            'sodium': 0.0      # Missing, should default to 0
        }
        
        self.assertEqual(result, expected)
    
    def test_none_nutrition_fields_default_to_zero(self):
        """Test that None nutrition fields default to zero."""
        # Create food with None values
        none_food = Mock()
        none_food.calories = None
        none_food.protein = 10.0
        none_food.carbs = None
        none_food.fat = 5.0
        none_food.fiber = None
        none_food.sugar = None
        none_food.sodium = None
        
        result = compute_nutrition(none_food, grams=200.0)
        
        expected = {
            'calories': 0.0,   # None -> 0
            'protein': 20.0,   # 10 * 2.0
            'carbs': 0.0,      # None -> 0
            'fat': 10.0,       # 5 * 2.0
            'fiber': 0.0,      # None -> 0
            'sugar': 0.0,      # None -> 0
            'sodium': 0.0      # None -> 0
        }
        
        self.assertEqual(result, expected)
    
    def test_fractional_quantity(self):
        """Test calculation with fractional serving quantity."""
        result = compute_nutrition(
            self.mock_food,
            serving=self.mock_serving,
            quantity=0.5
        )
        
        # 0.5 * 150.0 = 75.0 grams, multiplier = 0.75
        expected = {
            'calories': 150.0,  # 200 * 0.75
            'protein': 7.5,     # 10 * 0.75
            'carbs': 22.5,      # 30 * 0.75
            'fat': 3.75,        # 5 * 0.75
            'fiber': 6.0,       # 8 * 0.75
            'sugar': 1.5,       # 2 * 0.75
            'sodium': 75.0      # 100 * 0.75
        }
        
        self.assertEqual(result, expected)


class TestComputeNutritionValidation(unittest.TestCase):
    """Test validation logic for compute_nutrition function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_food = Mock()
        self.mock_food.calories = 100.0
        
        self.mock_serving = Mock()
        self.mock_serving.grams_per_unit = 100.0
    
    def test_grams_takes_precedence_over_serving(self):
        """Test that grams parameter takes precedence over serving."""
        # Create a simple mock food with just calories
        simple_food = Mock()
        simple_food.calories = 100.0
        simple_food.protein = None
        simple_food.carbs = None
        simple_food.fat = None
        simple_food.fiber = None
        simple_food.sugar = None
        simple_food.sodium = None
        
        result = compute_nutrition(
            simple_food,
            grams=50.0,
            serving=self.mock_serving,
            quantity=2.0
        )
        
        # Should use grams=50.0 (multiplier=0.5), not serving calculation
        expected_calories = 50.0  # 100 * 0.5
        self.assertEqual(result['calories'], expected_calories)
    
    def test_negative_grams_raises_error(self):
        """Test that negative grams raises ValueError."""
        with self.assertRaises(ValueError) as cm:
            compute_nutrition(self.mock_food, grams=-10.0)
        
        self.assertIn("grams must be non-negative", str(cm.exception))
    
    def test_negative_quantity_raises_error(self):
        """Test that negative quantity raises ValueError."""
        with self.assertRaises(ValueError) as cm:
            compute_nutrition(
                self.mock_food,
                serving=self.mock_serving,
                quantity=-1.0
            )
        
        self.assertIn("quantity must be non-negative", str(cm.exception))
    
    def test_serving_without_quantity_raises_error(self):
        """Test that serving without quantity raises ValueError."""
        with self.assertRaises(ValueError) as cm:
            compute_nutrition(self.mock_food, serving=self.mock_serving)
        
        self.assertIn("quantity must be provided when serving is specified", str(cm.exception))
    
    def test_no_parameters_raises_error(self):
        """Test that no calculation parameters raises ValueError."""
        with self.assertRaises(ValueError) as cm:
            compute_nutrition(self.mock_food)
        
        self.assertIn("Either grams or (serving + quantity) must be provided", str(cm.exception))
    
    def test_serving_without_grams_per_unit_raises_error(self):
        """Test that serving without grams_per_unit attribute raises ValueError."""
        invalid_serving = Mock(spec=[])  # Mock without grams_per_unit attribute
        
        with self.assertRaises(ValueError) as cm:
            compute_nutrition(
                self.mock_food,
                serving=invalid_serving,
                quantity=1.0
            )
        
        self.assertIn("serving must have grams_per_unit attribute", str(cm.exception))


class TestValidateNutritionInputs(unittest.TestCase):
    """Test cases for the validate_nutrition_inputs helper function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_serving = Mock()
        self.mock_serving.grams_per_unit = 200.0
    
    def test_validate_grams_input(self):
        """Test validation with grams input."""
        result = validate_nutrition_inputs(grams=150.0)
        self.assertEqual(result, 150.0)
    
    def test_validate_serving_input(self):
        """Test validation with serving and quantity."""
        result = validate_nutrition_inputs(
            serving=self.mock_serving,
            quantity=2.5
        )
        expected = 2.5 * 200.0  # 500.0
        self.assertEqual(result, expected)
    
    def test_validate_zero_inputs(self):
        """Test validation with zero values."""
        self.assertEqual(validate_nutrition_inputs(grams=0.0), 0.0)
        
        result = validate_nutrition_inputs(
            serving=self.mock_serving,
            quantity=0.0
        )
        self.assertEqual(result, 0.0)
    
    def test_validate_negative_grams_error(self):
        """Test validation error for negative grams."""
        with self.assertRaises(ValueError):
            validate_nutrition_inputs(grams=-5.0)
    
    def test_validate_negative_quantity_error(self):
        """Test validation error for negative quantity."""
        with self.assertRaises(ValueError):
            validate_nutrition_inputs(
                serving=self.mock_serving,
                quantity=-1.0
            )


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
