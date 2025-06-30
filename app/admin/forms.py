from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, TextAreaField, BooleanField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, NumberRange, Email, EqualTo, ValidationError, Optional
from app.models import User, Food

class FoodForm(FlaskForm):
    """Form for adding/editing food items."""
    name = StringField('Food Name', validators=[
        DataRequired(), 
        Length(min=2, max=100)
    ])
    brand = StringField('Brand', validators=[
        Optional(), 
        Length(max=50)
    ])
    category = SelectField('Category', choices=[
        ('', 'Select Category'),
        ('grains', 'Grains & Cereals'),
        ('vegetables', 'Vegetables'),
        ('fruits', 'Fruits'),
        ('dairy', 'Dairy Products'),
        ('meat', 'Meat & Poultry'),
        ('fish', 'Fish & Seafood'),
        ('legumes', 'Legumes & Pulses'),
        ('nuts', 'Nuts & Seeds'),
        ('beverages', 'Beverages'),
        ('snacks', 'Snacks'),
        ('sweets', 'Sweets & Desserts'),
        ('oils', 'Oils & Fats'),
        ('spices', 'Spices & Herbs'),
        ('processed', 'Processed Foods'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    
    # Nutritional information per 100g
    calories = FloatField('Calories (per 100g)', validators=[
        DataRequired(), 
        NumberRange(min=0, max=1000, message='Calories must be between 0 and 1000')
    ])
    protein = FloatField('Protein (g per 100g)', validators=[
        DataRequired(), 
        NumberRange(min=0, max=100, message='Protein must be between 0 and 100g')
    ])
    carbs = FloatField('Carbohydrates (g per 100g)', validators=[
        DataRequired(), 
        NumberRange(min=0, max=100, message='Carbohydrates must be between 0 and 100g')
    ])
    fat = FloatField('Fat (g per 100g)', validators=[
        DataRequired(), 
        NumberRange(min=0, max=100, message='Fat must be between 0 and 100g')
    ])
    fiber = FloatField('Fiber (g per 100g)', validators=[
        Optional(), 
        NumberRange(min=0, max=50, message='Fiber must be between 0 and 50g')
    ])
    sugar = FloatField('Sugar (g per 100g)', validators=[
        Optional(), 
        NumberRange(min=0, max=100, message='Sugar must be between 0 and 100g')
    ])
    sodium = FloatField('Sodium (mg per 100g)', validators=[
        Optional(), 
        NumberRange(min=0, max=10000, message='Sodium must be between 0 and 10000mg')
    ])
    serving_size = FloatField('Typical Serving Size (g)', validators=[
        Optional(), 
        NumberRange(min=1, max=1000, message='Serving size must be between 1 and 1000g')
    ])
    is_verified = BooleanField('Verified Food Item')
    submit = SubmitField('Save Food Item')

class UserManagementForm(FlaskForm):
    """Form for managing users."""
    username = StringField('Username', validators=[
        DataRequired(), 
        Length(min=3, max=80)
    ])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[
        DataRequired(), 
        Length(min=1, max=50)
    ])
    last_name = StringField('Last Name', validators=[
        DataRequired(), 
        Length(min=1, max=50)
    ])
    is_admin = BooleanField('Admin User')
    is_active = BooleanField('Active User')
    submit = SubmitField('Update User')

class AdminPasswordForm(FlaskForm):
    """Form for admin to change their password."""
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(), 
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Change Password')
    
    def validate_new_password(self, new_password):
        """Validate new password against policy."""
        is_valid, message = User.validate_password(new_password.data)
        if not is_valid:
            raise ValidationError(message)

class ResetUserPasswordForm(FlaskForm):
    """Form for admin to reset user password."""
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(), 
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Reset Password')
    
    def validate_new_password(self, new_password):
        """Validate new password against policy."""
        is_valid, message = User.validate_password(new_password.data)
        if not is_valid:
            raise ValidationError(message)

class ChallengeForm(FlaskForm):
    """Form for creating/editing challenges."""
    name = StringField('Challenge Name', validators=[
        DataRequired(), 
        Length(min=5, max=100)
    ])
    description = TextAreaField('Description', validators=[
        Optional(), 
        Length(max=500)
    ])
    challenge_type = SelectField('Challenge Type', choices=[
        ('protein', 'Protein Goal'),
        ('calories', 'Calorie Goal'),
        ('streak', 'Logging Streak'),
        ('weight', 'Weight Goal')
    ], validators=[DataRequired()])
    target_value = FloatField('Target Value', validators=[
        DataRequired(), 
        NumberRange(min=0.1, max=10000, message='Target value must be positive')
    ])
    duration_days = FloatField('Duration (days)', validators=[
        DataRequired(), 
        NumberRange(min=1, max=365, message='Duration must be between 1 and 365 days')
    ])
    is_active = BooleanField('Active Challenge', default=True)
    submit = SubmitField('Save Challenge')

class BulkFoodUploadForm(FlaskForm):
    """Form for bulk food upload via CSV."""
    csv_data = TextAreaField('CSV Data', validators=[
        DataRequired(),
        Length(min=10, message='CSV data is too short')
    ], render_kw={'rows': 10, 'placeholder': 'name,brand,category,calories,protein,carbs,fat,fiber,sugar,sodium,serving_size'})
    submit = SubmitField('Upload Foods')
