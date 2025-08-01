#!/usr/bin/env python3
"""
Test Script: Validate Food Upload Template with Description Field
Tests the corrected CSV template and upload functionality
"""

import sys
import os
import csv
import io

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_template_validation():
    """Test the new CSV template validation."""
    print("🧪 Testing CSV Template Validation")
    print("-" * 50)
    
    # Check if template file exists
    template_path = "app/static/templates/food_upload_template_v2.csv"
    if not os.path.exists(template_path):
        print("❌ Template file not found!")
        return False
    
    try:
        # Read and validate template structure
        with open(template_path, 'r', encoding='utf-8') as f:
            csv_content = f.read()
        
        print("✅ Template file found and readable")
        
        # Parse CSV
        csv_file = io.StringIO(csv_content)
        reader = csv.DictReader(csv_file)
        headers = reader.fieldnames or []
        
        print(f"📝 Headers found: {len(headers)}")
        for i, header in enumerate(headers, 1):
            print(f"   {i:2d}. {header}")
        
        # Check required headers
        required_headers = [
            'name', 'brand', 'category', 'base_unit', 'calories_per_100g', 
            'protein_per_100g', 'carbs_per_100g', 'fat_per_100g'
        ]
        
        missing_headers = [h for h in required_headers if h not in headers]
        if missing_headers:
            print(f"❌ Missing required headers: {missing_headers}")
            return False
        
        print("✅ All required headers present")
        
        # Check if description field is present
        if 'description' not in headers:
            print("❌ Description field is missing!")
            return False
        
        print("✅ Description field is present")
        
        # Validate data rows
        csv_file.seek(0)
        reader = csv.DictReader(csv_file)
        rows = list(reader)
        
        print(f"📊 Data rows found: {len(rows)}")
        
        # Test a few rows
        test_count = min(3, len(rows))
        for i, row in enumerate(rows[:test_count]):
            print(f"\n🔍 Testing row {i+1}:")
            print(f"   Name: {row.get('name', 'N/A')}")
            print(f"   Brand: {row.get('brand', 'N/A')}")
            print(f"   Category: {row.get('category', 'N/A')}")
            print(f"   Description: {row.get('description', 'N/A')}")
            print(f"   Calories: {row.get('calories_per_100g', 'N/A')}")
            
            # Validate required fields
            if not row.get('name', '').strip():
                print(f"   ❌ Missing name in row {i+1}")
                return False
            
            if not row.get('category', '').strip():
                print(f"   ❌ Missing category in row {i+1}")
                return False
            
            # Check if description has content
            if row.get('description', '').strip():
                print(f"   ✅ Description present and has content")
            else:
                print(f"   ⚠️  Description is empty")
        
        print("\n✅ Template validation completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error validating template: {e}")
        return False

def test_bulk_upload_processor():
    """Test the bulk upload processor with the new template."""
    print("\n🔄 Testing Bulk Upload Processor")
    print("-" * 50)
    
    try:
        from app.services.bulk_upload_processor import BulkUploadProcessor
        
        # Load template content
        template_path = "app/static/templates/food_upload_template_v2.csv"
        with open(template_path, 'r', encoding='utf-8') as f:
            csv_content = f.read()
        
        # Initialize processor
        processor = BulkUploadProcessor()
        
        # Test CSV validation
        print("🧪 Testing CSV format validation...")
        validation_result = processor.validate_csv_format(csv_content)
        
        if validation_result['is_valid']:
            print("✅ CSV validation passed")
            print(f"📊 Rows found: {validation_result.get('row_count', 'N/A')}")
            print(f"📝 Headers: {validation_result.get('headers', [])}")
        else:
            print(f"❌ CSV validation failed: {validation_result.get('error', 'Unknown error')}")
            return False
        
        # Test data sanitization
        print("\n🧹 Testing data sanitization...")
        csv_file = io.StringIO(csv_content)
        reader = csv.DictReader(csv_file)
        test_row = next(reader)
        
        sanitized_data = processor.sanitize_row_data(test_row)
        print(f"🔍 Original row: {test_row['name']} - {test_row.get('description', 'No description')}")
        print(f"✨ Sanitized data includes description: {'description' in sanitized_data}")
        
        if 'description' in sanitized_data:
            print(f"📝 Description value: '{sanitized_data['description']}'")
        
        print("✅ Bulk upload processor test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing bulk upload processor: {e}")
        return False

def test_template_download():
    """Test template download functionality."""
    print("\n⬇️ Testing Template Download")
    print("-" * 50)
    
    try:
        template_path = "app/static/templates/food_upload_template_v2.csv"
        
        # Check file exists and is readable
        if not os.path.exists(template_path):
            print("❌ Template file not found for download")
            return False
        
        # Check file size
        file_size = os.path.getsize(template_path)
        print(f"📦 Template file size: {file_size} bytes")
        
        if file_size == 0:
            print("❌ Template file is empty")
            return False
        
        # Test MIME type would be correct
        if template_path.endswith('.csv'):
            print("✅ Template has correct .csv extension")
        else:
            print("❌ Template does not have .csv extension")
            return False
        
        print("✅ Template download test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing template download: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 FOOD UPLOAD TEMPLATE VALIDATION TEST SUITE")
    print("=" * 70)
    
    tests = [
        ("Template Validation", test_template_validation),
        ("Bulk Upload Processor", test_bulk_upload_processor),
        ("Template Download", test_template_download)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            passed += 1
            print(f"✅ {test_name}: PASSED")
        else:
            print(f"❌ {test_name}: FAILED")
    
    print(f"\n{'='*70}")
    print(f"📊 TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Template is ready for use.")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
