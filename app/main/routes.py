from flask import render_template, redirect, url_for
from flask_login import current_user
from app.main import bp

@bp.route('/')
def index():
    """Homepage - redirect authenticated users to dashboard."""
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('dashboard.index'))
    return render_template('main/index.html', title='Welcome to Nutri Tracker')

@bp.route('/about')
def about():
    """About page."""
    return render_template('main/about.html', title='About Nutri Tracker')

@bp.route('/features')
def features():
    """Features page."""
    return render_template('main/features.html', title='Features')

@bp.route('/privacy')
def privacy():
    """Privacy policy page."""
    return render_template('main/privacy.html', title='Privacy Policy')

@bp.route('/terms')
def terms():
    """Terms of service page."""
    return render_template('main/terms.html', title='Terms of Service')
