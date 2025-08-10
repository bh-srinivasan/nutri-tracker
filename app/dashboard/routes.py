from datetime import datetime, date, timedelta
from flask import render_template, redirect, url_for, flash, request, jsonify, make_response
from flask_login import login_required, current_user
from sqlalchemy import func, desc, and_
from sqlalchemy.orm import joinedload
import csv
import io
from app import db
from app.dashboard import bp
from app.dashboard.forms import MealLogForm, NutritionGoalForm, FoodSearchForm
from app.models import User, Food, MealLog, NutritionGoal, Challenge, UserChallenge, FoodServing

def serialize_food_for_js(food: Food) -> dict:
    """Return a JSON-serializable dict for the front-end preselect."""
    return {
        "id": food.id,
        "name": food.name,
        "brand": food.brand,
        "description": food.description or "",
        "calories_per_100g": food.calories or 0,
        "protein_per_100g": food.protein or 0,
        "carbs_per_100g": food.carbs or 0,
        "fat_per_100g": food.fat or 0,
        "image_url": getattr(food, "image_url", "") or "",
    }

def calculate_target_date_from_duration(duration):
    """Calculate target date based on selected duration."""
    if not duration:
        return None
    
    today = date.today()
    duration_map = {
        '2_weeks': timedelta(weeks=2),
        '1_month': timedelta(days=30),
        '2_months': timedelta(days=60),
        '3_months': timedelta(days=90),
        '6_months': timedelta(days=180),
        '1_year': timedelta(days=365)
    }
    
    delta = duration_map.get(duration)
    if delta:
        return today + delta
    return None

@bp.route('/')
@login_required
def index():
    """User dashboard homepage."""
    today = date.today()
    
    # Get today's meal logs
    today_logs = MealLog.query.filter(
        MealLog.user_id == current_user.id,
        MealLog.date == today
    ).order_by(MealLog.logged_at.desc()).all()
    
    # Calculate today's nutrition totals
    today_nutrition = {
        'calories': sum(log.calories or 0 for log in today_logs),
        'protein': sum(log.protein or 0 for log in today_logs),
        'carbs': sum(log.carbs or 0 for log in today_logs),
        'fat': sum(log.fat or 0 for log in today_logs),
        'fiber': sum(log.fiber or 0 for log in today_logs)
    }
    
    # Get current nutrition goals
    current_goal = current_user.get_current_nutrition_goal()
    
    # Calculate progress percentages
    progress = {
        'calories': 0,
        'protein': 0,
        'carbs': 0,
        'fat': 0,
        'fiber': 0
    }
    if current_goal:
        progress = {
            'calories': (today_nutrition['calories'] / current_goal.target_calories * 100) if current_goal.target_calories else 0,
            'protein': (today_nutrition['protein'] / current_goal.target_protein * 100) if current_goal.target_protein else 0,
            'carbs': (today_nutrition['carbs'] / current_goal.target_carbs * 100) if current_goal.target_carbs else 0,
            'fat': (today_nutrition['fat'] / current_goal.target_fat * 100) if current_goal.target_fat else 0,
            'fiber': (today_nutrition['fiber'] / current_goal.target_fiber * 100) if current_goal.target_fiber else 0
        }
    
    # Get weekly streak
    streak = calculate_logging_streak(current_user.id)
    
    # Get recent challenges
    user_challenges = UserChallenge.query.filter(
        UserChallenge.user_id == current_user.id,
        UserChallenge.is_completed == False
    ).order_by(UserChallenge.start_date.desc()).limit(3).all()
    
    # Group logs by meal type for today
    meals_by_type = {
        'breakfast': [log for log in today_logs if log.meal_type == 'breakfast'],
        'lunch': [log for log in today_logs if log.meal_type == 'lunch'],
        'dinner': [log for log in today_logs if log.meal_type == 'dinner'],
        'snack': [log for log in today_logs if log.meal_type == 'snack']
    }
    
    return render_template('dashboard/index.html', title='Dashboard',
                         today_nutrition=today_nutrition, current_goal=current_goal,
                         progress=progress, streak=streak, user_challenges=user_challenges,
                         meals_by_type=meals_by_type, current_datetime=datetime.now())

