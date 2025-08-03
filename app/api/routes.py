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
        debug_info['servings'] = [s.unit_type for s in servings]
        
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
                'unit_type': s.serving_unit,
                'size_in_grams': s.serving_quantity,
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
            serving_size_id=data.get('serving_size_id'),
            quantity=data['quantity'],
            meal_type=data['meal_type'],
            log_date=datetime.strptime(data['log_date'], '%Y-%m-%d').date() if data.get('log_date') else date.today()
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
        log_date=target_date
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

@bp.route('/test')
def test_api():
    """Test endpoint to verify API is working."""
    return jsonify({'status': 'API is working', 'authenticated': current_user.is_authenticated})