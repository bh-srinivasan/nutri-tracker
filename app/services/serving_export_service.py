"""
Serving Data Export Service

This service handles exporting food serving information to various formats
with filtering capabilities and async job processing for large datasets.
"""

import csv
import json
import os
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from flask import current_app
from sqlalchemy import and_
from app import db
from app.models import Food, FoodServing, ExportJob, User
import uuid


class ServingExportService:
    """Handles serving data export functionality."""
    
    # Export formats
    SUPPORTED_FORMATS = ['servings_csv', 'servings_json']
    
    # CSV headers for export
    CSV_HEADERS = [
        'serving_id', 'food_id', 'food_name', 'food_brand', 
        'food_category', 'food_verified', 'serving_name', 
        'unit', 'grams_per_unit', 'created_at', 'created_by_username'
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
        Start asynchronous serving data export.
        
        Args:
            format_type: Export format ('servings_csv' or 'servings_json')
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
            
            # Ensure export directory exists
            self._ensure_export_directory()
            
            # Build query with filters
            query = self._build_serving_query(filters)
            servings = query.all()
            
            # Generate filename
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            file_format = format_type.split('_')[1]  # Extract 'csv' or 'json' from 'servings_csv'
            filename = f"serving_export_{timestamp}.{file_format}"
            file_path = os.path.join(self.export_directory, filename)
            
            # Export data
            if format_type == 'servings_csv':
                self._export_to_csv(servings, file_path)
            elif format_type == 'servings_json':
                self._export_to_json(servings, file_path)
            
            # Update job with file information
            file_size = os.path.getsize(file_path)
            job.filename = filename
            job.file_path = file_path
            job.file_size = file_size
            job.total_records = len(servings)
            job.status = 'completed'
            job.completed_at = datetime.utcnow()
            
            db.session.commit()
            
        except Exception as e:
            job.status = 'failed'
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            db.session.commit()
            raise
    
    def _build_serving_query(self, filters: Optional[Dict[str, Any]]):
        """
        Build SQLAlchemy query with filters.
        
        Args:
            filters: Filter criteria
            
        Returns:
            SQLAlchemy query object
        """
        # Base query with explicit join condition
        query = db.session.query(FoodServing).join(
            Food, FoodServing.food_id == Food.id
        )
        
        if not filters:
            return query.order_by(Food.id.asc(), FoodServing.serving_name.asc())
        
        # Food-based filters
        
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
        
        # Serving-specific filters
        
        # Unit filter
        if filters.get('unit'):
            query = query.filter(FoodServing.unit == filters['unit'])
        
        # Serving name search
        if filters.get('serving_name_contains'):
            query = query.filter(FoodServing.serving_name.ilike(f"%{filters['serving_name_contains']}%"))
        
        # Grams per unit range
        if filters.get('grams_min'):
            query = query.filter(FoodServing.grams_per_unit >= filters['grams_min'])
        
        if filters.get('grams_max'):
            query = query.filter(FoodServing.grams_per_unit <= filters['grams_max'])
        
        # Date range filters for serving creation
        if filters.get('created_after'):
            try:
                date_after = datetime.fromisoformat(filters['created_after'])
                query = query.filter(FoodServing.created_at >= date_after)
            except ValueError:
                pass
        
        if filters.get('created_before'):
            try:
                date_before = datetime.fromisoformat(filters['created_before'])
                query = query.filter(FoodServing.created_at <= date_before)
            except ValueError:
                pass
        
        return query.order_by(Food.id.asc(), FoodServing.serving_name.asc())
    
    def _export_to_csv(self, servings: List[FoodServing], file_path: str):
        """
        Export servings to CSV format.
        
        Args:
            servings: List of FoodServing objects
            file_path: Output file path
        """
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.CSV_HEADERS)
            writer.writeheader()
            
            for serving in servings:
                # Get creator username if available
                created_by_username = ''
                if serving.created_by:
                    creator = User.query.get(serving.created_by)
                    if creator:
                        created_by_username = creator.username
                
                # Build row data
                row = {
                    'serving_id': serving.id,
                    'food_id': serving.food_id,
                    'food_name': self._sanitize_csv_value(serving.food.name),
                    'food_brand': self._sanitize_csv_value(serving.food.brand or ''),
                    'food_category': self._sanitize_csv_value(serving.food.category or ''),
                    'food_verified': serving.food.is_verified,
                    'serving_name': self._sanitize_csv_value(serving.serving_name),
                    'unit': self._sanitize_csv_value(serving.unit),
                    'grams_per_unit': serving.grams_per_unit,
                    'created_at': serving.created_at.isoformat() if serving.created_at else '',
                    'created_by_username': self._sanitize_csv_value(created_by_username)
                }
                
                writer.writerow(row)
    
    def _sanitize_csv_value(self, value):
        """
        Sanitize values for CSV export to prevent injection attacks and formatting issues.
        
        Args:
            value: Value to sanitize
            
        Returns:
            Sanitized string value
        """
        if value is None:
            return ''
        
        # Convert to string and strip whitespace
        str_value = str(value).strip()
        
        # Remove potentially dangerous characters that could be interpreted as formulas
        dangerous_chars = ['=', '+', '-', '@', '\t', '\r', '\n']
        for char in dangerous_chars:
            if str_value.startswith(char):
                str_value = "'" + str_value  # Prefix with quote to make it literal
                break
        
        # Limit length to prevent extremely long values
        if len(str_value) > 1000:
            str_value = str_value[:997] + '...'
        
        return str_value
    
    def _export_to_json(self, servings: List[FoodServing], file_path: str):
        """
        Export servings to JSON format.
        
        Args:
            servings: List of FoodServing objects
            file_path: Output file path
        """
        export_data = {
            'export_info': {
                'generated_at': datetime.utcnow().isoformat(),
                'total_records': len(servings),
                'format': 'json',
                'version': '1.0'
            },
            'servings': []
        }
        
        for serving in servings:
            # Get creator username if available
            created_by_username = ''
            if serving.created_by:
                creator = User.query.get(serving.created_by)
                if creator:
                    created_by_username = creator.username
            
            serving_data = {
                'serving_id': serving.id,
                'serving_name': serving.serving_name,
                'unit': serving.unit,
                'grams_per_unit': serving.grams_per_unit,
                'created_at': serving.created_at.isoformat() if serving.created_at else None,
                'created_by_username': created_by_username,
                'food': {
                    'id': serving.food.id,
                    'name': serving.food.name,
                    'brand': serving.food.brand,
                    'category': serving.food.category,
                    'is_verified': serving.food.is_verified
                }
            }
            
            export_data['servings'].append(serving_data)
        
        with open(file_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(export_data, jsonfile, indent=2, ensure_ascii=False)
    
    def get_export_statistics(self) -> Dict[str, Any]:
        """Get statistics about exportable serving data."""
        total_servings = FoodServing.query.count()
        foods_with_servings = db.session.query(FoodServing.food_id).distinct().count()
        total_units = db.session.query(FoodServing.unit).distinct().count()
        serving_creators = db.session.query(FoodServing.created_by).filter(
            FoodServing.created_by.isnot(None)
        ).distinct().count()
        
        return {
            'total_servings': total_servings,
            'foods_with_servings': foods_with_servings,
            'total_units': total_units,
            'serving_creators': serving_creators,
            'last_updated': datetime.utcnow().isoformat()
        }
    
    def get_available_categories(self) -> List[str]:
        """Get list of available food categories for filtering."""
        # Reuse Food categories since servings are linked to foods
        categories = db.session.query(Food.category).distinct().filter(
            Food.category.isnot(None),
            Food.category != ''
        ).all()
        return sorted([cat[0] for cat in categories if cat[0]])
    
    def get_available_units(self) -> List[str]:
        """Get list of available serving units for filtering."""
        units = db.session.query(FoodServing.unit).distinct().filter(
            FoodServing.unit.isnot(None),
            FoodServing.unit != ''
        ).all()
        return sorted([unit[0] for unit in units if unit[0]])
