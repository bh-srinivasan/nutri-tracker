from flask import request, jsonify
from flask_login import current_user
from app.models import Food, User, MealLog, FoodServing
from app import db
from datetime import datetime, date
from functools import wraps
from app.api import bp

def api_login_required(f):
    """Custom decorator for API routes that handles authentication for AJAX requests."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/foods/search')
@api_login_required
def search_foods():
    """Search for foods."""
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'error': 'Query parameter required'}), 400
    
    foods = Food.query.filter(Food.name.ilike(f'%{query}%')).limit(20).all()
    
    return jsonify([{
        'id': f.id,
        'name': f.name,
        'category': f.category,
        'calories_per_100g': f.calories,
        'protein_per_100g': f.protein,
        'carbs_per_100g': f.carbs,
        'fat_per_100g': f.fat,
        'verified': f.is_verified
    } for f in foods])

@bp.route('/foods/search-verified')
def search_verified_foods():
    """API endpoint for searching only verified foods for meal logging."""
    try:
        # Get foods for search query with filter for verified foods
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'error': 'Query parameter required'}), 400
        
        # Search only verified foods
        verified_foods = Food.query.filter(
            Food.is_verified == True,
            Food.name.ilike(f'%{query}%')
        ).limit(50).all()
        
        return jsonify([{
            'id': f.id,
            'name': f.name,
            'category': f.category,
            'calories_per_100g': f.calories,
            'protein_per_100g': f.protein,
            'carbs_per_100g': f.carbs,
            'fat_per_100g': f.fat,
            'verified': f.is_verified,
            'default_serving_size_grams': f.default_serving_size_grams
        } for f in verified_foods])
        
    except Exception as e:
        return jsonify({'error': f'Search failed: {str(e)}'}), 500

@bp.route('/foods/<int:food_id>/debug')
@api_login_required
def debug_food_details(food_id):
    """Debug endpoint to help troubleshoot food loading issues."""
    try:
        debug_info = {
            'food_id': food_id,
            'user_authenticated': current_user.is_authenticated,
            'user_id': current_user.id if current_user.is_authenticated else None,
            'is_admin': current_user.is_admin if current_user.is_authenticated else False,
            'timestamp': datetime.now().isoformat()
        }
        
        # Check if food exists
        food = Food.query.get(food_id)
        if food:
            debug_info['food_exists'] = True
            debug_info['food_verified'] = food.is_verified
            debug_info['food_name'] = food.name
            debug_info['food_category'] = food.category
        else:
            debug_info['food_exists'] = False
            debug_info['error'] = 'Food not found in database'
            
        # Check servings
        servings = FoodServing.query.filter_by(food_id=food_id).all()
        debug_info['servings_count'] = len(servings)
        debug_info['servings'] = [s.unit for s in servings]
        
        return jsonify(debug_info)
        
    except Exception as e:
        return jsonify({
            'error': f'Debug failed: {str(e)}',
            'food_id': food_id,
            'timestamp': datetime.now().isoformat()
        }), 500

@bp.route('/foods/<int:food_id>/servings')
@api_login_required
def get_food_servings(food_id):
    """Get complete food details with serving sizes for meal logging."""
    try:
        # Get the food first
        food = Food.query.get(food_id)
        if not food:
            return jsonify({'error': 'Food not found'}), 404
            
        # Check if food is verified (non-admin users should only see verified foods)
        if not food.is_verified and not current_user.is_admin:
            return jsonify({'error': 'Food not available'}), 403
        
        # Get serving sizes for this food
        servings = FoodServing.query.filter_by(food_id=food_id).all()
        
        # Return complete food details with servings
        return jsonify({
            'food': {
                'id': food.id,
                'name': food.name,
                'brand': food.brand,
                'category': food.category,
                'calories_per_100g': food.calories,
                'protein_per_100g': food.protein,
                'carbs_per_100g': food.carbs,
                'fat_per_100g': food.fat,
                'fiber_per_100g': food.fiber if food.fiber else 0,
                'sugar_per_100g': food.sugar if food.sugar else 0,
                'sodium_per_100g': food.sodium if food.sodium else 0,
                'default_serving_size_grams': food.default_serving_size_grams if food.default_serving_size_grams else 100,
                'verified': food.is_verified
            },
            'servings': [{
                'id': s.id if s.id else None,
                'unit_type': s.unit,
                'size_in_grams': s.grams_per_unit,
                'description': s.serving_name
            } for s in servings]
        })
        
    except Exception as e:
        # Log the error for debugging
        print(f"[API ERROR] Failed to get food servings for food_id {food_id}: {str(e)}")
        return jsonify({'error': f'Failed to load food details: {str(e)}'}), 500

@bp.route('/foods/<int:food_id>/nutrition')
@api_login_required
def get_food_nutrition(food_id):
    """Get nutrition information for a specific food."""
    try:
        # Get the food first
        food = Food.query.get(food_id)
        if not food:
            return jsonify({'error': 'Food not found'}), 404
            
        # Check if food is verified (non-admin users should only see verified foods)
        if not food.is_verified and not current_user.is_admin:
            return jsonify({'error': 'Food not available'}), 403
        
        # Return nutrition information
        return jsonify({
            'id': food.id,
            'name': food.name,
            'brand': food.brand,
            'category': food.category,
            'description': food.description,
            'calories_per_100g': food.calories,
            'protein_per_100g': food.protein,
            'carbs_per_100g': food.carbs,
            'fat_per_100g': food.fat,
            'fiber_per_100g': food.fiber if food.fiber else 0,
            'sugar_per_100g': food.sugar if food.sugar else 0,
            'sodium_per_100g': food.sodium if food.sodium else 0,
            'verified': food.is_verified
        })
        
    except Exception as e:
        # Log the error for debugging
        print(f"[API ERROR] Failed to get food nutrition for food_id {food_id}: {str(e)}")
        return jsonify({'error': f'Failed to load food nutrition: {str(e)}'}), 500

@bp.route('/user/meals', methods=['POST'])
@api_login_required
def log_meal():
    """Log a meal for the current user."""
    try:
        data = request.get_json()
        
        meal_log = MealLog(
            user_id=current_user.id,
            food_id=data['food_id'],
            serving_id=data.get('serving_id'),
            quantity=data['quantity'],
            meal_type=data['meal_type'],
            date=datetime.strptime(data['date'], '%Y-%m-%d').date() if data.get('date') else date.today()
        )
        
        db.session.add(meal_log)
        db.session.commit()
        
        return jsonify({'success': True, 'id': meal_log.id}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to log meal: {str(e)}'}), 500

@bp.route('/user/meals')
@api_login_required
def get_user_meals():
    """Get meals for the current user."""
    date_str = request.args.get('date')
    if date_str:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        target_date = date.today()
    
    meals = MealLog.query.filter_by(
        user_id=current_user.id,
        date=target_date
    ).all()
    
    return jsonify([{
        'id': m.id,
        'food_name': m.food.name,
        'quantity': m.quantity,
        'meal_type': m.meal_type,
        'calories': m.calculate_calories(),
        'protein': m.calculate_protein(),
        'carbs': m.calculate_carbs(),
        'fat': m.calculate_fat()
    } for m in meals])

@bp.route('/meals/<int:meal_id>', methods=['DELETE'])
@api_login_required
def delete_meal_api(meal_id):
    """Delete a meal log entry via API."""
    try:
        # Find meal that belongs to current user
        meal_log = MealLog.query.filter(
            MealLog.id == meal_id,
            MealLog.user_id == current_user.id
        ).first()
        
        if not meal_log:
            return jsonify({'error': 'Meal not found or access denied'}), 404
        
        food_name = meal_log.food.name
        db.session.delete(meal_log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Removed {food_name} from your log.'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete meal: {str(e)}'}), 500

@bp.route('/meals/<int:meal_id>', methods=['GET'])
@api_login_required  
def get_meal_api(meal_id):
    """Get a specific meal log entry for editing."""
    try:
        # Find meal that belongs to current user
        meal_log = MealLog.query.filter(
            MealLog.id == meal_id,
            MealLog.user_id == current_user.id
        ).first()
        
        if not meal_log:
            return jsonify({'error': 'Meal not found or access denied'}), 404
        
        return jsonify({
            'id': meal_log.id,
            'food_id': meal_log.food_id,
            'food_name': meal_log.food.name,
            'quantity': meal_log.quantity,
            'meal_type': meal_log.meal_type,
            'date': meal_log.date.isoformat(),
            'original_quantity': meal_log.original_quantity or meal_log.quantity,
            'serving_id': meal_log.serving_id,
            'unit_type': 'serving' if meal_log.serving_id else 'grams'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get meal: {str(e)}'}), 500

@bp.route('/test')
def test_api():
    """Test endpoint to verify API is working."""
    return jsonify({'status': 'API is working', 'authenticated': current_user.is_authenticated})

# Admin User Management API Endpoints
@bp.route('/admin/users', methods=['POST'])
@api_login_required
def create_user():
    """Create a new user (Admin only)."""
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['user_id', 'first_name', 'last_name', 'password']
        for field in required_fields:
            if not data.get(field) or not str(data.get(field)).strip():
                return jsonify({'error': f'{field.replace("_", " ").title()} is required'}), 400
        
        # Validate user_id format
        user_id = str(data['user_id']).strip()
        
        # Use the model's validation method for user_id
        user_id_validation = User.validate_user_id(user_id)
        if not user_id_validation['is_valid']:
            return jsonify({'error': '; '.join(user_id_validation['errors'])}), 400
        
        # Check if username already exists (use user_id as username initially)
        if User.query.filter_by(username=user_id).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        # Validate email if provided
        email = data.get('email')
        if email and email.strip():
            email = email.strip()
            if User.query.filter_by(email=email).first():
                return jsonify({'error': 'Email already exists'}), 400
        else:
            email = None
        
        # Create new user
        new_user = User(
            user_id=user_id,
            username=user_id,  # Use user_id as username initially
            email=email,
            first_name=data['first_name'].strip(),
            last_name=data['last_name'].strip(),
            is_admin=bool(data.get('is_admin', False)),
            is_active=True
        )
        
        # Set password
        new_user.set_password(data['password'])
        
        # Add to database
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'message': 'User created successfully',
            'user': {
                'id': new_user.id,
                'user_id': new_user.user_id,
                'username': new_user.username,
                'email': new_user.email,
                'first_name': new_user.first_name,
                'last_name': new_user.last_name,
                'is_admin': new_user.is_admin,
                'is_active': new_user.is_active
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create user: {str(e)}'}), 500

@bp.route('/admin/users/<int:user_id>')
@api_login_required
def get_user(user_id):
    """Get user details (Admin only)."""
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    user = User.query.get_or_404(user_id)
    
    return jsonify({
        'id': user.id,
        'user_id': user.user_id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_admin': user.is_admin,
        'is_active': user.is_active,
        'created_at': user.created_at.isoformat() if user.created_at else None,
        'last_login': user.last_login.isoformat() if user.last_login else None
    })


def serialize_food_for_api_v2(food: Food) -> dict:
    """Extended serialization for API v2 with serving information."""
    # Get servings for this food
    servings = FoodServing.query.filter_by(food_id=food.id).all()
    
    # Build servings array
    servings_data = []
    for serving in servings:
        servings_data.append({
            'id': serving.id,
            'serving_name': serving.serving_name,
            'unit': serving.unit,
            'grams_per_unit': serving.grams_per_unit
        })
    
    # Base food data (existing per-100g fields)
    food_data = {
        'id': food.id,
        'name': food.name,
        'brand': food.brand,
        'category': food.category,
        'description': food.description,
        'calories_per_100g': food.calories,
        'protein_per_100g': food.protein,
        'carbs_per_100g': food.carbs,
        'fat_per_100g': food.fat,
        'fiber_per_100g': food.fiber,
        'sugar_per_100g': food.sugar,
        'sodium_per_100g': food.sodium,
        'verified': food.is_verified,
        'servings': servings_data,
        'default_serving_id': food.default_serving_id
    }
    
    return food_data


@bp.route('/v2/foods/<int:food_id>')
@api_login_required
def get_food_v2(food_id):
    """API v2: Get complete food details with serving information."""
    try:
        # Get the food
        food = Food.query.get(food_id)
        if not food:
            return jsonify({'error': 'Food not found'}), 404
            
        # Check if food is verified (non-admin users should only see verified foods)
        if not food.is_verified and not current_user.is_admin:
            return jsonify({'error': 'Food not available'}), 403
        
        # Return v2 format with servings data
        return jsonify(serialize_food_for_api_v2(food))
        
    except Exception as e:
        print(f"[API ERROR] Failed to get food v2 for food_id {food_id}: {str(e)}")
        return jsonify({'error': f'Failed to load food details: {str(e)}'}), 500


@bp.route('/v2/meals', methods=['POST'])
@api_login_required
def create_meal_log_v2():
    """
    API v2: Create a new meal log with flexible input support.
    
    Supports both grams-based and serving-based meal logging:
    - Grams-based: {"food_id": 123, "grams": 150, "meal_type": "lunch"}
    - Serving-based: {"food_id": 123, "serving_id": 456, "quantity": 1.5, "meal_type": "lunch"}
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        food_id = data.get('food_id')
        meal_type = data.get('meal_type')
        log_date = data.get('date')  # Optional, defaults to today
        
        if not food_id:
            return jsonify({'error': 'food_id is required'}), 400
        if not meal_type:
            return jsonify({'error': 'meal_type is required'}), 400
        if meal_type not in ['breakfast', 'lunch', 'dinner', 'snack']:
            return jsonify({'error': 'meal_type must be one of: breakfast, lunch, dinner, snack'}), 400
        
        # Validate food exists
        food = Food.query.get(food_id)
        if not food:
            return jsonify({'error': 'Food not found'}), 404
        
        # Handle date
        if log_date:
            try:
                log_date = datetime.strptime(log_date, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'date must be in YYYY-MM-DD format'}), 400
        else:
            log_date = date.today()
        
        # Determine input method and validate
        grams = data.get('grams')
        serving_id = data.get('serving_id')
        quantity = data.get('quantity')
        
        if grams is not None:
            # Grams-based logging
            try:
                grams = float(grams)
                if grams <= 0:
                    return jsonify({'error': 'grams must be greater than 0'}), 400
            except (ValueError, TypeError):
                return jsonify({'error': 'grams must be a valid number'}), 400
            
            # Create MealLog with grams
            meal_log = MealLog(
                user_id=current_user.id,
                food_id=food_id,
                quantity=grams,
                original_quantity=grams,
                unit_type='grams',
                logged_grams=grams,
                meal_type=meal_type,
                date=log_date
            )
            
        elif serving_id is not None and quantity is not None:
            # Serving-based logging
            try:
                quantity = float(quantity)
                if quantity <= 0:
                    return jsonify({'error': 'quantity must be greater than 0'}), 400
            except (ValueError, TypeError):
                return jsonify({'error': 'quantity must be a valid number'}), 400
            
            # Validate serving exists and belongs to food
            serving = FoodServing.query.get(serving_id)
            if not serving:
                return jsonify({'error': 'Serving not found'}), 404
            if serving.food_id != food_id:
                return jsonify({'error': 'Serving does not belong to the specified food'}), 400
            
            # Calculate logged_grams
            logged_grams = serving.grams_per_unit * quantity
            
            # Create MealLog with serving
            meal_log = MealLog(
                user_id=current_user.id,
                food_id=food_id,
                serving_id=serving_id,
                quantity=quantity,
                original_quantity=quantity,
                unit_type='serving',
                logged_grams=logged_grams,
                meal_type=meal_type,
                date=log_date
            )
            
        else:
            return jsonify({
                'error': 'Either "grams" OR both "serving_id" and "quantity" must be provided'
            }), 400
        
        # Calculate nutrition
        meal_log.calculate_nutrition()
        
        # Save to database
        db.session.add(meal_log)
        db.session.commit()
        
        # Return comprehensive response
        response_data = {
            'id': meal_log.id,
            'food_id': meal_log.food_id,
            'serving_id': meal_log.serving_id,
            'quantity': meal_log.quantity,
            'original_quantity': meal_log.original_quantity,
            'unit_type': meal_log.unit_type,
            'logged_grams': meal_log.logged_grams,
            'meal_type': meal_log.meal_type,
            'date': meal_log.date.isoformat(),
            'nutrition': {
                'calories': meal_log.calories,
                'protein': meal_log.protein,
                'carbs': meal_log.carbs,
                'fat': meal_log.fat,
                'fiber': meal_log.fiber,
                'sugar': meal_log.sugar,
                'sodium': meal_log.sodium
            },
            'food_info': {
                'name': food.name,
                'brand': food.brand,
                'category': food.category
            },
            'created_at': meal_log.created_at.isoformat() if meal_log.created_at else None
        }
        
        # Add serving info if applicable
        if meal_log.serving_id:
            serving = FoodServing.query.get(meal_log.serving_id)
            if serving:
                response_data['serving_info'] = {
                    'id': serving.id,
                    'serving_name': serving.serving_name,
                    'unit': serving.unit,
                    'grams_per_unit': serving.grams_per_unit
                }
        
        return jsonify({
            'message': 'Meal log created successfully',
            'meal_log': response_data
        }), 201
        
    except Exception as e:
        print(f"[API ERROR] Failed to create meal log v2: {str(e)}")
        return jsonify({'error': f'Failed to create meal log: {str(e)}'}), 500


