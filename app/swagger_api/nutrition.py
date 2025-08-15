"""
Nutrition Analysis API endpoints with Swagger documentation
"""
from flask import request
from flask_restx import Resource
from flask_login import current_user
from app.swagger_api import nutrition_ns, nutrition_summary_model, error_model, swagger_login_required
from app.models import MealLog
from app import db
from datetime import datetime, date, timedelta
from sqlalchemy import func

@nutrition_ns.route('/summary')
class NutritionSummary(Resource):
    @nutrition_ns.doc('get_nutrition_summary')
    @nutrition_ns.param('date', 'Specific date (YYYY-MM-DD, default: today)', required=False, type='string')
    @nutrition_ns.marshal_with(nutrition_summary_model)
    @nutrition_ns.response(200, 'Success', nutrition_summary_model)
    @nutrition_ns.response(400, 'Bad Request', error_model)
    @nutrition_ns.response(401, 'Authentication Required', error_model)
    @swagger_login_required
    def get(self):
        """
        Get nutrition summary for a specific date
        
        Returns total nutrition information and breakdown by meal type for the specified date.
        """
        date_param = request.args.get('date')
        
        if date_param:
            try:
                target_date = datetime.strptime(date_param, '%Y-%m-%d').date()
            except ValueError:
                nutrition_ns.abort(400, 'date must be in YYYY-MM-DD format')
        else:
            target_date = date.today()
        
        # Get all meal logs for the specified date
        meal_logs = MealLog.query.filter_by(
            user_id=current_user.id,
            date=target_date
        ).all()
        
        # Calculate totals
        total_calories = sum(log.calories or 0 for log in meal_logs)
        total_protein = sum(log.protein or 0 for log in meal_logs)
        total_carbs = sum(log.carbs or 0 for log in meal_logs)
        total_fat = sum(log.fat or 0 for log in meal_logs)
        total_fiber = sum(log.fiber or 0 for log in meal_logs)
        total_sugar = sum(log.sugar or 0 for log in meal_logs)
        total_sodium = sum(log.sodium or 0 for log in meal_logs)
        
        # Calculate breakdown by meal type
        meal_breakdown = {}
        for meal_type in ['breakfast', 'lunch', 'dinner', 'snack']:
            meal_logs_filtered = [log for log in meal_logs if log.meal_type == meal_type]
            meal_breakdown[meal_type] = {
                'calories': sum(log.calories or 0 for log in meal_logs_filtered),
                'protein': sum(log.protein or 0 for log in meal_logs_filtered),
                'carbs': sum(log.carbs or 0 for log in meal_logs_filtered),
                'fat': sum(log.fat or 0 for log in meal_logs_filtered),
                'fiber': sum(log.fiber or 0 for log in meal_logs_filtered),
                'sugar': sum(log.sugar or 0 for log in meal_logs_filtered),
                'sodium': sum(log.sodium or 0 for log in meal_logs_filtered),
                'count': len(meal_logs_filtered)
            }
        
        return {
            'date': target_date.isoformat(),
            'total_calories': round(total_calories, 2),
            'total_protein': round(total_protein, 2),
            'total_carbs': round(total_carbs, 2),
            'total_fat': round(total_fat, 2),
            'total_fiber': round(total_fiber, 2),
            'total_sugar': round(total_sugar, 2),
            'total_sodium': round(total_sodium, 2),
            'meal_breakdown': meal_breakdown
        }

