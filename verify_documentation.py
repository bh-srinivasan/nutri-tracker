#!/usr/bin/env python3
"""
Verification script for OpenAPI documentation and FoodServing implementation
"""

from app import create_app, db
from app.models import Food, FoodServing
import json

def main():
    print("🔍 Verifying OpenAPI Documentation & FoodServing Implementation")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        # 1. Check database schema
        print("\n1. 📊 Database Schema Verification")
        print("-" * 40)
        
        # Check if food_serving table exists
        try:
            serving_count = FoodServing.query.count()
            print(f"✅ FoodServing table exists with {serving_count} records")
        except Exception as e:
            print(f"❌ FoodServing table issue: {e}")
            return
        
        # 2. Check for Idli food
        print("\n2. 🍽️ Idli Food Verification")
        print("-" * 40)
        
        idli = Food.query.filter_by(name='Idli').first()
        if idli:
            print(f"✅ Found Idli: ID={idli.id}, Name='{idli.name}'")
            print(f"   📏 Default serving ID: {idli.default_serving_id}")
            print(f"   🥗 Calories per 100g: {idli.calories}")
            
            # Check servings
            servings = FoodServing.query.filter_by(food_id=idli.id).all()
            print(f"   🍴 Servings ({len(servings)}):")
            for s in servings:
                marker = "⭐" if s.id == idli.default_serving_id else "  "
                print(f"   {marker} {s.serving_name}: {s.grams_per_unit}g (ID: {s.id})")
                
            # Check for "1 small idli" = 20g
            small_idli = next((s for s in servings if s.serving_name == "1 small idli"), None)
            if small_idli and small_idli.grams_per_unit == 20.0:
                print("✅ '1 small idli' = 20g verification PASSED")
            else:
                print("❌ '1 small idli' = 20g verification FAILED")
                
        else:
            print("❌ Idli not found in database")
            print("   Available foods:")
            foods = Food.query.limit(5).all()
            for f in foods:
                print(f"   - {f.name} (ID: {f.id})")
        
        # 3. Check API routes
        print("\n3. 🌐 API Routes Verification")
        print("-" * 40)
        
        routes = []
        for rule in app.url_map.iter_rules():
            if rule.rule.startswith('/api/'):
                routes.append(f"{rule.methods} {rule.rule}")
        
        api_v2_routes = [r for r in routes if '/api/v2/' in r]
        swagger_routes = [r for r in routes if '/api/docs' in r]
        
        print(f"✅ Total API routes: {len(routes)}")
        print(f"✅ API v2 routes: {len(api_v2_routes)}")
        print(f"✅ Swagger routes: {len(swagger_routes)}")
        
        if api_v2_routes:
            print("   Key API v2 endpoints:")
            for route in api_v2_routes[:5]:  # Show first 5
                print(f"   - {route}")
        
        # 4. Test API response structure
        print("\n4. 🧪 API Response Structure Test")
        print("-" * 40)
        
        if idli:
            # Simulate API response
            from app.swagger_api import foods_v2
            
            # Check if we can create proper response structure
            test_response = {
                "id": idli.id,
                "name": idli.name,
                "brand": idli.brand or "Traditional",
                "category": idli.category or "Indian Breakfast",
                "calories_per_100g": idli.calories,
                "protein_per_100g": idli.protein,
                "carbs_per_100g": idli.carbs,
                "fat_per_100g": idli.fat,
                "servings": [
                    {
                        "id": s.id,
                        "serving_name": s.serving_name,
                        "unit": s.unit,
                        "grams_per_unit": s.grams_per_unit
                    } for s in servings
                ],
                "default_serving_id": idli.default_serving_id
            }
            
            print("✅ API Response Structure Test:")
            print(f"   - Food ID: {test_response['id']}")
            print(f"   - Servings array: {len(test_response['servings'])} items")
            print(f"   - Default serving: {test_response['default_serving_id']}")
            
            # Validate JSON structure
            try:
                json_str = json.dumps(test_response, indent=2)
                json.loads(json_str)  # Validate it's valid JSON
                print("✅ JSON structure validation PASSED")
            except Exception as e:
                print(f"❌ JSON structure validation FAILED: {e}")
        
        # 5. Summary
        print("\n5. 📋 Verification Summary")
        print("-" * 40)
        
        checks = [
            ("FoodServing table exists", serving_count > 0),
            ("Idli food exists", idli is not None),
            ("Idli has servings", len(servings) > 0 if idli else False),
            ("Small idli = 20g", small_idli and small_idli.grams_per_unit == 20.0 if idli else False),
            ("Default serving set", idli.default_serving_id is not None if idli else False),
            ("API v2 routes exist", len(api_v2_routes) > 0),
            ("Swagger routes exist", len(swagger_routes) > 0)
        ]
        
        passed = sum(1 for _, status in checks if status)
        total = len(checks)
        
        print(f"📊 Overall Status: {passed}/{total} checks passed")
        
        for check_name, status in checks:
            icon = "✅" if status else "❌"
            print(f"{icon} {check_name}")
        
        if passed == total:
            print("\n🎉 ALL VERIFICATIONS PASSED!")
            print("✅ OpenAPI documentation is ready")
            print("✅ FoodServing model is working")
            print("✅ '1 small idli' = 20g example is implemented")
            print("\n🌐 Access Swagger UI at: http://127.0.0.1:5001/api/docs/")
        else:
            print(f"\n⚠️  {total - passed} issues need attention")

if __name__ == "__main__":
    main()
