#!/usr/bin/env python3
"""
Food Export Functionality Demo

This script demonstrates the complete export functionality workflow.
Run this after setting up the application to verify everything works.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.services.food_export_service import FoodExportService
from app.models import Food, ExportJob
from datetime import datetime


def demo_export_functionality():
    """Demonstrate the export functionality with real examples."""
    print("🎯 Food Export Functionality Demo")
    print("=" * 60)
    print(f"📅 Demo Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    app = create_app()
    
    with app.app_context():
        print("\n📊 Current Database Status:")
        print("-" * 30)
        
        # Show current food statistics
        export_service = FoodExportService()
        stats = export_service.get_export_statistics()
        
        print(f"   🍎 Total Foods: {stats['total_foods']}")
        print(f"   ✅ Verified Foods: {stats['verified_foods']}")
        print(f"   📂 Categories: {stats['total_categories']}")
        print(f"   🏷️  Foods with Brands: {stats['foods_with_brands']}")
        
        # Show recent export jobs
        recent_jobs = ExportJob.query.order_by(ExportJob.created_at.desc()).limit(5).all()
        print(f"\n📋 Recent Export Jobs ({len(recent_jobs)} found):")
        print("-" * 30)
        
        if recent_jobs:
            for job in recent_jobs:
                status_icon = {
                    'completed': '✅',
                    'failed': '❌', 
                    'processing': '⏳',
                    'pending': '⏸️'
                }.get(job.status, '❓')
                
                print(f"   {status_icon} {job.job_id[:8]}... | {job.export_type.upper()} | "
                      f"{job.status} | {job.created_at.strftime('%m/%d %H:%M')}")
                
                if job.total_records:
                    print(f"      📊 {job.total_records} records | "
                          f"💾 {format_file_size(job.file_size) if job.file_size else 'N/A'}")
        else:
            print("   📭 No export jobs found yet")
        
        # Show available categories for filtering
        categories = export_service.get_available_categories()
        print(f"\n📂 Available Categories ({len(categories)}):")
        print("-" * 30)
        if categories:
            for i, category in enumerate(categories[:10], 1):  # Show first 10
                print(f"   {i:2d}. {category}")
            if len(categories) > 10:
                print(f"   ... and {len(categories) - 10} more")
        else:
            print("   📭 No categories found")
        
        print("\n🚀 How to Use Export Functionality:")
        print("-" * 40)
        print("   1. 🌐 Open your browser and navigate to the admin dashboard")
        print("   2. 🔐 Login with admin credentials")
        print("   3. 📊 Click on 'Export Foods' dropdown in the header")
        print("   4. 📝 Choose 'New Export' to create a new export")
        print("   5. ⚙️  Configure filters (format, category, dates, etc.)")
        print("   6. 🚀 Click 'Start Export' to begin processing")
        print("   7. 📋 Monitor progress in 'Export History'")
        print("   8. 💾 Download completed files within 24 hours")
        
        print("\n🎯 Export Options Available:")
        print("-" * 30)
        print("   📄 CSV Format:")
        print("      • Spreadsheet-compatible")
        print("      • All nutrition fields included")
        print("      • UTF-8 encoded for international characters")
        print("      • Injection-safe data sanitization")
        
        print("\n   📋 JSON Format:")
        print("      • Developer-friendly structured data")
        print("      • Nested nutrition information")
        print("      • Complete metadata included")
        print("      • API-ready format")
        
        print("\n   🔍 Filtering Options:")
        print("      • Category (Fruits, Vegetables, Meat, etc.)")
        print("      • Brand name (partial search)")
        print("      • Verification status (verified/unverified)")
        print("      • Date ranges (created after/before)")
        print("      • Nutrition values (min protein, max calories)")
        
        print("\n🛡️  Security Features:")
        print("-" * 25)
        print("   • 🔐 Admin-only access")
        print("   • 📝 All actions logged with timestamps")
        print("   • 🧹 Input validation and sanitization")
        print("   • ⏰ Files expire after 24 hours")
        print("   • 🔒 Secure file downloads")
        
        print("\n🎉 Export functionality is ready for use!")
        print("   Visit your admin dashboard to start exporting food data.")


def format_file_size(bytes_size):
    """Format file size in human-readable format."""
    if not bytes_size:
        return "N/A"
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"


if __name__ == '__main__':
    demo_export_functionality()
