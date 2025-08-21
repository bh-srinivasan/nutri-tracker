"""
Tests for API v2 endpoints.
Tests that food read includes servings and default_serving_id,
and meal log accepts serving payload with matching grams totals.
"""

import json
import pytest

from app import db
from app.models import Food, FoodServing, MealLog
from tests.conftest import login_user, login_admin


class TestAPIv2FoodEndpoints:
    """Test suite for API v2 food endpoints."""
    
    def test_food_read_includes_servings(self, client, app, sample_food, sample_food_servings, sample_user):
        """Test that v2 food read endpoint includes servings."""
        with app.app_context():
            # Login user
            login_user(client)
            
            # Make API request
            response = client.get(f'/api/v2/foods/{sample_food.id}')
            
            assert response.status_code == 200
            data = response.get_json()
            
            # Check basic food data
            assert data['id'] == sample_food.id
            assert data['name'] == sample_food.name
            assert data['calories'] == sample_food.calories
            
            # Check servings are included
            assert 'servings' in data
            servings = data['servings']
            assert len(servings) == len(sample_food_servings)
            
            # Verify serving data structure
            for serving_data in servings:
                assert 'id' in serving_data
                assert 'serving_name' in serving_data
                assert 'unit' in serving_data
                assert 'grams_per_unit' in serving_data
            
            # Find specific servings
            cup_serving = next((s for s in servings if s['serving_name'] == '1 cup'), None)
            assert cup_serving is not None
            assert cup_serving['grams_per_unit'] == 195.0
            assert cup_serving['unit'] == 'cup'
    
    def test_food_read_includes_default_serving_id(self, client, app, sample_food, sample_food_servings, sample_user):
        """Test that v2 food read endpoint includes default_serving_id."""
        with app.app_context():
            # Login user
            login_user(client)
            
            # Make API request
            response = client.get(f'/api/v2/foods/{sample_food.id}')
            
            assert response.status_code == 200
            data = response.get_json()
            
            # Check default_serving_id is included
            assert 'default_serving_id' in data
            assert data['default_serving_id'] == sample_food.default_serving_id
            
            # Verify it matches the cup serving (set in fixture)
            cup_serving = next(s for s in sample_food_servings if s.serving_name == '1 cup')
            assert data['default_serving_id'] == cup_serving.id
    
    def test_food_read_no_default_serving(self, client, app, sample_user, admin_user):
        """Test food read when no default serving is set."""
        with app.app_context():
            # Create food without default serving
            food = Food(
                name='No Default Food',
                calories=100.0,
                protein=5.0,
                carbs=10.0,
                fat=1.0,
                created_by=admin_user.id
            )
            db.session.add(food)
            db.session.commit()
            
            # Login user
            login_user(client)
            
            # Make API request
            response = client.get(f'/api/v2/foods/{food.id}')
            
            assert response.status_code == 200
            data = response.get_json()
            
            # default_serving_id should be null
            assert 'default_serving_id' in data
            assert data['default_serving_id'] is None
    
    def test_food_read_unauthorized(self, client, app, sample_food):
        """Test that unauthorized users cannot access food details."""
        with app.app_context():
            # Make API request without login
            response = client.get(f'/api/v2/foods/{sample_food.id}')
            
            assert response.status_code == 401
    
    def test_food_read_not_found(self, client, app, sample_user):
        """Test food read for non-existent food."""
        with app.app_context():
            # Login user
            login_user(client)
            
            # Make API request for non-existent food
            response = client.get('/api/v2/foods/99999')
            
            assert response.status_code == 404


