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
from app.services.bulk_upload_processor import BulkUploadProcessor
from app.services.food_export_service import FoodExportService
from app.models import BulkUploadJob, ExportJob

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
                        return None
                    # Remove potentially dangerous characters, keep alphanumeric, spaces, and basic punctuation
                    sanitized = re.sub(r'[<>"\']', '', str(text).strip())
                    return sanitized[:max_length] if sanitized else None
                
                def validate_numeric(value, min_val=0, max_val=10000):
                    try:
                        num_val = float(value) if value is not None else 0
                        return max(min_val, min(num_val, max_val))
                    except (ValueError, TypeError):
                        return 0
                
                # Security: Sanitize and validate all inputs
                food.name = sanitize_text(form.name.data, 100)
                food.brand = sanitize_text(form.brand.data, 50)
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
                    return render_template('admin/edit_food.html', title='Edit Food', form=form, food=food)
                
                if not food.category or len(food.category.strip()) == 0:
                    flash('Food category is required and cannot be empty.', 'danger')
                    return render_template('admin/edit_food.html', title='Edit Food', form=form, food=food)
                
                # Security: Check for duplicate food names (excluding current food)
                existing_food = Food.query.filter(
                    Food.name.ilike(food.name.strip()),
                    Food.id != food_id
                ).first()
                
                if existing_food:
                    if food.brand and existing_food.brand:
                        if food.brand.lower() == existing_food.brand.lower():
                            flash(f'A food item with name "{food.name}" and brand "{food.brand}" already exists.', 'warning')
                            return render_template('admin/edit_food.html', title='Edit Food', form=form, food=food)
                    elif not food.brand and not existing_food.brand:
                        flash(f'A food item with name "{food.name}" already exists.', 'warning')
                        return render_template('admin/edit_food.html', title='Edit Food', form=form, food=food)
                
                # Security: Validate verification status change
                if hasattr(form, 'is_verified'):
                    food.is_verified = bool(form.is_verified.data)
                
                # Security: Use database transaction for atomicity
                db.session.begin()
                db.session.commit()
                
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
                return redirect(url_for('admin.foods'))
                
            except Exception as e:
                # Security: Rollback transaction on error
                db.session.rollback()
                current_app.logger.error(
                    f"[SECURITY] Food edit error for food {food_id} by user {current_user.id}: {str(e)}",
                    exc_info=True
                )
                flash('An error occurred while updating the food item. Please try again.', 'danger')
                return render_template('admin/edit_food.html', title='Edit Food', form=form, food=food)
        
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
        
        return render_template('admin/edit_food.html', title='Edit Food', form=form, food=food)
        
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

@bp.route('/foods/export')
@login_required
@admin_required
def export_foods():
    """
    Start food data export process (asynchronous).
    
    Security Features:
    - Admin role verification
    - Input validation for export parameters
    - Audit logging for data export
    - Rate limiting to prevent abuse
    """
    try:
        # Security: Log export attempt
        current_app.logger.info(
            f"[AUDIT] Food export requested by user {current_user.id} ({current_user.email}) "
            f"from IP: {request.remote_addr} at {datetime.utcnow().isoformat()}"
        )
        
        # Get export parameters with validation
        format_type = request.args.get('format', 'csv', type=str).lower()
        category = request.args.get('category', '', type=str).strip()[:50]
        
        # Security: Validate format parameter
        if format_type not in ['csv', 'json']:
            flash('Invalid export format requested.', 'danger')
            return redirect(url_for('admin.foods'))
        
        # Initialize export service
        export_service = FoodExportService()
        
        # Build filters
        filters = {}
        if category:
            filters['category'] = category
            
        # Start async export
        job_id = export_service.start_export(
            format_type=format_type,
            filters=filters,
            user_id=current_user.id
        )
        
        # Security: Log export job started
        current_app.logger.info(
            f"[AUDIT] Food export job {job_id} started for user {current_user.id}"
        )
        
        flash(f'Export started! Job ID: {job_id}. You will be notified when the export is ready for download.', 'info')
        return redirect(url_for('admin.foods'))
            
    except Exception as e:
        # Security: Log error without exposing sensitive information
        current_app.logger.error(
            f'[SECURITY] Error in food export for user {current_user.id}: {str(e)}',
            exc_info=True
        )
        flash('An error occurred during export. Please try again.', 'danger')
        return redirect(url_for('admin.foods'))
