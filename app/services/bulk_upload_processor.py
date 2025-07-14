"""
Async Bulk Upload Processor for Food Data with UOM Support

This service handles asynchronous processing of bulk food uploads with comprehensive
validation, sanitization, and progress tracking. Supports Unit of Measure (UOM)
data for foods with detailed nutrition information and serving sizes.
"""

import csv
import io
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from flask import current_app
from app import db
from app.models import Food, FoodNutrition, FoodServing, BulkUploadJob, BulkUploadJobItem
import re
import uuid


class BulkUploadProcessor:
    """Handles asynchronous bulk upload processing for food data."""
    
    # Supported units mapping
    SUPPORTED_UNITS = {
        'weight': ['g', 'kg', 'oz', 'lb'],
        'volume': ['ml', 'l', 'fl oz', 'cup', 'tbsp', 'tsp'],
        'piece': ['piece', 'item', 'unit', 'serving']
    }
    
    # Required CSV headers
    REQUIRED_HEADERS = [
        'name', 'brand', 'category', 'base_unit', 'calories_per_100g', 
        'protein_per_100g', 'carbs_per_100g', 'fat_per_100g'
    ]
    
    # Optional CSV headers (only fields supported by Food model)
    OPTIONAL_HEADERS = [
        'fiber_per_100g', 'sugar_per_100g', 'sodium_per_100g', 
        'serving_size', 'description'  # description field can be ignored
    ]
    
    def __init__(self):
        """Initialize the bulk upload processor."""
        self.current_job = None
        self.processing_lock = threading.Lock()
    
    def validate_csv_format(self, csv_content: str) -> Dict[str, Any]:
        """
        Validate CSV format and headers.
        
        Args:
            csv_content: Raw CSV content as string
            
        Returns:
            Dict with validation results
        """
        try:
            # Parse CSV content
            csv_file = io.StringIO(csv_content)
            reader = csv.DictReader(csv_file)
            headers = reader.fieldnames or []
            
            # Check required headers
            missing_headers = [h for h in self.REQUIRED_HEADERS if h not in headers]
            if missing_headers:
                return {
                    'is_valid': False,
                    'error': f"Missing required headers: {', '.join(missing_headers)}",
                    'missing_headers': missing_headers
                }
            
            # Validate data rows
            rows = list(reader)
            if not rows:
                return {
                    'is_valid': False,
                    'error': "CSV file contains no data rows",
                    'row_count': 0
                }
            
            # Basic row validation
            invalid_rows = []
            for i, row in enumerate(rows, 1):
                row_errors = self._validate_row_basic(row, i)
                if row_errors:
                    invalid_rows.append({
                        'row': i,
                        'errors': row_errors,
                        'data': row
                    })
            
            return {
                'is_valid': len(invalid_rows) == 0,
                'row_count': len(rows),
                'headers': headers,
                'invalid_rows': invalid_rows[:10],  # Limit to first 10 errors
                'total_invalid': len(invalid_rows)
            }
            
        except Exception as e:
            return {
                'is_valid': False,
                'error': f"CSV parsing error: {str(e)}",
                'exception': str(e)
            }
    
    def _validate_row_basic(self, row: Dict[str, str], row_number: int) -> List[str]:
        """
        Perform basic validation on a single row.
        
        Args:
            row: CSV row data
            row_number: Row number for error reporting
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Required fields validation
        if not row.get('name', '').strip():
            errors.append("Food name is required")
        
        if not row.get('base_unit', '').strip():
            errors.append("Base unit is required")
        elif row['base_unit'].strip().lower() not in [u.lower() for units in self.SUPPORTED_UNITS.values() for u in units]:
            errors.append(f"Unsupported base unit: {row['base_unit']}")
        
        # Numeric field validation
        numeric_fields = [
            'calories_per_100g', 'protein_per_100g', 'carbs_per_100g', 'fat_per_100g',
            'fiber_per_100g', 'sugar_per_100g', 'sodium_per_100g', 'calcium_per_100g',
            'iron_per_100g', 'vitamin_c_per_100g', 'vitamin_d_per_100g', 'serving_quantity'
        ]
        
        for field in numeric_fields:
            value = row.get(field, '').strip()
            if value and not self._is_valid_number(value):
                errors.append(f"Invalid numeric value for {field}: {value}")
        
        # Name length validation
        if len(row.get('name', '')) > 200:
            errors.append("Food name too long (max 200 characters)")
        
        # Brand length validation
        if len(row.get('brand', '')) > 100:
            errors.append("Brand name too long (max 100 characters)")
        
        return errors
    
    def _format_error_message(self, error: Exception, row: Dict[str, str], row_number: int) -> str:
        """
        Format detailed error message for user feedback.
        
        Args:
            error: The exception that occurred
            row: CSV row data that caused the error
            row_number: Row number in the CSV
            
        Returns:
            Formatted error message
        """
        error_msg = str(error)
        
        # Check for common validation errors
        if "is an invalid keyword argument" in error_msg:
            field_name = error_msg.split("'")[1] if "'" in error_msg else "unknown field"
            return f"Unsupported field '{field_name}' found in CSV. Please remove this column."
        
        elif "cannot be null" in error_msg or "NOT NULL constraint failed" in error_msg:
            missing_field = "name" if "name" in error_msg else "required field"
            return f"Missing required field: {missing_field}. Please ensure all required columns have values."
        
        elif "UNIQUE constraint failed" in error_msg:
            food_name = row.get('name', 'Unknown')
            brand = row.get('brand', '')
            identifier = f"{food_name} ({brand})" if brand else food_name
            return f"Duplicate food entry: {identifier} already exists in database."
        
        elif "invalid literal" in error_msg and "float" in error_msg:
            # Find which field caused the numeric conversion error
            numeric_fields = ['calories_per_100g', 'protein_per_100g', 'carbs_per_100g', 'fat_per_100g', 
                            'fiber_per_100g', 'sugar_per_100g', 'sodium_per_100g', 'serving_size']
            problem_field = None
            for field in numeric_fields:
                if field in row and row[field] and not self._is_valid_number(row[field]):
                    problem_field = field
                    break
            
            if problem_field:
                return f"Invalid numeric value in field '{problem_field}': '{row[problem_field]}'. Please use valid numbers only."
            else:
                return f"Invalid numeric value found. Please check all numeric fields contain valid numbers."
        
        elif "name" in error_msg.lower() and ("empty" in error_msg.lower() or "blank" in error_msg.lower()):
            return "Food name cannot be empty. Please provide a valid food name."
        
        elif "category" in error_msg.lower():
            return f"Invalid category value. Please use a valid food category."
        
        else:
            # Generic error with context
            food_name = row.get('name', 'Unknown')
            return f"Error processing '{food_name}': {error_msg}"
    
    def _is_valid_number(self, value: str) -> bool:
        """Check if a string represents a valid number."""
        try:
            float(value.strip())
            return True
        except (ValueError, AttributeError):
            return False
    
    def sanitize_row_data(self, row: Dict[str, str]) -> Dict[str, Any]:
        """
        Sanitize and convert row data to appropriate types.
        
        Args:
            row: Raw CSV row data
            
        Returns:
            Sanitized data dictionary
        """
        sanitized = {}
        
        # String fields - trim and clean (only supported fields)
        string_fields = ['name', 'brand', 'category', 'description', 'base_unit']
        for field in string_fields:
            value = row.get(field, '').strip()
            if value:
                # Remove extra whitespace and special characters
                value = re.sub(r'\s+', ' ', value)
                value = value.replace('\n', '').replace('\r', '')
                sanitized[field] = value
        
        # Numeric fields - convert to float
        numeric_fields = [
            'calories_per_100g', 'protein_per_100g', 'carbs_per_100g', 'fat_per_100g',
            'fiber_per_100g', 'sugar_per_100g', 'sodium_per_100g', 'calcium_per_100g',
            'iron_per_100g', 'vitamin_c_per_100g', 'vitamin_d_per_100g', 'serving_quantity'
        ]
        
        for field in numeric_fields:
            value = row.get(field, '').strip()
            if value:
                try:
                    sanitized[field] = float(value)
                except (ValueError, TypeError):
                    sanitized[field] = 0.0
            else:
                sanitized[field] = 0.0
        
        # Ensure required defaults
        if 'base_unit' not in sanitized or not sanitized['base_unit']:
            sanitized['base_unit'] = 'g'
        
        return sanitized
    
    def start_async_upload(self, csv_content: str, filename: str, user_id: int, file_hash: str = None) -> str:
        """
        Start asynchronous bulk upload processing with enhanced security.
        
        Args:
            csv_content: Raw CSV content
            filename: Original filename
            user_id: ID of user initiating upload
            file_hash: Optional SHA256 hash of file for integrity verification
            
        Returns:
            Job ID for tracking progress
        """
        # Validate CSV format first
        validation_result = self.validate_csv_format(csv_content)
        if not validation_result['is_valid']:
            raise ValueError(f"CSV validation failed: {validation_result['error']}")
        
        # Create job record with enhanced metadata
        job = BulkUploadJob(
            filename=filename,
            total_rows=validation_result['row_count'],
            created_by=user_id,
            status='pending'
        )
        
        # Add file hash to job metadata if provided
        if file_hash:
            job.metadata = {'file_hash': file_hash, 'validation_passed': True}
        
        db.session.add(job)
        db.session.commit()
          # Start processing in background thread
        from flask import current_app
        app = current_app._get_current_object()  # Get actual app instance
        thread = threading.Thread(
            target=self._process_upload_async,
            args=(app, job.job_id, csv_content, user_id),
            daemon=True
        )
        thread.start()

        return job.job_id
    
    def _process_upload_async(self, app, job_id: str, csv_content: str, user_id: int):
        """
        Process bulk upload asynchronously.
        
        Args:
            app: Flask app instance
            job_id: Job ID to update
            csv_content: CSV content to process
            user_id: User ID
        """
        with self.processing_lock:
            try:
                # Create app context for database operations
                with app.app_context():
                    self._process_upload_job(job_id, csv_content, user_id)
            except Exception as e:
                # Update job with error
                with app.app_context():
                    job = BulkUploadJob.query.filter_by(job_id=job_id).first()
                    if job:
                        job.status = 'failed'
                        job.error_message = str(e)
                        job.completed_at = datetime.utcnow()
                        db.session.commit()
    
    def _process_upload_job(self, job_id: str, csv_content: str, user_id: int):
        """
        Main job processing logic.
        
        Args:
            job_id: Job ID to update
            csv_content: CSV content to process
            user_id: User ID
        """
        job = BulkUploadJob.query.filter_by(job_id=job_id).first()
        if not job:
            return
        
        try:
            # Update job status
            job.status = 'processing'
            job.started_at = datetime.utcnow()
            db.session.commit()
            
            # Parse CSV
            csv_file = io.StringIO(csv_content)
            reader = csv.DictReader(csv_file)
            rows = list(reader)
            
            # Process each row
            for i, row in enumerate(rows, 1):
                try:
                    self._process_single_row(job, row, i, user_id)
                    job.processed_rows = i
                    job.successful_rows += 1
                except Exception as row_error:
                    # Create detailed error message based on error type
                    error_details = self._format_error_message(row_error, row, i)
                    
                    # Create failed job item
                    job_item = BulkUploadJobItem(
                        job_id=job.id,
                        row_number=i,
                        food_name=row.get('name', 'Unknown'),
                        status='failed',
                        error_message=error_details,
                        processed_at=datetime.utcnow()
                    )
                    db.session.add(job_item)
                    job.processed_rows = i
                    job.failed_rows += 1
                
                # Commit progress every 10 rows
                if i % 10 == 0:
                    db.session.commit()
            
            # Final job update
            job.status = 'completed'
            job.completed_at = datetime.utcnow()
            db.session.commit()
            
        except Exception as e:
            job.status = 'failed'
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            db.session.commit()
            raise
    
    def _process_single_row(self, job: BulkUploadJob, row: Dict[str, str], row_number: int, user_id: int):
        """
        Process a single CSV row.
        
        Args:
            job: Upload job instance
            row: CSV row data
            row_number: Row number
            user_id: ID of user performing upload
        """
        # Sanitize data
        data = self.sanitize_row_data(row)
        
        # Check if food already exists
        existing_food = Food.query.filter_by(
            name=data['name'],
            brand=data.get('brand', '')
        ).first()
        
        if existing_food:
            # Create skipped job item
            job_item = BulkUploadJobItem(
                job_id=job.id,
                row_number=row_number,
                food_name=data['name'],
                status='skipped',
                error_message='Food already exists',
                food_id=existing_food.id,
                processed_at=datetime.utcnow()
            )
            db.session.add(job_item)
            return
        
        # Create new food record
        food = Food(
            name=data['name'],
            brand=data.get('brand', ''),
            category=data.get('category', 'Other'),
            description=data.get('description', ''),
            calories=data.get('calories_per_100g', 0),
            protein=data.get('protein_per_100g', 0),
            carbs=data.get('carbs_per_100g', 0),
            fat=data.get('fat_per_100g', 0),
            fiber=data.get('fiber_per_100g', 0),
            sugar=data.get('sugar_per_100g', 0),
            sodium=data.get('sodium_per_100g', 0),
            serving_size=data.get('serving_size', 100),
            is_verified=True,  # Assume admin uploads are verified
            created_by=user_id
        )
        
        db.session.add(food)
        db.session.flush()  # Get food ID
        
        # Create nutrition info with UOM support
        nutrition = FoodNutrition(
            food_id=food.id,
            base_unit=data['base_unit'],
            base_quantity=100.0,  # Nutrition is per 100g/ml
            calories_per_base=data.get('calories_per_100g', 0),
            protein_per_base=data.get('protein_per_100g', 0),
            carbs_per_base=data.get('carbs_per_100g', 0),
            fat_per_base=data.get('fat_per_100g', 0),
            fiber_per_base=data.get('fiber_per_100g', 0),
            sugar_per_base=data.get('sugar_per_100g', 0),
            sodium_per_base=data.get('sodium_per_100g', 0),
            calcium_per_base=data.get('calcium_per_100g', 0),
            iron_per_base=data.get('iron_per_100g', 0),
            vitamin_c_per_base=data.get('vitamin_c_per_100g', 0),
            vitamin_d_per_base=data.get('vitamin_d_per_100g', 0)
        )
        
        db.session.add(nutrition)
        
        # Create serving size if provided
        if data.get('serving_name') and data.get('serving_unit') and data.get('serving_quantity'):
            serving = FoodServing(
                food_id=food.id,
                serving_name=data['serving_name'],
                serving_unit=data['serving_unit'],
                serving_quantity=data['serving_quantity'],
                is_default=True
            )
            db.session.add(serving)
        
        # Create successful job item
        job_item = BulkUploadJobItem(
            job_id=job.id,
            row_number=row_number,
            food_name=data['name'],
            status='success',
            food_id=food.id,
            processed_at=datetime.utcnow()
        )
        db.session.add(job_item)
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current status of upload job.
        
        Args:
            job_id: Job ID to check
            
        Returns:
            Job status information
        """
        job = BulkUploadJob.query.filter_by(job_id=job_id).first()
        if not job:
            return None
        
        return {
            'job_id': job.job_id,
            'filename': job.filename,
            'status': job.status,
            'total_rows': job.total_rows,
            'processed_rows': job.processed_rows,
            'successful_rows': job.successful_rows,
            'failed_rows': job.failed_rows,
            'progress_percentage': job.progress_percentage,
            'error_message': job.error_message,
            'created_at': job.created_at.isoformat(),
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'completed_at': job.completed_at.isoformat() if job.completed_at else None
        }
    
    def get_job_details(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed job information including failed items.
        
        Args:
            job_id: Job ID to check
            
        Returns:
            Detailed job information
        """
        job = BulkUploadJob.query.filter_by(job_id=job_id).first()
        if not job:
            return None
        
        # Get failed items
        failed_items = BulkUploadJobItem.query.filter_by(
            job_id=job.id,
            status='failed'
        ).all()
        
        failed_details = []
        for item in failed_items:
            failed_details.append({
                'row_number': item.row_number,
                'food_name': item.food_name,
                'error_message': item.error_message,
                'processed_at': item.processed_at.isoformat() if item.processed_at else None
            })
        
        return {
            'job_id': job.job_id,
            'filename': job.filename,
            'status': job.status,
            'total_rows': job.total_rows,
            'processed_rows': job.processed_rows,
            'successful_rows': job.successful_rows,
            'failed_rows': job.failed_rows,
            'progress_percentage': job.progress_percentage,
            'error_message': job.error_message,
            'created_at': job.created_at.isoformat(),
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'completed_at': job.completed_at.isoformat() if job.completed_at else None,
            'failed_items': failed_details,
            'created_by': job.user.username
        }
