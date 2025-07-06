from flask import jsonify, request
from flask_login import login_required, current_user
from flask_wtf.csrf import validate_csrf
from wtforms.validators import ValidationError
from app.api import bp
from app.models import Food, MealLog, User
from app import db
from functools import wraps
from datetime import datetime
import logging

# Set up logging
logger = logging.getLogger(__name__)

def admin_required(f):
    """Decorator to require admin access for API endpoints."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        if not current_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def api_login_required(f):
    """Custom login_required decorator for API endpoints that returns JSON instead of redirecting."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/foods/search')
@api_login_required
def search_foods():
    """API endpoint for food search with autocomplete."""
    query = request.args.get('q', '', type=str)
    category = request.args.get('category', '', type=str)
    limit = request.args.get('limit', 10, type=int)
    
    if not query or len(query) < 2:
        return jsonify({'foods': []})
    
    # Build query
    foods_query = Food.query.filter(
        Food.name.contains(query) |
        Food.brand.contains(query)
    )
    
    if category:
        foods_query = foods_query.filter(Food.category == category)
    
    foods = foods_query.order_by(Food.name).limit(limit).all()
    
    # Format response
    foods_data = []
    for food in foods:
        brand_text = f" ({food.brand})" if food.brand else ""
        foods_data.append({
            'id': food.id,
            'name': food.name,
            'brand': food.brand,
            'display_name': f"{food.name}{brand_text}",
            'category': food.category,
            'calories': food.calories,
            'protein': food.protein,
            'carbs': food.carbs,
            'fat': food.fat,
            'fiber': food.fiber,
            'serving_size': food.serving_size
        })
    
    return jsonify({'foods': foods_data})

@bp.route('/foods/<int:food_id>/nutrition')
@api_login_required
def get_food_nutrition(food_id):
    """Get nutrition information for a specific food item."""
    food = Food.query.get_or_404(food_id)
    
    nutrition_data = {
        'id': food.id,
        'name': food.name,
        'brand': food.brand,
        'category': food.category,
        'per_100g': {
            'calories': food.calories,
            'protein': food.protein,
            'carbs': food.carbs,
            'fat': food.fat,
            'fiber': food.fiber,
            'sugar': food.sugar,
            'sodium': food.sodium
        },
        'serving_size': food.serving_size,
        'per_serving': food.get_nutrition_per_serving()
    }
    
    return jsonify(nutrition_data)

@bp.route('/nutrition/calculate', methods=['POST'])
@login_required
def calculate_nutrition():
    """Calculate nutrition for a given quantity of food."""
    data = request.get_json()
    
    if not data or 'food_id' not in data or 'quantity' not in data:
        return jsonify({'error': 'Missing food_id or quantity'}), 400
    
    food = Food.query.get(data['food_id'])
    if not food:
        return jsonify({'error': 'Food not found'}), 404
    
    quantity = float(data['quantity'])
    factor = quantity / 100  # Convert to per quantity
    
    nutrition = {
        'calories': round(food.calories * factor, 1),
        'protein': round(food.protein * factor, 1),
        'carbs': round(food.carbs * factor, 1),
        'fat': round(food.fat * factor, 1),
        'fiber': round(food.fiber * factor, 1),
        'sugar': round(food.sugar * factor, 1),
        'sodium': round(food.sodium * factor, 1)
    }
    
    return jsonify({
        'food_name': food.name,
        'quantity': quantity,
        'nutrition': nutrition
    })

@bp.route('/dashboard/stats')
@login_required
def dashboard_stats():
    """Get dashboard statistics for the current user."""
    from datetime import date, timedelta
    from sqlalchemy import func
    
    today = date.today()
    
    # Today's nutrition
    today_logs = MealLog.query.filter(
        MealLog.user_id == current_user.id,
        MealLog.date == today
    ).all()
    
    today_nutrition = {
        'calories': sum(log.calories or 0 for log in today_logs),
        'protein': sum(log.protein or 0 for log in today_logs),
        'carbs': sum(log.carbs or 0 for log in today_logs),
        'fat': sum(log.fat or 0 for log in today_logs),
        'fiber': sum(log.fiber or 0 for log in today_logs)
    }
    
    # Weekly average
    week_ago = today - timedelta(days=7)
    weekly_data = db.session.query(
        func.avg(MealLog.calories).label('avg_calories'),
        func.avg(MealLog.protein).label('avg_protein'),
        func.avg(MealLog.carbs).label('avg_carbs'),
        func.avg(MealLog.fat).label('avg_fat')
    ).filter(
        MealLog.user_id == current_user.id,
        MealLog.date >= week_ago
    ).first()
    
    weekly_avg = {
        'calories': round(weekly_data.avg_calories or 0, 1),
        'protein': round(weekly_data.avg_protein or 0, 1),
        'carbs': round(weekly_data.avg_carbs or 0, 1),
        'fat': round(weekly_data.avg_fat or 0, 1)
    }
    
    # Current goals
    current_goal = current_user.get_current_nutrition_goal()
    goals = {}
    if current_goal:
        goals = {
            'calories': current_goal.target_calories,
            'protein': current_goal.target_protein,
            'carbs': current_goal.target_carbs,
            'fat': current_goal.target_fat,
            'fiber': current_goal.target_fiber
        }
    
    return jsonify({
        'today': today_nutrition,
        'weekly_average': weekly_avg,
        'goals': goals,
        'date': today.isoformat()
    })

