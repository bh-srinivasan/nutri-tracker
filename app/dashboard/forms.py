from flask_wtf import FlaskForm
from wtforms import SelectField, FloatField, StringField, SubmitField, HiddenField, DateField
from wtforms.validators import DataRequired, NumberRange, Optional
from datetime import date

class MealLogForm(FlaskForm):
    """Form for logging meals."""
    food_id = HiddenField('Food ID', validators=[DataRequired()])
    food_name = StringField('Food', render_kw={'readonly': True})
    quantity = FloatField('Quantity (grams)', validators=[
        DataRequired(), 
        NumberRange(min=0.1, max=2000, message='Quantity must be between 0.1 and 2000 grams')
    ])
    meal_type = SelectField('Meal Type', choices=[
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack')
    ], validators=[DataRequired()])
    date = DateField('Date', default=date.today, validators=[DataRequired()])
    submit = SubmitField('Log Meal')

class NutritionGoalForm(FlaskForm):
    """Form for setting nutrition goals."""
    goal_type = SelectField('Goal Type', choices=[
        ('lose', 'Lose Weight'),
        ('maintain', 'Maintain Weight'),
        ('gain', 'Gain Weight')
    ], validators=[DataRequired()])
    target_calories = FloatField('Target Calories', validators=[
        DataRequired(), 
        NumberRange(min=800, max=5000, message='Target calories must be between 800 and 5000')
    ])
    target_protein = FloatField('Target Protein (g)', validators=[
        DataRequired(), 
        NumberRange(min=10, max=300, message='Target protein must be between 10 and 300g')
    ])
    target_carbs = FloatField('Target Carbs (g)', validators=[
        Optional(), 
        NumberRange(min=0, max=500, message='Target carbs must be between 0 and 500g')
    ])
    target_fat = FloatField('Target Fat (g)', validators=[
        Optional(), 
        NumberRange(min=0, max=200, message='Target fat must be between 0 and 200g')
    ])
    target_fiber = FloatField('Target Fiber (g)', validators=[
        Optional(), 
        NumberRange(min=0, max=100, message='Target fiber must be between 0 and 100g')
    ])
    submit = SubmitField('Set Goals')

class FoodSearchForm(FlaskForm):
    """Form for searching foods."""
    search = StringField('Search Foods', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('', 'All Categories'),
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
    ])
    submit = SubmitField('Search')

class QuickLogForm(FlaskForm):
    """Form for quick meal logging from dashboard."""
    food_search = StringField('Search Food', validators=[DataRequired()])
    submit = SubmitField('Search')
