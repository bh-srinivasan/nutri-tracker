from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, TextAreaField, BooleanField, SubmitField, PasswordField, HiddenField
from wtforms.validators import DataRequired, Length, NumberRange, Email, EqualTo, ValidationError, Optional
from app.models import User, Food, FoodServing

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
    is_verified = BooleanField('Verified Food Item', default=True)
    submit = SubmitField('Save Food Item')

class UserManagementForm(FlaskForm):
    """Form for managing users."""
    username = StringField('Username', validators=[
        DataRequired(), 
        Length(min=3, max=80)
    ])
    email = StringField('Email', validators=[Optional(), Email(message="Please enter a valid email address")])
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

    def __init__(self, user_id=None, *args, **kwargs):
        super(UserManagementForm, self).__init__(*args, **kwargs)
        self.user_id = user_id

    def validate_username(self, username):
        """Validate username is not already taken by another user."""
        query = User.query.filter_by(username=username.data)
        if self.user_id:
            query = query.filter(User.id != self.user_id)
        user = query.first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')

    def validate_email(self, email):
        """Validate email is not already taken by another user (only if email is provided).""" 
        # Skip validation if email is empty (since it's now optional)
        if not email.data or not email.data.strip():
            return
            
        query = User.query.filter_by(email=email.data.strip())
        if self.user_id:
            query = query.filter(User.id != self.user_id)
        user = query.first()
        if user:
            raise ValidationError('Email already exists. Please choose a different one.')

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

class FoodServingForm(FlaskForm):
    """Form for adding/editing food servings with comprehensive validation."""
    food_id = HiddenField('Food ID', validators=[DataRequired()])
    serving_name = StringField('Serving Name', validators=[
        DataRequired(message='Serving name is required'), 
        Length(min=2, max=50, message='Serving name must be between 2 and 50 characters')
    ], render_kw={
        'placeholder': 'e.g., 1 cup, 1 piece, 1 slice',
        'maxlength': '50'
    })
    unit = StringField('Unit', validators=[
        DataRequired(message='Unit is required'), 
        Length(min=1, max=20, message='Unit must be between 1 and 20 characters')
    ], render_kw={
        'placeholder': 'e.g., cup, piece, slice',
        'maxlength': '20'
    })
    grams_per_unit = FloatField('Grams per Unit', validators=[
        DataRequired(message='Grams per unit is required'),
        NumberRange(min=0.1, max=2000, message='Grams per unit must be between 0.1 and 2000 grams')
    ], render_kw={
        'step': '0.1',
        'min': '0.1',
        'max': '2000',
        'placeholder': 'e.g., 250'
    })
    is_default = BooleanField('Set as Default Serving', default=False)
    submit = SubmitField('Add Serving')

    def __init__(self, food_id=None, serving_id=None, *args, **kwargs):
        super(FoodServingForm, self).__init__(*args, **kwargs)
        self.food_id_value = food_id
        self.serving_id = serving_id
        if food_id:
            self.food_id.data = food_id

    def validate_serving_name(self, serving_name):
        """Validate serving name using model method."""
        is_valid, message = FoodServing.validate_serving_name(serving_name.data)
        if not is_valid:
            raise ValidationError(message)

    def validate_unit(self, unit):
        """Validate unit using model method."""
        is_valid, message = FoodServing.validate_unit(unit.data)
        if not is_valid:
            raise ValidationError(message)

    def validate_grams_per_unit(self, grams_per_unit):
        """Validate grams per unit using model method."""
        is_valid, message = FoodServing.validate_grams_per_unit(grams_per_unit.data)
        if not is_valid:
            raise ValidationError(message)

    def validate(self, extra_validators=None):
        """Custom validation to check for duplicates."""
        if not super().validate(extra_validators):
            return False

        # Check for duplicate serving
        if self.food_id_value and self.serving_name.data and self.unit.data:
            if FoodServing.check_duplicate(
                self.food_id_value,
                self.serving_name.data,
                self.unit.data,
                self.serving_id
            ):
                self.serving_name.errors.append(
                    f'A serving with name "{self.serving_name.data}" and unit "{self.unit.data}" already exists for this food'
                )
                return False

        return True

class EditFoodServingForm(FoodServingForm):
    """Form for editing existing food servings."""
    submit = SubmitField('Update Serving')

class DefaultServingForm(FlaskForm):
    """Form for setting default serving for a food."""
    food_id = HiddenField('Food ID', validators=[DataRequired()])
    default_serving_id = SelectField('Default Serving', coerce=int, validators=[Optional()])
    submit = SubmitField('Set Default Serving')

    def __init__(self, food_id=None, *args, **kwargs):
        super(DefaultServingForm, self).__init__(*args, **kwargs)
        self.food_id_value = food_id
        if food_id:
            self.food_id.data = food_id
            # Populate choices with current servings
            servings = FoodServing.query.filter_by(food_id=food_id).order_by(FoodServing.serving_name).all()
            choices = [('', 'No default serving (100g fallback)')]
            choices.extend([(s.id, f'{s.serving_name} ({s.grams_per_unit}g)') for s in servings])
            self.default_serving_id.choices = choices
