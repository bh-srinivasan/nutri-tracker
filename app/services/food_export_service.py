"""
Food Data Export Service

This service handles exporting food database information to various formats
with filtering capabilities and async job processing for large datasets.
"""

import csv
import json
import os
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from flask import current_app
from app import db
from app.models import Food, FoodNutrition, FoodServing, ExportJob
import uuid


class FoodExportService:
    """Handles food data export functionality."""
    
    # Export formats
    SUPPORTED_FORMATS = ['csv', 'json']
    
    # CSV headers for export
    CSV_HEADERS = [
        'id', 'name', 'brand', 'category', 'description', 'barcode',
        'calories', 'protein', 'carbs', 'fat', 'fiber',
        'base_unit', 'base_quantity', 'calories_per_base', 'protein_per_base',
        'carbs_per_base', 'fat_per_base', 'fiber_per_base', 'sugar_per_base',
        'sodium_per_base', 'calcium_per_base', 'iron_per_base',
        'vitamin_c_per_base', 'vitamin_d_per_base',
        'serving_name', 'serving_unit', 'serving_quantity',
        'is_verified', 'created_at'
    ]
    
    def __init__(self):
        """Initialize the export service."""
        self.processing_lock = threading.Lock()
        # Initialize export_directory when app context is available
        self.export_directory = None
    
    def _ensure_export_directory(self):
        """Ensure export directory exists."""
        if not self.export_directory:
            self.export_directory = os.path.join(current_app.instance_path, 'exports')
        if not os.path.exists(self.export_directory):
            os.makedirs(self.export_directory, exist_ok=True)
    
    def start_export(self, format_type: str, filters: Optional[Dict[str, Any]] = None, user_id: int = None) -> str:
        """
        Start asynchronous food data export.
        
        Args:
            format_type: Export format ('csv' or 'json')
            filters: Optional filters to apply
            user_id: ID of user requesting export
            
        Returns:
            Job ID for tracking progress
        """
        if format_type not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported export format: {format_type}")
        
        # Create export job
        job = ExportJob(
            export_type=format_type,
            filter_criteria=json.dumps(filters or {}),
            created_by=user_id,
            status='pending'
        )
        
        db.session.add(job)
        db.session.commit()
        
        # Start export in background thread with app instance
        thread = threading.Thread(
            target=self._process_export_async,
            args=(current_app._get_current_object(), job.job_id, format_type, filters),
            daemon=True
        )
        thread.start()
        
        return job.job_id
    
    def _process_export_async(self, app, job_id: str, format_type: str, filters: Optional[Dict[str, Any]]):
        """
        Process export asynchronously with proper app context.
        
        Args:
            app: Flask app instance
            job_id: Export job ID
            format_type: Export format
            filters: Applied filters
        """
        with self.processing_lock:
            try:
                with app.app_context():
                    self._process_export_job(job_id, format_type, filters)
            except Exception as e:
                with app.app_context():
                    job = ExportJob.query.filter_by(job_id=job_id).first()
                    if job:
                        job.status = 'failed'
                        job.error_message = str(e)
                        job.completed_at = datetime.utcnow()
                        db.session.commit()
    
    def _process_export_job(self, job_id: str, format_type: str, filters: Optional[Dict[str, Any]]):
        """
        Main export processing logic.
        
        Args:
            job_id: Export job ID
            format_type: Export format
            filters: Applied filters
        """
        job = ExportJob.query.filter_by(job_id=job_id).first()
        if not job:
            return
        
        try:
            # Update job status
            job.status = 'processing'
            job.started_at = datetime.utcnow()
            db.session.commit()
            
            # Build query with filters
            query = self._build_food_query(filters)
            foods = query.all()
            
            # Generate filename
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f"food_export_{timestamp}.{format_type}"
            file_path = os.path.join(self.export_directory, filename)
            
            # Export data
            if format_type == 'csv':
                self._export_to_csv(foods, file_path)
            elif format_type == 'json':
                self._export_to_json(foods, file_path)
            
            # Update job with file information
            file_size = os.path.getsize(file_path)
            job.filename = filename
            job.file_path = file_path
            job.file_size = file_size
            job.total_records = len(foods)
            job.status = 'completed'
            job.completed_at = datetime.utcnow()
            
            db.session.commit()
            
        except Exception as e:
            job.status = 'failed'
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            db.session.commit()
            raise
    
    def _build_food_query(self, filters: Optional[Dict[str, Any]]):
        """
        Build SQLAlchemy query with filters.
        
        Args:
            filters: Filter criteria
            
        Returns:
            SQLAlchemy query object
        """
        query = Food.query
        
        if not filters:
            return query
        
        # Category filter
        if filters.get('category'):
            query = query.filter(Food.category == filters['category'])
        
        # Brand filter
        if filters.get('brand'):
            query = query.filter(Food.brand.ilike(f"%{filters['brand']}%"))
        
        # Name search
        if filters.get('name_contains'):
            query = query.filter(Food.name.ilike(f"%{filters['name_contains']}%"))
        
        # Verification status
        if filters.get('is_verified') is not None:
            query = query.filter(Food.is_verified == filters['is_verified'])
        
        # Date range filters
        if filters.get('created_after'):
            try:
                date_after = datetime.fromisoformat(filters['created_after'])
                query = query.filter(Food.created_at >= date_after)
            except ValueError:
                pass
        
        if filters.get('created_before'):
            try:
                date_before = datetime.fromisoformat(filters['created_before'])
                query = query.filter(Food.created_at <= date_before)
            except ValueError:
                pass
        
        # Nutrition value filters
        if filters.get('min_protein'):
            query = query.filter(Food.protein >= filters['min_protein'])
        
        if filters.get('max_calories'):
            query = query.filter(Food.calories <= filters['max_calories'])
        
        return query.order_by(Food.name)
    
    def _export_to_csv(self, foods: List[Food], file_path: str):
        """
        Export foods to CSV format.
        
        Args:
            foods: List of Food objects
            file_path: Output file path
        """
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.CSV_HEADERS)
            writer.writeheader()
            
            for food in foods:
                # Get related nutrition and serving data
                nutrition = food.nutrition_info[0] if food.nutrition_info else None
                serving = food.servings[0] if food.servings else None
                
                row = {
                    'id': food.id,
                    'name': food.name,
                    'brand': food.brand or '',
                    'category': food.category or '',
                    'description': food.description or '',
                    'barcode': food.barcode or '',
                    'calories': food.calories,
                    'protein': food.protein,
                    'carbs': food.carbs,
                    'fat': food.fat,
                    'fiber': food.fiber,
                    'is_verified': food.is_verified,
                    'created_at': food.created_at.isoformat() if food.created_at else ''
                }
                
                # Add nutrition info
                if nutrition:
                    row.update({
                        'base_unit': nutrition.base_unit,
                        'base_quantity': nutrition.base_quantity,
                        'calories_per_base': nutrition.calories_per_base,
                        'protein_per_base': nutrition.protein_per_base,
                        'carbs_per_base': nutrition.carbs_per_base,
                        'fat_per_base': nutrition.fat_per_base,
                        'fiber_per_base': nutrition.fiber_per_base,
                        'sugar_per_base': nutrition.sugar_per_base,
                        'sodium_per_base': nutrition.sodium_per_base,
                        'calcium_per_base': nutrition.calcium_per_base,
                        'iron_per_base': nutrition.iron_per_base,
                        'vitamin_c_per_base': nutrition.vitamin_c_per_base,
                        'vitamin_d_per_base': nutrition.vitamin_d_per_base
                    })
                else:
                    # Fill with empty values
                    nutrition_fields = [
                        'base_unit', 'base_quantity', 'calories_per_base', 'protein_per_base',
                        'carbs_per_base', 'fat_per_base', 'fiber_per_base', 'sugar_per_base',
                        'sodium_per_base', 'calcium_per_base', 'iron_per_base',
                        'vitamin_c_per_base', 'vitamin_d_per_base'
                    ]
                    for field in nutrition_fields:
                        row[field] = ''
                
                # Add serving info
                if serving:
                    row.update({
                        'serving_name': serving.serving_name,
                        'serving_unit': serving.serving_unit,
                        'serving_quantity': serving.serving_quantity
                    })
                else:
                    row.update({
                        'serving_name': '',
                        'serving_unit': '',
                        'serving_quantity': ''
                    })
                
                writer.writerow(row)
    
    def _export_to_json(self, foods: List[Food], file_path: str):
        """
        Export foods to JSON format.
        
        Args:
            foods: List of Food objects
            file_path: Output file path
        """
        export_data = {
            'export_info': {
                'generated_at': datetime.utcnow().isoformat(),
                'total_records': len(foods),
                'format': 'json'
            },
            'foods': []
        }
        
        for food in foods:
            food_data = {
                'id': food.id,
                'name': food.name,
                'brand': food.brand,
                'category': food.category,
                'description': food.description,
                'barcode': food.barcode,
                'basic_nutrition': {
                    'calories': food.calories,
                    'protein': food.protein,
                    'carbs': food.carbs,
                    'fat': food.fat,
                    'fiber': food.fiber
                },
                'is_verified': food.is_verified,
                'created_at': food.created_at.isoformat() if food.created_at else None
            }
            
            # Add detailed nutrition info
            if food.nutrition_info:
                nutrition = food.nutrition_info[0]
                food_data['detailed_nutrition'] = {
                    'base_unit': nutrition.base_unit,
                    'base_quantity': nutrition.base_quantity,
                    'per_base_unit': {
                        'calories': nutrition.calories_per_base,
                        'protein': nutrition.protein_per_base,
                        'carbs': nutrition.carbs_per_base,
                        'fat': nutrition.fat_per_base,
                        'fiber': nutrition.fiber_per_base,
                        'sugar': nutrition.sugar_per_base,
                        'sodium': nutrition.sodium_per_base,
                        'calcium': nutrition.calcium_per_base,
                        'iron': nutrition.iron_per_base,
                        'vitamin_c': nutrition.vitamin_c_per_base,
                        'vitamin_d': nutrition.vitamin_d_per_base
                    }
                }
            
            # Add serving sizes
            if food.servings:
                food_data['servings'] = []
                for serving in food.servings:
                    food_data['servings'].append({
                        'name': serving.serving_name,
                        'unit': serving.serving_unit,
                        'quantity': serving.serving_quantity,
                        'is_default': serving.is_default
                    })
            
            export_data['foods'].append(food_data)
        
        with open(file_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(export_data, jsonfile, indent=2, ensure_ascii=False)
    
    def get_export_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get export job status.
        
        Args:
            job_id: Export job ID
            
        Returns:
            Job status information
        """
        job = ExportJob.query.filter_by(job_id=job_id).first()
        if not job:
            return None
        
        return {
            'job_id': job.job_id,
            'export_type': job.export_type,
            'status': job.status,
            'total_records': job.total_records,
            'filename': job.filename,
            'file_size': job.file_size,
            'error_message': job.error_message,
            'is_expired': job.is_expired,
            'created_at': job.created_at.isoformat(),
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'completed_at': job.completed_at.isoformat() if job.completed_at else None,
            'expires_at': job.expires_at.isoformat()
        }
    
    def get_download_path(self, job_id: str) -> Optional[str]:
        """
        Get file path for completed export job.
        
        Args:
            job_id: Export job ID
            
        Returns:
            File path if available
        """
        job = ExportJob.query.filter_by(job_id=job_id).first()
        if not job or job.status != 'completed' or job.is_expired:
            return None
        
        if job.file_path and os.path.exists(job.file_path):
            return job.file_path
        
        return None
    
    def cleanup_expired_exports(self):
        """Clean up expired export files and database records."""
        try:
            # Find expired jobs
            expired_jobs = ExportJob.query.filter(
                ExportJob.expires_at < datetime.utcnow(),
                ExportJob.status == 'completed'
            ).all()
            
            for job in expired_jobs:
                # Delete file if exists
                if job.file_path and os.path.exists(job.file_path):
                    try:
                        os.remove(job.file_path)
                    except OSError:
                        pass  # File might be in use or already deleted
                
                # Update job status
                job.status = 'expired'
                job.file_path = None
            
            db.session.commit()
            
        except Exception as e:
            current_app.logger.error(f"Error cleaning up expired exports: {str(e)}")
            db.session.rollback()
    
    def get_available_categories(self) -> List[str]:
        """Get list of available food categories for filtering."""
        categories = db.session.query(Food.category).distinct().filter(
            Food.category.isnot(None),
            Food.category != ''
        ).all()
        return sorted([cat[0] for cat in categories if cat[0]])
    
    def get_available_brands(self, limit: int = 50) -> List[str]:
        """Get list of available brands for filtering."""
        brands = db.session.query(Food.brand).distinct().filter(
            Food.brand.isnot(None),
            Food.brand != ''
        ).limit(limit).all()
        return sorted([brand[0] for brand in brands if brand[0]])
    
    def get_export_statistics(self) -> Dict[str, Any]:
        """Get statistics about exportable data."""
        total_foods = Food.query.count()
        verified_foods = Food.query.filter_by(is_verified=True).count()
        categories = len(self.get_available_categories())
        brands = Food.query.filter(Food.brand.isnot(None), Food.brand != '').count()
        
        return {
            'total_foods': total_foods,
            'verified_foods': verified_foods,
            'unverified_foods': total_foods - verified_foods,
            'total_categories': categories,
            'foods_with_brands': brands,
            'last_updated': datetime.utcnow().isoformat()
        }
