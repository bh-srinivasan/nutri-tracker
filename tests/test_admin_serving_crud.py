"""
Tests for admin CRUD operations on FoodServing.
Tests admin interface for creating, reading, updating, deleting servings
and setting default serving flow.
"""

import json
from unittest.mock import patch

from app import db
from app.models import Food, FoodServing
from tests.conftest import login_admin, login_user


class TestAdminFoodServingCRUD:
    """Test suite for admin CRUD operations on food servings."""
    
    def test_admin_view_food_servings(self, client, app, sample_food, sample_food_servings, admin_user):
        """Test that admin can view food servings."""
        with app.app_context():
            # Login as admin
            login_admin(client)
            
            # Visit food management page
            response = client.get(f'/admin/foods/{sample_food.id}/servings')
            
            assert response.status_code == 200
            html = response.get_data(as_text=True)
            
            # Check that servings are displayed
            assert '1 cup' in html
            assert '1/2 cup' in html
            assert '1 tablespoon' in html
            
            # Check serving details
            assert '195.0' in html  # grams for cup
            assert '97.5' in html   # grams for half cup
            assert '12.0' in html   # grams for tablespoon
    
    def test_admin_create_food_serving_form(self, client, app, sample_food, admin_user):
        """Test admin can access create serving form."""
        with app.app_context():
            # Login as admin
            login_admin(client)
            
            # Visit create serving form
            response = client.get(f'/admin/foods/{sample_food.id}/servings/new')
            
            assert response.status_code == 200
            html = response.get_data(as_text=True)
            
            # Check form elements
            assert 'name="serving_name"' in html
            assert 'name="unit"' in html
            assert 'name="grams_per_unit"' in html
            assert 'Create Serving' in html
    
    def test_admin_create_food_serving_post(self, client, app, sample_food, admin_user):
        """Test admin can create new serving via POST."""
        with app.app_context():
            # Login as admin
            login_admin(client)
            
            # Create serving data
            serving_data = {
                'serving_name': '1 slice',
                'unit': 'slice',
                'grams_per_unit': 25.0
            }
            
            # Post to create serving
            response = client.post(f'/admin/foods/{sample_food.id}/servings',
                                 data=serving_data,
                                 follow_redirects=True)
            
            assert response.status_code == 200
            
            # Verify serving was created in database
            serving = FoodServing.query.filter_by(
                food_id=sample_food.id,
                serving_name='1 slice'
            ).first()
            
            assert serving is not None
            assert serving.unit == 'slice'
            assert serving.grams_per_unit == 25.0
            
            # Check success message in response
            html = response.get_data(as_text=True)
            assert 'Serving created successfully' in html or '1 slice' in html
    
    def test_admin_create_duplicate_serving_fails(self, client, app, sample_food, sample_food_servings, admin_user):
        """Test that creating duplicate serving fails."""
        with app.app_context():
            # Login as admin
            login_admin(client)
            
            # Try to create duplicate serving (1 cup already exists)
            serving_data = {
                'serving_name': '1 cup',
                'unit': 'cup',
                'grams_per_unit': 200.0  # Different grams but same name
            }
            
            # Post to create serving
            response = client.post(f'/admin/foods/{sample_food.id}/servings',
                                 data=serving_data)
            
            assert response.status_code in [400, 422]  # Validation error
            
            # Verify original serving unchanged
            cup_serving = FoodServing.query.filter_by(
                food_id=sample_food.id,
                serving_name='1 cup'
            ).first()
            
            assert cup_serving.grams_per_unit == 195.0  # Original value
    
    def test_admin_edit_food_serving_form(self, client, app, sample_food, sample_food_servings, admin_user):
        """Test admin can access edit serving form."""
        with app.app_context():
            # Login as admin
            login_admin(client)
            
            # Get cup serving
            cup_serving = next(s for s in sample_food_servings if s.serving_name == '1 cup')
            
            # Visit edit serving form
            response = client.get(f'/admin/foods/{sample_food.id}/servings/{cup_serving.id}/edit')
            
            assert response.status_code == 200
            html = response.get_data(as_text=True)
            
            # Check form is pre-populated
            assert 'value="1 cup"' in html
            assert 'value="cup"' in html
            assert 'value="195.0"' in html
            assert 'Update Serving' in html
    
    def test_admin_update_food_serving_post(self, client, app, sample_food, sample_food_servings, admin_user):
        """Test admin can update serving via POST."""
        with app.app_context():
            # Login as admin
            login_admin(client)
            
            # Get cup serving
            cup_serving = next(s for s in sample_food_servings if s.serving_name == '1 cup')
            
            # Update serving data
            update_data = {
                'serving_name': '1 large cup',
                'unit': 'cup',
                'grams_per_unit': 210.0
            }
            
            # Post update
            response = client.post(f'/admin/foods/{sample_food.id}/servings/{cup_serving.id}',
                                 data=update_data,
                                 follow_redirects=True)
            
            assert response.status_code == 200
            
            # Verify serving was updated
            db.session.refresh(cup_serving)
            assert cup_serving.serving_name == '1 large cup'
            assert cup_serving.grams_per_unit == 210.0
            
            # Check success message
            html = response.get_data(as_text=True)
            assert 'Serving updated successfully' in html or '1 large cup' in html
    
    def test_admin_delete_food_serving(self, client, app, sample_food, sample_food_servings, admin_user):
        """Test admin can delete serving."""
        with app.app_context():
            # Login as admin
            login_admin(client)
            
            # Get tablespoon serving to delete
            tbsp_serving = next(s for s in sample_food_servings if s.serving_name == '1 tablespoon')
            serving_id = tbsp_serving.id
            
            # Delete serving
            response = client.delete(f'/admin/foods/{sample_food.id}/servings/{serving_id}')
            
            assert response.status_code in [200, 204]
            
            # Verify serving was deleted
            deleted_serving = FoodServing.query.get(serving_id)
            assert deleted_serving is None
            
            # Verify other servings still exist
            remaining_servings = FoodServing.query.filter_by(food_id=sample_food.id).all()
            assert len(remaining_servings) == 2  # Cup and half-cup remain
    
    def test_admin_delete_serving_via_ajax(self, client, app, sample_food, sample_food_servings, admin_user):
        """Test admin can delete serving via AJAX request."""
        with app.app_context():
            # Login as admin
            login_admin(client)
            
            # Get tablespoon serving
            tbsp_serving = next(s for s in sample_food_servings if s.serving_name == '1 tablespoon')
            
            # Make AJAX delete request
            response = client.delete(f'/admin/api/servings/{tbsp_serving.id}',
                                   headers={'X-Requested-With': 'XMLHttpRequest'})
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            
            # Verify serving deleted
            deleted_serving = FoodServing.query.get(tbsp_serving.id)
            assert deleted_serving is None


