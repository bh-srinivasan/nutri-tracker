from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
import re
import uuid

class User(UserMixin, db.Model):
    """User model for authentication and user management."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), unique=True, nullable=False, index=True)  # UUID field for editable unique ID
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    password_changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # User profile information
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    height = db.Column(db.Float)  # in cm
    weight = db.Column(db.Float)  # in kg
    activity_level = db.Column(db.String(20))  # sedentary, light, moderate, active, very_active
    
    # Relationships
    meal_logs = db.relationship('MealLog', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    nutrition_goals = db.relationship('NutritionGoal', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        """Initialize user with auto-generated user_id if not provided."""
        # Generate user_id if not provided
        if 'user_id' not in kwargs or not kwargs['user_id']:
            kwargs['user_id'] = self.generate_user_id()
        super(User, self).__init__(**kwargs)
    
    def set_password(self, password):
        """Set password hash."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash."""
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def validate_password(password):
        """Validate password against policy."""
        errors = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        if not re.search(r'\d', password):
            errors.append("Password must contain at least one number")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }
    
    @staticmethod
    def validate_email(email):
        """Validate email format."""
        if not email:
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def generate_username(first_name, last_name):
        """Generate username from first and last name."""
        # Clean and normalize names
        first = re.sub(r'[^a-zA-Z]', '', first_name.lower())
        last = re.sub(r'[^a-zA-Z]', '', last_name.lower())
        
        # Generate base username
        username = f"{first}{last}"
        
        # If username already exists, append numbers
        counter = 1
        original_username = username
        while User.query.filter_by(username=username).first():
            username = f"{original_username}{counter}"
            counter += 1
        
        return username

    @staticmethod
    def generate_user_id():
        """Generate a unique user ID using UUID4."""
        return str(uuid.uuid4())
    
    @staticmethod
    def validate_user_id(user_id, exclude_id=None):
        """Validate user ID format and uniqueness."""
        errors = []
        
        # Check if user_id is provided
        if not user_id or not user_id.strip():
            errors.append("User ID is required")
            return {'is_valid': False, 'errors': errors}
        
        user_id = user_id.strip()
        
        # Check length (UUID is 36 characters, but allow custom formats up to 36 chars)
        if len(user_id) > 36:
            errors.append("User ID must be 36 characters or less")
        
        # Check for valid characters (alphanumeric, hyphens, underscores)
        if not re.match(r'^[a-zA-Z0-9\-_]+$', user_id):
            errors.append("User ID can only contain letters, numbers, hyphens, and underscores")
        
        # Check uniqueness (exclude current user if editing)
        existing_user = User.query.filter_by(user_id=user_id).first()
        if existing_user and (exclude_id is None or existing_user.id != exclude_id):
            errors.append("User ID already exists")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }

    @staticmethod
    def check_user_id_exists(user_id):
        """Check if a user ID already exists."""
        return User.query.filter_by(user_id=user_id).first() is not None
    
    @staticmethod
    def is_user_id_available(user_id, exclude_id=None):
        """Check if user_id is available (not taken by another user)."""
        query = User.query.filter_by(user_id=user_id)
        if exclude_id:
            query = query.filter(User.id != exclude_id)
        return query.first() is None

    def get_current_nutrition_goal(self):
        """Get the user's current nutrition goal."""
        return self.nutrition_goals.filter_by(is_active=True).first()
    
    def calculate_bmr(self):
        """Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation."""
        if not all([self.age, self.gender, self.height, self.weight]):
            return None
        
        if self.gender.lower() == 'male':
            bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age + 5
        else:
            bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age - 161
        
        return bmr
    
    def calculate_tdee(self):
        """Calculate Total Daily Energy Expenditure."""
        bmr = self.calculate_bmr()
        if not bmr or not self.activity_level:
            return None
        
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9
        }
        
        return bmr * activity_multipliers.get(self.activity_level, 1.2)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Food(db.Model):
    """Food model for nutrition database."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    brand = db.Column(db.String(50))  # For branded products like Amul, Nestlé
    category = db.Column(db.String(50), nullable=False, index=True)
    
    # Nutritional information per 100g
    calories = db.Column(db.Float, nullable=False, default=0)
    protein = db.Column(db.Float, nullable=False, default=0)
    carbs = db.Column(db.Float, nullable=False, default=0)
    fat = db.Column(db.Float, nullable=False, default=0)
    fiber = db.Column(db.Float, default=0)
    sugar = db.Column(db.Float, default=0)
    sodium = db.Column(db.Float, default=0)  # in mg
    
    # Additional information
    serving_size = db.Column(db.Float, default=100)  # in grams
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relationships
    meal_logs = db.relationship('MealLog', backref='food', lazy='dynamic')
    
    def get_nutrition_per_serving(self):
        """Get nutrition information per serving size."""
        factor = self.serving_size / 100
        return {
            'calories': self.calories * factor,
            'protein': self.protein * factor,
            'carbs': self.carbs * factor,
            'fat': self.fat * factor,
            'fiber': self.fiber * factor,
            'sugar': self.sugar * factor,
            'sodium': self.sodium * factor
        }
    
    def __repr__(self):
        return f'<Food {self.name}>'

class MealLog(db.Model):
    """Meal logging model."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    food_id = db.Column(db.Integer, db.ForeignKey('food.id'), nullable=False)
    
    quantity = db.Column(db.Float, nullable=False)  # in grams
    meal_type = db.Column(db.String(20), nullable=False)  # breakfast, lunch, dinner, snack
    logged_at = db.Column(db.DateTime, default=datetime.utcnow)
    date = db.Column(db.Date, default=datetime.utcnow().date(), index=True)
    
    # Calculated nutrition values (stored for performance)
    calories = db.Column(db.Float)
    protein = db.Column(db.Float)
    carbs = db.Column(db.Float)
    fat = db.Column(db.Float)
    fiber = db.Column(db.Float)
    
    def calculate_nutrition(self):
        """Calculate nutrition values based on quantity."""
        if self.food:
            factor = self.quantity / 100
            self.calories = self.food.calories * factor
            self.protein = self.food.protein * factor
            self.carbs = self.food.carbs * factor
            self.fat = self.food.fat * factor
            self.fiber = self.food.fiber * factor
    
    def __repr__(self):
        return f'<MealLog {self.user.username} - {self.food.name}>'

class NutritionGoal(db.Model):
    """User nutrition goals model."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Daily targets
    target_calories = db.Column(db.Float, nullable=False)
    target_protein = db.Column(db.Float, nullable=False)
    target_carbs = db.Column(db.Float)
    target_fat = db.Column(db.Float)
    target_fiber = db.Column(db.Float)
    
    # Goal settings
    goal_type = db.Column(db.String(20), nullable=False)  # lose, maintain, gain
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<NutritionGoal {self.user.username} - {self.goal_type}>'

class Challenge(db.Model):
    """Gamified challenges model."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    challenge_type = db.Column(db.String(20), nullable=False)  # protein, calories, streak
    target_value = db.Column(db.Float, nullable=False)
    duration_days = db.Column(db.Integer, default=30)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user_challenges = db.relationship('UserChallenge', backref='challenge', lazy='dynamic')
    
    def __repr__(self):
        return f'<Challenge {self.name}>'

class UserChallenge(db.Model):
    """User participation in challenges."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'), nullable=False)
    
    start_date = db.Column(db.Date, default=datetime.utcnow().date())
    end_date = db.Column(db.Date)
    current_progress = db.Column(db.Float, default=0)
    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    user = db.relationship('User', backref='user_challenges')
    
    def __repr__(self):
        return f'<UserChallenge {self.user.username} - {self.challenge.name}>'
