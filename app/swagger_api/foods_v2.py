"""
Interactive Foods API v2 with Swagger UI
"""
from flask import request, jsonify
from flask_restx import Resource
from flask_login import login_required, current_user
from app.swagger_api import foods_ns, food_v2_model, food_search_response_v2, error_model, swagger_login_required
from app.models import Food, FoodServing
from app import db
from sqlalchemy import or_

@foods_ns.route('/search')
class FoodSearchV2(Resource):
    @foods_ns.doc('search_foods_v2')
    @foods_ns.marshal_with(food_search_response_v2)
    @foods_ns.param('q', 'Search query string', required=True, type='string')
    @foods_ns.param('category', 'Filter by category', required=False, type='string')
    @foods_ns.param('brand', 'Filter by brand', required=False, type='string')
    @foods_ns.param('page', 'Page number (default: 1)', required=False, type='integer', default=1)
    @foods_ns.param('per_page', 'Results per page (default: 20, max: 100)', required=False, type='integer', default=20)
    @foods_ns.response(200, 'Success', food_search_response_v2)
    @foods_ns.response(400, 'Bad Request', error_model)
    @foods_ns.response(401, 'Authentication Required', error_model)
    @swagger_login_required
    def get(self):
        """
        Search for foods with serving information (Interactive API v2)
        
        **Interactive Endpoint**: Test directly in Swagger UI with real data!
        
        **Features:**
        - Returns foods with complete serving information
        - Supports flexible search across food names, brands, and categories
        - Enhanced pagination with detailed metadata
        - Results include all available servings for each food
        
        **Example Response Structure:**
        ```json
        {
          "foods": [
            {
              "id": 123,
              "name": "Chicken Breast",
              "brand": "Fresh Farm",
              "category": "Protein",
              "calories_per_100g": 165,
              "protein_per_100g": 31,
              "servings": [
                {
                  "id": 456,
                  "serving_name": "1 piece (medium)",
                  "unit": "piece", 
                  "grams_per_unit": 150
                }
              ],
              "default_serving_id": 456
            }
          ],
          "pagination": {
            "page": 1,
            "per_page": 20,
            "total": 150,
            "pages": 8,
            "has_next": true
          }
        }
        ```
        """
        # Get query parameters
        query = request.args.get('q', '').strip()
        category = request.args.get('category', '').strip()
        brand = request.args.get('brand', '').strip()
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        if not query:
            return {'error': 'Search query (q) is required'}, 400
        
        # Build query
        search_query = Food.query.filter(Food.is_verified == True)
        
        # Add search filters
        if query:
            search_terms = query.split()
            for term in search_terms:
                search_query = search_query.filter(
                    or_(
                        Food.name.ilike(f'%{term}%'),
                        Food.brand.ilike(f'%{term}%'),
                        Food.description.ilike(f'%{term}%')
                    )
                )
        
        if category:
            search_query = search_query.filter(Food.category.ilike(f'%{category}%'))
        
        if brand:
            search_query = search_query.filter(Food.brand.ilike(f'%{brand}%'))
        
        # Paginate results
        paginated = search_query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Format results with servings
        foods = []
        for food in paginated.items:
            servings = [
                {
                    'id': serving.id,
                    'serving_name': serving.serving_name,
                    'unit': serving.unit,
                    'grams_per_unit': serving.grams_per_unit
                }
                for serving in food.servings
            ]
            
            foods.append({
                'id': food.id,
                'name': food.name,
                'brand': food.brand or '',
                'category': food.category or '',
                'description': food.description or '',
                'calories_per_100g': food.calories,
                'protein_per_100g': food.protein,
                'carbs_per_100g': food.carbs,
                'fat_per_100g': food.fat,
                'fiber_per_100g': food.fiber or 0,
                'sugar_per_100g': food.sugar or 0,
                'sodium_per_100g': food.sodium or 0,
                'verified': food.is_verified,
                'servings': servings,
                'default_serving_id': servings[0]['id'] if servings else None
            })
        
        return {
            'foods': foods,
            'pagination': {
                'page': paginated.page,
                'per_page': paginated.per_page,
                'total': paginated.total,
                'pages': paginated.pages,
                'has_prev': paginated.has_prev,
                'has_next': paginated.has_next
            }
        }

@foods_ns.route('/<int:food_id>')
class FoodDetailV2(Resource):
    @foods_ns.doc('get_food_detail_v2')
    @foods_ns.marshal_with(food_v2_model)
    @foods_ns.response(200, 'Success', food_v2_model)
    @foods_ns.response(404, 'Food not found', error_model)
    @foods_ns.response(401, 'Authentication Required', error_model)
    @swagger_login_required
    def get(self, food_id):
        """
        Get detailed food information with servings (API v2)
        
        **IMPORTANT**: This documentation endpoint redirects to the actual API v2 endpoint.
        
        **Actual API Endpoint**: `GET /api/v2/foods/{food_id}`
        
        **Features:**
        - Complete nutrition information per 100g
        - All available serving sizes for the food
        - Default serving information
        - Verification status
        
        **Example Response:**
        ```json
        {
          "id": 123,
          "name": "Chicken Breast",
          "brand": "Fresh Farm",
          "category": "Protein",
          "description": "Skinless chicken breast",
          "calories_per_100g": 165,
          "protein_per_100g": 31,
          "carbs_per_100g": 0,
          "fat_per_100g": 3.6,
          "verified": true,
          "servings": [
            {
              "id": 456,
              "serving_name": "1 piece (medium)",
              "unit": "piece",
              "grams_per_unit": 150
            },
            {
              "id": 457,
              "serving_name": "1 cup, diced",
              "unit": "cup",
              "grams_per_unit": 140
            }
          ],
          "default_serving_id": 456
        }
        ```
        """
        food = Food.query.filter_by(id=food_id, is_verified=True).first()
        if not food:
            return {'error': f'Food with ID {food_id} not found'}, 404
        
        # Get all servings for this food
        servings = [
            {
                'id': serving.id,
                'serving_name': serving.serving_name,
                'unit': serving.unit,
                'grams_per_unit': serving.grams_per_unit
            }
            for serving in food.servings
        ]
        
        return {
            'id': food.id,
            'name': food.name,
            'brand': food.brand or '',
            'category': food.category or '',
            'description': food.description or '',
            'calories_per_100g': food.calories,
            'protein_per_100g': food.protein,
            'carbs_per_100g': food.carbs,
            'fat_per_100g': food.fat,
            'fiber_per_100g': food.fiber or 0,
            'sugar_per_100g': food.sugar or 0,
            'sodium_per_100g': food.sodium or 0,
            'verified': food.is_verified,
            'servings': servings,
            'default_serving_id': servings[0]['id'] if servings else None
        }