@bp.route('/meal-logs', methods=['GET'])
@login_required
def get_meal_logs():
    """Get meal logs for a specific date range."""
    start_date = request.args.get('start_date', type=str)
    end_date = request.args.get('end_date', type=str)
    
    query = MealLog.query.filter(MealLog.user_id == current_user.id)
    
    if start_date:
        from datetime import datetime
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        query = query.filter(MealLog.date >= start_date_obj)
    
    if end_date:
        from datetime import datetime
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        query = query.filter(MealLog.date <= end_date_obj)
    
    logs = query.order_by(MealLog.date.desc(), MealLog.logged_at.desc()).all()
    
    logs_data = []
    for log in logs:
        logs_data.append({
            'id': log.id,
            'date': log.date.isoformat(),
            'meal_type': log.meal_type,
            'food_name': log.food.name,
            'food_brand': log.food.brand,
            'quantity': log.quantity,
            'calories': log.calories,
            'protein': log.protein,
            'carbs': log.carbs,
            'fat': log.fat,
            'fiber': log.fiber
        })
    
    return jsonify({'meal_logs': logs_data})

@bp.route('/suggestions/high-protein')
@login_required
def high_protein_suggestions():
    """Get high-protein food suggestions."""
    # Get Indian high-protein foods
    high_protein_foods = Food.query.filter(
        Food.protein >= 15,  # Foods with 15g+ protein per 100g
        Food.category.in_(['legumes', 'dairy', 'meat', 'fish', 'nuts'])
    ).order_by(Food.protein.desc()).limit(10).all()
    
    suggestions = []
    for food in high_protein_foods:
        brand_text = f" ({food.brand})" if food.brand else ""
        suggestions.append({
            'id': food.id,
            'name': f"{food.name}{brand_text}",
            'protein': food.protein,
            'calories': food.calories,
            'category': food.category,
            'protein_per_calorie': round(food.protein / food.calories * 100, 1) if food.calories > 0 else 0
        })
    
    return jsonify({'suggestions': suggestions})

@bp.route('/user/profile')
@login_required
def user_profile():
    """Get current user profile information."""
    bmr = current_user.calculate_bmr()
    tdee = current_user.calculate_tdee()
    
    profile = {
        'username': current_user.username,
        'email': current_user.email,
        'first_name': current_user.first_name,
        'last_name': current_user.last_name,
        'age': current_user.age,
        'gender': current_user.gender,
        'height': current_user.height,
        'weight': current_user.weight,
        'activity_level': current_user.activity_level,
        'bmr': bmr,
        'tdee': tdee,
        'member_since': current_user.created_at.isoformat() if current_user.created_at else None
    }
    
    return jsonify({'profile': profile})

