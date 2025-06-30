from flask import jsonify, request
from flask_login import login_required, current_user
from app.api import bp
from app.models import Food, MealLog, User
from app import db

@bp.route('/foods/search')
@login_required
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
@login_required
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
