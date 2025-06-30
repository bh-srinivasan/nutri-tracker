import csv
import io
from datetime import datetime, timedelta
from flask import render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import desc, func
from app import db
from app.admin import bp
from app.admin.forms import (
    FoodForm, UserManagementForm, AdminPasswordForm, ResetUserPasswordForm,
    ChallengeForm, BulkFoodUploadForm
)
from app.models import User, Food, MealLog, NutritionGoal, Challenge, UserChallenge

def admin_required(f):
    """Decorator to require admin access."""
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You need admin privileges to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with statistics."""
    # Get statistics
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    total_foods = Food.query.count()
    verified_foods = Food.query.filter_by(is_verified=True).count()
    
    # Recent activity
    recent_users = User.query.order_by(desc(User.created_at)).limit(5).all()
    recent_foods = Food.query.order_by(desc(Food.created_at)).limit(5).all()
    
    # User activity in last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    active_users_30d = User.query.filter(User.last_login >= thirty_days_ago).count()
    
    # Meal logs in last 7 days
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_logs = MealLog.query.filter(MealLog.logged_at >= seven_days_ago).count()
    
    stats = {
        'total_users': total_users,
        'active_users': active_users,
        'total_foods': total_foods,
        'verified_foods': verified_foods,
        'active_users_30d': active_users_30d,
        'recent_logs': recent_logs
    }
    
    return render_template('admin/dashboard.html', title='Admin Dashboard',
                         stats=stats, recent_users=recent_users, recent_foods=recent_foods)

# User Management Routes
@bp.route('/users')
@login_required
@admin_required
def users():
    """List all users."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    
    query = User.query
    if search:
        query = query.filter(
            User.username.contains(search) |
            User.email.contains(search) |
            User.first_name.contains(search) |
            User.last_name.contains(search)
        )
    
    users = query.order_by(desc(User.created_at)).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/users.html', title='User Management',
                         users=users, search=search)

@bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Edit user details."""
    user = User.query.get_or_404(user_id)
    form = UserManagementForm()
    
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.is_admin = form.is_admin.data
        user.is_active = form.is_active.data
        
        db.session.commit()
        flash(f'User {user.username} updated successfully!', 'success')
        return redirect(url_for('admin.users'))
    
    elif request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        form.first_name.data = user.first_name
        form.last_name.data = user.last_name
        form.is_admin.data = user.is_admin
        form.is_active.data = user.is_active
    
    return render_template('admin/edit_user.html', title='Edit User', form=form, user=user)

@bp.route('/users/<int:user_id>/reset-password', methods=['GET', 'POST'])
@login_required
@admin_required
def reset_user_password(user_id):
    """Reset user password."""
    user = User.query.get_or_404(user_id)
    form = ResetUserPasswordForm()
    
    if form.validate_on_submit():
        user.set_password(form.new_password.data)
        db.session.commit()
        flash(f'Password reset for user {user.username}!', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/reset_password.html', title='Reset Password', form=form, user=user)

@bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete user account."""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('You cannot delete your own account!', 'danger')
        return redirect(url_for('admin.users'))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {username} deleted successfully!', 'success')
    return redirect(url_for('admin.users'))

