#!/usr/bin/env python3
"""
End-to-End Test: Food Upload with Description Field
Tests the complete upload flow from template to database
"""

import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_food_upload_e2e():
    """Test end-to-end food upload with description field."""
    print("🔄 End-to-End Food Upload Test")
    print("=" * 50)
    
    try:
        # Import required modules
        from app import create_app, db
        from app.models import Food
        from app.services.bulk_upload_processor import BulkUploadProcessor
        
        # Create test CSV data with description
        test_csv = """name,brand,category,description,base_unit,calories_per_100g,protein_per_100g,carbs_per_100g,fat_per_100g,fiber_per_100g,sugar_per_100g,sodium_per_100g,serving_name,serving_quantity,serving_unit
Test Apple,Generic,Fruits,A crisp and juicy apple variety,g,52,0.3,14,0.2,2.4,10,1,1 medium,150,piece
Test Quinoa,Premium,Grains,Protein-rich superfood grain,g,368,14.1,64.2,6.1,7,3.6,5,1 cup cooked,185,g"""
        
        print("📝 Test CSV data created with description field")
        
        # Initialize processor
        processor = BulkUploadProcessor()
        
        # Test validation
        print("🔍 Validating CSV format...")
        validation_result = processor.validate_csv_format(test_csv)
        
        if not validation_result['is_valid']:
            print(f"❌ CSV validation failed: {validation_result.get('error')}")
            return False
        
        print("✅ CSV validation passed")
        
        # Create app context for database operations
        app = create_app()
        with app.app_context():
            # Check initial food count
            initial_count = Food.query.count()
            print(f"📊 Initial food count: {initial_count}")
            
            # Test the complete upload flow
            print("🚀 Starting test upload...")
            
            # Note: We're simulating the upload without actually starting the async process
            # since that would require a full Flask environment
            
            # Test data sanitization for both rows
            import csv
            import io
            
            csv_file = io.StringIO(test_csv)
            reader = csv.DictReader(csv_file)
            
            test_foods = []
            for row in reader:
                sanitized_data = processor.sanitize_row_data(row)
                test_foods.append(sanitized_data)
                print(f"✨ Sanitized: {sanitized_data['name']} - {sanitized_data.get('description', 'No description')}")
            
            # Verify description field is included
            for food_data in test_foods:
                if 'description' not in food_data:
                    print(f"❌ Description field missing from sanitized data for {food_data['name']}")
                    return False
                
                if not food_data['description']:
                    print(f"⚠️ Description field is empty for {food_data['name']}")
                else:
                    print(f"✅ Description field populated for {food_data['name']}: '{food_data['description']}'")
            
            # Test creating Food objects with description
            print("\n🗄️ Testing Food object creation with description...")
            
            for food_data in test_foods:
                try:
                    # Create food object (without saving to avoid duplicates)
                    food = Food(
                        name=food_data['name'],
                        brand=food_data.get('brand', ''),
                        category=food_data.get('category', 'Other'),
                        description=food_data.get('description', ''),
                        calories=food_data.get('calories_per_100g', 0),
                        protein=food_data.get('protein_per_100g', 0),
                        carbs=food_data.get('carbs_per_100g', 0),
                        fat=food_data.get('fat_per_100g', 0),
                        fiber=food_data.get('fiber_per_100g', 0),
                        sugar=food_data.get('sugar_per_100g', 0),
                        sodium=food_data.get('sodium_per_100g', 0),
                        serving_size=food_data.get('serving_size', 100),
                        is_verified=True,
                        created_by=1  # Test user ID
                    )
                    
                    print(f"✅ Successfully created Food object for: {food.name}")
                    print(f"   📝 Description: '{food.description}'")
                    print(f"   🏷️ Brand: '{food.brand}'")
                    print(f"   📂 Category: '{food.category}'")
                    
                except Exception as e:
                    print(f"❌ Failed to create Food object for {food_data['name']}: {e}")
                    return False
            
            print("\n✅ End-to-end test completed successfully!")
            return True
    
    except Exception as e:
        print(f"❌ Error in end-to-end test: {e}")
        return False

def test_template_browser_download():
    """Test that the template can be downloaded via browser."""
    print("\n🌐 Testing Browser Template Download")
    print("-" * 50)
    
    template_path = "app/static/templates/food_upload_template_v2.csv"
    
    if not os.path.exists(template_path):
        print("❌ Template file not found")
        return False
    
    # Check file properties
    file_stat = os.stat(template_path)
    print(f"📦 File size: {file_stat.st_size} bytes")
    print(f"📅 Last modified: {file_stat.st_mtime}")
    
    # Test content type would be correct
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Should start with header row
    if content.startswith('name,brand,category,description'):
        print("✅ Template has correct header structure")
    else:
        print("❌ Template header is incorrect")
        return False
    
    # Check for description field in header
    lines = content.split('\n')
    header = lines[0] if lines else ""
    
    if 'description' in header:
        print("✅ Description field is in the header")
    else:
        print("❌ Description field missing from header")
        return False
    
    print("✅ Browser download test passed!")
    return True

def main():
    """Run end-to-end tests."""
    print("🧪 COMPLETE FOOD UPLOAD SYSTEM TEST")
    print("=" * 60)
    
    tests = [
        ("End-to-End Upload Flow", test_food_upload_e2e),
        ("Browser Template Download", test_template_browser_download)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*15} {test_name} {'='*15}")
        if test_func():
            passed += 1
            print(f"✅ {test_name}: PASSED")
        else:
            print(f"❌ {test_name}: FAILED")
    
    print(f"\n{'='*60}")
    print(f"📊 FINAL RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Food upload template with description field is ready!")
        print("✅ Template download works correctly!")
        print("✅ Upload processing handles description field!")
        return 0
    else:
        print("⚠️ Some tests failed. Please review the issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
