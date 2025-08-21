#!/usr/bin/env python3
"""
Create Idli food with servings for documentation examples
"""

from app import create_app, db
from app.models import Food, FoodServing

def create_idli_example():
    print("🍽️ Creating Idli Example for OpenAPI Documentation")
    print("=" * 50)
    
    app = create_app()
    
    with app.app_context():
        # Check if Idli already exists
        existing_idli = Food.query.filter_by(name='Idli').first()
        if existing_idli:
            print(f"✅ Idli already exists with ID: {existing_idli.id}")
            idli = existing_idli
        else:
            # Create Idli food
            idli = Food(
                name='Idli',
                brand='Traditional',
                category='Indian Breakfast',
                calories=58,          # per 100g
                protein=2.5,          # per 100g
                carbs=12.0,           # per 100g
                fat=0.1,              # per 100g
                fiber=0.9,            # per 100g
                sugar=0.5,            # per 100g
                sodium=5.0,           # per 100g
                description='Traditional South Indian steamed rice and lentil cake',
                is_verified=True
            )
            
            db.session.add(idli)
            db.session.flush()  # Get the ID
            print(f"✅ Created Idli with ID: {idli.id}")
        
        # Check if servings already exist
        existing_servings = FoodServing.query.filter_by(food_id=idli.id).all()
        if existing_servings:
            print(f"✅ Found {len(existing_servings)} existing servings")
            for s in existing_servings:
                print(f"   - {s.serving_name}: {s.grams_per_unit}g (ID: {s.id})")
        else:
            # Create servings
            servings_data = [
                {
                    'serving_name': '1 small idli',
                    'unit': 'piece',
                    'grams_per_unit': 20.0
                },
                {
                    'serving_name': '1 medium idli',
                    'unit': 'piece',
                    'grams_per_unit': 35.0
                },
                {
                    'serving_name': '1 large idli',
                    'unit': 'piece',
                    'grams_per_unit': 50.0
                }
            ]
            
            created_servings = []
            for serving_data in servings_data:
                serving = FoodServing(
                    food_id=idli.id,
                    **serving_data
                )
                db.session.add(serving)
                created_servings.append(serving)
            
            db.session.flush()  # Get the IDs
            
            print("✅ Created servings:")
            for s in created_servings:
                print(f"   - {s.serving_name}: {s.grams_per_unit}g (ID: {s.id})")
        
        # Set default serving to "1 small idli"
        small_idli_serving = FoodServing.query.filter_by(
            food_id=idli.id, 
            serving_name='1 small idli'
        ).first()
        
        if small_idli_serving:
            idli.default_serving_id = small_idli_serving.id
            print(f"✅ Set default serving to '1 small idli' (ID: {small_idli_serving.id})")
        
        # Commit all changes
        db.session.commit()
        
        print("\n🎉 Idli Example Creation Complete!")
        print("=" * 50)
        
        # Verify the results
        print("\n📊 Verification:")
        print(f"   🍽️  Food: {idli.name} (ID: {idli.id})")
        print(f"   🏷️  Brand: {idli.brand}")
        print(f"   📂 Category: {idli.category}")
        print(f"   🔥 Calories: {idli.calories}/100g")
        print(f"   ⭐ Default serving: {idli.default_serving_id}")
        
        all_servings = FoodServing.query.filter_by(food_id=idli.id).all()
        print(f"\n🍴 Servings ({len(all_servings)}):")
        for s in all_servings:
            marker = "⭐" if s.id == idli.default_serving_id else "  "
            print(f"   {marker} {s.serving_name}: {s.grams_per_unit}g (ID: {s.id})")
        
        # Test calculation
        if small_idli_serving:
            quantity = 3
            total_grams = quantity * small_idli_serving.grams_per_unit
            total_calories = (total_grams / 100) * idli.calories
            print(f"\n🧮 Example Calculation:")
            print(f"   3 small idlis = 3 × {small_idli_serving.grams_per_unit}g = {total_grams}g")
            print(f"   Calories = {total_grams}g × ({idli.calories}/100g) = {total_calories:.1f} cal")
        
        print(f"\n🌐 Test the API at:")
        print(f"   - Swagger UI: http://127.0.0.1:5001/api/docs/")
        print(f"   - Food API: http://127.0.0.1:5001/api/v2/foods/{idli.id}")
        
        return idli.id

if __name__ == "__main__":
    food_id = create_idli_example()
    print(f"\n✅ Idli created with ID: {food_id}")
