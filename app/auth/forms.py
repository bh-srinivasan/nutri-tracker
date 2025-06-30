from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, IntegerField, FloatField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, NumberRange, Optional
from app.models import User

class LoginForm(FlaskForm):
    """User login form."""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    """User registration form."""
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
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[
        DataRequired(), 
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        """Check if username is already taken."""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')
    
    def validate_email(self, email):
        """Check if email is already registered."""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email address.')
    
    def validate_password(self, password):
        """Validate password against policy."""
        is_valid, message = User.validate_password(password.data)
        if not is_valid:
            raise ValidationError(message)

class ProfileForm(FlaskForm):
    """User profile form."""
    first_name = StringField('First Name', validators=[
        DataRequired(), 
        Length(min=1, max=50)
    ])
    last_name = StringField('Last Name', validators=[
        DataRequired(), 
        Length(min=1, max=50)
    ])
    email = StringField('Email', validators=[DataRequired(), Email()])
    age = IntegerField('Age', validators=[
        Optional(), 
        NumberRange(min=13, max=120, message='Age must be between 13 and 120')
    ])
    gender = SelectField('Gender', choices=[
        ('', 'Select Gender'),
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], validators=[Optional()])
    height = FloatField('Height (cm)', validators=[
        Optional(), 
        NumberRange(min=100, max=250, message='Height must be between 100 and 250 cm')
    ])
    weight = FloatField('Weight (kg)', validators=[
        Optional(), 
        NumberRange(min=30, max=300, message='Weight must be between 30 and 300 kg')
    ])
    activity_level = SelectField('Activity Level', choices=[
        ('', 'Select Activity Level'),
        ('sedentary', 'Sedentary (little or no exercise)'),
        ('light', 'Light (light exercise/sports 1-3 days/week)'),
        ('moderate', 'Moderate (moderate exercise/sports 3-5 days/week)'),
        ('active', 'Active (hard exercise/sports 6-7 days a week)'),
        ('very_active', 'Very Active (very hard exercise & physical job)')
    ], validators=[Optional()])
    submit = SubmitField('Update Profile')
    
    def __init__(self, original_email, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.original_email = original_email
    
    def validate_email(self, email):
        """Check if email is already registered by another user."""
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email already registered. Please use a different email address.')

class ChangePasswordForm(FlaskForm):
    """Change password form."""
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    new_password2 = PasswordField('Repeat New Password', validators=[
        DataRequired(), 
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Change Password')
    
    def validate_new_password(self, new_password):
        """Validate new password against policy."""
        is_valid, message = User.validate_password(new_password.data)
        if not is_valid:
            raise ValidationError(message)

class ResetPasswordRequestForm(FlaskForm):
    """Password reset request form."""
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    """Password reset form."""
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[
        DataRequired(), 
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Reset Password')
    
    def validate_password(self, password):
        """Validate password against policy."""
        is_valid, message = User.validate_password(password.data)
        if not is_valid:
            raise ValidationError(message)
