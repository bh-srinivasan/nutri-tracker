import csv
import io
import json
from datetime import datetime, timedelta
from flask import render_template, redirect, url_for, flash, request, jsonify, current_app, session
from flask_login import login_required, current_user
from sqlalchemy import desc, func
from app import db
from app.admin import bp
from app.admin.forms import (
    FoodForm, UserManagementForm, AdminPasswordForm, ResetUserPasswordForm,
    ChallengeForm, BulkFoodUploadForm
)
from app.models import User, Food, MealLog, NutritionGoal, Challenge, UserChallenge, FoodServing
from app.services.bulk_upload_processor import BulkUploadProcessor
from app.services.food_export_service import FoodExportService
from app.models import BulkUploadJob, ExportJob, ServingUploadJob, ServingUploadJobItem
from flask_wtf.csrf import generate_csrf

# Security: Rate limiting for bulk upload
from functools import wraps
from datetime import datetime, timedelta
import json

# In-memory rate limiting (for production, use Redis or database)
upload_attempts = {}

def rate_limit_upload(max_attempts=3, window_minutes=10):
    """
    Rate limiting decorator for upload endpoints.
    
    Args:
        max_attempts: Maximum attempts allowed
        window_minutes: Time window in minutes
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.remote_addr
            user_id = current_user.id if current_user.is_authenticated else None
            
            # Create unique key for rate limiting
            rate_key = f"{client_ip}_{user_id}" if user_id else client_ip
            now = datetime.utcnow()
            
            # Clean old entries
            cutoff_time = now - timedelta(minutes=window_minutes)
            if rate_key in upload_attempts:
                upload_attempts[rate_key] = [
                    attempt for attempt in upload_attempts[rate_key] 
                    if attempt > cutoff_time
                ]
            
            # Check rate limit
            attempts = upload_attempts.get(rate_key, [])
            if len(attempts) >= max_attempts:
                current_app.logger.warning(
                    f"[SECURITY] Rate limit exceeded for {rate_key}. "
                    f"Attempts: {len(attempts)} in {window_minutes} minutes"
                )
                return jsonify({
                    'error': f'Rate limit exceeded. Maximum {max_attempts} attempts per {window_minutes} minutes.'
                }), 429
            
            # Record this attempt
            if rate_key not in upload_attempts:
                upload_attempts[rate_key] = []
            upload_attempts[rate_key].append(now)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Decorator to require admin access."""
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You need admin privileges to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@bp.route('/')
@login_required
@admin_required
def index():
    """Admin root route - redirects to dashboard."""
    return redirect(url_for('admin.dashboard'))

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
    
    # Get pending jobs count for unified food uploads interface
    pending_jobs_count = BulkUploadJob.query.filter(
        BulkUploadJob.created_by == current_user.id,
        BulkUploadJob.status.in_(['pending', 'processing'])
    ).count() if current_user.is_authenticated else 0
    
    return render_template('admin/dashboard.html', title='Admin Dashboard',
                         stats=stats, recent_users=recent_users, recent_foods=recent_foods,
                         pending_jobs_count=pending_jobs_count)

# User Management Routes
@bp.route('/users')
@login_required
@admin_required
def users():
    """List all users."""
    try:
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '', type=str)
        status = request.args.get('status', '', type=str)
        role = request.args.get('role', '', type=str)
        show_details = request.args.get('show_details', '') == '1'
        
        # Filter out admin users from the main list
        query = User.query.filter(User.is_admin == False)
        
        if search:
            search_filter = f'%{search}%'
            query = query.filter(
                User.username.like(search_filter) |
                User.email.like(search_filter) |
                User.first_name.like(search_filter) |
                User.last_name.like(search_filter)
            )
        
        # Status filter
        if status == 'active':
            query = query.filter(User.is_active == True)
        elif status == 'inactive':
            query = query.filter(User.is_active == False)
        
        # Role filter (although all non-admin users will be 'user' role)
        if role == 'user':
            query = query.filter(User.is_admin == False)
        
        users_pagination = query.order_by(User.id.asc()).paginate(
            page=page, per_page=20, error_out=False
        )
        
        # Debug logging
        current_app.logger.info(f'Users page accessed - Page: {page}, Search: "{search}", Show details: {show_details}')
        current_app.logger.info(f'Query found {len(users_pagination.items)} users')
        for user in users_pagination.items:
            current_app.logger.info(f'  - {user.username} ({user.email}) - Admin: {user.is_admin}, Active: {user.is_active}')
        
        return render_template('admin/users.html', title='User Management',
                             users=users_pagination.items, pagination=users_pagination, 
                             search=search, show_details=show_details)
    except Exception as e:
        current_app.logger.error(f'Error loading users: {str(e)}')
        flash(f'Error loading users: {str(e)}', 'danger')
        # Return empty data with safe defaults
        return render_template('admin/users.html', title='User Management',
                             users=[], pagination=None, search=search or '', show_details=show_details)

@bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Edit user details."""
    user = User.query.get_or_404(user_id)
    form = UserManagementForm(user_id=user_id)
    
    if form.validate_on_submit():
        try:
            user.username = form.username.data
            user.email = form.email.data
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.is_admin = form.is_admin.data
            user.is_active = form.is_active.data
            
            db.session.commit()
            flash(f'User {user.username} updated successfully!', 'success')
            return redirect(url_for('admin.users'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating user: {str(e)}', 'danger')
    
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
    """
    Enhanced food management with secure sorting and comprehensive data protection.
    
    Security Features:
    - Input validation and sanitization
    - SQL injection prevention via SQLAlchemy ORM
    - XSS protection through proper escaping
    - Comprehensive audit logging
    - Role-based access control
    """
    import re
    from sqlalchemy import asc, desc, func
    
    try:
        # Security: Log access attempt with user details
        current_app.logger.info(
            f"[AUDIT] Food management accessed by user {current_user.id} ({current_user.email}) "
            f"from IP: {request.remote_addr} at {datetime.utcnow().isoformat()}"
        )
        
        # Security: Input validation and sanitization
        page = max(1, request.args.get('page', 1, type=int))  # Ensure positive page number
        search = request.args.get('search', '', type=str).strip()[:100]  # Limit length, strip whitespace
        category = request.args.get('category', '', type=str).strip()[:50]
        status = request.args.get('status', '', type=str).strip()[:20]
        brand = request.args.get('brand', '', type=str).strip()[:100]
        sort_by = request.args.get('sort', '', type=str).strip()[:20]
        order = request.args.get('order', 'asc', type=str).strip().lower()
        
        # Security: Validate sort parameters against whitelist
        ALLOWED_SORT_COLUMNS = {
            'id': Food.id,
            'name': Food.name,
            'brand': Food.brand,
            'category': Food.category,
            'calories': Food.calories,
            'protein': Food.protein,
            'status': Food.is_verified,
            'created_at': Food.created_at
        }
        
        # Security: Validate order parameter
        if order not in ['asc', 'desc']:
            order = 'asc'
        
        # Security: Sanitize search input to prevent injection attacks
        if search:
            # Remove potentially dangerous characters but keep spaces and alphanumeric
            search = re.sub(r'[^\w\s\-\(\)\[\]\.]', '', search)
            if len(search.strip()) == 0:
                search = ''
        
        # Security: Validate category against known categories
        if category:
            valid_categories = db.session.query(Food.category).distinct().scalar_subquery()
            category_exists = db.session.query(
                db.session.query(valid_categories).filter(valid_categories == category).exists()
            ).scalar()
            if not category_exists:
                category = ''
        
        # Security: Validate status parameter
        if status and status not in ['verified', 'pending']:
            status = ''
        
        # Build secure query using SQLAlchemy ORM (prevents SQL injection)
        query = Food.query
        
        # Apply search filter with security
        if search:
            search_filter = f'%{search}%'
            query = query.filter(
                db.or_(
                    Food.name.ilike(search_filter),
                    db.and_(Food.brand.isnot(None), Food.brand.ilike(search_filter))
                )
            )
            
            # Security: Log search for audit trail
            current_app.logger.info(
                f"[AUDIT] Food search performed by user {current_user.id}: '{search}'"
            )
        
        # Apply category filter
        if category:
            query = query.filter(Food.category == category)
        
        # Apply status filter
        if status:
            is_verified = (status == 'verified')
            query = query.filter(Food.is_verified == is_verified)
        
        # Apply brand filter
        if brand:
            brand_filter = f'%{brand}%'
            query = query.filter(
                db.and_(Food.brand.isnot(None), Food.brand.ilike(brand_filter))
            )
        
        # Apply secure sorting
        if sort_by and sort_by in ALLOWED_SORT_COLUMNS:
            sort_column = ALLOWED_SORT_COLUMNS[sort_by]
            if order == 'desc':
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
                
            # Security: Log sort action for audit trail
            current_app.logger.info(
                f"[AUDIT] Food table sorted by user {current_user.id}: {sort_by} {order}"
            )
        else:
            # Default sort by ID ascending
            query = query.order_by(asc(Food.id))
        
        # Execute paginated query with error handling
        try:
            foods_pagination = query.paginate(
                page=page, 
                per_page=20, 
                error_out=False,
                max_per_page=100  # Security: Limit max items per page
            )
        except Exception as e:
            current_app.logger.error(f"[SECURITY] Pagination error for user {current_user.id}: {str(e)}")
            foods_pagination = Food.query.limit(20).offset(0).paginate(
                page=1, per_page=20, error_out=False
            )
        
        # Get categories for filter with security
        try:
            categories = db.session.query(Food.category).distinct().filter(
                Food.category.isnot(None),
                Food.category != ''
            ).order_by(Food.category).all()
            categories = [cat[0] for cat in categories]
        except Exception as e:
            current_app.logger.error(f"[SECURITY] Error fetching categories: {str(e)}")
            categories = []
        
        # Security: Log successful data access
        current_app.logger.info(
            f"[AUDIT] Food data accessed by user {current_user.id}: "
            f"{len(foods_pagination.items)} records on page {page}"
        )
        
        # Security: Sanitize output data before rendering
        for food in foods_pagination.items:
            if food.name:
                food.name = food.name.strip()
            if food.brand:
                food.brand = food.brand.strip()
            if food.category:
                food.category = food.category.strip()
        
        return render_template(
            'admin/foods.html', 
            title='Food Management',
            foods=foods_pagination.items, 
            pagination=foods_pagination, 
            search=search, 
            category=category,
            status=status,
            brand=brand,
            categories=categories,
            current_sort=sort_by,
            current_order=order
        )
        
    except Exception as e:
        # Security: Log error without exposing sensitive information
        current_app.logger.error(
            f'[SECURITY] Error in food management for user {current_user.id}: {str(e)}',
            exc_info=True
        )
        flash('An error occurred while loading foods. Please try again.', 'danger')
        
        # Return safe fallback with empty data
        return render_template(
            'admin/foods.html', 
            title='Food Management',
            foods=[], 
            pagination=None, 
            search='', 
            category='',
            status='',
            brand='',
            categories=[],
            current_sort='',
            current_order='asc'
        )

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
    """
    Enhanced food editing with comprehensive security and audit logging.
    
    Security Features:
    - Input validation and sanitization
    - Data integrity checks
    - Audit trail logging
    - Transaction safety
    - XSS prevention
    """
    import re
    from decimal import Decimal, InvalidOperation
    
    try:
        # Security: Validate food_id parameter
        if food_id <= 0 or food_id > 999999999:  # Reasonable upper limit
            current_app.logger.warning(
                f"[SECURITY] Invalid food_id {food_id} accessed by user {current_user.id}"
            )
            flash('Invalid food ID.', 'danger')
            return redirect(url_for('admin.foods'))
        
        # Security: Log edit attempt
        current_app.logger.info(
            f"[AUDIT] Food edit attempt - Food ID: {food_id}, User: {current_user.id} ({current_user.email}) "
            f"from IP: {request.remote_addr} at {datetime.utcnow().isoformat()}"
        )
        
        food = Food.query.get_or_404(food_id)
        form = FoodForm()
        
        # Debug: Log form validation status
        current_app.logger.debug(f"Form validation for food {food_id}: valid={form.validate_on_submit()}")
        if not form.validate_on_submit() and request.method == 'POST':
            current_app.logger.debug(f"Form errors: {form.errors}")
            current_app.logger.debug(f"Form data: {request.form}")
        
        if form.validate_on_submit():
            try:
                # Security: Store original values for audit trail
                original_values = {
                    'name': food.name,
                    'brand': food.brand,
                    'category': food.category,
                    'calories': food.calories,
                    'protein': food.protein,
                    'carbs': food.carbs,
                    'fat': food.fat,
                    'fiber': food.fiber,
                    'sugar': food.sugar,
                    'sodium': food.sodium,
                    'serving_size': food.serving_size,
                    'is_verified': food.is_verified
                }
                
                # Security: Input validation and sanitization
                def sanitize_text(text, max_length=100):
                    if not text:
                        return ""  # Return empty string instead of None
                    # Remove potentially dangerous characters, keep alphanumeric, spaces, and basic punctuation
                    sanitized = re.sub(r'[<>"\']', '', str(text).strip())
                    return sanitized[:max_length] if sanitized else ""
                
                def validate_numeric(value, min_val=0, max_val=10000):
                    try:
                        num_val = float(value) if value is not None else 0
                        return max(min_val, min(num_val, max_val))
                    except (ValueError, TypeError):
                        return 0
                
                # Security: Sanitize and validate all inputs
                food.name = sanitize_text(form.name.data, 100)
                food.brand = sanitize_text(form.brand.data, 50) or None  # Keep None for optional fields
                food.category = sanitize_text(form.category.data, 50)
                
                # Security: Validate nutritional values
                food.calories = validate_numeric(form.calories.data, 0, 1000)
                food.protein = validate_numeric(form.protein.data, 0, 100)
                food.carbs = validate_numeric(form.carbs.data, 0, 100)
                food.fat = validate_numeric(form.fat.data, 0, 100)
                food.fiber = validate_numeric(form.fiber.data, 0, 100)
                food.sugar = validate_numeric(form.sugar.data, 0, 100)
                food.sodium = validate_numeric(form.sodium.data, 0, 50000)  # mg
                food.serving_size = validate_numeric(form.serving_size.data, 1, 1000)
                
                # Security: Validate required fields
                if not food.name or len(food.name.strip()) == 0:
                    flash('Food name is required and cannot be empty.', 'danger')
                    servings = FoodServing.query.filter_by(food_id=food_id).order_by(FoodServing.serving_name).all()
                    return render_template('admin/edit_food.html', title='Edit Food', form=form, food=food, servings=servings)
                
                if not food.category or len(food.category.strip()) == 0:
                    flash('Food category is required and cannot be empty.', 'danger')
                    servings = FoodServing.query.filter_by(food_id=food_id).order_by(FoodServing.serving_name).all()
                    return render_template('admin/edit_food.html', title='Edit Food', form=form, food=food, servings=servings)
                
                # Security: Check for duplicate food names (excluding current food)
                existing_food = Food.query.filter(
                    Food.name.ilike(food.name.strip()),
                    Food.id != food_id
                ).first()
                
                if existing_food:
                    if food.brand and existing_food.brand:
                        if food.brand.lower() == existing_food.brand.lower():
                            flash(f'A food item with name "{food.name}" and brand "{food.brand}" already exists.', 'warning')
                            servings = FoodServing.query.filter_by(food_id=food_id).order_by(FoodServing.serving_name).all()
                            return render_template('admin/edit_food.html', title='Edit Food', form=form, food=food, servings=servings)
                    elif not food.brand and not existing_food.brand:
                        flash(f'A food item with name "{food.name}" already exists.', 'warning')
                        servings = FoodServing.query.filter_by(food_id=food_id).order_by(FoodServing.serving_name).all()
                        return render_template('admin/edit_food.html', title='Edit Food', form=form, food=food, servings=servings)
                
                # Security: Validate verification status change
                if hasattr(form, 'is_verified'):
                    food.is_verified = bool(form.is_verified.data)
                
                # Security: Use database transaction for atomicity - let SQLAlchemy handle it
                try:
                    db.session.commit()
                except Exception as commit_error:
                    db.session.rollback()
                    raise commit_error
                
                # Security: Log all changes for audit trail
                changes = []
                for field, original_value in original_values.items():
                    new_value = getattr(food, field)
                    if original_value != new_value:
                        changes.append(f"{field}: '{original_value}' -> '{new_value}'")
                
                if changes:
                    current_app.logger.info(
                        f"[AUDIT] Food {food_id} updated by user {current_user.id}: {'; '.join(changes)}"
                    )
                else:
                    current_app.logger.info(
                        f"[AUDIT] Food {food_id} edit submitted by user {current_user.id} with no changes"
                    )
                
                flash(f'Food item "{food.name}" updated successfully!', 'success')
                return redirect(url_for('admin.edit_food', food_id=food_id))
                
            except Exception as e:
                # Security: Rollback transaction on error
                db.session.rollback()
                current_app.logger.error(
                    f"[SECURITY] Food edit error for food {food_id} by user {current_user.id}: {str(e)}",
                    exc_info=True
                )
                flash('An error occurred while updating the food item. Please try again.', 'danger')
                servings = FoodServing.query.filter_by(food_id=food_id).order_by(FoodServing.serving_name).all()
                return render_template('admin/edit_food.html', title='Edit Food', form=form, food=food, servings=servings)
        
        elif request.method == 'GET':
            # Security: Populate form with sanitized data
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
            if hasattr(form, 'is_verified'):
                form.is_verified.data = food.is_verified
        
        # Get servings for this food
        servings = FoodServing.query.filter_by(food_id=food_id).order_by(FoodServing.serving_name).all()
        
        return render_template('admin/edit_food.html', title='Edit Food', form=form, food=food, servings=servings)
        
    except Exception as e:
        current_app.logger.error(
            f"[SECURITY] Unexpected error in food edit for food {food_id} by user {current_user.id}: {str(e)}",
            exc_info=True
        )
        flash('An unexpected error occurred. Please try again.', 'danger')
        return redirect(url_for('admin.foods'))

@bp.route('/foods/<int:food_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_food(food_id):
    """
    Enhanced food deletion with comprehensive security and data integrity checks.
    
    Security Features:
    - Referential integrity validation
    - Audit trail logging
    - Transaction safety
    - Input validation
    - Cascade impact analysis
    """
    try:
        # Security: Validate food_id parameter
        if food_id <= 0 or food_id > 999999999:
            current_app.logger.warning(
                f"[SECURITY] Invalid food_id {food_id} for deletion by user {current_user.id}"
            )
            return jsonify({'error': 'Invalid food ID'}), 400
        
        # Security: Log deletion attempt
        current_app.logger.info(
            f"[AUDIT] Food deletion attempt - Food ID: {food_id}, User: {current_user.id} ({current_user.email}) "
            f"from IP: {request.remote_addr} at {datetime.utcnow().isoformat()}"
        )
        
        food = Food.query.get_or_404(food_id)
        
        # Security: Store food details for audit trail before deletion
        food_details = {
            'id': food.id,
            'name': food.name,
            'brand': food.brand,
            'category': food.category,
            'created_by': food.created_by,
            'created_at': food.created_at.isoformat() if food.created_at else None
        }
        
        # Security: Check referential integrity - prevent deletion if food is referenced
        try:
            meal_logs_count = MealLog.query.filter_by(food_id=food_id).count()
            
            if meal_logs_count > 0:
                current_app.logger.warning(
                    f"[AUDIT] Food deletion blocked - Food {food_id} '{food.name}' is referenced by {meal_logs_count} meal logs. "
                    f"Attempted by user {current_user.id}"
                )
                
                if request.is_json:
                    return jsonify({
                        'error': f'Cannot delete "{food.name}" as it is used in {meal_logs_count} meal logs.'
                    }), 409
                else:
                    flash(f'Cannot delete "{food.name}" as it is used in {meal_logs_count} meal logs.', 'danger')
                    return redirect(url_for('admin.foods'))
            
            # Security: Check for other potential references (nutrition goals, etc.)
            # Add additional referential integrity checks here as needed
            
        except Exception as e:
            current_app.logger.error(
                f"[SECURITY] Error checking referential integrity for food {food_id}: {str(e)}"
            )
            if request.is_json:
                return jsonify({'error': 'Error checking data integrity'}), 500
            else:
                flash('Error checking data integrity. Please try again.', 'danger')
                return redirect(url_for('admin.foods'))
        
        # Security: Use transaction for atomicity
        try:
            food_name = food.name
            db.session.begin()
            db.session.delete(food)
            db.session.commit()
            
            # Security: Log successful deletion with full audit details
            current_app.logger.info(
                f"[AUDIT] Food successfully deleted by user {current_user.id}: "
                f"ID: {food_details['id']}, Name: '{food_details['name']}', "
                f"Brand: '{food_details['brand']}', Category: '{food_details['category']}', "
                f"Originally created by user: {food_details['created_by']}"
            )
            
            if request.is_json:
                return jsonify({
                    'success': True,
                    'message': f'Food item "{food_name}" deleted successfully!'
                })
            else:
                flash(f'Food item "{food_name}" deleted successfully!', 'success')
                return redirect(url_for('admin.foods'))
                
        except Exception as e:
            # Security: Rollback transaction on error
            db.session.rollback()
            current_app.logger.error(
                f"[SECURITY] Food deletion failed for food {food_id} by user {current_user.id}: {str(e)}",
                exc_info=True
            )
            
            if request.is_json:
                return jsonify({'error': 'Failed to delete food item'}), 500
            else:
                flash('Failed to delete food item. Please try again.', 'danger')
                return redirect(url_for('admin.foods'))
                
    except Exception as e:
        current_app.logger.error(
            f"[SECURITY] Unexpected error in food deletion for food {food_id} by user {current_user.id}: {str(e)}",
            exc_info=True
        )
        
        if request.is_json:
            return jsonify({'error': 'An unexpected error occurred'}), 500
        else:
            flash('An unexpected error occurred. Please try again.', 'danger')
            return redirect(url_for('admin.foods'))

# Food Serving Management Routes
@bp.route('/foods/<int:food_id>/servings/add', methods=['POST'])
@login_required
@admin_required
def add_food_serving(food_id):
    """Add a new serving to a food item."""
    try:
        food = Food.query.get_or_404(food_id)
        
        # Get form data
        serving_name = request.form.get('serving_name', '').strip()
        unit = request.form.get('unit', '').strip()
        grams_per_unit = request.form.get('grams_per_unit', '').strip()
        
        # Validation
        if not serving_name or not unit or not grams_per_unit:
            return jsonify({'error': 'All fields are required'}), 400
        
        try:
            grams_per_unit = float(grams_per_unit)
            if grams_per_unit <= 0:
                return jsonify({'error': 'Grams per unit must be greater than 0'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid grams per unit value'}), 400
        
        # Check for duplicate serving name and unit for this food (case-insensitive)
        existing_serving = FoodServing.query.filter(
            FoodServing.food_id == food_id,
            func.lower(FoodServing.serving_name) == func.lower(serving_name),
            func.lower(FoodServing.unit) == func.lower(unit)
        ).first()
        
        if existing_serving:
            return jsonify({'error': 'A serving with this name and unit already exists'}), 409
        
        # Create new serving
        serving = FoodServing(
            food_id=food_id,
            serving_name=serving_name,
            unit=unit,
            grams_per_unit=grams_per_unit,
            created_by=current_user.id
        )
        
        db.session.add(serving)
        db.session.commit()
        
        current_app.logger.info(f"Food serving added by user {current_user.id}: Food {food_id}, Serving '{serving_name}'")
        
        return jsonify({
            'success': True,
            'serving': {
                'id': serving.id,
                'serving_name': serving.serving_name,
                'unit': serving.unit,
                'grams_per_unit': serving.grams_per_unit,
                'is_default': food.default_serving_id == serving.id
            }
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error adding serving to food {food_id}: {str(e)}")
        return jsonify({'error': 'Failed to add serving'}), 500

@bp.route('/foods/<int:food_id>/servings/<int:serving_id>/edit', methods=['POST'])
@login_required
@admin_required
def edit_food_serving(food_id, serving_id):
    """Edit an existing serving."""
    try:
        food = Food.query.get_or_404(food_id)
        serving = FoodServing.query.filter_by(id=serving_id, food_id=food_id).first_or_404()
        
        # Get form data
        serving_name = request.form.get('serving_name', '').strip()
        unit = request.form.get('unit', '').strip()
        grams_per_unit = request.form.get('grams_per_unit', '').strip()
        
        # Validation
        if not serving_name or not unit or not grams_per_unit:
            return jsonify({'error': 'All fields are required'}), 400
        
        try:
            grams_per_unit = float(grams_per_unit)
            if grams_per_unit <= 0:
                return jsonify({'error': 'Grams per unit must be greater than 0'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid grams per unit value'}), 400
        
        # Check for duplicate serving name (excluding current serving)
        existing_serving = FoodServing.query.filter(
            FoodServing.food_id == food_id,
            FoodServing.serving_name == serving_name,
            FoodServing.id != serving_id
        ).first()
        
        if existing_serving:
            return jsonify({'error': 'A serving with this name already exists for this food'}), 400
        
        # Update serving
        serving.serving_name = serving_name
        serving.unit = unit
        serving.grams_per_unit = grams_per_unit
        
        db.session.commit()
        
        current_app.logger.info(f"Food serving edited by user {current_user.id}: Food {food_id}, Serving {serving_id}")
        
        return jsonify({
            'success': True,
            'serving': {
                'id': serving.id,
                'serving_name': serving.serving_name,
                'unit': serving.unit,
                'grams_per_unit': serving.grams_per_unit,
                'is_default': food.default_serving_id == serving.id
            }
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error editing serving {serving_id} for food {food_id}: {str(e)}")
        return jsonify({'error': 'Failed to edit serving'}), 500

@bp.route('/foods/<int:food_id>/servings/<int:serving_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_food_serving(food_id, serving_id):
    """Delete a serving."""
    try:
        food = Food.query.get_or_404(food_id)
        serving = FoodServing.query.filter_by(id=serving_id, food_id=food_id).first_or_404()
        
        # Check if this serving is referenced in meal logs
        from app.models import MealLog
        meal_log_count = MealLog.query.filter_by(serving_id=serving_id).count()
        
        if meal_log_count > 0:
            return jsonify({
                'error': f'Cannot delete this serving as it is used in {meal_log_count} meal logs'
            }), 409
        
        # If this is the default serving, clear the default
        if food.default_serving_id == serving_id:
            food.default_serving_id = None
        
        db.session.delete(serving)
        db.session.commit()
        
        current_app.logger.info(f"Food serving deleted by user {current_user.id}: Food {food_id}, Serving {serving_id}")
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting serving {serving_id} for food {food_id}: {str(e)}")
        return jsonify({'error': 'Failed to delete serving'}), 500

@bp.route('/foods/<int:food_id>/servings/<int:serving_id>/set-default', methods=['POST'])
@login_required
@admin_required
def set_default_serving(food_id, serving_id):
    """Set a serving as the default for a food item."""
    try:
        food = Food.query.get_or_404(food_id)
        serving = FoodServing.query.filter_by(id=serving_id, food_id=food_id).first_or_404()
        
        # Set as default
        food.default_serving_id = serving_id
        db.session.commit()
        
        current_app.logger.info(f"Default serving set by user {current_user.id}: Food {food_id}, Serving {serving_id}")
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error setting default serving {serving_id} for food {food_id}: {str(e)}")
        return jsonify({'error': 'Failed to set default serving'}), 500

@bp.route('/foods/<int:food_id>/servings/<int:serving_id>/unset-default', methods=['POST'])
@login_required
@admin_required
def unset_default_serving(food_id, serving_id):
    """Unset a serving as the default for a food item."""
    try:
        food = Food.query.get_or_404(food_id)
        
        if food.default_serving_id == serving_id:
            food.default_serving_id = None
            db.session.commit()
        
        current_app.logger.info(f"Default serving unset by user {current_user.id}: Food {food_id}, Serving {serving_id}")
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error unsetting default serving {serving_id} for food {food_id}: {str(e)}")
        return jsonify({'error': 'Failed to unset default serving'}), 500

@bp.route('/foods/bulk-upload', methods=['GET'])
@login_required
@admin_required
def bulk_upload_foods():
    """
    Redesigned bulk upload page with enhanced security and single async upload method.
    
    Security Features:
    - File type validation (CSV only)
    - File size limits (10MB max)
    - Content validation before processing
    - User action logging
    - Secure file handling
    """
    # Security: Log page access
    current_app.logger.info(f"Bulk upload page accessed by user {current_user.id} ({current_user.email})")
    
    return render_template(
        'admin/bulk_upload_redesigned.html', 
        title='Food Database Upload',
        max_file_size_mb=10,
        allowed_extensions=['.csv']
    )

# Redirect old bulk upload route to new one
@bp.route('/bulk-upload', methods=['GET'])
@login_required
@admin_required
def bulk_upload_redirect():
    """Redirect old bulk upload route to new redesigned page."""
    return redirect(url_for('admin.bulk_upload_foods'))

# Async Bulk Upload Routes
@bp.route('/bulk-upload-async', methods=['POST'])
@rate_limit_upload(max_attempts=5, window_minutes=15)  # Security: Rate limiting
@login_required
@admin_required
def bulk_upload_async():
    """
    Enhanced async bulk upload with comprehensive security and validation.
    
    Security Features:
    - File type validation (CSV only)
    - File size limits (10MB max)
    - Content sanitization
    - Malicious file detection
    - Request rate limiting
    - Comprehensive logging
    """
    import time
    import hashlib
    
    start_time = time.time()
    
    try:
        # Security: Log upload attempt with user details
        current_app.logger.info(
            f"[SECURITY] Async upload attempt by user {current_user.id} ({current_user.email}) "
            f"from IP: {request.remote_addr} at {time.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        # Security: Validate request has file
        if 'file' not in request.files:
            current_app.logger.warning(f"[SECURITY] No file in upload request from user {current_user.id}")
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        # Security: Validate file is selected
        if file.filename == '':
            current_app.logger.warning(f"[SECURITY] Empty filename in upload from user {current_user.id}")
            return jsonify({'error': 'No file selected'}), 400
        
        # Security: Validate file extension
        if not file.filename.lower().endswith('.csv'):
            current_app.logger.warning(
                f"[SECURITY] Invalid file type '{file.filename}' uploaded by user {current_user.id}"
            )
            return jsonify({'error': 'Only CSV files are supported'}), 400
        
        # Security: Validate filename for malicious patterns
        import re
        if re.search(r'[<>:"/\\|?*]', file.filename) or '..' in file.filename:
            current_app.logger.warning(
                f"[SECURITY] Malicious filename detected: '{file.filename}' by user {current_user.id}"
            )
            return jsonify({'error': 'Invalid filename detected'}), 400
        
        # Security: Read and validate file size
        file_content = file.read()
        file_size_mb = len(file_content) / (1024 * 1024)
        
        if file_size_mb > 10:  # 10MB limit
            current_app.logger.warning(
                f"[SECURITY] File too large ({file_size_mb:.2f}MB) uploaded by user {current_user.id}"
            )
            return jsonify({'error': f'File too large ({file_size_mb:.2f}MB). Maximum size is 10MB.'}), 400
        
        # Security: Generate file hash for integrity checking
        file_hash = hashlib.sha256(file_content).hexdigest()
        current_app.logger.info(f"[SECURITY] File hash: {file_hash}, Size: {file_size_mb:.2f}MB")
        
        # Security: Validate file content encoding
        try:
            csv_content = file_content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                csv_content = file_content.decode('latin-1')
                current_app.logger.info(f"[SECURITY] File decoded using latin-1 encoding")
            except UnicodeDecodeError:
                current_app.logger.error(f"[SECURITY] Unable to decode file from user {current_user.id}")
                return jsonify({'error': 'File encoding not supported. Please use UTF-8 encoding.'}), 400
        
        # Security: Basic CSV structure validation
        import csv
        import io
        try:
            csv_reader = csv.reader(io.StringIO(csv_content))
            first_row = next(csv_reader, None)
            if not first_row:
                return jsonify({'error': 'Empty CSV file'}), 400
            
            # Check for required columns
            required_columns = ['name', 'category', 'base_unit', 'calories_per_100g', 'protein_per_100g', 'carbs_per_100g', 'fat_per_100g']
            missing_columns = [col for col in required_columns if col not in first_row]
            if missing_columns:
                return jsonify({'error': f'Missing required columns: {", ".join(missing_columns)}'}), 400
                
        except Exception as e:
            current_app.logger.error(f"[SECURITY] CSV validation failed for user {current_user.id}: {str(e)}")
            return jsonify({'error': 'Invalid CSV format'}), 400
        
        # Security: Log successful validation
        current_app.logger.info(
            f"[SECURITY] File validation passed - "
            f"User: {current_user.id}, "
            f"File: {file.filename}, "
            f"Size: {file_size_mb:.2f}MB, "
            f"Hash: {file_hash[:16]}..."
        )
        
        # Initialize processor and start upload
        processor = BulkUploadProcessor()
        job_id = processor.start_async_upload(
            csv_content=csv_content,
            filename=file.filename,
            user_id=current_user.id,
            file_hash=file_hash  # Add file hash for audit trail
        )
        
        processing_time = time.time() - start_time
        
        # Security: Log successful upload start
        current_app.logger.info(
            f"[SECURITY] Upload started successfully - "
            f"User: {current_user.id}, "
            f"Job ID: {job_id}, "
            f"Processing time: {processing_time:.3f}s"
        )
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': 'Bulk upload started successfully',
            'file_hash': file_hash,
            'file_size_mb': round(file_size_mb, 2),
            'processing_time_ms': round(processing_time * 1000, 2)
        })
        
    except ValueError as e:
        current_app.logger.error(f"[SECURITY] ValueError in bulk upload by user {current_user.id}: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(
            f"[SECURITY] Bulk upload error by user {current_user.id}: {str(e)}", 
            exc_info=True
        )
        return jsonify({'error': 'Failed to start bulk upload. Please try again.'}), 500

@bp.route('/bulk-upload-status/<job_id>')
@login_required
@admin_required
def bulk_upload_status(job_id):
    """Get bulk upload job status."""
    try:
        processor = BulkUploadProcessor()
        status = processor.get_job_status(job_id)
        
        if not status:
            return jsonify({'error': 'Job not found'}), 404
        
        return jsonify(status)
        
    except Exception as e:
        current_app.logger.error(f"Status check error: {str(e)}")
        return jsonify({'error': 'Failed to get job status'}), 500

@bp.route('/bulk-upload-details/<job_id>')
@login_required
@admin_required
def bulk_upload_details(job_id):
    """
    Get detailed information about a specific bulk upload job.
    
    This endpoint provides comprehensive job details including failed items
    for the unified food uploads interface.
    """
    try:
        # Get job with security check
        job = BulkUploadJob.query.filter_by(
            job_id=job_id,
            created_by=current_user.id
        ).first()
        
        if not job:
            return jsonify({
                'error': 'Job not found or access denied'
            }), 404
        
        # Build response data
        job_data = {
            'job_id': job.job_id,
            'filename': job.filename,
            'status': job.status,
            'total_rows': job.total_rows or 0,
            'processed_rows': job.processed_rows or 0,
            'successful_rows': job.successful_rows or 0,
            'failed_rows': job.failed_rows or 0,
            'created_at': job.created_at.isoformat() if job.created_at else None,
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'completed_at': job.completed_at.isoformat() if job.completed_at else None,
            'error_message': job.error_message
        }
        
        # Add failed items details if available
        if job.failed_rows and job.failed_rows > 0:
            failed_details = []
            
            # Get failed items from job items
            failed_job_items = job.job_items.filter_by(status='failed').limit(100).all()
            
            for item in failed_job_items:
                failed_details.append({
                    'row_number': item.row_number,
                    'data': json.loads(item.data) if item.data else {},
                    'error_message': item.error_message
                })
            
            job_data['failed_details'] = failed_details
        
        # Log access for security audit
        current_app.logger.info(
            f"Job details accessed: {job_id} by user {current_user.id}"
        )
        
        return jsonify(job_data)
        
    except Exception as e:
        current_app.logger.error(f"Error fetching job details {job_id}: {str(e)}")
        return jsonify({
            'error': 'Failed to fetch job details'
        }), 500

@bp.route('/food-uploads')
@login_required
@admin_required
def food_uploads():
    """
    Unified Food Uploads interface - combines bulk upload and job history.
    
    This route replaces separate bulk upload and upload jobs pages with a 
    unified tabbed interface for better user experience and maintainability.
    """
    try:
        # Get query parameters for tab selection and pagination
        active_tab = request.args.get('tab', 'upload')
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config.get('UPLOAD_JOBS_PER_PAGE', 10)
        
        # Initialize variables
        jobs = None
        pending_jobs_count = 0
        
        # If history tab is requested, fetch job data
        if active_tab == 'history':
            # Get paginated jobs with most recent first
            jobs = BulkUploadJob.query\
                .filter_by(created_by=current_user.id)\
                .order_by(desc(BulkUploadJob.created_at))\
                .paginate(
                    page=page, 
                    per_page=per_page, 
                    error_out=False
                )
        
        # Get count of pending jobs for badge display
        pending_jobs_count = BulkUploadJob.query.filter(
            BulkUploadJob.created_by == current_user.id,
            BulkUploadJob.status.in_(['pending', 'processing'])
        ).count()
        
        # Log access for audit trail
        current_app.logger.info(
            f"Admin food uploads accessed by user {current_user.id} "
            f"(tab: {active_tab}, page: {page})"
        )
        
        return render_template(
            'admin/food_uploads.html',
            title='Food Uploads - Admin',
            jobs=jobs,
            pending_jobs_count=pending_jobs_count,
            active_tab=active_tab
        )
        
    except Exception as e:
        current_app.logger.error(f"Food uploads page error: {str(e)}")
        flash('Error loading food uploads page', 'danger')
        return redirect(url_for('admin.dashboard'))

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

@bp.route('/foods/export-legacy')
@login_required
@admin_required
def export_foods():
    """
    Legacy route for backward compatibility - redirects to new export page.
    """
    return redirect(url_for('admin.export_foods_page'))


@bp.route('/foods/export', methods=['GET', 'POST'])
@login_required
@admin_required
def export_foods_page():
    """
    Food export interface with form handling.
    
    GET: Show export form with filters
    POST: Process export request and start job
    """
    try:
        export_service = FoodExportService()
        
        if request.method == 'GET':
            # Get statistics and categories for the form
            stats = export_service.get_export_statistics()
            categories = export_service.get_available_categories()
            
            return render_template(
                'admin/export_foods.html',
                title='Export Foods',
                stats=stats,
                categories=categories
            )
            
        elif request.method == 'POST':
            # Security: Log export attempt
            current_app.logger.info(
                f"[AUDIT] Food export form submitted by user {current_user.id} ({current_user.email}) "
                f"from IP: {request.remote_addr} at {datetime.utcnow().isoformat()}"
            )
            
            # Get and validate form data
            format_type = request.form.get('format', 'csv').lower().strip()
            
            # Security: Validate format parameter
            if format_type not in ['csv', 'json']:
                flash('Invalid export format requested.', 'danger')
                return redirect(url_for('admin.export_foods_page'))
            
            # Build filters from form data
            filters = {}
            
            # Category filter
            category = request.form.get('category', '').strip()
            if category:
                filters['category'] = category[:50]  # Limit length
            
            # Brand filter
            brand = request.form.get('brand', '').strip()
            if brand:
                filters['brand'] = brand[:50]  # Limit length
            
            # Name search filter
            name_contains = request.form.get('name_contains', '').strip()
            if name_contains:
                filters['name_contains'] = name_contains[:100]  # Limit length
            
            # Verification status filter
            is_verified = request.form.get('is_verified', '').strip()
            if is_verified == 'true':
                filters['is_verified'] = True
            elif is_verified == 'false':
                filters['is_verified'] = False
            
            # Date range filters
            created_after = request.form.get('created_after', '').strip()
            if created_after:
                try:
                    # Validate date format
                    datetime.strptime(created_after, '%Y-%m-%d')
                    filters['created_after'] = created_after
                except ValueError:
                    pass  # Invalid date, ignore
            
            created_before = request.form.get('created_before', '').strip()
            if created_before:
                try:
                    # Validate date format and add time component
                    datetime.strptime(created_before, '%Y-%m-%d')
                    filters['created_before'] = created_before + ' 23:59:59'
                except ValueError:
                    pass  # Invalid date, ignore
            
            # Nutrition filters
            min_protein = request.form.get('min_protein', '').strip()
            if min_protein:
                try:
                    filters['min_protein'] = float(min_protein)
                except ValueError:
                    pass  # Invalid number, ignore
            
            max_calories = request.form.get('max_calories', '').strip()
            if max_calories:
                try:
                    filters['max_calories'] = float(max_calories)
                except ValueError:
                    pass  # Invalid number, ignore
            
            # Start async export
            try:
                job_id = export_service.start_export(
                    format_type=format_type,
                    filters=filters,
                    user_id=current_user.id
                )
                
                # Security: Log export job started
                current_app.logger.info(
                    f"[AUDIT] Food export job {job_id} started for user {current_user.id} "
                    f"with filters: {json.dumps(filters, default=str)}"
                )
                
                flash(
                    f'Export started successfully! Job ID: {job_id}. '
                    f'You can monitor progress in the Export Jobs section.',
                    'success'
                )
                return redirect(url_for('admin.export_jobs'))
                
            except Exception as e:
                current_app.logger.error(f'Error starting export: {str(e)}', exc_info=True)
                flash('Failed to start export. Please try again.', 'danger')
                return redirect(url_for('admin.export_foods_page'))
                
    except Exception as e:
        current_app.logger.error(
            f'[SECURITY] Error in export foods page for user {current_user.id}: {str(e)}',
            exc_info=True
        )
        flash('An error occurred. Please try again.', 'danger')
        return redirect(url_for('admin.foods'))


@bp.route('/export-jobs')
@login_required
@admin_required
def export_jobs():
    """
    Display export jobs with pagination and status tracking.
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        # Get export jobs for current user (admins can see all)
        query = ExportJob.query
        
        # Order by creation date (newest first)
        query = query.order_by(ExportJob.created_at.desc())
        
        # Paginate results
        jobs = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return render_template(
            'admin/export_jobs.html',
            title='Export Jobs',
            jobs=jobs
        )
        
    except Exception as e:
        current_app.logger.error(f'Error loading export jobs: {str(e)}', exc_info=True)
        flash('Error loading export jobs.', 'danger')
        return redirect(url_for('admin.dashboard'))