class TestAdminDefaultServingFlow:
    """Test suite for admin setting default serving functionality."""
    
    def test_admin_set_default_serving_form(self, client, app, sample_food, sample_food_servings, admin_user):
        """Test admin can access set default serving form."""
        with app.app_context():
            # Login as admin
            login_admin(client)
            
            # Visit set default serving form
            response = client.get(f'/admin/foods/{sample_food.id}/default-serving')
            
            assert response.status_code == 200
            html = response.get_data(as_text=True)
            
            # Check form elements
            assert 'name="default_serving_id"' in html
            assert '1 cup' in html
            assert '1/2 cup' in html
            assert '1 tablespoon' in html
    
    def test_admin_set_default_serving_post(self, client, app, sample_food, sample_food_servings, admin_user):
        """Test admin can set default serving via POST."""
        with app.app_context():
            # Login as admin
            login_admin(client)
            
            # Get half cup serving
            half_cup_serving = next(s for s in sample_food_servings if s.serving_name == '1/2 cup')
            
            # Set default serving
            default_data = {
                'default_serving_id': half_cup_serving.id
            }
            
            response = client.post(f'/admin/foods/{sample_food.id}/default-serving',
                                 data=default_data,
                                 follow_redirects=True)
            
            assert response.status_code == 200
            
            # Verify default serving was set
            db.session.refresh(sample_food)
            assert sample_food.default_serving_id == half_cup_serving.id
            
            # Check success message
            html = response.get_data(as_text=True)
            assert 'Default serving updated' in html or 'successfully' in html
    
    def test_admin_clear_default_serving(self, client, app, sample_food, sample_food_servings, admin_user):
        """Test admin can clear default serving."""
        with app.app_context():
            # Login as admin
            login_admin(client)
            
            # Ensure food has a default serving first
            cup_serving = next(s for s in sample_food_servings if s.serving_name == '1 cup')
            sample_food.default_serving_id = cup_serving.id
            db.session.commit()
            
            # Clear default serving (set to None/empty)
            clear_data = {
                'default_serving_id': ''  # Empty string should clear
            }
            
            response = client.post(f'/admin/foods/{sample_food.id}/default-serving',
                                 data=clear_data,
                                 follow_redirects=True)
            
            assert response.status_code == 200
            
            # Verify default serving was cleared
            db.session.refresh(sample_food)
            assert sample_food.default_serving_id is None
    
    def test_admin_set_invalid_default_serving_fails(self, client, app, sample_food, admin_user):
        """Test that setting invalid default serving fails."""
        with app.app_context():
            # Login as admin
            login_admin(client)
            
            # Try to set non-existent serving as default
            invalid_data = {
                'default_serving_id': 99999  # Non-existent serving
            }
            
            response = client.post(f'/admin/foods/{sample_food.id}/default-serving',
                                 data=invalid_data)
            
            assert response.status_code in [400, 422]  # Validation error
            
            # Verify default serving unchanged
            db.session.refresh(sample_food)
            # Should still be the original default from fixture
            assert sample_food.default_serving_id != 99999
    
    def test_admin_default_serving_ajax_update(self, client, app, sample_food, sample_food_servings, admin_user):
        """Test admin can update default serving via AJAX."""
        with app.app_context():
            # Login as admin
            login_admin(client)
            
            # Get half cup serving
            half_cup_serving = next(s for s in sample_food_servings if s.serving_name == '1/2 cup')
            
            # Update via AJAX
            ajax_data = {
                'default_serving_id': half_cup_serving.id
            }
            
            response = client.put(f'/admin/api/foods/{sample_food.id}/default-serving',
                                data=json.dumps(ajax_data),
                                content_type='application/json',
                                headers={'X-Requested-With': 'XMLHttpRequest'})
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert data['default_serving_id'] == half_cup_serving.id
            
            # Verify in database
            db.session.refresh(sample_food)
            assert sample_food.default_serving_id == half_cup_serving.id


