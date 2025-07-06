#!/usr/bin/env python3
"""
Simple Database Backup Script for Nutri Tracker
Run this script regularly (daily) to create database backups
"""

import os
import shutil
import sqlite3
from datetime import datetime, timedelta
import sys

class SimpleBackupManager:
    def __init__(self, db_path="instance/nutri_tracker.db", backup_dir="backups/"):
        self.db_path = db_path
        self.backup_dir = backup_dir
        
        # Create backup directory if it doesn't exist
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_backup(self):
        """Create a timestamped backup of the database"""
        try:
            # Check if database exists
            if not os.path.exists(self.db_path):
                print(f"❌ Database file not found: {self.db_path}")
                return False
            
            # Generate backup filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"nutri_tracker_backup_{timestamp}.db"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # Create the backup
            shutil.copy2(self.db_path, backup_path)
            
            # Verify the backup
            if self._verify_backup(backup_path):
                file_size = os.path.getsize(backup_path)
                print(f"✅ Backup created successfully!")
                print(f"   📁 File: {backup_path}")
                print(f"   📊 Size: {file_size:,} bytes")
                print(f"   🕒 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                return True
            else:
                # Remove invalid backup
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                print(f"❌ Backup verification failed")
                return False
                
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return False
    
    def _verify_backup(self, backup_path):
        """Verify that the backup file is a valid SQLite database"""
        try:
            conn = sqlite3.connect(backup_path)
            cursor = conn.cursor()
            
            # Check if essential tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            essential_tables = ['user', 'food', 'meal_log']
            has_essential_tables = all(table in tables for table in essential_tables)
            
            # Check if there's at least one user record (admin should exist)
            cursor.execute("SELECT COUNT(*) FROM user")
            user_count = cursor.fetchone()[0]
            
            conn.close()
            
            return has_essential_tables and user_count > 0
            
        except Exception as e:
            print(f"⚠️ Backup verification error: {e}")
            return False
    
    def list_backups(self):
        """List all available backups"""
        backups = []
        
        if not os.path.exists(self.backup_dir):
            print("📂 No backup directory found")
            return backups
        
        for filename in os.listdir(self.backup_dir):
            if filename.startswith('nutri_tracker_backup_') and filename.endswith('.db'):
                file_path = os.path.join(self.backup_dir, filename)
                file_stat = os.stat(file_path)
                
                backups.append({
                    'filename': filename,
                    'path': file_path,
                    'date': datetime.fromtimestamp(file_stat.st_mtime),
                    'size': file_stat.st_size
                })
        
        # Sort by date (newest first)
        backups.sort(key=lambda x: x['date'], reverse=True)
        
        if backups:
            print(f"\n📋 Available Backups ({len(backups)} total):")
            print("=" * 60)
            for backup in backups:
                print(f"📁 {backup['filename']}")
                print(f"   🕒 {backup['date'].strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   📊 {backup['size']:,} bytes")
                print()
        else:
            print("📂 No backups found")
        
        return backups
    
    def cleanup_old_backups(self, days_to_keep=30):
        """Remove backup files older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        removed_count = 0
        
        if not os.path.exists(self.backup_dir):
            return removed_count
        
        for filename in os.listdir(self.backup_dir):
            if filename.startswith('nutri_tracker_backup_') and filename.endswith('.db'):
                file_path = os.path.join(self.backup_dir, filename)
                file_date = datetime.fromtimestamp(os.path.getctime(file_path))
                
                if file_date < cutoff_date:
                    try:
                        os.remove(file_path)
                        print(f"🗑️ Removed old backup: {filename}")
                        removed_count += 1
                    except Exception as e:
                        print(f"❌ Failed to remove {filename}: {e}")
        
        if removed_count == 0:
            print(f"🧹 No old backups to clean up (keeping {days_to_keep} days)")
        else:
            print(f"🧹 Cleaned up {removed_count} old backup(s)")
        
        return removed_count

def main():
    """Main function to handle command line operations"""
    backup_manager = SimpleBackupManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'create':
            backup_manager.create_backup()
        elif command == 'list':
            backup_manager.list_backups()
        elif command == 'cleanup':
            days = 30
            if len(sys.argv) > 2:
                try:
                    days = int(sys.argv[2])
                except ValueError:
                    print("❌ Invalid number of days")
                    return
            backup_manager.cleanup_old_backups(days)
        elif command == 'full':
            print("🔄 Running full backup process...")
            if backup_manager.create_backup():
                backup_manager.cleanup_old_backups()
                backup_manager.list_backups()
        else:
            print("❌ Unknown command. Available commands:")
            print("   create  - Create a new backup")
            print("   list    - List all backups")
            print("   cleanup [days] - Remove old backups (default: 30 days)")
            print("   full    - Create backup, cleanup old ones, and list all")
    else:
        # Default action: create backup
        print("📦 Creating database backup...")
        backup_manager.create_backup()

if __name__ == "__main__":
    main()
