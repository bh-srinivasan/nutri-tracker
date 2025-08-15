"""
Meal Logging API endpoints with Swagger documentation
"""
from flask import request
from flask_restx import Resource
from flask_login import current_user
from app.swagger_api import meals_ns, meal_log_model, meal_log_input_model, error_model, success_model, swagger_login_required
from app.models import Food, FoodServing, MealLog
from app import db
from datetime import datetime, date

@meals_ns.route('/')
class MealLogList(Resource):
    @meals_ns.doc('create_meal_log')
    @meals_ns.expect(meal_log_input_model)
    @meals_ns.marshal_with(meal_log_model)
    @meals_ns.response(201, 'Meal log created successfully', meal_log_model)
    @meals_ns.response(400, 'Bad Request', error_model)
    @meals_ns.response(401, 'Authentication Required', error_model)
    @meals_ns.response(404, 'Food or Serving not found', error_model)
    @swagger_login_required
    def post(self):
        """
        Create a new meal log entry
        
        Supports both grams-based and serving-based meal logging.
        For grams-based: provide food_id, quantity (in grams), unit_type='grams'
        For serving-based: provide food_id, serving_id, quantity (number of servings), unit_type='serving'
        """
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['food_id', 'quantity', 'unit_type', 'meal_type']
        for field in required_fields:
            if field not in data:
                meals_ns.abort(400, f'Missing required field: {field}')
        
        food_id = data['food_id']
        quantity = float(data['quantity'])
        unit_type = data['unit_type']
        meal_type = data['meal_type']
        serving_id = data.get('serving_id')
        log_date = data.get('date')
        
        # Validate unit_type
        if unit_type not in ['grams', 'serving']:
            meals_ns.abort(400, 'unit_type must be "grams" or "serving"')
        
        # Validate meal_type
        if meal_type not in ['breakfast', 'lunch', 'dinner', 'snack']:
            meals_ns.abort(400, 'meal_type must be one of: breakfast, lunch, dinner, snack')
        
        # Validate quantity
        if quantity <= 0:
            meals_ns.abort(400, 'quantity must be greater than 0')
        
        # Validate food exists
        food = Food.query.get(food_id)
        if not food:
            meals_ns.abort(404, f'Food with ID {food_id} not found')
        
        # Handle date
        if log_date:
            try:
                if isinstance(log_date, str):
                    log_date = datetime.strptime(log_date, '%Y-%m-%d').date()
            except ValueError:
                meals_ns.abort(400, 'date must be in YYYY-MM-DD format')
        else:
            log_date = date.today()
        
        # Validate serving-based logging
        if unit_type == 'serving':
            if not serving_id:
                meals_ns.abort(400, 'serving_id is required when unit_type is "serving"')
            
            serving = FoodServing.query.get(serving_id)
            if not serving:
                meals_ns.abort(404, f'Serving with ID {serving_id} not found')
            
            if serving.food_id != food_id:
                meals_ns.abort(400, f'Serving {serving_id} does not belong to food {food_id}')
            
            # Calculate logged_grams for serving-based
            logged_grams = serving.grams_per_unit * quantity
        else:
            # For grams-based logging
            logged_grams = quantity
            serving_id = None
        
        # Create the meal log
        meal_log = MealLog(
            user_id=current_user.id,
            food_id=food_id,
            serving_id=serving_id,
            quantity=quantity,
            original_quantity=quantity,
            unit_type=unit_type,
            logged_grams=logged_grams,
            meal_type=meal_type,
            date=log_date
        )
        
        # Calculate nutrition
        meal_log.calculate_nutrition()
        
        # Save to database
        db.session.add(meal_log)
        db.session.commit()
        
        return {
            'id': meal_log.id,
            'user_id': meal_log.user_id,
            'food_id': meal_log.food_id,
            'serving_id': meal_log.serving_id,
            'quantity': meal_log.quantity,
            'original_quantity': meal_log.original_quantity,
            'unit_type': meal_log.unit_type,
            'logged_grams': meal_log.logged_grams,
            'meal_type': meal_log.meal_type,
            'date': meal_log.date.isoformat(),
            'calories': meal_log.calories,
            'protein': meal_log.protein,
            'carbs': meal_log.carbs,
            'fat': meal_log.fat,
            'fiber': meal_log.fiber,
            'sugar': meal_log.sugar,
            'sodium': meal_log.sodium,
            'created_at': meal_log.created_at.isoformat() if meal_log.created_at else None
        }, 201

    @meals_ns.doc('get_meal_logs')
    @meals_ns.param('date', 'Filter by date (YYYY-MM-DD)', required=False, type='string')
    @meals_ns.param('meal_type', 'Filter by meal type', required=False, type='string', enum=['breakfast', 'lunch', 'dinner', 'snack'])
    @meals_ns.param('page', 'Page number (default: 1)', required=False, type='integer', default=1)
    @meals_ns.param('per_page', 'Results per page (default: 50, max: 100)', required=False, type='integer', default=50)
    @meals_ns.marshal_list_with(meal_log_model)
    @meals_ns.response(200, 'Success', [meal_log_model])
    @meals_ns.response(400, 'Bad Request', error_model)
    @meals_ns.response(401, 'Authentication Required', error_model)
    @swagger_login_required
    def get(self):
        """
        Get meal log entries for the current user
        
        Returns paginated meal log entries with optional filtering by date and meal type.
        """
        # Parse query parameters
        date_filter = request.args.get('date')
        meal_type_filter = request.args.get('meal_type')
        page = max(1, int(request.args.get('page', 1)))
        per_page = min(100, max(1, int(request.args.get('per_page', 50))))
        
        # Build query
        query = MealLog.query.filter_by(user_id=current_user.id)
        
        # Apply date filter
        if date_filter:
            try:
                filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                query = query.filter(MealLog.date == filter_date)
            except ValueError:
                meals_ns.abort(400, 'date must be in YYYY-MM-DD format')
        
        # Apply meal type filter
        if meal_type_filter:
            if meal_type_filter not in ['breakfast', 'lunch', 'dinner', 'snack']:
                meals_ns.abort(400, 'meal_type must be one of: breakfast, lunch, dinner, snack')
            query = query.filter(MealLog.meal_type == meal_type_filter)
        
        # Order by most recent first
        query = query.order_by(MealLog.date.desc(), MealLog.created_at.desc())
        
        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        meal_logs_data = []
        for meal_log in pagination.items:
            meal_log_dict = {
                'id': meal_log.id,
                'user_id': meal_log.user_id,
                'food_id': meal_log.food_id,
                'serving_id': meal_log.serving_id,
                'quantity': meal_log.quantity,
                'original_quantity': meal_log.original_quantity,
                'unit_type': meal_log.unit_type,
                'logged_grams': meal_log.logged_grams,
                'meal_type': meal_log.meal_type,
                'date': meal_log.date.isoformat(),
                'calories': meal_log.calories,
                'protein': meal_log.protein,
                'carbs': meal_log.carbs,
                'fat': meal_log.fat,
                'fiber': meal_log.fiber,
                'sugar': meal_log.sugar,
                'sodium': meal_log.sodium,
                'created_at': meal_log.created_at.isoformat() if meal_log.created_at else None
            }
            meal_logs_data.append(meal_log_dict)
        
        return meal_logs_data

