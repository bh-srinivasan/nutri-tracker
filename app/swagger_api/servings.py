"""
Food Servings API endpoints with Swagger documentation
"""
from flask import request
from flask_restx import Resource
from app.swagger_api import servings_ns, food_serving_model, error_model, swagger_login_required
from app.models import Food, FoodServing
from app import db

@servings_ns.route('/food/<int:food_id>')
class FoodServings(Resource):
    @servings_ns.doc('get_food_servings')
    @servings_ns.marshal_list_with(food_serving_model)
    @servings_ns.response(200, 'Success', [food_serving_model])
    @servings_ns.response(404, 'Food not found', error_model)
    @servings_ns.response(401, 'Authentication Required', error_model)
    @swagger_login_required
    def get(self, food_id):
        """
        Get all available servings for a specific food
        
        Returns all serving options available for the specified food item.
        """
        food = Food.query.get(food_id)
        if not food:
            servings_ns.abort(404, f'Food with ID {food_id} not found')
        
        servings = FoodServing.query.filter_by(food_id=food_id).order_by(FoodServing.serving_name).all()
        
        servings_data = []
        for serving in servings:
            serving_dict = {
                'id': serving.id,
                'food_id': serving.food_id,
                'serving_name': serving.serving_name,
                'unit': serving.unit,
                'grams_per_unit': serving.grams_per_unit,
                'created_at': serving.created_at.isoformat() if serving.created_at else None
            }
            servings_data.append(serving_dict)
        
        return servings_data

@servings_ns.route('/<int:serving_id>')
class ServingDetail(Resource):
    @servings_ns.doc('get_serving_detail')
    @servings_ns.marshal_with(food_serving_model)
    @servings_ns.response(200, 'Success', food_serving_model)
    @servings_ns.response(404, 'Serving not found', error_model)
    @servings_ns.response(401, 'Authentication Required', error_model)
    @swagger_login_required
    def get(self, serving_id):
        """
        Get detailed information about a specific serving
        
        Returns complete information about a food serving.
        """
        serving = FoodServing.query.get(serving_id)
        if not serving:
            servings_ns.abort(404, f'Serving with ID {serving_id} not found')
        
        return {
            'id': serving.id,
            'food_id': serving.food_id,
            'serving_name': serving.serving_name,
            'unit': serving.unit,
            'grams_per_unit': serving.grams_per_unit,
            'created_at': serving.created_at.isoformat() if serving.created_at else None
        }

@servings_ns.route('/<int:serving_id>/nutrition')
class ServingNutrition(Resource):
    @servings_ns.doc('get_serving_nutrition')
    @servings_ns.param('quantity', 'Number of servings (default: 1)', required=False, type='float', default=1.0)
    @servings_ns.response(200, 'Success')
    @servings_ns.response(404, 'Serving not found', error_model)
    @servings_ns.response(401, 'Authentication Required', error_model)
    @swagger_login_required
    def get(self, serving_id):
        """
        Calculate nutrition information for a specific serving
        
        Returns calculated nutrition values based on the serving size and quantity.
        """
        serving = FoodServing.query.get(serving_id)
        if not serving:
            servings_ns.abort(404, f'Serving with ID {serving_id} not found')
        
        food = Food.query.get(serving.food_id)
        if not food:
            servings_ns.abort(404, f'Food not found for serving {serving_id}')
        
        quantity = float(request.args.get('quantity', 1.0))
        if quantity <= 0:
            servings_ns.abort(400, 'Quantity must be greater than 0')
        
        # Calculate total grams
        total_grams = serving.grams_per_unit * quantity
        
        # Calculate nutrition per gram ratio
        gram_ratio = total_grams / 100.0
        
        nutrition = {
            'serving_info': {
                'serving_name': serving.serving_name,
                'unit': serving.unit,
                'grams_per_unit': serving.grams_per_unit,
                'quantity': quantity,
                'total_grams': total_grams
            },
            'nutrition': {
                'calories': round(food.calories * gram_ratio, 2) if food.calories else 0,
                'protein': round(food.protein * gram_ratio, 2) if food.protein else 0,
                'carbs': round(food.carbs * gram_ratio, 2) if food.carbs else 0,
                'fat': round(food.fat * gram_ratio, 2) if food.fat else 0,
                'fiber': round(food.fiber * gram_ratio, 2) if food.fiber else 0,
                'sugar': round(food.sugar * gram_ratio, 2) if food.sugar else 0,
                'sodium': round(food.sodium * gram_ratio, 2) if food.sodium else 0
            },
            'food_info': {
                'id': food.id,
                'name': food.name,
                'brand': food.brand,
                'category': food.category
            }
        }
        
        return nutrition
