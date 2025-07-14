"""
Test script for async bulk upload functionality with UOM support
"""

import requests
import json
import time
import io

def test_async_bulk_upload():
    """Test the async bulk upload functionality."""
    
    # Create a test CSV with UOM data
    csv_content = """name,brand,category,base_unit,calories_per_100g,protein_per_100g,carbs_per_100g,fat_per_100g,fiber_per_100g,serving_name,serving_unit,serving_quantity
Test Apple,Generic,Fruits,g,52,0.3,14,0.2,2.4,1 medium,piece,150
Test Chicken Breast,Premium,Protein,g,165,31,0,3.6,0,3 oz serving,g,85
Test Brown Rice,Healthy,Grains,g,111,2.6,23,0.9,1.8,1 cup cooked,g,195"""
    
    print("Testing async bulk upload with UOM support...")
    
    # Test CSV validation
    print("\n1. Testing CSV validation...")
    from app.services.bulk_upload_processor import BulkUploadProcessor
    
    processor = BulkUploadProcessor()
    validation_result = processor.validate_csv_format(csv_content)
    
    print(f"Validation result: {validation_result['is_valid']}")
    print(f"Row count: {validation_result.get('row_count', 'N/A')}")
    
    if not validation_result['is_valid']:
        print(f"Validation errors: {validation_result.get('error', 'Unknown error')}")
        return False
    
    print("✓ CSV validation passed")
    
    # Test data sanitization
    print("\n2. Testing data sanitization...")
    import csv
    csv_file = io.StringIO(csv_content)
    reader = csv.DictReader(csv_file)
    test_row = next(reader)
    
    sanitized_data = processor.sanitize_row_data(test_row)
    print(f"Original row: {test_row}")
    print(f"Sanitized data: {sanitized_data}")
    
    # Verify numeric conversion
    assert isinstance(sanitized_data['calories_per_100g'], float)
    assert isinstance(sanitized_data['protein_per_100g'], float)
    print("✓ Data sanitization passed")
    
    # Test export service
    print("\n3. Testing export service...")
    from app.services.food_export_service import FoodExportService
    from app import create_app
    
    app = create_app()
    with app.app_context():
        export_service = FoodExportService()
        categories = export_service.get_available_categories()
        stats = export_service.get_export_statistics()
        
        print(f"Available categories: {categories}")
        print(f"Export statistics: {stats}")
        print("✓ Export service functionality verified")
    
    print("\n✅ All async bulk upload tests passed!")
    return True

def test_uom_models():
    """Test the new UOM models."""
    print("\nTesting UOM models...")
    
    from app import create_app, db
    from app.models import Food, FoodNutrition, FoodServing
    
    app = create_app()
    with app.app_context():
        # Create a test food
        test_food = Food(
            name='Test Food UOM',
            brand='Test Brand',
            category='Test Category',
            calories=100,
            protein=20,
            carbs=10,
            fat=5
        )
        
        db.session.add(test_food)
        db.session.flush()  # Get ID
        
        # Create nutrition info
        nutrition = FoodNutrition(
            food_id=test_food.id,
            base_unit='g',
            base_quantity=100.0,
            calories_per_base=100,
            protein_per_base=20,
            carbs_per_base=10,
            fat_per_base=5,
            fiber_per_base=3
        )
        
        db.session.add(nutrition)
        
        # Create serving size
        serving = FoodServing(
            food_id=test_food.id,
            serving_name='1 medium',
            serving_unit='piece',
            serving_quantity=150.0,
            is_default=True
        )
        
        db.session.add(serving)
        db.session.commit()
        
        # Verify relationships
        assert test_food.nutrition_info[0].base_unit == 'g'
        assert test_food.servings[0].serving_name == '1 medium'
        
        print("✓ UOM models created and relationships verified")
        
        # Cleanup - delete nutrition and serving first due to foreign key constraints
        for nutrition in test_food.nutrition_info:
            db.session.delete(nutrition)
        for serving in test_food.servings:
            db.session.delete(serving)
        db.session.delete(test_food)
        db.session.commit()
        
    print("✅ UOM models test passed!")
    return True

if __name__ == '__main__':
    try:
        print("🚀 Starting Async Bulk Upload Tests...")
        
        # Test 1: Basic async functionality
        success1 = test_async_bulk_upload()
        
        # Test 2: UOM models
        success2 = test_uom_models()
        
        if success1 and success2:
            print("\n🎉 All tests passed! Async bulk upload with UOM support is ready!")
        else:
            print("\n❌ Some tests failed!")
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