# Food Management Routes
@bp.route('/foods')
@login_required
@admin_required
def foods():
    """List all food items."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    category = request.args.get('category', '', type=str)
    
    query = Food.query
    if search:
        query = query.filter(
            Food.name.contains(search) |
            Food.brand.contains(search)
        )
    if category:
        query = query.filter(Food.category == category)
    
    foods = query.order_by(desc(Food.created_at)).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Get categories for filter
    categories = db.session.query(Food.category).distinct().all()
    categories = [cat[0] for cat in categories if cat[0]]
    
    return render_template('admin/foods.html', title='Food Management',
                         foods=foods, search=search, category=category, categories=categories)

@bp.route('/foods/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_food():
    """Add new food item."""
    form = FoodForm()
    
    if form.validate_on_submit():
        food = Food(
            name=form.name.data,
            brand=form.brand.data,
            category=form.category.data,
            calories=form.calories.data,
            protein=form.protein.data,
            carbs=form.carbs.data,
            fat=form.fat.data,
            fiber=form.fiber.data or 0,
            sugar=form.sugar.data or 0,
            sodium=form.sodium.data or 0,
            serving_size=form.serving_size.data or 100,
            is_verified=form.is_verified.data,
            created_by=current_user.id
        )
        
        db.session.add(food)
        db.session.commit()
        
        flash(f'Food item "{food.name}" added successfully!', 'success')
        return redirect(url_for('admin.foods'))
    
    return render_template('admin/add_food.html', title='Add Food', form=form)

@bp.route('/foods/<int:food_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_food(food_id):
    """Edit food item."""
    food = Food.query.get_or_404(food_id)
    form = FoodForm()
    
    if form.validate_on_submit():
        food.name = form.name.data
        food.brand = form.brand.data
        food.category = form.category.data
        food.calories = form.calories.data
        food.protein = form.protein.data
        food.carbs = form.carbs.data
        food.fat = form.fat.data
        food.fiber = form.fiber.data or 0
        food.sugar = form.sugar.data or 0
        food.sodium = form.sodium.data or 0
        food.serving_size = form.serving_size.data or 100
        food.is_verified = form.is_verified.data
        
        db.session.commit()
        flash(f'Food item "{food.name}" updated successfully!', 'success')
        return redirect(url_for('admin.foods'))
    
    elif request.method == 'GET':
        form.name.data = food.name
        form.brand.data = food.brand
        form.category.data = food.category
        form.calories.data = food.calories
        form.protein.data = food.protein
        form.carbs.data = food.carbs
        form.fat.data = food.fat
        form.fiber.data = food.fiber
        form.sugar.data = food.sugar
        form.sodium.data = food.sodium
        form.serving_size.data = food.serving_size
        form.is_verified.data = food.is_verified
    
    return render_template('admin/edit_food.html', title='Edit Food', form=form, food=food)

@bp.route('/foods/<int:food_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_food(food_id):
    """Delete food item."""
    food = Food.query.get_or_404(food_id)
    
    # Check if food is used in meal logs
    meal_logs_count = MealLog.query.filter_by(food_id=food_id).count()
    if meal_logs_count > 0:
        flash(f'Cannot delete "{food.name}" as it is used in {meal_logs_count} meal logs.', 'danger')
        return redirect(url_for('admin.foods'))
    
    food_name = food.name
    db.session.delete(food)
    db.session.commit()
    
    flash(f'Food item "{food_name}" deleted successfully!', 'success')
    return redirect(url_for('admin.foods'))

@bp.route('/foods/bulk-upload', methods=['GET', 'POST'])
@login_required
@admin_required
def bulk_upload_foods():
    """Bulk upload foods via CSV."""
    form = BulkFoodUploadForm()
    
    if form.validate_on_submit():
        try:
            csv_data = form.csv_data.data
            csv_reader = csv.DictReader(io.StringIO(csv_data))
            
            foods_added = 0
            errors = []
            
            for row_num, row in enumerate(csv_reader, start=2):
                try:
                    food = Food(
                        name=row.get('name', '').strip(),
                        brand=row.get('brand', '').strip() or None,
                        category=row.get('category', '').strip(),
                        calories=float(row.get('calories', 0)),
                        protein=float(row.get('protein', 0)),
                        carbs=float(row.get('carbs', 0)),
                        fat=float(row.get('fat', 0)),
                        fiber=float(row.get('fiber', 0)) if row.get('fiber') else 0,
                        sugar=float(row.get('sugar', 0)) if row.get('sugar') else 0,
                        sodium=float(row.get('sodium', 0)) if row.get('sodium') else 0,
                        serving_size=float(row.get('serving_size', 100)) if row.get('serving_size') else 100,
                        is_verified=True,
                        created_by=current_user.id
                    )
                    
                    if not food.name or not food.category:
                        errors.append(f"Row {row_num}: Name and category are required")
                        continue
                    
                    db.session.add(food)
                    foods_added += 1
                    
                except (ValueError, KeyError) as e:
                    errors.append(f"Row {row_num}: {str(e)}")
            
            if foods_added > 0:
                db.session.commit()
                flash(f'Successfully added {foods_added} food items!', 'success')
            
            if errors:
                for error in errors[:5]:  # Show first 5 errors
                    flash(error, 'warning')
                if len(errors) > 5:
                    flash(f'...and {len(errors) - 5} more errors', 'warning')
            
            return redirect(url_for('admin.foods'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error processing CSV: {str(e)}', 'danger')
    
    return render_template('admin/bulk_upload.html', title='Bulk Upload Foods', form=form)

@bp.route('/change-password', methods=['GET', 'POST'])
@login_required
@admin_required
def change_password():
    """Admin change password."""
    form = AdminPasswordForm()
    
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('admin.change_password'))
        
        current_user.set_password(form.new_password.data)
        db.session.commit()
        
        flash('Password changed successfully!', 'success')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/change_password.html', title='Change Password', form=form)
