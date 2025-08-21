"""
Test configuration and fixtures for the Nutri Tracker application.
"""

import pytest
import tempfile
import os
from datetime import datetime, date

from app import create_app, db
from app.models import User, Food, FoodServing, FoodNutrition, MealLog


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    from flask import Flask
    from config import config
    from app import db, login_manager
    
    # Create Flask app with testing config
    app = Flask(__name__)
    app.config.from_object(config['testing'])
    
    # Initialize extensions 
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Register blueprints (minimal set for testing)
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    with app.app_context():
        # Create fresh database tables for each test
        db.create_all()
        yield app
        
        # Clean up database after test
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test runner for CLI commands."""
    return app.test_cli_runner()


@pytest.fixture
def auth_headers():
    """Common headers for authenticated requests."""
    return {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }


@pytest.fixture
def sample_user(app):
    """Create a sample user for testing."""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            is_admin=False,
            is_active=True
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def admin_user(app):
    """Create an admin user for testing."""
    with app.app_context():
        admin = User(
            username='admin',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            is_admin=True,
            is_active=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        return admin


@pytest.fixture
def sample_food(app):
    """Create a sample food item for testing."""
    with app.app_context():
        food = Food(
            name='Basmati Rice',
            brand='Test Brand',
            category='Grains',
            calories=130.0,
            protein=3.0,
            carbs=28.0,
            fat=0.3,
            fiber=0.4,
            sugar=0.1,
            sodium=1.0,
            description='Long grain basmati rice',
            serving_size=100.0,
            default_serving_size_grams=100.0,
            is_verified=True,
            created_by=1
        )
        db.session.add(food)
        db.session.flush()  # Get the ID
        
        # Add nutrition data
        nutrition = FoodNutrition(
            food_id=food.id,
            base_unit='g',
            base_quantity=100.0,
            calories_per_base=130.0,
            protein_per_base=3.0,
            carbs_per_base=28.0,
            fat_per_base=0.3,
            fiber_per_base=0.4,
            sugar_per_base=0.1,
            sodium_per_base=1.0
        )
        db.session.add(nutrition)
        db.session.commit()
        return food


@pytest.fixture
def sample_food_servings(app, sample_food):
    """Create sample food servings for testing."""
    with app.app_context():
        servings = []
        
        # Default 100g serving
        serving_100g = FoodServing(
            food_id=sample_food.id,
            serving_name='100 g',
            unit='g',
            grams_per_unit=100.0,
            created_by=1
        )
        servings.append(serving_100g)
        
        # 1 cup serving
        serving_cup = FoodServing(
            food_id=sample_food.id,
            serving_name='1 cup',
            unit='cup',
            grams_per_unit=195.0,
            created_by=1
        )
        servings.append(serving_cup)
        
        # 1/2 cup serving
        serving_half_cup = FoodServing(
            food_id=sample_food.id,
            serving_name='1/2 cup',
            unit='cup',
            grams_per_unit=97.5,
            created_by=1
        )
        servings.append(serving_half_cup)
        
        for serving in servings:
            db.session.add(serving)
        
        db.session.flush()
        
        # Set the default serving to the cup serving
        sample_food.default_serving_id = serving_cup.id
        db.session.commit()
        
        return servings


def login_user(client, username='testuser', password='password123'):
    """Helper function to log in a user."""
    return client.post('/auth/login', data={
        'username': username,
        'password': password
    }, follow_redirects=True)


def login_admin(client, username='admin', password='admin123'):
    """Helper function to log in an admin user."""
    return client.post('/auth/login', data={
        'username': username,
        'password': password
    }, follow_redirects=True)