@nutrition_ns.route('/weekly')
class WeeklyNutrition(Resource):
    @nutrition_ns.doc('get_weekly_nutrition')
    @nutrition_ns.param('start_date', 'Start date for week (YYYY-MM-DD, default: 7 days ago)', required=False, type='string')
    @nutrition_ns.response(200, 'Success')
    @nutrition_ns.response(400, 'Bad Request', error_model)
    @nutrition_ns.response(401, 'Authentication Required', error_model)
    @swagger_login_required
    def get(self):
        """
        Get nutrition summary for a 7-day period
        
        Returns daily nutrition totals for a week period.
        """
        start_date_param = request.args.get('start_date')
        
        if start_date_param:
            try:
                start_date = datetime.strptime(start_date_param, '%Y-%m-%d').date()
            except ValueError:
                nutrition_ns.abort(400, 'start_date must be in YYYY-MM-DD format')
        else:
            start_date = date.today() - timedelta(days=6)  # Last 7 days including today
        
        end_date = start_date + timedelta(days=6)
        
        # Get all meal logs for the date range
        meal_logs = MealLog.query.filter(
            MealLog.user_id == current_user.id,
            MealLog.date >= start_date,
            MealLog.date <= end_date
        ).all()
        
        # Group by date
        daily_nutrition = {}
        current_date = start_date
        
        while current_date <= end_date:
            daily_logs = [log for log in meal_logs if log.date == current_date]
            
            daily_nutrition[current_date.isoformat()] = {
                'date': current_date.isoformat(),
                'calories': round(sum(log.calories or 0 for log in daily_logs), 2),
                'protein': round(sum(log.protein or 0 for log in daily_logs), 2),
                'carbs': round(sum(log.carbs or 0 for log in daily_logs), 2),
                'fat': round(sum(log.fat or 0 for log in daily_logs), 2),
                'fiber': round(sum(log.fiber or 0 for log in daily_logs), 2),
                'sugar': round(sum(log.sugar or 0 for log in daily_logs), 2),
                'sodium': round(sum(log.sodium or 0 for log in daily_logs), 2),
                'meal_count': len(daily_logs)
            }
            
            current_date += timedelta(days=1)
        
        # Calculate weekly averages
        weekly_avg = {
            'avg_calories': round(sum(day['calories'] for day in daily_nutrition.values()) / 7, 2),
            'avg_protein': round(sum(day['protein'] for day in daily_nutrition.values()) / 7, 2),
            'avg_carbs': round(sum(day['carbs'] for day in daily_nutrition.values()) / 7, 2),
            'avg_fat': round(sum(day['fat'] for day in daily_nutrition.values()) / 7, 2),
            'avg_fiber': round(sum(day['fiber'] for day in daily_nutrition.values()) / 7, 2),
            'avg_sugar': round(sum(day['sugar'] for day in daily_nutrition.values()) / 7, 2),
            'avg_sodium': round(sum(day['sodium'] for day in daily_nutrition.values()) / 7, 2),
            'total_meals': sum(day['meal_count'] for day in daily_nutrition.values())
        }
        
        return {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'daily_nutrition': daily_nutrition,
            'weekly_averages': weekly_avg
        }

@nutrition_ns.route('/trends')
class NutritionTrends(Resource):
    @nutrition_ns.doc('get_nutrition_trends')
    @nutrition_ns.param('days', 'Number of days to analyze (default: 30, max: 90)', required=False, type='integer', default=30)
    @nutrition_ns.response(200, 'Success')
    @nutrition_ns.response(400, 'Bad Request', error_model)
    @nutrition_ns.response(401, 'Authentication Required', error_model)
    @swagger_login_required
    def get(self):
        """
        Get nutrition trends over time
        
        Returns nutrition trends and statistics over a specified period.
        """
        days = min(90, max(1, int(request.args.get('days', 30))))
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        # Get aggregated nutrition data by date
        nutrition_data = db.session.query(
            MealLog.date,
            func.sum(MealLog.calories).label('total_calories'),
            func.sum(MealLog.protein).label('total_protein'),
            func.sum(MealLog.carbs).label('total_carbs'),
            func.sum(MealLog.fat).label('total_fat'),
            func.sum(MealLog.fiber).label('total_fiber'),
            func.sum(MealLog.sugar).label('total_sugar'),
            func.sum(MealLog.sodium).label('total_sodium'),
            func.count(MealLog.id).label('meal_count')
        ).filter(
            MealLog.user_id == current_user.id,
            MealLog.date >= start_date,
            MealLog.date <= end_date
        ).group_by(MealLog.date).order_by(MealLog.date).all()
        
        # Calculate statistics
        if nutrition_data:
            calories_list = [row.total_calories or 0 for row in nutrition_data]
            protein_list = [row.total_protein or 0 for row in nutrition_data]
            
            avg_calories = sum(calories_list) / len(calories_list)
            avg_protein = sum(protein_list) / len(protein_list)
            
            max_calories = max(calories_list)
            min_calories = min(calories_list)
            max_protein = max(protein_list)
            min_protein = min(protein_list)
            
            total_meals = sum(row.meal_count for row in nutrition_data)
            days_with_data = len(nutrition_data)
        else:
            avg_calories = avg_protein = 0
            max_calories = min_calories = max_protein = min_protein = 0
            total_meals = days_with_data = 0
        
        # Format daily data
        daily_data = []
        for row in nutrition_data:
            daily_data.append({
                'date': row.date.isoformat(),
                'calories': round(row.total_calories or 0, 2),
                'protein': round(row.total_protein or 0, 2),
                'carbs': round(row.total_carbs or 0, 2),
                'fat': round(row.total_fat or 0, 2),
                'fiber': round(row.total_fiber or 0, 2),
                'sugar': round(row.total_sugar or 0, 2),
                'sodium': round(row.total_sodium or 0, 2),
                'meal_count': row.meal_count
            })
        
        return {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days_requested': days,
                'days_with_data': days_with_data
            },
            'statistics': {
                'avg_daily_calories': round(avg_calories, 2),
                'avg_daily_protein': round(avg_protein, 2),
                'max_daily_calories': round(max_calories, 2),
                'min_daily_calories': round(min_calories, 2),
                'max_daily_protein': round(max_protein, 2),
                'min_daily_protein': round(min_protein, 2),
                'total_meals_logged': total_meals,
                'avg_meals_per_day': round(total_meals / max(1, days_with_data), 2)
            },
            'daily_data': daily_data
        }
