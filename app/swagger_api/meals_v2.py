"""
Interactive Meals API v2 with Swagger UI
"""
from flask import request, jsonify
from flask_restx import Resource
from flask_login import current_user
from datetime import datetime, date
from app.swagger_api import (
    meals_ns, meal_log_grams_input, meal_log_serving_input, 
    meal_log_response, error_model, swagger_login_required
)
from app.models import Food, FoodServing, MealLog, db

@meals_ns.route('/')
class MealLogV2(Resource):
    @meals_ns.doc('create_meal_log_v2', 
                  body=meal_log_grams_input,
                  description="Use either grams-based OR serving-based input. See examples below.")
    @meals_ns.expect([meal_log_grams_input, meal_log_serving_input], validate=False)
    @meals_ns.marshal_with(meal_log_response)
    @meals_ns.response(201, 'Meal log created successfully', meal_log_response)
    @meals_ns.response(400, 'Bad Request', error_model)
    @meals_ns.response(401, 'Authentication Required', error_model)
    @meals_ns.response(404, 'Food or Serving not found', error_model)
    @swagger_login_required
    def post(self):
        """
        Create a new meal log with flexible input (Interactive API v2)
        
        **Interactive Endpoint**: Test directly in Swagger UI with real data!
        
        **Flexible Input Support:**
        
        This endpoint supports **TWO DIFFERENT INPUT METHODS** for maximum flexibility:
        
        ### 1. Grams-Based Input
        Log meals by weight - perfect for precise tracking:
        ```json
        {
          "food_id": 123,
          "grams": 150.0,
          "meal_type": "lunch",
          "date": "2025-08-14"
        }
        ```
        
        ### 2. Serving-Based Input  
        Log meals by serving size - user-friendly and intuitive:
        ```json
        {
          "food_id": 123,
          "serving_id": 456,
          "quantity": 1.5,
          "meal_type": "dinner",
          "date": "2025-08-14"
        }
        ```
        
        **Key Features:**
        - **Automatic Conversion**: Serving-based inputs are automatically converted to grams
        - **Nutrition Calculation**: Nutrition values calculated based on actual grams consumed
        - **Flexible Quantities**: Support decimal quantities (e.g., 1.5 servings, 75.5 grams)
        - **Date Support**: Optional date parameter (defaults to today)
        - **Comprehensive Response**: Returns complete meal log with nutrition breakdown
        
        **Validation:**
        - Food must exist and be accessible to user
        - Serving (if provided) must belong to the specified food
        - Quantities must be positive numbers
        - Meal type must be valid (breakfast, lunch, dinner, snack)
        """
        data = request.get_json()
        
        if not data:
            return {'error': 'Request body is required'}, 400
        
        # Validate required fields
        food_id = data.get('food_id')
        meal_type = data.get('meal_type')
        
        if not food_id or not meal_type:
            return {'error': 'food_id and meal_type are required'}, 400
        
        if meal_type not in ['breakfast', 'lunch', 'dinner', 'snack']:
            return {'error': 'meal_type must be one of: breakfast, lunch, dinner, snack'}, 400
        
        # Check if food exists
        food = Food.query.filter_by(id=food_id, is_verified=True).first()
        if not food:
            return {'error': f'Food with ID {food_id} not found'}, 404
        
        # Determine input method and validate
        grams = data.get('grams')
        serving_id = data.get('serving_id')
        quantity = data.get('quantity', 1.0)
        
        if grams is not None:
            # Grams-based input
            if grams <= 0:
                return {'error': 'grams must be greater than 0'}, 400
            
            logged_grams = grams
            unit_type = 'grams'
            original_quantity = grams
            used_serving_id = None
            serving_info = None
            
        elif serving_id is not None:
            # Serving-based input
            if quantity <= 0:
                return {'error': 'quantity must be greater than 0'}, 400
            
            serving = FoodServing.query.filter_by(id=serving_id, food_id=food_id).first()
            if not serving:
                return {'error': f'Serving with ID {serving_id} not found for food {food_id}'}, 404
            
            logged_grams = serving.grams_per_unit * quantity
            unit_type = 'serving'
            original_quantity = quantity
            used_serving_id = serving_id
            serving_info = {
                'id': serving.id,
                'serving_name': serving.serving_name,
                'unit': serving.unit,
                'grams_per_unit': serving.grams_per_unit
            }
            
        else:
            return {'error': 'Either grams or serving_id+quantity must be provided'}, 400
        
        # Parse date
        meal_date = data.get('date')
        if meal_date:
            try:
                if isinstance(meal_date, str):
                    meal_date = datetime.strptime(meal_date, '%Y-%m-%d').date()
            except ValueError:
                return {'error': 'date must be in YYYY-MM-DD format'}, 400
        else:
            meal_date = date.today()
        
        # Calculate nutrition
        calories = (food.calories * logged_grams) / 100
        protein = (food.protein * logged_grams) / 100
        carbs = (food.carbs * logged_grams) / 100
        fat = (food.fat * logged_grams) / 100
        fiber = ((food.fiber or 0) * logged_grams) / 100
        
        # Create meal log
        meal_log = MealLog(
            user_id=current_user.id,
            food_id=food_id,
            serving_id=used_serving_id,
            quantity=logged_grams,  # DEPRECATED field but still required (NOT NULL)
            original_quantity=original_quantity,  # Original quantity entered by user
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
        
        db.session.add(meal_log)
        db.session.commit()
        
        # Format response
        meal_data = {
            'id': meal_log.id,
            'food_id': meal_log.food_id,
            'serving_id': meal_log.serving_id,
            'quantity': meal_log.quantity,
            'unit_type': unit_type,
            'logged_grams': logged_grams,
            'meal_type': meal_type,
            'date': meal_date.strftime('%Y-%m-%d'),
            'nutrition': {
                'calories': round(calories, 2),
                'protein': round(protein, 2),
                'carbs': round(carbs, 2),
                'fat': round(fat, 2),
                'fiber': round(fiber, 2)
            },
            'food_info': {
                'name': food.name,
                'brand': food.brand or '',
                'category': food.category or ''
            },
            'serving_info': serving_info
        }
        
        return {
            'message': 'Meal log created successfully',
            'meal_log': meal_data
        }, 201

@meals_ns.expect(meal_log_serving_input, validate=False) 
class MealLogServingExample(Resource):
    """Example documentation for serving-based meal logging"""
    pass
