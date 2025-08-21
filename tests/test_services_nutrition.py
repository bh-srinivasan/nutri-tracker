"""
Tests for nutrition computation service.
Tests equivalence between grams and serving paths for compute_nutrition().
"""

import pytest

from app.services.nutrition import compute_nutrition


class MockFood:
    """Mock food object for testing."""
    def __init__(self, calories=100, protein=10, carbs=20, fat=5, fiber=2, sugar=1, sodium=50):
        self.calories = calories
        self.protein = protein
        self.carbs = carbs
        self.fat = fat
        self.fiber = fiber
        self.sugar = sugar
        self.sodium = sodium


class MockServing:
    """Mock serving object for testing."""
    def __init__(self, grams_per_unit):
        self.grams_per_unit = grams_per_unit


class TestNutritionServiceValidation:
    """Test suite for nutrition service input validation."""
    
    def test_negative_grams_raises_error(self):
        """Test that negative grams raises ValueError."""
        food = MockFood()
        
        with pytest.raises(ValueError, match="grams must be non-negative"):
            compute_nutrition(food, grams=-10.0)
    
    def test_negative_quantity_raises_error(self):
        """Test that negative quantity raises ValueError."""
        food = MockFood()
        serving = MockServing(100.0)
        
        with pytest.raises(ValueError, match="quantity must be non-negative"):
            compute_nutrition(food, serving=serving, quantity=-1.0)
    
    def test_serving_without_quantity_raises_error(self):
        """Test that providing serving without quantity raises ValueError."""
        food = MockFood()
        serving = MockServing(100.0)
        
        with pytest.raises(ValueError, match="quantity must be provided when serving is specified"):
            compute_nutrition(food, serving=serving)
    
    def test_no_parameters_raises_error(self):
        """Test that providing no calculation parameters raises ValueError."""
        food = MockFood()
        
        with pytest.raises(ValueError, match="Either grams or \\(serving \\+ quantity\\) must be provided"):
            compute_nutrition(food)
    
    def test_zero_grams_valid(self):
        """Test that zero grams is valid input."""
        food = MockFood()
        
        nutrition = compute_nutrition(food, grams=0.0)
        
        # All nutrition values should be zero
        assert nutrition['calories'] == 0.0
        assert nutrition['protein'] == 0.0
        assert nutrition['carbs'] == 0.0
        assert nutrition['fat'] == 0.0
    
    def test_zero_quantity_valid(self):
        """Test that zero quantity is valid input."""
        food = MockFood()
        serving = MockServing(100.0)
        
        nutrition = compute_nutrition(food, serving=serving, quantity=0.0)
        
        # All nutrition values should be zero
        assert nutrition['calories'] == 0.0
        assert nutrition['protein'] == 0.0
        assert nutrition['carbs'] == 0.0
        assert nutrition['fat'] == 0.0


class TestNutritionServiceEquivalence:
    """Test suite for nutrition computation equivalence between grams and serving paths."""
    
    def test_grams_serving_equivalence(self):
        """Test that equivalent grams and serving calculations produce same results."""
        food = MockFood(calories=200, protein=20, carbs=30, fat=5)
        serving = MockServing(195.0)  # 1 cup = 195g
        
        # Calculate nutrition using grams
        grams_nutrition = compute_nutrition(food, grams=195.0)
        
        # Calculate nutrition using serving
        serving_nutrition = compute_nutrition(food, serving=serving, quantity=1.0)
        
        # Results should be identical
        assert grams_nutrition['calories'] == serving_nutrition['calories']
        assert grams_nutrition['protein'] == serving_nutrition['protein']
        assert grams_nutrition['carbs'] == serving_nutrition['carbs']
        assert grams_nutrition['fat'] == serving_nutrition['fat']
    
    def test_partial_serving_calculation(self):
        """Test calculation with partial serving amounts."""
        food = MockFood(calories=200, protein=20, carbs=30, fat=5)
        serving = MockServing(200.0)  # 200g per serving
        
        # Test 0.5 servings (100g)
        nutrition = compute_nutrition(food, serving=serving, quantity=0.5)
        
        # Expected values for 100g (1.0 multiplier since food values are per 100g)
        # 0.5 servings * 200g/serving = 100g, which is 1.0x the base nutrition
        assert nutrition['calories'] == 200.0  # 200 * 1.0
        assert nutrition['protein'] == 20.0    # 20 * 1.0
        assert nutrition['carbs'] == 30.0      # 30 * 1.0
        assert nutrition['fat'] == 5.0         # 5 * 1.0
    
    def test_multiple_servings_calculation(self):
        """Test calculation with multiple serving amounts."""
        food = MockFood(calories=100, protein=10, carbs=15, fat=2)
        serving = MockServing(50.0)  # 50g per serving
        
        # Test 3 servings (150g)
        nutrition = compute_nutrition(food, serving=serving, quantity=3.0)
        
        # Expected values for 150g (3 * 50g) = 1.5 * 100g base
        multiplier = 1.5
        assert nutrition['calories'] == 100.0 * multiplier
        assert nutrition['protein'] == 10.0 * multiplier
        assert nutrition['carbs'] == 15.0 * multiplier
        assert nutrition['fat'] == 2.0 * multiplier
    
    def test_direct_grams_calculation(self):
        """Test direct grams calculation."""
        food = MockFood(calories=200, protein=15, carbs=25, fat=8)
        
        # Test 150g
        nutrition = compute_nutrition(food, grams=150.0)
        
        # Expected values for 150g (1.5 * 100g base)
        multiplier = 1.5
        assert nutrition['calories'] == 200.0 * multiplier
        assert nutrition['protein'] == 15.0 * multiplier
        assert nutrition['carbs'] == 25.0 * multiplier
        assert nutrition['fat'] == 8.0 * multiplier


class TestNutritionServiceEdgeCases:
    """Test suite for edge cases in nutrition computation."""
    
    def test_food_with_none_nutrition_values(self):
        """Test nutrition calculation when food has None values."""
        # Create food with some None nutrition values
        food = MockFood(calories=100.0, protein=None, carbs=20.0, fat=None)
        
        nutrition = compute_nutrition(food, grams=100.0)
        
        # None values should be treated as 0
        assert nutrition['calories'] == 100.0
        assert nutrition['protein'] == 0.0  # None -> 0
        assert nutrition['carbs'] == 20.0
        assert nutrition['fat'] == 0.0      # None -> 0
    
    def test_very_large_quantities(self):
        """Test nutrition calculation with very large quantities."""
        food = MockFood(calories=100, protein=10, carbs=15, fat=2)
        serving = MockServing(100.0)
        
        # Test with very large quantity
        large_quantity = 1000.0
        nutrition = compute_nutrition(food, serving=serving, quantity=large_quantity)
        
        # Should scale linearly
        expected_multiplier = large_quantity  # 1000 * 100g = 100,000g = 1000x
        assert nutrition['calories'] == 100.0 * expected_multiplier
        assert nutrition['protein'] == 10.0 * expected_multiplier
    
    def test_very_small_quantities(self):
        """Test nutrition calculation with very small quantities."""
        food = MockFood(calories=100, protein=10, carbs=15, fat=2)
        serving = MockServing(100.0)
        
        # Test with very small quantity
        tiny_quantity = 0.001
        nutrition = compute_nutrition(food, serving=serving, quantity=tiny_quantity)
        
        # Should scale linearly even for tiny amounts
        expected_multiplier = tiny_quantity  # 0.001 * 100g = 0.1g = 0.001x
        assert nutrition['calories'] == 100.0 * expected_multiplier
        assert nutrition['protein'] == 10.0 * expected_multiplier
