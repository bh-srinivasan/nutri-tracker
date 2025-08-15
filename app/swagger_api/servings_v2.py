"""
Interactive Servings API v2 with Swagger UI
"""
from flask import request, jsonify
from flask_restx import Resource
from app.swagger_api import servings_ns, servings_response_v2, error_model, swagger_login_required
from app.models import Food, FoodServing

@servings_ns.route('/food/<int:food_id>')
class FoodServingsV2(Resource):
    @servings_ns.doc('get_food_servings_v2')
    @servings_ns.marshal_with(servings_response_v2)
    @servings_ns.response(200, 'Success', servings_response_v2)
    @servings_ns.response(404, 'Food not found', error_model)
    @servings_ns.response(401, 'Authentication Required', error_model)
    @swagger_login_required
    def get(self, food_id):
        """
        Get all available servings for a specific food (Interactive API v2)
        
        **Interactive Endpoint**: Test directly in Swagger UI with real data!
        
        **Features:**
        - All available serving sizes for the food
        - Conversion factors (grams per unit)
        - Default serving information
        - Creation timestamps
        
        **Use Cases:**
        - Display serving options in meal logging UI
        - Calculate nutrition for different serving sizes
        - Provide user-friendly portion options
        
        **Example Response:**
        ```json
        {
          "food_id": 123,
          "food_name": "Chicken Breast",
          "servings": [
            {
              "id": 456,
              "food_id": 123,
              "serving_name": "1 piece (medium)",
              "unit": "piece",
              "grams_per_unit": 150,
              "created_at": "2025-08-14T10:30:00"
            },
            {
              "id": 457,
              "food_id": 123,
              "serving_name": "1 cup, diced",
              "unit": "cup",
              "grams_per_unit": 140,
              "created_at": "2025-08-14T10:31:00"
            }
          ],
          "default_serving_id": 456
        }
        ```
        
        **Integration Notes:**
        - Use serving IDs for meal logging with serving-based input
        - `grams_per_unit` is used to calculate total grams consumed
        - Default serving can be pre-selected in UI
        """
        # Check if food exists
        food = Food.query.filter_by(id=food_id, is_verified=True).first()
        if not food:
            return {'error': f'Food with ID {food_id} not found'}, 404
        
        # Get all servings for this food
        servings = [
            {
                'id': serving.id,
                'food_id': serving.food_id,
                'serving_name': serving.serving_name,
                'unit': serving.unit,
                'grams_per_unit': serving.grams_per_unit,
                'created_at': serving.created_at.isoformat() if serving.created_at else None
            }
            for serving in food.servings
        ]
        
        return {
            'food_id': food.id,
            'food_name': food.name,
            'servings': servings,
            'default_serving_id': servings[0]['id'] if servings else None
        }
