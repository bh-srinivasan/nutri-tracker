"""
Foods API endpoints with Swagger documentation
"""
from flask import request
from flask_restx import Resource
from app.swagger_api import foods_ns, food_model, food_search_response_model, error_model, swagger_login_required
from app.models import Food, FoodServing
from app import db
from sqlalchemy import or_

@foods_ns.route('/search')
class FoodSearch(Resource):
    @foods_ns.doc('search_foods')
    @foods_ns.marshal_with(food_search_response_model)
    @foods_ns.param('q', 'Search query string', required=True, type='string')
    @foods_ns.param('category', 'Filter by category', required=False, type='string')
    @foods_ns.param('brand', 'Filter by brand', required=False, type='string')
    @foods_ns.param('page', 'Page number (default: 1)', required=False, type='integer', default=1)
    @foods_ns.param('per_page', 'Results per page (default: 20, max: 100)', required=False, type='integer', default=20)
    @foods_ns.response(200, 'Success', food_search_response_model)
    @foods_ns.response(400, 'Bad Request', error_model)
    @foods_ns.response(401, 'Authentication Required', error_model)
    @swagger_login_required
    def get(self):
        """
        Search for foods by name, brand, or category
        
        Supports flexible search across food names, brands, and categories.
        Results can be filtered and paginated.
        """
        query = request.args.get('q', '').strip()
        if not query:
            foods_ns.abort(400, 'Query parameter "q" is required')
        
        category = request.args.get('category', '').strip()
        brand = request.args.get('brand', '').strip()
        page = max(1, int(request.args.get('page', 1)))
        per_page = min(100, max(1, int(request.args.get('per_page', 20))))
        
        # Build the search query
        search_filter = or_(
            Food.name.ilike(f'%{query}%'),
            Food.brand.ilike(f'%{query}%'),
            Food.category.ilike(f'%{query}%')
        )
        
        foods_query = Food.query.filter(search_filter)
        
        # Apply additional filters
        if category:
            foods_query = foods_query.filter(Food.category.ilike(f'%{category}%'))
        if brand:
            foods_query = foods_query.filter(Food.brand.ilike(f'%{brand}%'))
        
        # Order by verified foods first, then by name
        foods_query = foods_query.order_by(Food.is_verified.desc(), Food.name)
        
        # Paginate
        pagination = foods_query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        foods_data = []
        for food in pagination.items:
            food_dict = {
                'id': food.id,
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
                'default_serving_size_grams': food.default_serving_size_grams,
                'is_verified': food.is_verified
            }
            foods_data.append(food_dict)
        
        return {
            'foods': foods_data,
            'total': pagination.total,
            'page': page,
            'per_page': per_page
        }

@foods_ns.route('/<int:food_id>')
class FoodDetail(Resource):
    @foods_ns.doc('get_food_detail')
    @foods_ns.marshal_with(food_model)
    @foods_ns.response(200, 'Success', food_model)
    @foods_ns.response(404, 'Food not found', error_model)
    @foods_ns.response(401, 'Authentication Required', error_model)
    @swagger_login_required
    def get(self, food_id):
        """
        Get detailed information about a specific food
        
        Returns complete nutrition information for a food item.
        """
        food = Food.query.get(food_id)
        if not food:
            foods_ns.abort(404, f'Food with ID {food_id} not found')
        
        return {
            'id': food.id,
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
            'default_serving_size_grams': food.default_serving_size_grams,
            'is_verified': food.is_verified
        }

@foods_ns.route('/categories')
class FoodCategories(Resource):
    @foods_ns.doc('get_food_categories')
    @foods_ns.response(200, 'Success')
    @foods_ns.response(401, 'Authentication Required', error_model)
    @swagger_login_required
    def get(self):
        """
        Get list of all available food categories
        
        Returns unique food categories available in the database.
        """
        categories = db.session.query(Food.category).distinct().filter(
            Food.category.isnot(None),
            Food.category != ''
        ).order_by(Food.category).all()
        
        return {
            'categories': [cat[0] for cat in categories if cat[0]]
        }

@foods_ns.route('/brands')
class FoodBrands(Resource):
    @foods_ns.doc('get_food_brands')
    @foods_ns.response(200, 'Success')
    @foods_ns.response(401, 'Authentication Required', error_model)
    @swagger_login_required
    def get(self):
        """
        Get list of all available food brands
        
        Returns unique food brands available in the database.
        """
        brands = db.session.query(Food.brand).distinct().filter(
            Food.brand.isnot(None),
            Food.brand != ''
        ).order_by(Food.brand).all()
        
        return {
            'brands': [brand[0] for brand in brands if brand[0]]
        }
