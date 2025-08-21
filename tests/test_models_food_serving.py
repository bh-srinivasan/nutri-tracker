"""
Tests for FoodServing model functionality.
Tests uniqueness constraints and positive grams validation.
"""

import pytest
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import Food, FoodServing, User


class TestFoodServingModel:
    """Test suite for FoodServing model."""
    
    def test_food_serving_creation(self, app, sample_food, admin_user):
        """Test basic FoodServing creation."""
        with app.app_context():
            serving = FoodServing(
                food_id=sample_food.id,
                serving_name='1 medium bowl',
                unit='bowl',
                grams_per_unit=150.0,
                created_by=admin_user.id
            )
            db.session.add(serving)
            db.session.commit()
            
            assert serving.id is not None
            assert serving.serving_name == '1 medium bowl'
            assert serving.unit == 'bowl'
            assert serving.grams_per_unit == 150.0
            assert serving.food_id == sample_food.id
            assert serving.created_by == admin_user.id
            assert serving.created_at is not None
    
    def test_food_serving_uniqueness_constraint(self, app, sample_food, admin_user):
        """Test that serving names must be unique per food."""
        with app.app_context():
            # Create first serving
            serving1 = FoodServing(
                food_id=sample_food.id,
                serving_name='1 cup',
                unit='cup',
                grams_per_unit=195.0,
                created_by=admin_user.id
            )
            db.session.add(serving1)
            db.session.commit()
            
            # Try to create duplicate serving name for same food
            serving2 = FoodServing(
                food_id=sample_food.id,
                serving_name='1 cup',  # Same name as serving1
                unit='cup',
                grams_per_unit=200.0,  # Different grams
                created_by=admin_user.id
            )
            db.session.add(serving2)
            
            # Should raise IntegrityError due to uniqueness constraint
            with pytest.raises(IntegrityError):
                db.session.commit()
    
    def test_food_serving_uniqueness_different_foods(self, app, admin_user):
        """Test that same serving names are allowed for different foods."""
        with app.app_context():
            # Create two different foods
            food1 = Food(
                name='Rice',
                calories=130.0,
                protein=3.0,
                carbs=28.0,
                fat=0.3,
                created_by=admin_user.id
            )
            food2 = Food(
                name='Quinoa',
                calories=120.0,
                protein=4.0,
                carbs=22.0,
                fat=2.0,
                created_by=admin_user.id
            )
            db.session.add_all([food1, food2])
            db.session.flush()
            
            # Create servings with same name for different foods
            serving1 = FoodServing(
                food_id=food1.id,
                serving_name='1 cup',
                unit='cup',
                grams_per_unit=195.0,
                created_by=admin_user.id
            )
            serving2 = FoodServing(
                food_id=food2.id,
                serving_name='1 cup',  # Same name, different food
                unit='cup',
                grams_per_unit=185.0,
                created_by=admin_user.id
            )
            
            db.session.add_all([serving1, serving2])
            db.session.commit()  # Should not raise error
            
            assert serving1.id != serving2.id
            assert serving1.food_id != serving2.food_id
            assert serving1.serving_name == serving2.serving_name
    
    def test_positive_grams_validation(self, app, sample_food, admin_user):
        """Test that grams_per_unit must be positive."""
        with app.app_context():
            # Test zero grams (should be invalid)
            serving_zero = FoodServing(
                food_id=sample_food.id,
                serving_name='zero grams',
                unit='g',
                grams_per_unit=0.0,
                created_by=admin_user.id
            )
            db.session.add(serving_zero)
            
            with pytest.raises(ValueError, match="Grams per unit must be positive"):
                db.session.commit()
    
    def test_negative_grams_validation(self, app, sample_food, admin_user):
        """Test that negative grams are not allowed."""
        with app.app_context():
            # Test negative grams (should be invalid)
            serving_negative = FoodServing(
                food_id=sample_food.id,
                serving_name='negative grams',
                unit='g',
                grams_per_unit=-10.0,
                created_by=admin_user.id
            )
            db.session.add(serving_negative)
            
            with pytest.raises(ValueError, match="Grams per unit must be positive"):
                db.session.commit()
    
    def test_very_small_positive_grams(self, app, sample_food, admin_user):
        """Test that very small positive values are allowed."""
        with app.app_context():
            serving = FoodServing(
                food_id=sample_food.id,
                serving_name='1 pinch',
                unit='pinch',
                grams_per_unit=0.1,  # Very small but positive
                created_by=admin_user.id
            )
            db.session.add(serving)
            db.session.commit()
            
            assert serving.id is not None
            assert serving.grams_per_unit == 0.1
    
    def test_food_serving_relationship(self, app, sample_food, admin_user):
        """Test the relationship between FoodServing and Food."""
        with app.app_context():
            serving = FoodServing(
                food_id=sample_food.id,
                serving_name='1 tablespoon',
                unit='tbsp',
                grams_per_unit=15.0,
                created_by=admin_user.id
            )
            db.session.add(serving)
            db.session.commit()
            
            # Test forward relationship
            assert serving.food == sample_food
            assert serving.food.name == sample_food.name
            
            # Test reverse relationship
            food_servings = sample_food.servings
            assert serving in food_servings
    
    def test_food_serving_str_representation(self, app, sample_food, admin_user):
        """Test the string representation of FoodServing."""
        with app.app_context():
            serving = FoodServing(
                food_id=sample_food.id,
                serving_name='1 cup',
                unit='cup',
                grams_per_unit=195.0,
                created_by=admin_user.id
            )
            db.session.add(serving)
            db.session.commit()
            
            str_repr = str(serving)
            assert '1 cup' in str_repr
            assert '195.0g' in str_repr
    
    def test_food_serving_cascade_delete(self, app, admin_user):
        """Test that servings are deleted when food is deleted."""
        with app.app_context():
            # Create food with serving
            food = Food(
                name='Test Food',
                calories=100.0,
                protein=5.0,
                carbs=10.0,
                fat=1.0,
                created_by=admin_user.id
            )
            db.session.add(food)
            db.session.flush()
            
            serving = FoodServing(
                food_id=food.id,
                serving_name='1 serving',
                unit='serving',
                grams_per_unit=100.0,
                created_by=admin_user.id
            )
            db.session.add(serving)
            db.session.commit()
            
            serving_id = serving.id
            
            # Delete the food
            db.session.delete(food)
            db.session.commit()
            
            # Serving should be deleted too
            deleted_serving = FoodServing.query.get(serving_id)
            assert deleted_serving is None
    
    def test_multiple_servings_per_food(self, app, sample_food, admin_user):
        """Test that a food can have multiple servings."""
        with app.app_context():
            servings_data = [
                ('1 cup', 'cup', 195.0),
                ('1/2 cup', 'cup', 97.5),
                ('1 tablespoon', 'tbsp', 12.0),
                ('1 teaspoon', 'tsp', 4.0),
                ('100 g', 'g', 100.0)
            ]
            
            created_servings = []
            for name, unit, grams in servings_data:
                serving = FoodServing(
                    food_id=sample_food.id,
                    serving_name=name,
                    unit=unit,
                    grams_per_unit=grams,
                    created_by=admin_user.id
                )
                db.session.add(serving)
                created_servings.append(serving)
            
            db.session.commit()
            
            # Verify all servings were created
            assert len(created_servings) == 5
            for serving in created_servings:
                assert serving.id is not None
                assert serving.food_id == sample_food.id
            
            # Verify through food relationship
            food_servings = sample_food.servings
            assert len(food_servings) >= 5  # >= because sample_food_servings fixture may add more