@bp.route('/export-status/<job_id>')
@login_required
@admin_required
def export_status(job_id):
    """
    Get export job status (AJAX endpoint).
    """
    try:
        export_service = FoodExportService()
        status = export_service.get_export_status(job_id)
        
        if not status:
            return jsonify({'error': 'Job not found'}), 404
        
        return jsonify(status)
        
    except Exception as e:
        current_app.logger.error(f'Error getting export status: {str(e)}', exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@bp.route('/download-export/<job_id>')
@login_required
@admin_required
def download_export(job_id):
    """
    Download completed export file.
    """
    try:
        export_service = FoodExportService()
        
        # Get job details
        status = export_service.get_export_status(job_id)
        if not status:
            flash('Export job not found.', 'danger')
            return redirect(url_for('admin.export_jobs'))
        
        if status['status'] != 'completed':
            flash('Export is not ready for download yet.', 'warning')
            return redirect(url_for('admin.export_jobs'))
        
        if status['is_expired']:
            flash('Export file has expired.', 'warning')
            return redirect(url_for('admin.export_jobs'))
        
        # Get file path
        file_path = export_service.get_download_path(job_id)
        if not file_path:
            flash('Export file not found or has been deleted.', 'danger')
            return redirect(url_for('admin.export_jobs'))
        
        # Security: Log download attempt
        current_app.logger.info(
            f"[AUDIT] Export file download: {job_id} by user {current_user.id} "
            f"from IP: {request.remote_addr} at {datetime.utcnow().isoformat()}"
        )
        
        # Send file
        from flask import send_file
        return send_file(
            file_path,
            as_attachment=True,
            download_name=status['filename'],
            mimetype='application/octet-stream'
        )
        
    except Exception as e:
        current_app.logger.error(f'Error downloading export: {str(e)}', exc_info=True)
        flash('Error downloading file. Please try again.', 'danger')
        return redirect(url_for('admin.export_jobs'))


@bp.route('/cleanup-exports', methods=['POST'])
@login_required
@admin_required
def cleanup_exports():
    """
    Clean up expired export files.
    """
    try:
        export_service = FoodExportService()
        export_service.cleanup_expired_exports()
        
        # Security: Log cleanup action
        current_app.logger.info(
            f"[AUDIT] Export cleanup performed by user {current_user.id} "
            f"from IP: {request.remote_addr} at {datetime.utcnow().isoformat()}"
        )
        
        flash('Expired export files have been cleaned up.', 'success')
        
    except Exception as e:
        current_app.logger.error(f'Error cleaning up exports: {str(e)}', exc_info=True)
        flash('Error during cleanup. Please try again.', 'danger')
    
    return redirect(url_for('admin.export_jobs'))


# Food Servings Uploads Management
@bp.route('/food-servings/uploads')
@login_required
@admin_required
def food_servings_uploads():
    """
    Unified Food Servings Uploads interface - combines bulk upload and job history.
    
    This route provides a unified tabbed interface for uploading servings data
    and viewing upload history with detailed progress tracking.
    """
    try:
        # Handle JSON API requests based on action parameter
        action = request.args.get('action')
        
        if action == 'job_details':
            job_id = request.args.get('job_id')
            if not job_id:
                return jsonify({'error': 'job_id required'}), 400
                
            job = ServingUploadJob.query.filter_by(
                job_id=job_id, 
                created_by=current_user.id
            ).first()
            
            if job:
                return jsonify({
                    'job_id': job.job_id,
                    'filename': job.filename,
                    'status': job.status,
                    'total_rows': job.total_rows,
                    'processed_rows': job.processed_rows,
                    'successful_rows': job.successful_rows,
                    'failed_rows': job.failed_rows,
                    'created_at': job.created_at.isoformat(),
                    'started_at': job.started_at.isoformat() if job.started_at else None,
                    'completed_at': job.completed_at.isoformat() if job.completed_at else None,
                    'error_message': job.error_message
                })
            else:
                return jsonify({'error': 'Job not found'}), 404
        
        elif action == 'status_check':
            active_jobs = ServingUploadJob.query.filter(
                ServingUploadJob.created_by == current_user.id,
                ServingUploadJob.status.in_(['pending', 'processing'])
            ).all()
            
            job_statuses = []
            for job in active_jobs:
                progress_percentage = 0
                if job.total_rows and job.total_rows > 0:
                    progress_percentage = round((job.processed_rows or 0) / job.total_rows * 100, 1)
                
                job_statuses.append({
                    'job_id': job.job_id,
                    'status': job.status,
                    'processed_rows': job.processed_rows or 0,
                    'total_rows': job.total_rows or 0,
                    'progress_percentage': progress_percentage
                })
            
            return jsonify(job_statuses)
        
        # Get query parameters for tab selection and pagination
        active_tab = request.args.get('tab', 'upload')
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config.get('UPLOAD_JOBS_PER_PAGE', 10)
        
        # Initialize variables
        jobs = None
        pending_jobs_count = 0
        
        # If history tab is requested, fetch job data
        if active_tab == 'history':
            # Get paginated jobs with most recent first
            jobs = ServingUploadJob.query\
                .filter_by(created_by=current_user.id)\
                .order_by(ServingUploadJob.created_at.desc())\
                .paginate(
                    page=page, 
                    per_page=per_page, 
                    error_out=False
                )
        
        # Get count of pending and processing jobs for badge display
        pending_jobs_count = ServingUploadJob.query.filter(
            ServingUploadJob.created_by == current_user.id,
            ServingUploadJob.status.in_(['pending', 'processing'])
        ).count()
        
        return render_template(
            'admin/food_servings_uploads.html',
            jobs=jobs,
            pending_jobs_count=pending_jobs_count,
            active_tab=active_tab,
            csrf_token=generate_csrf
        )
        
    except Exception as e:
        error_msg = f'Error in food_servings_uploads: {str(e)}'
        current_app.logger.error(error_msg, exc_info=True)
        
        # More detailed error for debugging
        import traceback
        traceback_str = traceback.format_exc()
        current_app.logger.error(f'Full traceback: {traceback_str}')
        
        # Show more specific error message
        flash(f'Error loading upload interface: {str(e)}. Please check logs for details.', 'danger')
        return redirect(url_for('admin.dashboard'))


# Legacy route - redirect to unified interface
@bp.route('/food-servings/upload', methods=['GET', 'POST'])
@login_required
@admin_required
def food_servings_upload():
    """Legacy route - redirects to unified interface"""
    if request.method == 'POST':
        # Handle POST requests with async processing
        return food_servings_upload_async()
    else:
        # Redirect GET requests to unified interface
        return redirect(url_for('admin.food_servings_uploads'))


@bp.route('/food-servings/upload-async', methods=['POST'])
@login_required
@admin_required
def food_servings_upload_async():
    """
    Async bulk upload for food servings via CSV.
    Creates a job and processes in background.
    """
    try:
        from app.models import ServingUploadJob, ServingUploadJobItem
        import uuid
        
        # Validate file upload
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.csv'):
            return jsonify({'error': 'Invalid file type. Please upload a CSV file.'}), 400
        
        # Create upload job
        job_id = str(uuid.uuid4())
        upload_job = ServingUploadJob(
            job_id=job_id,
            filename=file.filename,
            created_by=current_user.id,
            status='pending'
        )
        
        try:
            # Read and validate CSV
            file_content = file.read().decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(file_content))
            
            # Validate headers
            required_headers = {'food_key', 'serving_name', 'unit', 'grams_per_unit', 'is_default'}
            if not required_headers.issubset(set(csv_reader.fieldnames or [])):
                missing_headers = required_headers - set(csv_reader.fieldnames or [])
                return jsonify({
                    'error': f'Missing required columns: {", ".join(missing_headers)}. Please use the template.'
                }), 400
            
            # Count rows for progress tracking
            rows = list(csv_reader)
            upload_job.total_rows = len(rows)
            
            # Save job to database
            db.session.add(upload_job)
            db.session.commit()
            
            # Process CSV synchronously for now (can be made async later)
            results = process_food_servings_csv_with_job(rows, upload_job)
            
            # Update job status
            upload_job.status = 'completed' if results['success'] > 0 else 'failed'
            upload_job.completed_at = datetime.utcnow()
            db.session.commit()
            
            current_app.logger.info(
                f"Food servings async upload completed for user {current_user.id}: "
                f"job_id={job_id}, processed={results['processed']}, "
                f"success={results['success']}, errors={len(results['errors'])}"
            )
            
            return jsonify({
                'success': True,
                'job_id': job_id,
                'message': f'Upload completed. Processed: {results["processed"]}, Success: {results["success"]}, Errors: {len(results["errors"])}'
            })
            
        except UnicodeDecodeError:
            upload_job.status = 'failed'
            upload_job.error_message = 'File encoding error. Please save your CSV file as UTF-8.'
            upload_job.completed_at = datetime.utcnow()
            db.session.commit()
            return jsonify({'error': 'File encoding error. Please save your CSV file as UTF-8.'}), 400
            
        except Exception as e:
            upload_job.status = 'failed'
            upload_job.error_message = str(e)
            upload_job.completed_at = datetime.utcnow()
            db.session.commit()
            
            current_app.logger.error(f'Error in async serving upload: {str(e)}', exc_info=True)
            return jsonify({'error': 'Error processing file. Please try again.'}), 500
            
    except Exception as e:
        current_app.logger.error(f'Error in food_servings_upload_async: {str(e)}', exc_info=True)
        return jsonify({'error': 'Upload failed. Please try again.'}), 500