# Admin API Endpoints
@bp.route('/admin/users/<int:user_id>')
@login_required
@admin_required
def get_user(user_id):
    """Get user details for editing."""
    try:
        user = User.query.get_or_404(user_id)
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_admin': user.is_admin,
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'last_login': user.last_login.isoformat() if user.last_login else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/admin/users/<int:user_id>', methods=['PUT'])
@login_required
@admin_required  
def update_user(user_id):
    """Update user details."""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        # Validate CSRF token if provided
        csrf_token = request.headers.get('X-CSRFToken')
        if csrf_token:
            try:
                validate_csrf(csrf_token)
            except ValidationError:
                return jsonify({'error': 'CSRF token validation failed'}), 400
        
        # Validate email format if provided (only validate non-empty emails)
        if 'email' in data and data['email'] and data['email'].strip():
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, data['email'].strip()):
                return jsonify({'error': 'Invalid email format'}), 400
                
            # Check for duplicate email (excluding current user)
            existing_user = User.query.filter(User.email == data['email'].strip(), User.id != user_id).first()
            if existing_user:
                return jsonify({'error': 'Email already exists'}), 400
        
        # Validate username if provided
        if 'username' in data and data['username']:
            if len(data['username']) < 3:
                return jsonify({'error': 'Username must be at least 3 characters'}), 400
                
            # Check for duplicate username (excluding current user)
            existing_user = User.query.filter(User.username == data['username'], User.id != user_id).first()
            if existing_user:
                return jsonify({'error': 'Username already exists'}), 400
        
        # Validate required fields (email is now optional)
        required_fields = ['first_name', 'last_name', 'username']
        for field in required_fields:
            if field in data and not data[field].strip():
                return jsonify({'error': f'{field.replace("_", " ").title()} is required'}), 400
        
        # Prevent self-deactivation
        if 'is_active' in data and not data['is_active'] and user.id == current_user.id:
            return jsonify({'error': 'Cannot deactivate your own account'}), 400
        
        # Update user fields
        if 'first_name' in data:
            user.first_name = data['first_name'].strip()
        if 'last_name' in data:
            user.last_name = data['last_name'].strip()
        if 'email' in data:
            # Handle optional email field - set to None if empty
            email_value = data['email'].strip() if data['email'] else None
            user.email = email_value if email_value else None
        if 'username' in data:
            user.username = data['username'].strip()
        if 'is_admin' in data:
            user.is_admin = bool(data['is_admin'])
        if 'is_active' in data:
            user.is_active = bool(data['is_active'])
            
        db.session.commit()
        logger.info(f'User {user.id} updated by admin {current_user.id}')
        
        return jsonify({
            'message': 'User updated successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_admin': user.is_admin,
                'is_active': user.is_active
            }
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error updating user {user_id}: {str(e)}')
        return jsonify({'error': str(e)}), 500

@bp.route('/admin/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    """Toggle user active status."""
    try:
        user = User.query.get_or_404(user_id)
        
        # Prevent deactivating the current admin user
        if user.id == current_user.id:
            return jsonify({'error': 'Cannot deactivate your own account'}), 400
            
        user.is_active = not user.is_active
        db.session.commit()
        
        status = 'activated' if user.is_active else 'deactivated'
        return jsonify({
            'message': f'User {status} successfully',
            'is_active': user.is_active
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/admin/users/<int:user_id>/reset-password', methods=['POST'])
@login_required
@admin_required
def reset_user_password(user_id):
    """API endpoint for admin-initiated password reset."""
    try:
        user = User.query.get_or_404(user_id)
        
        # Prevent admin from resetting their own password this way
        if user.id == current_user.id:
            return jsonify({
                'success': False,
                'message': 'You cannot reset your own password using this method. Use the change password feature instead.'
            }), 400
        
        # Prevent resetting admin passwords
        if user.is_admin:
            return jsonify({
                'success': False,
                'message': 'Admin passwords cannot be reset using this method for security reasons.'
            }), 400
        
        # Get password from request
        data = request.get_json()
        if not data or 'new_password' not in data:
            return jsonify({
                'success': False,
                'message': 'New password is required.'
            }), 400
        
        new_password = data['new_password']
        
        # Validate password strength
        validation_result = User.validate_password(new_password)
        if not validation_result['is_valid']:
            return jsonify({
                'success': False,
                'message': 'Password does not meet security requirements.',
                'errors': validation_result['errors']
            }), 400
        
        # Set the new password
        user.set_password(new_password)
        user.password_changed_at = datetime.utcnow()
        db.session.commit()
        
        # Log the password reset action
        logger.info(f'Admin {current_user.username} reset password for user {user.username}')
        
        return jsonify({
            'success': True,
            'message': f'Password successfully reset for user {user.username}',
            'username': user.username
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error resetting password for user {user_id}: {str(e)}')
        return jsonify({
            'success': False,
            'message': 'An error occurred while resetting the password. Please try again.'
        }), 500

@bp.route('/admin/users', methods=['POST'])
@login_required
@admin_required
def add_user():
    """Add a new user."""
    try:
        data = request.get_json()
        
        # Input validation and sanitization
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        email = data.get('email', '').strip() if data.get('email') else None
        password = data.get('password', '')
        is_admin = data.get('is_admin', False)
        
        # Validate required fields
        if not first_name:
            return jsonify({'error': 'First name is required'}), 400
        if not last_name:
            return jsonify({'error': 'Last name is required'}), 400
        if not password:
            return jsonify({'error': 'Password is required'}), 400
            
        # Validate email if provided (optional field)
        if email and not User.validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
            
        # Check if email already exists (if provided)
        if email and User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        # Generate username from first and last name
        username = User.generate_username(first_name, last_name)
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Generated username already exists. Please try different names.'}), 400
        
        # Validate password
        validation_result = User.validate_password(password)
        if not validation_result['is_valid']:
            return jsonify({
                'error': 'Password does not meet security requirements: ' + ', '.join(validation_result['errors'])
            }), 400
        
        # Create new user
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_admin=is_admin,
            is_active=True
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        logger.info(f'Admin {current_user.username} created new user: {username}')
        
        return jsonify({
            'id': user.id,
            'username': user.username,
            'message': f'User {username} created successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error creating user: {str(e)}')
        return jsonify({'error': f'Failed to create user: {str(e)}'}), 500
