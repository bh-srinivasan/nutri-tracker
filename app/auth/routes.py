from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, current_user, login_required
from urllib.parse import urlparse
from app import db
from app.auth import bp
from app.auth.forms import (
    LoginForm, RegistrationForm, ProfileForm, ChangePasswordForm,
    ResetPasswordRequestForm, ResetPasswordForm
)
from app.models import User

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login route."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))
        
        if not user.is_active:
            flash('Your account has been deactivated. Please contact administrator.', 'warning')
            return redirect(url_for('auth.login'))
        
        # Update last login time
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        login_user(user, remember=form.remember_me.data)
        
        # Redirect to intended page or dashboard
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            if user.is_admin:
                next_page = url_for('admin.dashboard')
            else:
                next_page = url_for('dashboard.index')
        
        flash(f'Welcome back, {user.first_name or user.username}!', 'success')
        return redirect(next_page)
    
    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/logout')
@login_required
def logout():
    """User logout route."""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Register', form=form)

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile management route."""
    form = ProfileForm(current_user.username, current_user.email or '')
    
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        # Handle optional email field - set to None if empty
        current_user.email = form.email.data if form.email.data and form.email.data.strip() else None
        current_user.age = form.age.data
        current_user.gender = form.gender.data
        current_user.height = form.height.data
        current_user.weight = form.weight.data
        current_user.activity_level = form.activity_level.data
        
        db.session.commit()
        flash('Your profile has been updated successfully!', 'success')
        return redirect(url_for('auth.profile'))
    
    elif request.method == 'GET':
        # Pre-populate form with current user data
        form.username.data = current_user.username
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        # Handle optional email field - show empty string if None
        form.email.data = current_user.email if current_user.email else ''
        form.age.data = current_user.age
        form.gender.data = current_user.gender
        form.height.data = current_user.height
        form.weight.data = current_user.weight
        form.activity_level.data = current_user.activity_level
    
    # Calculate BMR and TDEE if user has complete profile
    bmr = current_user.calculate_bmr()
    tdee = current_user.calculate_tdee()
    
    return render_template('auth/profile.html', title='Profile', form=form, 
                         bmr=bmr, tdee=tdee)

@bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password route."""
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('auth.change_password'))
        
        current_user.set_password(form.new_password.data)
        db.session.commit()
        
        flash('Your password has been changed successfully!', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/change_password.html', title='Change Password', form=form)

@bp.route('/reset-password-request', methods=['GET', 'POST'])
def reset_password_request():
    """Password reset request route."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # In a real application, you would send a reset email here
            flash('Password reset instructions have been sent to your email.', 'info')
        else:
            flash('Email address not found.', 'danger')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password_request.html', 
                         title='Reset Password', form=form)