@bp.route('/log-meal', methods=['GET', 'POST'])
@login_required
def log_meal():
    """Log a meal with UOM support."""
    form = MealLogForm()
    
    # Parse ?edit=...
    edit_param = request.args.get('edit')
    try:
        edit_meal_id = int(edit_param) if edit_param else None
    except ValueError:
        edit_meal_id = None

    edit_meal = None
    if edit_meal_id:
        edit_meal = MealLog.query.options(
            db.joinedload(MealLog.food)
        ).filter(
            MealLog.id == edit_meal_id,
            MealLog.user_id == current_user.id
        ).first()
        if not edit_meal:
            flash('Meal not found or access denied.', 'danger')
            return redirect(url_for('dashboard.index'))

    # Pre-populate on GET
    if edit_meal and request.method == 'GET':
        form.food_id.data = edit_meal.food_id
        form.quantity.data = edit_meal.original_quantity
        form.unit_type.data = edit_meal.unit_type
        form.serving_id.data = edit_meal.serving_id
        form.meal_type.data = edit_meal.meal_type
        form.date.data = edit_meal.date

    # On submit, use form.date.data for both edit and create
    if form.validate_on_submit():
        food = Food.query.get(form.food_id.data)
        if not food:
            flash('Food not found.', 'danger')
            return redirect(url_for('dashboard.log_meal'))
        
        if not food.is_verified:
            flash('This food has not been verified yet. Please choose a verified food.', 'warning')
            return redirect(url_for('dashboard.log_meal'))
        
        # Calculate normalized quantity in grams
        original_quantity = form.quantity.data
        normalized_quantity = original_quantity
        serving_id = None
        
        if form.unit_type.data == 'serving' and form.serving_id.data:
            # Convert serving to grams
            serving = FoodServing.query.get(form.serving_id.data)
            if serving and serving.food_id == food.id:
                normalized_quantity = original_quantity * serving.serving_quantity
                serving_id = serving.id
            else:
                flash('Invalid serving size selected.', 'danger')
                return redirect(url_for('dashboard.log_meal'))
        
        if edit_meal:
            meal_log = edit_meal
            meal_log.food_id = food.id
            meal_log.quantity = normalized_quantity
            meal_log.original_quantity = original_quantity
            meal_log.unit_type = form.unit_type.data
            meal_log.serving_id = serving_id
            meal_log.meal_type = form.meal_type.data
            meal_log.date = form.date.data
            meal_log.calculate_nutrition()
            flash(f'Successfully updated {food.name} for {form.meal_type.data}!', 'success')
        else:
            meal_log = MealLog(
                user_id=current_user.id,
                food_id=food.id,
                quantity=normalized_quantity,
                original_quantity=original_quantity,
                unit_type=form.unit_type.data,
                serving_id=serving_id,
                meal_type=form.meal_type.data,
                date=form.date.data,  # <--- important
            )
            meal_log.calculate_nutrition()
            db.session.add(meal_log)
            flash(f'Successfully logged {food.name} for {form.meal_type.data}!', 'success')

        db.session.commit()
        return redirect(url_for('dashboard.index'))

    # GET request - show form
    # Get selected food if provided (and not editing)
    if not edit_meal and request.args.get('food_id'):
        selected_food = Food.query.get(request.args.get('food_id'))
    else:
        selected_food = None
    
    # Pre-select meal type from query parameter
    meal_type = request.args.get('meal_type')
    if meal_type in ['breakfast', 'lunch', 'dinner', 'snack']:
        form.meal_type.data = meal_type
    
    # Get recently logged foods for quick access
    recent_foods = db.session.query(Food).join(MealLog).filter(
        MealLog.user_id == current_user.id,
        Food.is_verified == True
    ).distinct().order_by(MealLog.logged_at.desc()).limit(10).all()
    
    # Build JSON-safe selected_food for template
    selected_food_json = None
    if edit_meal:
        try:
            selected_food_json = serialize_food_for_js(edit_meal.food)
        except Exception as e:
            print(f"Error serializing food for edit meal {edit_meal_id}: {e}")
            flash('Error loading food details for edit.', 'warning')

    return render_template(
        'dashboard/log_meal.html',
        title='Log Meal',
        form=form,
        selected_food=selected_food_json,  # <-- dict or None (never ORM)
        recent_foods=recent_foods,
        edit_meal=edit_meal,
    )