@meals_ns.route('/<int:meal_log_id>')
class MealLogDetail(Resource):
    @meals_ns.doc('get_meal_log_detail')
    @meals_ns.marshal_with(meal_log_model)
    @meals_ns.response(200, 'Success', meal_log_model)
    @meals_ns.response(401, 'Authentication Required', error_model)
    @meals_ns.response(403, 'Access denied', error_model)
    @meals_ns.response(404, 'Meal log not found', error_model)
    @swagger_login_required
    def get(self, meal_log_id):
        """
        Get detailed information about a specific meal log entry
        """
        meal_log = MealLog.query.get(meal_log_id)
        if not meal_log:
            meals_ns.abort(404, f'Meal log with ID {meal_log_id} not found')
        
        # Check if the meal log belongs to the current user
        if meal_log.user_id != current_user.id:
            meals_ns.abort(403, 'Access denied to this meal log')
        
        return {
            'id': meal_log.id,
            'user_id': meal_log.user_id,
            'food_id': meal_log.food_id,
            'serving_id': meal_log.serving_id,
            'quantity': meal_log.quantity,
            'original_quantity': meal_log.original_quantity,
            'unit_type': meal_log.unit_type,
            'logged_grams': meal_log.logged_grams,
            'meal_type': meal_log.meal_type,
            'date': meal_log.date.isoformat(),
            'calories': meal_log.calories,
            'protein': meal_log.protein,
            'carbs': meal_log.carbs,
            'fat': meal_log.fat,
            'fiber': meal_log.fiber,
            'sugar': meal_log.sugar,
            'sodium': meal_log.sodium,
            'created_at': meal_log.created_at.isoformat() if meal_log.created_at else None
        }
    
    @meals_ns.doc('delete_meal_log')
    @meals_ns.marshal_with(success_model)
    @meals_ns.response(200, 'Meal log deleted successfully', success_model)
    @meals_ns.response(401, 'Authentication Required', error_model)
    @meals_ns.response(403, 'Access denied', error_model)
    @meals_ns.response(404, 'Meal log not found', error_model)
    @swagger_login_required
    def delete(self, meal_log_id):
        """
        Delete a meal log entry
        """
        meal_log = MealLog.query.get(meal_log_id)
        if not meal_log:
            meals_ns.abort(404, f'Meal log with ID {meal_log_id} not found')
        
        # Check if the meal log belongs to the current user
        if meal_log.user_id != current_user.id:
            meals_ns.abort(403, 'Access denied to this meal log')
        
        db.session.delete(meal_log)
        db.session.commit()
        
        return {
            'message': f'Meal log {meal_log_id} deleted successfully',
            'data': {'deleted_id': meal_log_id}
        }
