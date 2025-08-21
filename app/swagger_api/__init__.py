"""
Swagger API Blueprint for Nutri Tracker
Provides REST API with automatic Swagger UI documentation for existing API v2 endpoints
"""
from flask import Blueprint
from flask_restx import Api, Resource, fields, Namespace
from flask_login import current_user
from functools import wraps

# Create the blueprint
swagger_bp = Blueprint('swagger_api', __name__, url_prefix='/api/docs')

# Create the API with Swagger documentation
api = Api(
    swagger_bp,
    version='2.0',
    title='Nutri Tracker API v2',
    description='''
    A comprehensive nutrition tracking API for managing foods, meals, and nutrition goals.
    
    This API supports flexible meal logging with both:
    - **Grams-based input**: Log meals by weight (e.g., 150g chicken breast)
    - **Serving-based input**: Log meals by serving size (e.g., 1.5 pieces, 2 cups)
    
    **Authentication**: All endpoints require user authentication via existing session.
    **Base URL**: /api/v2/
    ''',
    doc='/',  # Swagger UI will be available at /api/docs/
    authorizations={
        'SessionAuth': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Cookie',
            'description': 'Session-based authentication (login to web app first)'
        }
    },
    security='SessionAuth'
)

# Authentication decorator for API routes
def swagger_login_required(f):
    """Custom decorator for Swagger API routes that handles authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            api.abort(401, 'Authentication required')
        return f(*args, **kwargs)
    return decorated_function

# Define models for API v2 (matching actual endpoints)
food_v2_model = api.model('FoodV2', {
    'id': fields.Integer(required=True, description='Food ID', example=42),
    'name': fields.String(required=True, description='Food name', example='Idli'),
    'brand': fields.String(description='Brand name', example='Traditional'),
    'category': fields.String(description='Food category', example='Indian Breakfast'),
    'description': fields.String(description='Food description', example='Steamed rice and lentil cake'),
    'calories_per_100g': fields.Float(required=True, description='Calories per 100g', example=58.0),
    'protein_per_100g': fields.Float(required=True, description='Protein in grams per 100g', example=2.5),
    'carbs_per_100g': fields.Float(required=True, description='Carbohydrates in grams per 100g', example=12.0),
    'fat_per_100g': fields.Float(required=True, description='Fat in grams per 100g', example=0.1),
    'fiber_per_100g': fields.Float(description='Fiber in grams per 100g', example=0.9),
    'sugar_per_100g': fields.Float(description='Sugar in grams per 100g', example=0.5),
    'sodium_per_100g': fields.Float(description='Sodium in mg per 100g', example=5.0),
    'verified': fields.Boolean(description='Whether the food is verified', example=True),
    'servings': fields.List(fields.Nested(api.model('ServingV2', {
        'id': fields.Integer(description='Serving ID', example=84),
        'serving_name': fields.String(description='Serving name (e.g., "1 cup", "1 piece")', example='1 piece (medium)'),
        'unit': fields.String(description='Unit of measurement', example='piece'),
        'grams_per_unit': fields.Float(description='Grams per unit', example=35.0)
    })), description='Available serving sizes for this food'),
    'default_serving_id': fields.Integer(description='ID of default serving for this food', example=84)
})

# Input models for v2 API
meal_log_grams_input = api.model('MealLogGramsInput', {
    'food_id': fields.Integer(required=True, description='Food ID', example=42),
    'grams': fields.Float(required=True, description='Amount in grams', example=70.0),
    'meal_type': fields.String(required=True, description='Type of meal', enum=['breakfast', 'lunch', 'dinner', 'snack'], example='breakfast'),
    'date': fields.Date(description='Date of meal (YYYY-MM-DD, defaults to today)', example='2025-08-18')
})

meal_log_serving_input = api.model('MealLogServingInput', {
    'food_id': fields.Integer(required=True, description='Food ID', example=42),
    'serving_id': fields.Integer(required=True, description='Serving ID', example=84),
    'quantity': fields.Float(required=True, description='Number of servings (e.g., 1.5 for 1.5 servings)', example=2.0),
    'meal_type': fields.String(required=True, description='Type of meal', enum=['breakfast', 'lunch', 'dinner', 'snack'], example='breakfast'),
    'date': fields.Date(description='Date of meal (YYYY-MM-DD, defaults to today)', example='2025-08-18')
})

# Response models for v2 API
meal_log_response = api.model('MealLogResponse', {
    'message': fields.String(description='Success message', example='Meal logged successfully'),
    'meal_log': fields.Nested(api.model('MealLogData', {
        'id': fields.Integer(description='Meal log ID', example=1001),
        'food_id': fields.Integer(description='Food ID', example=42),
        'serving_id': fields.Integer(description='Serving ID (if serving-based)', example=84),
        'quantity': fields.Float(description='Quantity logged', example=2.0),
        'original_quantity': fields.Float(description='Original quantity as entered', example=2.0),
        'unit_type': fields.String(description='Input type: "grams" or "serving"', example='serving'),
        'logged_grams': fields.Float(description='Total grams consumed', example=70.0),
        'meal_type': fields.String(description='Meal type', example='breakfast'),
        'date': fields.Date(description='Date of meal', example='2025-08-18'),
        'nutrition': fields.Nested(api.model('NutritionData', {
            'calories': fields.Float(description='Total calories', example=40.6),
            'protein': fields.Float(description='Total protein (g)', example=1.75),
            'carbs': fields.Float(description='Total carbohydrates (g)', example=8.4),
            'fat': fields.Float(description='Total fat (g)', example=0.07),
            'fiber': fields.Float(description='Total fiber (g)', example=0.63),
            'sugar': fields.Float(description='Total sugar (g)', example=0.35),
            'sodium': fields.Float(description='Total sodium (mg)', example=3.5)
        })),
        'food_info': fields.Nested(api.model('FoodInfo', {
            'name': fields.String(description='Food name', example='Idli'),
            'brand': fields.String(description='Brand name', example='Traditional'),
            'category': fields.String(description='Food category', example='Indian Breakfast')
        })),
        'serving_info': fields.Nested(api.model('ServingInfo', {
            'id': fields.Integer(description='Serving ID', example=84),
            'serving_name': fields.String(description='Serving name', example='1 piece (medium)'),
            'unit': fields.String(description='Unit of measurement', example='piece'),
            'grams_per_unit': fields.Float(description='Grams per unit', example=35.0)
        }), description='Serving info (only present for serving-based logs)'),
        'created_at': fields.DateTime(description='When meal log was created', example='2025-08-18T10:30:00Z')
    }))
})

food_search_response_v2 = api.model('FoodSearchResponseV2', {
    'foods': fields.List(fields.Nested(food_v2_model), description='List of foods with serving information'),
    'pagination': fields.Nested(api.model('PaginationInfo', {
        'page': fields.Integer(description='Current page'),
        'per_page': fields.Integer(description='Results per page'),
        'total': fields.Integer(description='Total number of results'),
        'pages': fields.Integer(description='Total number of pages'),
        'has_prev': fields.Boolean(description='Has previous page'),
        'has_next': fields.Boolean(description='Has next page')
    }))
})

servings_response_v2 = api.model('ServingsResponseV2', {
    'food_id': fields.Integer(description='Food ID'),
    'food_name': fields.String(description='Food name'),
    'servings': fields.List(fields.Nested(api.model('ServingDetail', {
        'id': fields.Integer(description='Serving ID'),
        'food_id': fields.Integer(description='Food ID'),
        'serving_name': fields.String(description='Serving name'),
        'unit': fields.String(description='Unit of measurement'),
        'grams_per_unit': fields.Float(description='Grams per unit'),
        'created_at': fields.DateTime(description='When serving was created')
    }))),
    'default_serving_id': fields.Integer(description='Default serving ID for this food')
})

# Error models
error_model = api.model('Error', {
    'error': fields.String(required=True, description='Error message')
})

# Create namespaces for different API sections
foods_ns = Namespace('foods', description='Food management operations (API v2)')
servings_ns = Namespace('servings', description='Food serving management operations (API v2)') 
meals_ns = Namespace('meals', description='Flexible meal logging operations (API v2)')

# Add namespaces to the API
api.add_namespace(foods_ns, path='/foods')
api.add_namespace(servings_ns, path='/servings')
api.add_namespace(meals_ns, path='/meals')

# Import all endpoint modules to register routes
from app.swagger_api import foods_v2, servings_v2, meals_v2
