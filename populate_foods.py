"""
Sample Indian food data for populating the database.
This script adds common Indian foods and branded products to the database.
"""

from app import create_app, db
from app.models import Food

def populate_indian_foods():
    """Populate database with Indian food items."""
    
    foods_data = [
        # Grains & Cereals
        {"name": "Basmati Rice (cooked)", "category": "grains", "calories": 130, "protein": 2.7, "carbs": 28.0, "fat": 0.3, "fiber": 0.4},
        {"name": "Brown Rice (cooked)", "category": "grains", "calories": 112, "protein": 2.6, "carbs": 23.0, "fat": 0.9, "fiber": 1.8},
        {"name": "Wheat Chapati", "category": "grains", "calories": 104, "protein": 3.1, "carbs": 18.0, "fat": 0.4, "fiber": 2.8},
        {"name": "Quinoa (cooked)", "category": "grains", "calories": 120, "protein": 4.4, "carbs": 22.0, "fat": 1.9, "fiber": 2.8},
        {"name": "Oats", "category": "grains", "calories": 389, "protein": 16.9, "carbs": 66.3, "fat": 6.9, "fiber": 10.6},
        
        # Legumes & Pulses
        {"name": "Moong Dal (cooked)", "category": "legumes", "calories": 104, "protein": 7.6, "carbs": 16.3, "fat": 0.4, "fiber": 5.4},
        {"name": "Toor Dal (cooked)", "category": "legumes", "calories": 118, "protein": 8.9, "carbs": 17.1, "fat": 0.7, "fiber": 5.1},
        {"name": "Chana Dal (cooked)", "category": "legumes", "calories": 164, "protein": 8.9, "carbs": 27.4, "fat": 2.6, "fiber": 7.6},
        {"name": "Rajma (cooked)", "category": "legumes", "calories": 127, "protein": 8.7, "carbs": 22.8, "fat": 0.5, "fiber": 6.4},
        {"name": "Chickpeas (cooked)", "category": "legumes", "calories": 164, "protein": 8.9, "carbs": 27.4, "fat": 2.6, "fiber": 7.6},
        
        # Vegetables
        {"name": "Spinach (Palak)", "category": "vegetables", "calories": 23, "protein": 2.9, "carbs": 3.6, "fat": 0.4, "fiber": 2.2},
        {"name": "Tomato", "category": "vegetables", "calories": 18, "protein": 0.9, "carbs": 3.9, "fat": 0.2, "fiber": 1.2},
        {"name": "Onion", "category": "vegetables", "calories": 40, "protein": 1.1, "carbs": 9.3, "fat": 0.1, "fiber": 1.7},
        {"name": "Potato", "category": "vegetables", "calories": 77, "protein": 2.0, "carbs": 17.5, "fat": 0.1, "fiber": 2.2},
        {"name": "Broccoli", "category": "vegetables", "calories": 34, "protein": 2.8, "carbs": 6.6, "fat": 0.4, "fiber": 2.6},
        {"name": "Cauliflower (Gobi)", "category": "vegetables", "calories": 25, "protein": 1.9, "carbs": 5.0, "fat": 0.3, "fiber": 2.0},
        {"name": "Bell Pepper (Capsicum)", "category": "vegetables", "calories": 31, "protein": 1.0, "carbs": 7.3, "fat": 0.3, "fiber": 2.5},
        {"name": "Okra (Bhindi)", "category": "vegetables", "calories": 33, "protein": 1.9, "carbs": 7.5, "fat": 0.2, "fiber": 3.2},
        
        # Fruits
        {"name": "Apple", "category": "fruits", "calories": 52, "protein": 0.3, "carbs": 13.8, "fat": 0.2, "fiber": 2.4},
        {"name": "Banana", "category": "fruits", "calories": 89, "protein": 1.1, "carbs": 22.8, "fat": 0.3, "fiber": 2.6},
        {"name": "Mango", "category": "fruits", "calories": 60, "protein": 0.8, "carbs": 15.0, "fat": 0.4, "fiber": 1.6},
        {"name": "Orange", "category": "fruits", "calories": 47, "protein": 0.9, "carbs": 11.8, "fat": 0.1, "fiber": 2.4},
        {"name": "Papaya", "category": "fruits", "calories": 43, "protein": 0.5, "carbs": 10.8, "fat": 0.3, "fiber": 1.7},
        {"name": "Guava", "category": "fruits", "calories": 68, "protein": 2.6, "carbs": 14.3, "fat": 1.0, "fiber": 5.4},
        
        # Dairy Products
        {"name": "Milk (full fat)", "category": "dairy", "calories": 61, "protein": 3.2, "carbs": 4.8, "fat": 3.3, "fiber": 0},
        {"name": "Milk (low fat)", "category": "dairy", "calories": 42, "protein": 3.4, "carbs": 5.0, "fat": 1.0, "fiber": 0},
        {"name": "Yogurt (plain)", "category": "dairy", "calories": 59, "protein": 10.0, "carbs": 3.6, "fat": 0.4, "fiber": 0},
        {"name": "Paneer", "category": "dairy", "calories": 265, "protein": 18.3, "carbs": 1.2, "fat": 20.8, "fiber": 0},
        {"name": "Cheddar Cheese", "category": "dairy", "calories": 403, "protein": 25.0, "carbs": 1.3, "fat": 33.1, "fiber": 0},
        
        # Meat & Poultry
        {"name": "Chicken Breast (cooked)", "category": "meat", "calories": 165, "protein": 31.0, "carbs": 0, "fat": 3.6, "fiber": 0},
        {"name": "Chicken Thigh (cooked)", "category": "meat", "calories": 209, "protein": 26.0, "carbs": 0, "fat": 10.9, "fiber": 0},
        {"name": "Mutton (cooked)", "category": "meat", "calories": 258, "protein": 25.6, "carbs": 0, "fat": 16.6, "fiber": 0},
        {"name": "Egg (whole)", "category": "meat", "calories": 155, "protein": 13.0, "carbs": 1.1, "fat": 10.6, "fiber": 0},
        {"name": "Egg White", "category": "meat", "calories": 52, "protein": 10.9, "carbs": 0.7, "fat": 0.2, "fiber": 0},
        
        # Fish & Seafood
        {"name": "Salmon (cooked)", "category": "fish", "calories": 206, "protein": 22.0, "carbs": 0, "fat": 12.4, "fiber": 0},
        {"name": "Tuna (cooked)", "category": "fish", "calories": 184, "protein": 25.4, "carbs": 0, "fat": 6.3, "fiber": 0},
        {"name": "Rohu Fish (cooked)", "category": "fish", "calories": 97, "protein": 16.6, "carbs": 0, "fat": 2.2, "fiber": 0},
        {"name": "Pomfret (cooked)", "category": "fish", "calories": 112, "protein": 18.8, "carbs": 0, "fat": 4.2, "fiber": 0},
        {"name": "Prawns (cooked)", "category": "fish", "calories": 99, "protein": 18.9, "carbs": 0.9, "fat": 1.4, "fiber": 0},
        
        # Nuts & Seeds
        {"name": "Almonds", "category": "nuts", "calories": 579, "protein": 21.2, "carbs": 21.6, "fat": 49.9, "fiber": 12.5},
        {"name": "Walnuts", "category": "nuts", "calories": 654, "protein": 15.2, "carbs": 13.7, "fat": 65.2, "fiber": 6.7},
        {"name": "Cashew Nuts", "category": "nuts", "calories": 553, "protein": 18.2, "carbs": 30.2, "fat": 43.9, "fiber": 3.3},
        {"name": "Peanuts", "category": "nuts", "calories": 567, "protein": 25.8, "carbs": 16.1, "fat": 49.2, "fiber": 8.5},
        {"name": "Sunflower Seeds", "category": "nuts", "calories": 584, "protein": 20.8, "carbs": 20.0, "fat": 51.5, "fiber": 8.6},
        
        # Branded Products - Amul
        {"name": "Amul Butter", "brand": "Amul", "category": "dairy", "calories": 717, "protein": 0.9, "carbs": 0.1, "fat": 81.1, "fiber": 0},
        {"name": "Amul Cheese Slices", "brand": "Amul", "category": "dairy", "calories": 280, "protein": 22.0, "carbs": 4.0, "fat": 20.0, "fiber": 0},
        {"name": "Amul Lassi", "brand": "Amul", "category": "beverages", "calories": 85, "protein": 3.0, "carbs": 13.0, "fat": 2.5, "fiber": 0},
        {"name": "Amul Taaza Milk", "brand": "Amul", "category": "dairy", "calories": 67, "protein": 3.2, "carbs": 4.4, "fat": 4.1, "fiber": 0},
        
        # Branded Products - Nestlé
        {"name": "Maggi 2-Minute Noodles", "brand": "Nestlé", "category": "processed", "calories": 444, "protein": 10.4, "carbs": 60.1, "fat": 17.4, "fiber": 3.2},
        {"name": "Nestlé Cerelac", "brand": "Nestlé", "category": "processed", "calories": 408, "protein": 13.6, "carbs": 59.7, "fat": 12.8, "fiber": 4.5},
        {"name": "Kit Kat Chocolate", "brand": "Nestlé", "category": "sweets", "calories": 518, "protein": 7.3, "carbs": 59.0, "fat": 27.8, "fiber": 0},
        
        # Branded Products - Britannia
        {"name": "Britannia Marie Gold Biscuits", "brand": "Britannia", "category": "snacks", "calories": 443, "protein": 8.1, "carbs": 72.6, "fat": 13.5, "fiber": 1.2},
        {"name": "Britannia Good Day Cookies", "brand": "Britannia", "category": "snacks", "calories": 480, "protein": 6.8, "carbs": 68.5, "fat": 19.8, "fiber": 2.1},
        {"name": "Britannia Bread", "brand": "Britannia", "category": "grains", "calories": 265, "protein": 8.9, "carbs": 49.0, "fat": 4.2, "fiber": 2.7},
        
        # Beverages
        {"name": "Green Tea", "category": "beverages", "calories": 2, "protein": 0.2, "carbs": 0, "fat": 0, "fiber": 0},
        {"name": "Black Coffee", "category": "beverages", "calories": 2, "protein": 0.3, "carbs": 0, "fat": 0, "fiber": 0},
        {"name": "Coconut Water", "category": "beverages", "calories": 19, "protein": 0.7, "carbs": 3.7, "fat": 0.2, "fiber": 1.1},
        {"name": "Sugarcane Juice", "category": "beverages", "calories": 269, "protein": 0, "carbs": 73.0, "fat": 0, "fiber": 0},
        
        # Indian Sweets
        {"name": "Gulab Jamun", "category": "sweets", "calories": 387, "protein": 6.2, "carbs": 52.7, "fat": 17.0, "fiber": 0.8},
        {"name": "Rasgulla", "category": "sweets", "calories": 186, "protein": 4.0, "carbs": 32.0, "fat": 4.9, "fiber": 0},
        {"name": "Jalebi", "category": "sweets", "calories": 416, "protein": 3.7, "carbs": 56.0, "fat": 20.1, "fiber": 0.5},
        {"name": "Laddu", "category": "sweets", "calories": 418, "protein": 7.4, "carbs": 51.8, "fat": 20.6, "fiber": 2.1},
        
        # Oils & Fats
        {"name": "Coconut Oil", "category": "oils", "calories": 862, "protein": 0, "carbs": 0, "fat": 99.1, "fiber": 0},
        {"name": "Mustard Oil", "category": "oils", "calories": 884, "protein": 0, "carbs": 0, "fat": 100.0, "fiber": 0},
        {"name": "Olive Oil", "category": "oils", "calories": 884, "protein": 0, "carbs": 0, "fat": 100.0, "fiber": 0},
        {"name": "Ghee", "category": "oils", "calories": 876, "protein": 0.3, "carbs": 0, "fat": 99.5, "fiber": 0},
        
        # Spices & Herbs
        {"name": "Turmeric Powder", "category": "spices", "calories": 354, "protein": 7.8, "carbs": 64.9, "fat": 9.9, "fiber": 21.1},
        {"name": "Cumin Seeds", "category": "spices", "calories": 375, "protein": 17.8, "carbs": 44.2, "fat": 22.3, "fiber": 10.5},
        {"name": "Coriander Seeds", "category": "spices", "calories": 298, "protein": 12.4, "carbs": 54.9, "fat": 17.8, "fiber": 41.9},
        {"name": "Red Chili Powder", "category": "spices", "calories": 282, "protein": 13.5, "carbs": 49.7, "fat": 14.3, "fiber": 28.7},
    ]
    
    # Add foods to database
    for food_data in foods_data:
        # Check if food already exists
        existing_food = Food.query.filter_by(
            name=food_data['name'], 
            brand=food_data.get('brand')
        ).first()
        
        if not existing_food:
            food = Food(
                name=food_data['name'],
                brand=food_data.get('brand'),
                category=food_data['category'],
                calories=food_data['calories'],
                protein=food_data['protein'],
                carbs=food_data['carbs'],
                fat=food_data['fat'],
                fiber=food_data.get('fiber', 0),
                sugar=food_data.get('sugar', 0),
                sodium=food_data.get('sodium', 0),
                serving_size=food_data.get('serving_size', 100),
                is_verified=True
            )
            db.session.add(food)
    
    db.session.commit()
    print(f"Added {len(foods_data)} food items to the database!")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        populate_indian_foods()