@bp.route('/food-servings/status/<job_id>')
@login_required
@admin_required
def servings_upload_status_check(job_id):
    """
    Check the status of a specific servings upload job.
    Returns JSON with job status and progress information.
    """
    try:
        job = ServingUploadJob.query.filter_by(
            job_id=job_id,
            created_by=current_user.id
        ).first()
        
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        # Calculate progress percentage
        progress_percentage = 0
        if job.total_rows and job.total_rows > 0:
            progress_percentage = round((job.processed_rows or 0) / job.total_rows * 100, 1)
        
        return jsonify({
            'job_id': job.job_id,
            'status': job.status,
            'processed_rows': job.processed_rows or 0,
            'total_rows': job.total_rows or 0,
            'successful_rows': job.successful_rows or 0,
            'failed_rows': job.failed_rows or 0,
            'progress_percentage': progress_percentage,
            'error_message': job.error_message,
            'created_at': job.created_at.isoformat() if job.created_at else None,
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'completed_at': job.completed_at.isoformat() if job.completed_at else None
        })
        
    except Exception as e:
        current_app.logger.error(f'Error checking servings upload status: {str(e)}', exc_info=True)
        return jsonify({'error': 'Failed to check job status'}), 500


# Food Servings Bulk Upload Routes
@bp.route('/food-servings/upload-old', methods=['GET', 'POST'])
@login_required
@admin_required
def food_servings_upload_old():
    """
    Bulk upload food servings via CSV.
    GET: Display upload form with template download
    POST: Process uploaded CSV file
    """
    if request.method == 'GET':
        current_app.logger.info(f"Food servings upload page accessed by user {current_user.id}")
        from flask_wtf.csrf import generate_csrf
        return render_template('admin/food_servings_upload.html', csrf_token=generate_csrf)
    
    # POST: Handle file upload
    try:
        # Validate file upload
        if 'file' not in request.files:
            flash('No file uploaded. Please select a CSV file.', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected. Please choose a CSV file.', 'danger')
            return redirect(request.url)
        
        if not file.filename.lower().endswith('.csv'):
            flash('Invalid file type. Please upload a CSV file.', 'danger')
            return redirect(request.url)
        
        # Read and validate CSV
        try:
            # Read file content
            file_content = file.read().decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(file_content))
            
            # Validate headers
            required_headers = {'food_key', 'serving_name', 'unit', 'grams_per_unit', 'is_default'}
            if not required_headers.issubset(set(csv_reader.fieldnames or [])):
                missing_headers = required_headers - set(csv_reader.fieldnames or [])
                flash(f'Missing required columns: {", ".join(missing_headers)}. Please use the template.', 'danger')
                return redirect(request.url)
            
            # Process rows
            results = process_food_servings_csv(csv_reader)
            
            # Flash results
            if results['errors']:
                flash(f'Upload completed with errors. Processed: {results["processed"]}, '
                      f'Success: {results["success"]}, Errors: {len(results["errors"])}', 'warning')
                # Store errors in session for display
                session['upload_errors'] = results['errors'][:50]  # Limit to first 50 errors
            else:
                flash(f'Upload successful! Processed: {results["processed"]}, '
                      f'Success: {results["success"]}', 'success')
                # Clear any previous errors
                session.pop('upload_errors', None)
            
            current_app.logger.info(
                f"Food servings upload by user {current_user.id}: "
                f"processed={results['processed']}, success={results['success']}, "
                f"errors={len(results['errors'])}"
            )
            
        except UnicodeDecodeError:
            flash('File encoding error. Please save your CSV file as UTF-8.', 'danger')
        except Exception as e:
            current_app.logger.error(f'Error processing CSV: {str(e)}', exc_info=True)
            flash('Error processing CSV file. Please check the format and try again.', 'danger')
        
        return redirect(request.url)
        
    except Exception as e:
        current_app.logger.error(f'Error in food servings upload: {str(e)}', exc_info=True)
        flash('Upload failed. Please try again.', 'danger')
        return redirect(request.url)