class TestAPIv2MealLogEndpoints:
    """Test suite for API v2 meal log endpoints."""
    
    def test_meal_log_create_with_serving_payload(self, client, app, sample_food, sample_food_servings, sample_user):
        """Test creating meal log with serving payload."""
        with app.app_context():
            # Login user
            login_user(client)
            
            # Get the cup serving
            cup_serving = next(s for s in sample_food_servings if s.serving_name == '1 cup')
            
            # Create meal log payload with serving
            payload = {
                'food_id': sample_food.id,
                'quantity': 1.5,
                'unit_type': 'serving',
                'serving_id': cup_serving.id,
                'meal_type': 'lunch'
            }
            
            response = client.post('/api/v2/meal-logs', 
                                 data=json.dumps(payload),
                                 content_type='application/json')
            
            assert response.status_code == 201
            data = response.get_json()
            
            # Check response data
            assert data['food_id'] == sample_food.id
            assert data['quantity'] == 1.5
            assert data['unit_type'] == 'serving'
            assert data['serving_id'] == cup_serving.id
            assert data['meal_type'] == 'lunch'
            
            # Verify grams calculation: 1.5 cups * 195g/cup = 292.5g
            expected_grams = 1.5 * 195.0
            assert data['logged_grams'] == expected_grams
            
            # Verify nutrition calculation
            expected_multiplier = expected_grams / 100.0
            assert data['calories'] == sample_food.calories * expected_multiplier
            assert data['protein'] == sample_food.protein * expected_multiplier
    
    def test_meal_log_create_with_grams_payload(self, client, app, sample_food, sample_user):
        """Test creating meal log with grams payload."""
        with app.app_context():
            # Login user
            login_user(client)
            
            # Create meal log payload with grams
            payload = {
                'food_id': sample_food.id,
                'quantity': 250.0,
                'unit_type': 'grams',
                'meal_type': 'dinner'
            }
            
            response = client.post('/api/v2/meal-logs',
                                 data=json.dumps(payload),
                                 content_type='application/json')
            
            assert response.status_code == 201
            data = response.get_json()
            
            # Check response data
            assert data['food_id'] == sample_food.id
            assert data['quantity'] == 250.0
            assert data['unit_type'] == 'grams'
            assert data['serving_id'] is None
            assert data['meal_type'] == 'dinner'
            
            # Verify grams matches quantity for grams unit
            assert data['logged_grams'] == 250.0
            
            # Verify nutrition calculation
            expected_multiplier = 250.0 / 100.0
            assert data['calories'] == sample_food.calories * expected_multiplier
            assert data['protein'] == sample_food.protein * expected_multiplier
    
    def test_meal_log_grams_serving_equivalence(self, client, app, sample_food, sample_food_servings, sample_user):
        """Test that equivalent grams and serving create same nutrition totals."""
        with app.app_context():
            # Login user
            login_user(client)
            
            # Get the cup serving (195g)
            cup_serving = next(s for s in sample_food_servings if s.serving_name == '1 cup')
            
            # Create meal log with grams (195g)
            grams_payload = {
                'food_id': sample_food.id,
                'quantity': 195.0,
                'unit_type': 'grams',
                'meal_type': 'breakfast'
            }
            
            grams_response = client.post('/api/v2/meal-logs',
                                       data=json.dumps(grams_payload),
                                       content_type='application/json')
            
            # Create meal log with serving (1 cup = 195g)
            serving_payload = {
                'food_id': sample_food.id,
                'quantity': 1.0,
                'unit_type': 'serving',
                'serving_id': cup_serving.id,
                'meal_type': 'lunch'
            }
            
            serving_response = client.post('/api/v2/meal-logs',
                                         data=json.dumps(serving_payload),
                                         content_type='application/json')
            
            assert grams_response.status_code == 201
            assert serving_response.status_code == 201
            
            grams_data = grams_response.get_json()
            serving_data = serving_response.get_json()
            
            # Both should have same logged_grams
            assert grams_data['logged_grams'] == serving_data['logged_grams']
            assert grams_data['logged_grams'] == 195.0
            
            # Both should have same nutrition values
            assert grams_data['calories'] == serving_data['calories']
            assert grams_data['protein'] == serving_data['protein']
            assert grams_data['carbs'] == serving_data['carbs']
            assert grams_data['fat'] == serving_data['fat']
    
    def test_meal_log_multiple_servings_grams_match(self, client, app, sample_food, sample_food_servings, sample_user):
        """Test that multiple servings calculate correct grams total."""
        with app.app_context():
            # Login user
            login_user(client)
            
            # Get the half cup serving (97.5g)
            half_cup_serving = next(s for s in sample_food_servings if s.serving_name == '1/2 cup')
            
            # Create meal log with 3 half-cup servings
            payload = {
                'food_id': sample_food.id,
                'quantity': 3.0,
                'unit_type': 'serving',
                'serving_id': half_cup_serving.id,
                'meal_type': 'snack'
            }
            
            response = client.post('/api/v2/meal-logs',
                                 data=json.dumps(payload),
                                 content_type='application/json')
            
            assert response.status_code == 201
            data = response.get_json()
            
            # Expected grams: 3 * 97.5g = 292.5g
            expected_grams = 3.0 * 97.5
            assert data['logged_grams'] == expected_grams
            
            # Verify nutrition scales correctly
            expected_multiplier = expected_grams / 100.0
            assert data['calories'] == sample_food.calories * expected_multiplier
    
    def test_meal_log_invalid_serving_id(self, client, app, sample_food, sample_user):
        """Test meal log creation with invalid serving ID."""
        with app.app_context():
            # Login user
            login_user(client)
            
            # Create payload with non-existent serving ID
            payload = {
                'food_id': sample_food.id,
                'quantity': 1.0,
                'unit_type': 'serving',
                'serving_id': 99999,  # Non-existent serving
                'meal_type': 'lunch'
            }
            
            response = client.post('/api/v2/meal-logs',
                                 data=json.dumps(payload),
                                 content_type='application/json')
            
            assert response.status_code == 400
            data = response.get_json()
            assert 'error' in data
    
    def test_meal_log_serving_without_serving_id(self, client, app, sample_food, sample_user):
        """Test meal log creation with serving unit but no serving_id."""
        with app.app_context():
            # Login user
            login_user(client)
            
            # Create payload with serving unit but no serving_id
            payload = {
                'food_id': sample_food.id,
                'quantity': 1.0,
                'unit_type': 'serving',
                'meal_type': 'lunch'
                # Missing serving_id
            }
            
            response = client.post('/api/v2/meal-logs',
                                 data=json.dumps(payload),
                                 content_type='application/json')
            
            assert response.status_code == 400
            data = response.get_json()
            assert 'error' in data
    
    def test_meal_log_update_serving_to_grams(self, client, app, sample_food, sample_food_servings, sample_user):
        """Test updating meal log from serving to grams maintains nutrition."""
        with app.app_context():
            # Login user
            login_user(client)
            
            # Get the cup serving
            cup_serving = next(s for s in sample_food_servings if s.serving_name == '1 cup')
            
            # Create meal log with serving
            create_payload = {
                'food_id': sample_food.id,
                'quantity': 1.0,
                'unit_type': 'serving',
                'serving_id': cup_serving.id,
                'meal_type': 'lunch'
            }
            
            create_response = client.post('/api/v2/meal-logs',
                                        data=json.dumps(create_payload),
                                        content_type='application/json')
            
            assert create_response.status_code == 201
            meal_log_data = create_response.get_json()
            meal_log_id = meal_log_data['id']
            
            # Update to equivalent grams (195g)
            update_payload = {
                'quantity': 195.0,
                'unit_type': 'grams',
                'serving_id': None
            }
            
            update_response = client.put(f'/api/v2/meal-logs/{meal_log_id}',
                                       data=json.dumps(update_payload),
                                       content_type='application/json')
            
            assert update_response.status_code == 200
            updated_data = update_response.get_json()
            
            # Nutrition should remain the same
            assert updated_data['logged_grams'] == meal_log_data['logged_grams']
            assert updated_data['calories'] == meal_log_data['calories']
            assert updated_data['protein'] == meal_log_data['protein']
    
    def test_meal_log_unauthorized(self, client, app, sample_food):
        """Test that unauthorized users cannot create meal logs."""
        with app.app_context():
            payload = {
                'food_id': sample_food.id,
                'quantity': 100.0,
                'unit_type': 'grams',
                'meal_type': 'lunch'
            }
            
            # Make request without login
            response = client.post('/api/v2/meal-logs',
                                 data=json.dumps(payload),
                                 content_type='application/json')
            
            assert response.status_code == 401