class TestAdminServingAccessControl:
    """Test suite for admin access control on serving operations."""
    
    def test_regular_user_cannot_access_serving_crud(self, client, app, sample_food, sample_user):
        """Test that regular users cannot access serving CRUD operations."""
        with app.app_context():
            # Login as regular user
            login_user(client)
            
            # Try to access servings page
            response = client.get(f'/admin/foods/{sample_food.id}/servings')
            assert response.status_code in [401, 403, 302]  # Unauthorized or redirect
            
            # Try to access create form
            response = client.get(f'/admin/foods/{sample_food.id}/servings/new')
            assert response.status_code in [401, 403, 302]
            
            # Try to post new serving
            response = client.post(f'/admin/foods/{sample_food.id}/servings',
                                 data={'serving_name': 'test', 'unit': 'test', 'grams_per_unit': 10})
            assert response.status_code in [401, 403, 302]
    
    def test_unauthenticated_user_cannot_access_serving_crud(self, client, app, sample_food):
        """Test that unauthenticated users cannot access serving operations."""
        with app.app_context():
            # No login
            
            # Try to access servings page
            response = client.get(f'/admin/foods/{sample_food.id}/servings')
            assert response.status_code in [401, 302]  # Unauthorized or redirect to login
            
            # Try AJAX delete
            response = client.delete(f'/admin/api/servings/1')
            assert response.status_code in [401, 302]
    
    def test_admin_serving_operations_require_csrf(self, client, app, sample_food, admin_user):
        """Test that serving operations require CSRF protection."""
        with app.app_context():
            # Login as admin
            login_admin(client)
            
            # Try to create serving without CSRF token
            with patch('flask_wtf.csrf.validate_csrf') as mock_csrf:
                mock_csrf.side_effect = Exception("CSRF token missing")
                
                response = client.post(f'/admin/foods/{sample_food.id}/servings',
                                     data={'serving_name': 'test', 'unit': 'test', 'grams_per_unit': 10})
                
                # Should fail due to CSRF
                assert response.status_code in [400, 403, 422]