@bp.route('/search-foods')
@login_required
def search_foods():
    """Search for verified foods to log."""
    form = FoodSearchForm()
    foods = []
    
    search_query = request.args.get('q', '')
    category_filter = request.args.get('category', '')
    page = request.args.get('page', 1, type=int)
    
    if search_query:
        query = Food.query.filter(Food.is_verified == True)  # Only verified foods
        
        # Text search
        query = query.filter(
            Food.name.contains(search_query) |
            Food.brand.contains(search_query)
        )
        
        # Category filter
        if category_filter:
            query = query.filter(Food.category == category_filter)
        
        # Paginate results
        pagination = query.order_by(Food.name).paginate(
            page=page, per_page=12, error_out=False)
        foods = pagination.items
        
        if not foods and page == 1:
            flash(f'No verified foods found for "{search_query}". Try a different search term.', 'info')
    else:
        pagination = None
    
    # Get categories for filter dropdown
    categories = db.session.query(Food.category).filter(
        Food.is_verified == True,
        Food.category.isnot(None),
        Food.category != ''
    ).distinct().order_by(Food.category).all()
    categories = [cat[0] for cat in categories]
    
    form.search.data = search_query
    form.category.data = category_filter
    
    return render_template('dashboard/search_foods.html', title='Search Foods',
                         form=form, foods=foods, search_query=search_query,
                         categories=categories, pagination=pagination)

@bp.route('/nutrition-goals', methods=['GET', 'POST'])
@login_required
def nutrition_goals():
    """Set nutrition goals."""
    form = NutritionGoalForm()
    current_goal = current_user.get_current_nutrition_goal()
    
    if form.validate_on_submit():
        # Update user's personal information
        current_user.weight = form.weight.data
        current_user.height = form.height.data
        current_user.age = int(form.age.data)
        current_user.gender = form.gender.data
        current_user.activity_level = form.activity_level.data
        
        # Calculate target date if duration is selected but no manual date is set
        target_date = form.target_date.data
        if form.target_duration.data and not target_date:
            target_date = calculate_target_date_from_duration(form.target_duration.data)
        
        # Deactivate current goal if exists
        if current_goal:
            current_goal.is_active = False
        
        # Create new goal
        new_goal = NutritionGoal(
            user_id=current_user.id,
            goal_type=form.goal_type.data,
            target_calories=form.target_calories.data,
            target_protein=form.target_protein.data,
            target_carbs=form.target_carbs.data or 0,
            target_fat=form.target_fat.data or 0,
            target_fiber=form.target_fiber.data or 0,
            target_weight=form.target_weight.data,
            target_duration=form.target_duration.data,
            target_date=target_date,
            goal_date=datetime.utcnow(),
            is_active=True
        )
        
        db.session.add(new_goal)
        db.session.commit()
        
        # Create success message with target date info
        success_msg = 'Nutrition goals updated successfully!'
        if target_date:
            success_msg += f' Target date set for {target_date.strftime("%B %d, %Y")}.'
        
        flash(success_msg, 'success')
        return redirect(url_for('dashboard.index'))
    
    elif request.method == 'GET':
        # Pre-populate form with current user data and goals
        if current_user.weight:
            form.weight.data = current_user.weight
        if current_user.height:
            form.height.data = current_user.height
        if current_user.age:
            form.age.data = current_user.age
        if current_user.gender:
            form.gender.data = current_user.gender
        if current_user.activity_level:
            form.activity_level.data = current_user.activity_level
            
        if current_goal:
            form.goal_type.data = current_goal.goal_type
            form.target_calories.data = current_goal.target_calories
            form.target_protein.data = current_goal.target_protein
            form.target_carbs.data = current_goal.target_carbs
            form.target_fat.data = current_goal.target_fat
            form.target_fiber.data = current_goal.target_fiber
            form.target_weight.data = current_goal.target_weight
            form.target_duration.data = current_goal.target_duration
            form.target_date.data = current_goal.target_date
    
    # Calculate recommended values based on user profile
    recommended = calculate_recommended_nutrition(current_user)
    
    return render_template('dashboard/nutrition_goals.html', title='Nutrition Goals',
                         form=form, current_goal=current_goal, recommended=recommended, today=date.today())

@bp.route('/history')
@login_required
def history():
    """View meal history."""
    page = request.args.get('page', 1, type=int)
    start_date = request.args.get('start_date', '', type=str)
    end_date = request.args.get('end_date', '', type=str)
    meal_type = request.args.get('meal_type', '', type=str)
    
    # Build query
    query = MealLog.query.filter(MealLog.user_id == current_user.id)
    
    if start_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(MealLog.date >= start_date_obj)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(MealLog.date <= end_date_obj)
        except ValueError:
            pass
    
    if meal_type:
        query = query.filter(MealLog.meal_type == meal_type)
    
    # Get paginated results
    pagination = query.order_by(desc(MealLog.date), desc(MealLog.logged_at)).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('dashboard/history.html', title='Meal History',
                         meal_logs=pagination.items, pagination=pagination, 
                         start_date=start_date, end_date=end_date,
                         meal_type=meal_type)