@bp.route('/food-servings/template')
@login_required
@admin_required
def download_food_servings_template():
    """Download CSV template for food servings upload."""
    try:
        # Create CSV template
        output = io.StringIO()
        writer = csv.writer(output, lineterminator='\n')
        
        # Headers
        writer.writerow(['food_key', 'serving_name', 'unit', 'grams_per_unit', 'is_default'])
        
        # Example rows
        writer.writerow(['1', '1 cup', 'cup', '240.0', 'true'])
        writer.writerow(['1', '1 tablespoon', 'tbsp', '15.0', 'false'])
        writer.writerow(['RICE001', '1 bowl', 'bowl', '200.0', 'true'])
        writer.writerow(['RICE001', '1 cup', 'cup', '160.0', 'false'])
        
        # Create response
        from flask import Response
        response = Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=food_servings_template.csv'}
        )
        
        current_app.logger.info(f"Food servings template downloaded by user {current_user.id}")
        return response
        
    except Exception as e:
        current_app.logger.error(f'Error generating template: {str(e)}', exc_info=True)
        flash('Error generating template. Please try again.', 'danger')
        return redirect(url_for('admin.food_servings_upload'))


def process_food_servings_csv(csv_reader):
    """
    Process CSV data and upsert food servings.
    
    Args:
        csv_reader: CSV DictReader object
        
    Returns:
        dict: Results summary with processed, success, and error counts
    """
    results = {
        'processed': 0,
        'success': 0,
        'errors': []
    }
    
    try:
        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 for header
            results['processed'] += 1
            
            try:
                # Extract and validate data
                food_key = str(row.get('food_key', '')).strip()
                serving_name = str(row.get('serving_name', '')).strip()
                unit = str(row.get('unit', '')).strip()
                grams_per_unit_str = str(row.get('grams_per_unit', '')).strip()
                is_default_str = str(row.get('is_default', '')).strip().lower()
                
                # Validate required fields
                if not all([food_key, serving_name, unit, grams_per_unit_str]):
                    results['errors'].append(f'Row {row_num}: Missing required fields')
                    continue
                
                # Find food by ID or custom key
                food = None
                if food_key.isdigit():
                    food = Food.query.get(int(food_key))
                else:
                    # Look for food by name or custom identifier
                    food = Food.query.filter(
                        db.or_(
                            Food.name.ilike(f'%{food_key}%'),
                            Food.brand.ilike(f'%{food_key}%')
                        )
                    ).first()
                
                if not food:
                    results['errors'].append(f'Row {row_num}: Food not found for key "{food_key}"')
                    continue
                
                # Validate grams_per_unit
                try:
                    grams_per_unit = float(grams_per_unit_str)
                    if grams_per_unit <= 0:
                        results['errors'].append(f'Row {row_num}: grams_per_unit must be greater than 0')
                        continue
                except ValueError:
                    results['errors'].append(f'Row {row_num}: Invalid grams_per_unit "{grams_per_unit_str}"')
                    continue
                
                # Parse is_default
                is_default = is_default_str in ('true', '1', 'yes', 'y')
                
                # Check for existing serving (idempotent operation)
                existing_serving = FoodServing.query.filter_by(
                    food_id=food.id,
                    serving_name=serving_name,
                    unit=unit
                ).first()
                
                if existing_serving:
                    # Update existing serving
                    existing_serving.grams_per_unit = grams_per_unit
                    existing_serving.created_by = current_user.id
                    serving = existing_serving
                else:
                    # Create new serving
                    serving = FoodServing(
                        food_id=food.id,
                        serving_name=serving_name,
                        unit=unit,
                        grams_per_unit=grams_per_unit,
                        created_by=current_user.id
                    )
                    db.session.add(serving)
                
                # Handle default setting
                if is_default:
                    # First commit the serving to get its ID
                    db.session.flush()
                    
                    # Set as default serving for the food
                    food.default_serving_id = serving.id
                
                db.session.commit()
                results['success'] += 1
                
            except Exception as e:
                db.session.rollback()
                results['errors'].append(f'Row {row_num}: {str(e)}')
                current_app.logger.error(f'Error processing row {row_num}: {str(e)}')
                continue
        
        return results
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error in process_food_servings_csv: {str(e)}', exc_info=True)
        results['errors'].append(f'Processing error: {str(e)}')
        return results