@bp.route('/v2/foods/search')
@api_login_required
def search_foods_v2():
    """API v2: Search for foods with enhanced serving information."""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'error': 'Query parameter "q" is required'}), 400
        
        category = request.args.get('category', '').strip()
        brand = request.args.get('brand', '').strip()
        page = max(1, int(request.args.get('page', 1)))
        per_page = min(100, max(1, int(request.args.get('per_page', 20))))
        
        # Build the search query (same as v1 but with v2 serialization)
        from sqlalchemy import or_
        search_filter = or_(
            Food.name.ilike(f'%{query}%'),
            Food.brand.ilike(f'%{query}%'),
            Food.category.ilike(f'%{query}%')
        )
        
        foods_query = Food.query.filter(search_filter)
        
        # Apply additional filters
        if category:
            foods_query = foods_query.filter(Food.category.ilike(f'%{category}%'))
        if brand:
            foods_query = foods_query.filter(Food.brand.ilike(f'%{brand}%'))
        
        # Order by verified foods first, then by name
        foods_query = foods_query.order_by(Food.is_verified.desc(), Food.name)
        
        # Paginate
        pagination = foods_query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # Serialize foods with v2 format (includes servings)
        foods_data = []
        for food in pagination.items:
            foods_data.append(serialize_food_for_api_v2(food))
        
        return jsonify({
            'foods': foods_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_prev': pagination.has_prev,
                'has_next': pagination.has_next
            }
        })
        
    except Exception as e:
        print(f"[API ERROR] Failed to search foods v2: {str(e)}")
        return jsonify({'error': f'Failed to search foods: {str(e)}'}), 500


@bp.route('/v2/foods/<int:food_id>/servings')
@api_login_required
def get_food_servings_v2(food_id):
    """API v2: Get all servings for a specific food."""
    try:
        # Validate food exists
        food = Food.query.get(food_id)
        if not food:
            return jsonify({'error': 'Food not found'}), 404
        
        # Get all servings for this food
        servings = FoodServing.query.filter_by(food_id=food_id).order_by(FoodServing.serving_name).all()
        
        servings_data = []
        for serving in servings:
            servings_data.append({
                'id': serving.id,
                'food_id': serving.food_id,
                'serving_name': serving.serving_name,
                'unit': serving.unit,
                'grams_per_unit': serving.grams_per_unit,
                'created_at': serving.created_at.isoformat() if serving.created_at else None
            })
        
        return jsonify({
            'food_id': food_id,
            'food_name': food.name,
            'servings': servings_data,
            'default_serving_id': food.default_serving_id
        })
        
    except Exception as e:
        print(f"[API ERROR] Failed to get servings v2 for food_id {food_id}: {str(e)}")
        return jsonify({'error': f'Failed to get servings: {str(e)}'}), 500