@bp.route('/reports')
@login_required
def reports():
    """View nutrition reports and analytics."""
    # Get period from request parameters (default 30 days)
    period = int(request.args.get('period', 30))
    
    # Get date range based on period
    end_date = date.today()
    start_date = end_date - timedelta(days=period)
    
    # Get daily nutrition data
    daily_data = db.session.query(
        MealLog.date,
        func.sum(MealLog.calories).label('calories'),
        func.sum(MealLog.protein).label('protein'),
        func.sum(MealLog.carbs).label('carbs'),
        func.sum(MealLog.fat).label('fat'),
        func.count(MealLog.id).label('meal_count')
    ).filter(
        MealLog.user_id == current_user.id,
        MealLog.date >= start_date,
        MealLog.date <= end_date
    ).group_by(MealLog.date).order_by(MealLog.date).all()
    
    # Get weekly averages
    if daily_data:
        avg_calories = sum(day.calories or 0 for day in daily_data) / len(daily_data)
        avg_protein = sum(day.protein or 0 for day in daily_data) / len(daily_data)
        avg_carbs = sum(day.carbs or 0 for day in daily_data) / len(daily_data)
        avg_fat = sum(day.fat or 0 for day in daily_data) / len(daily_data)
    else:
        avg_calories = avg_protein = avg_carbs = avg_fat = 0
    
    # Get top foods
    top_foods = db.session.query(
        Food.name,
        func.count(MealLog.id).label('log_count'),
        func.sum(MealLog.quantity).label('total_quantity')
    ).join(MealLog).filter(
        MealLog.user_id == current_user.id,
        MealLog.date >= start_date
    ).group_by(Food.id).order_by(desc('log_count')).limit(10).all()
    
    # Get current goals for comparison
    current_goal = current_user.get_current_nutrition_goal()
    
    # Create summary object that matches template expectations
    summary = type('Summary', (), {
        'avg_calories': avg_calories,
        'avg_protein': avg_protein,
        'avg_carbs': avg_carbs,
        'avg_fat': avg_fat
    })()
    
    return render_template('dashboard/reports.html', title='Reports',
                         daily_data=daily_data, summary=summary, top_foods=top_foods,
                         current_goal=current_goal, start_date=start_date, end_date=end_date, period=period)

@bp.route('/export-data')
@login_required
def export_data():
    """Export nutrition data in CSV or PDF format."""
    
    format_type = request.args.get('format', 'csv').lower()
    period = request.args.get('period', '30').lower()
    
    # Calculate date range based on period
    end_date = datetime.now().date()
    if period == '7':
        start_date = end_date - timedelta(days=7)
        period_name = "Last 7 Days"
    elif period == '30':
        start_date = end_date - timedelta(days=30)
        period_name = "Last 30 Days"
    elif period == '90':
        start_date = end_date - timedelta(days=90)
        period_name = "Last 90 Days"
    else:
        start_date = end_date - timedelta(days=30)
        period_name = "Last 30 Days"
    
    # Get meal logs for the period
    meal_logs = MealLog.query.filter(
        MealLog.user_id == current_user.id,
        MealLog.date >= start_date,
        MealLog.date <= end_date
    ).order_by(MealLog.date.desc(), MealLog.logged_at.desc()).all()
    
    if format_type == 'csv':
        # Create CSV export
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow([
            'Date', 'Meal Type', 'Food Name', 'Brand', 'Quantity', 
            'Calories', 'Protein (g)', 'Carbs (g)', 'Fat (g)', 'Fiber (g)'
        ])
        
        # Write data rows
        for meal_log in meal_logs:
            writer.writerow([
                meal_log.date.strftime('%Y-%m-%d'),
                meal_log.meal_type.title(),
                meal_log.food.name,
                meal_log.food.brand or '',
                f"{meal_log.quantity:.1f}g" if meal_log.quantity else "0.0g",
                f"{meal_log.calories:.1f}" if meal_log.calories else "0.0",
                f"{meal_log.protein:.1f}" if meal_log.protein else "0.0",
                f"{meal_log.carbs:.1f}" if meal_log.carbs else "0.0",
                f"{meal_log.fat:.1f}" if meal_log.fat else "0.0",
                f"{meal_log.fiber:.1f}" if meal_log.fiber else "0.0"
            ])
        
        # Create response
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=nutrition_data_{period}_{end_date.strftime("%Y%m%d")}.csv'
        
        return response
    
    elif format_type == 'pdf':
        # For now, redirect to CSV until PDF library is installed
        flash('PDF export coming soon! Using CSV format instead.', 'info')
        return redirect(url_for('dashboard.export_data', format='csv', period=period))
    
    else:
        flash('Invalid export format. Please use CSV or PDF.', 'error')
        return redirect(url_for('dashboard.reports'))