def process_food_servings_csv_with_job(rows, upload_job):
    """
    Process CSV data and upsert food servings with job tracking.
    
    Args:
        rows: List of CSV row dictionaries
        upload_job: ServingUploadJob instance for tracking progress
        
    Returns:
        dict: Results summary with processed, success, and error counts
    """
    from app.models import ServingUploadJobItem
    
    results = {
        'processed': 0,
        'success': 0,
        'errors': []
    }
    
    try:
        upload_job.status = 'processing'
        upload_job.started_at = datetime.utcnow()
        db.session.commit()
        
        for row_num, row in enumerate(rows, start=2):  # Start at 2 for header
            results['processed'] += 1
            upload_job.processed_rows = results['processed']
            
            # Create job item for tracking
            job_item = ServingUploadJobItem(
                job_id=upload_job.id,
                row_number=row_num,
                food_key=str(row.get('food_key', '')).strip(),
                serving_name=str(row.get('serving_name', '')).strip(),
                status='processing'
            )
            db.session.add(job_item)
            
            try:
                # Extract and validate data
                food_key = str(row.get('food_key', '')).strip()
                serving_name = str(row.get('serving_name', '')).strip()
                unit = str(row.get('unit', '')).strip()
                grams_per_unit_str = str(row.get('grams_per_unit', '')).strip()
                is_default_str = str(row.get('is_default', 'false')).strip().lower()
                
                # Validation
                if not food_key:
                    raise ValueError("food_key is required")
                
                if not serving_name:
                    raise ValueError("serving_name is required")
                
                if not unit:
                    raise ValueError("unit is required")
                
                # Convert grams_per_unit to float
                try:
                    grams_per_unit = float(grams_per_unit_str)
                    if grams_per_unit <= 0:
                        raise ValueError("grams_per_unit must be positive")
                except (ValueError, TypeError):
                    raise ValueError(f"Invalid grams_per_unit: '{grams_per_unit_str}'. Must be a positive number.")
                
                # Convert is_default to boolean
                is_default = is_default_str in ('true', '1', 'yes', 'y')
                
                # Find the food (by ID or food_key)
                food = None
                
                # Try as integer ID first
                try:
                    food_id = int(food_key)
                    food = Food.query.get(food_id)
                except (ValueError, TypeError):
                    pass
                
                # If not found by ID, try by name (food_key as name)
                if not food:
                    food = Food.query.filter_by(name=food_key).first()
                
                if not food:
                    raise ValueError(f"Food not found for key: '{food_key}'")
                
                # Check for existing serving (upsert logic)
                existing_serving = FoodServing.query.filter_by(
                    food_id=food.id,
                    serving_name=serving_name
                ).first()
                
                if existing_serving:
                    # Update existing serving
                    existing_serving.unit = unit
                    existing_serving.grams_per_unit = grams_per_unit
                    current_serving = existing_serving
                else:
                    # Create new serving
                    current_serving = FoodServing(
                        food_id=food.id,
                        serving_name=serving_name,
                        unit=unit,
                        grams_per_unit=grams_per_unit
                    )
                    db.session.add(current_serving)
                
                # Flush to get the serving ID
                db.session.flush()
                
                # Handle default serving logic using food.default_serving_id
                if is_default:
                    food.default_serving_id = current_serving.id
                
                # Commit this row
                db.session.commit()
                
                # Update job item
                job_item.status = 'success'
                job_item.serving_id = current_serving.id
                job_item.processed_at = datetime.utcnow()
                
                results['success'] += 1
                upload_job.successful_rows = results['success']
                
                db.session.commit()
                
            except Exception as e:
                db.session.rollback()
                error_msg = str(e)
                results['errors'].append(f'Row {row_num}: {error_msg}')
                
                # Update job item
                job_item.status = 'failed'
                job_item.error_message = error_msg
                job_item.processed_at = datetime.utcnow()
                
                upload_job.failed_rows = len(results['errors'])
                
                db.session.commit()
                
                current_app.logger.error(f'Error processing serving row {row_num}: {str(e)}')
                continue
        
        return results
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error in process_food_servings_csv_with_job: {str(e)}', exc_info=True)
        results['errors'].append(f'Processing error: {str(e)}')
        return results
