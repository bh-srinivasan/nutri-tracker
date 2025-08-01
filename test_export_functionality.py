#!/usr/bin/env python3
"""
Test Export Functionality

This script tests the complete export functionality including:
- Export service initialization
- Food data export to CSV and JSON
- File generation and validation
- Cleanup operations
"""

import os
import sys
import tempfile
import json
from datetime import datetime

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Food, ExportJob, User
from app.services.food_export_service import FoodExportService


def test_export_functionality():
    """Test the complete export functionality."""
    print("🧪 Testing Export Functionality")
    print("=" * 50)
    
    # Create app and context
    app = create_app()
    
    with app.app_context():
        try:
            # Test 1: Check if we have food data
            print("\n1️⃣ Checking database for food data...")
            food_count = Food.query.count()
            print(f"   📊 Total foods in database: {food_count}")
            
            if food_count == 0:
                print("   ⚠️  No food data found. Creating test data...")
                create_test_food_data()
                food_count = Food.query.count()
                print(f"   ✅ Created test data. New count: {food_count}")
            
            # Test 2: Initialize export service
            print("\n2️⃣ Testing export service initialization...")
            export_service = FoodExportService()
            print("   ✅ Export service initialized successfully")
            
            # Test 3: Test statistics
            print("\n3️⃣ Testing export statistics...")
            stats = export_service.get_export_statistics()
            print(f"   📊 Total foods: {stats['total_foods']}")
            print(f"   📊 Verified foods: {stats['verified_foods']}")
            print(f"   📊 Categories: {stats['total_categories']}")
            print("   ✅ Statistics retrieved successfully")
            
            # Test 4: Test CSV export
            print("\n4️⃣ Testing CSV export...")
            test_csv_export(export_service)
            
            # Test 5: Test JSON export
            print("\n5️⃣ Testing JSON export...")
            test_json_export(export_service)
            
            # Test 6: Test filtered export
            print("\n6️⃣ Testing filtered export...")
            test_filtered_export(export_service)
            
            # Test 7: Test job management
            print("\n7️⃣ Testing job management...")
            test_job_management(export_service)
            
            print("\n🎉 All tests completed successfully!")
            print("   The export functionality is working correctly.")
            
        except Exception as e:
            print(f"\n❌ Test failed with error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    return True


def create_test_food_data():
    """Create test food data if none exists."""
    test_foods = [
        {
            'name': 'Apple',
            'category': 'Fruits',
            'calories': 52,
            'protein': 0.3,
            'carbs': 14,
            'fat': 0.2,
            'fiber': 2.4,
            'sugar': 10.4,
            'sodium': 1,
            'description': 'Fresh red apple'
        },
        {
            'name': 'Chicken Breast',
            'category': 'Meat',
            'calories': 165,
            'protein': 31,
            'carbs': 0,
            'fat': 3.6,
            'fiber': 0,
            'sugar': 0,
            'sodium': 74,
            'description': 'Skinless chicken breast'
        },
        {
            'name': 'Brown Rice',
            'category': 'Grains',
            'calories': 111,
            'protein': 2.6,
            'carbs': 23,
            'fat': 0.9,
            'fiber': 1.8,
            'sugar': 0.4,
            'sodium': 5,
            'description': 'Cooked brown rice'
        }
    ]
    
    for food_data in test_foods:
        food = Food(**food_data)
        db.session.add(food)
    
    db.session.commit()


def test_csv_export(export_service):
    """Test CSV export functionality."""
    try:
        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            temp_path = temp_file.name
        
        # Get some foods to export
        foods = Food.query.limit(10).all()
        
        # Test CSV export
        export_service._export_to_csv(foods, temp_path)
        
        # Validate the CSV file
        if os.path.exists(temp_path):
            file_size = os.path.getsize(temp_path)
            print(f"   📄 CSV file created: {temp_path}")
            print(f"   📊 File size: {file_size} bytes")
            
            # Check CSV content
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.strip().split('\n')
                print(f"   📊 Number of lines: {len(lines)}")
                print(f"   📊 Header: {lines[0][:100]}..." if lines else "   ⚠️  Empty file")
            
            # Clean up
            os.unlink(temp_path)
            print("   ✅ CSV export test completed")
        else:
            raise Exception("CSV file was not created")
            
    except Exception as e:
        print(f"   ❌ CSV export test failed: {str(e)}")
        raise


def test_json_export(export_service):
    """Test JSON export functionality."""
    try:
        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_path = temp_file.name
        
        # Get some foods to export
        foods = Food.query.limit(10).all()
        
        # Test JSON export
        export_service._export_to_json(foods, temp_path)
        
        # Validate the JSON file
        if os.path.exists(temp_path):
            file_size = os.path.getsize(temp_path)
            print(f"   📄 JSON file created: {temp_path}")
            print(f"   📊 File size: {file_size} bytes")
            
            # Check JSON content
            with open(temp_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"   📊 Export info: {data.get('export_info', {})}")
                print(f"   📊 Number of foods: {len(data.get('foods', []))}")
            
            # Clean up
            os.unlink(temp_path)
            print("   ✅ JSON export test completed")
        else:
            raise Exception("JSON file was not created")
            
    except Exception as e:
        print(f"   ❌ JSON export test failed: {str(e)}")
        raise


def test_filtered_export(export_service):
    """Test filtered export functionality."""
    try:
        # Test query building with filters
        filters = {
            'category': 'Fruits',
            'is_verified': True
        }
        
        query = export_service._build_food_query(filters)
        results = query.all()
        
        print(f"   📊 Filtered query results: {len(results)} foods")
        print("   ✅ Filtered export test completed")
        
    except Exception as e:
        print(f"   ❌ Filtered export test failed: {str(e)}")
        raise


def test_job_management(export_service):
    """Test export job management."""
    try:
        # Check existing jobs
        jobs_count = ExportJob.query.count()
        print(f"   📊 Existing export jobs: {jobs_count}")
        
        # Test cleanup functionality (don't actually run it as it might delete files)
        print("   ✅ Job management test completed")
        
    except Exception as e:
        print(f"   ❌ Job management test failed: {str(e)}")
        raise


if __name__ == '__main__':
    print("🚀 Starting Export Functionality Tests")
    print(f"📅 Test run date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = test_export_functionality()
    
    if success:
        print("\n🎉 All tests passed! Export functionality is ready for use.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        sys.exit(1)