@bp.route('/delete-meal/<int:meal_id>', methods=['POST'])
@login_required
def delete_meal(meal_id):
    """Delete a meal log entry."""
    meal_log = MealLog.query.filter(
        MealLog.id == meal_id,
        MealLog.user_id == current_user.id
    ).first_or_404()
    
    food_name = meal_log.food.name
    db.session.delete(meal_log)
    db.session.commit()
    
    flash(f'Removed {food_name} from your log.', 'success')
    return redirect(request.referrer or url_for('dashboard.index'))

@bp.route('/challenges')
@login_required
def challenges():
    """View and join challenges."""
    # Get available challenges
    available_challenges = Challenge.query.filter(Challenge.is_active == True).all()
    
    # Get user's active challenges
    user_challenges = UserChallenge.query.filter(
        UserChallenge.user_id == current_user.id,
        UserChallenge.is_completed == False
    ).all()
    
    # Get completed challenges
    completed_challenges = UserChallenge.query.filter(
        UserChallenge.user_id == current_user.id,
        UserChallenge.is_completed == True
    ).order_by(desc(UserChallenge.completed_at)).limit(5).all()
    
    return render_template('dashboard/challenges.html', title='Challenges',
                         available_challenges=available_challenges,
                         user_challenges=user_challenges,
                         completed_challenges=completed_challenges)

@bp.route('/join-challenge/<int:challenge_id>', methods=['POST'])
@login_required
def join_challenge(challenge_id):
    """Join a challenge."""
    challenge = Challenge.query.get_or_404(challenge_id)
    
    # Check if user already joined this challenge
    existing = UserChallenge.query.filter(
        UserChallenge.user_id == current_user.id,
        UserChallenge.challenge_id == challenge_id,
        UserChallenge.is_completed == False
    ).first()
    
    if existing:
        flash('You are already participating in this challenge!', 'warning')
        return redirect(url_for('dashboard.challenges'))
    
    # Create user challenge
    user_challenge = UserChallenge(
        user_id=current_user.id,
        challenge_id=challenge_id,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=challenge.duration_days)
    )
    
    db.session.add(user_challenge)
    db.session.commit()
    
    flash(f'Successfully joined "{challenge.name}" challenge!', 'success')
    return redirect(url_for('dashboard.challenges'))

# Helper functions
def calculate_logging_streak(user_id):
    """Calculate consecutive days of meal logging."""
    today = date.today()
    streak = 0
    current_date = today
    
    while True:
        logs_count = MealLog.query.filter(
            MealLog.user_id == user_id,
            MealLog.date == current_date
        ).count()
        
        if logs_count > 0:
            streak += 1
            current_date -= timedelta(days=1)
        else:
            break
    
    return streak

def calculate_recommended_nutrition(user):
    """Calculate recommended nutrition based on user profile."""
    if not all([user.age, user.gender, user.height, user.weight]):
        return {
            'calories': 2000,
            'protein': 50,
            'carbs': 250,
            'fat': 65,
            'fiber': 25
        }
    
    # Calculate TDEE
    tdee = user.calculate_tdee()
    if not tdee:
        tdee = 2000
    
    # Adjust based on goal
    current_goal = user.get_current_nutrition_goal()
    if current_goal:
        if current_goal.goal_type == 'lose':
            calories = tdee - 500  # 500 calorie deficit
        elif current_goal.goal_type == 'gain':
            calories = tdee + 500  # 500 calorie surplus
        else:
            calories = tdee
    else:
        calories = tdee
    
    # Calculate macros (protein: 0.8-1.2g per kg, carbs: 45-65%, fat: 20-35%)
    protein = user.weight * 1.0  # 1g per kg body weight
    fat = calories * 0.25 / 9  # 25% of calories from fat
    carbs = (calories - (protein * 4) - (fat * 9)) / 4  # Remaining calories from carbs
    fiber = calories / 80  # Rough estimate
    
    return {
        'calories': round(calories),
        'protein': round(protein),
        'carbs': round(carbs),
        'fat': round(fat),
        'fiber': round(fiber)
    }
