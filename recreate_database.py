#!/usr/bin/env python3
"""
Recreate Database Script for Resort Booking System
This script recreates the database with the correct schema while preserving data.
"""

import os
import sqlite3
from pathlib import Path
from datetime import datetime

def get_database_path():
    """Get the path to the SQLite database"""
    current_dir = Path(__file__).parent
    db_path = current_dir / 'instance' / 'resort_booking.db'
    return str(db_path)

def backup_database_data(db_path):
    """Export all data to SQL file as backup"""
    backup_path = db_path + '.data_backup.sql'
    try:
        conn = sqlite3.connect(db_path)
        with open(backup_path, 'w') as f:
            for line in conn.iterdump():
                f.write('%s\n' % line)
        conn.close()
        print(f"✅ Data backup created: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"⚠️  Failed to create data backup: {e}")
        return None

def recreate_database():
    """Recreate the database with correct schema"""
    print("🔄 Recreating database with correct schema...")
    
    # Get database path
    db_path = get_database_path()
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return False
    
    print(f"📁 Database location: {db_path}")
    
    # Create data backup
    backup_path = backup_database_data(db_path)
    if not backup_path:
        print("❌ Cannot proceed without data backup")
        return False
    
    # Remove old database
    old_db_path = db_path + '.old'
    try:
        os.rename(db_path, old_db_path)
        print(f"✅ Old database moved to: {old_db_path}")
    except Exception as e:
        print(f"❌ Failed to move old database: {e}")
        return False
    
    # Create new database using Flask models
    try:
        from app import app, db
        
        with app.app_context():
            # Import all models
            import models
            
            # Create all tables with correct schema
            db.create_all()
            print("✅ New database created with correct schema")
            
            # Test that user_id is nullable
            from models import Booking
            test_booking = Booking(
                user_id=None,  # This should work now
                room_id=1,
                check_in_date=datetime(2025, 12, 25).date(),
                check_out_date=datetime(2025, 12, 26).date(),
                num_guests=2,
                total_amount=100.0,
                first_name="Test",
                last_name="Guest",
                email="test@example.com"
            )
            
            db.session.add(test_booking)
            db.session.commit()
            print("✅ Verified: user_id can be NULL")
            
            # Remove test booking
            db.session.delete(test_booking)
            db.session.commit()
            print("✅ Test booking removed")
            
            return True
            
    except Exception as e:
        print(f"❌ Failed to recreate database: {e}")
        # Restore old database
        if os.path.exists(old_db_path):
            try:
                os.rename(old_db_path, db_path)
                print(f"🔄 Restored old database")
            except:
                pass
        return False

def restore_sample_data():
    """Restore sample data if available"""
    print("🔄 Checking for sample data...")
    
    try:
        # Check if create_sample_data.py exists
        sample_data_script = Path(__file__).parent / 'create_sample_data.py'
        if sample_data_script.exists():
            print("✅ Sample data script found")
            
            # Import and run sample data creation
            import subprocess
            result = subprocess.run(['python', str(sample_data_script)], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Sample data restored")
                return True
            else:
                print(f"⚠️  Sample data script failed: {result.stderr}")
                return False
        else:
            print("⚠️  No sample data script found")
            return False
            
    except Exception as e:
        print(f"⚠️  Error restoring sample data: {e}")
        return False

def main():
    """Main function"""
    print("🏨 Resort Booking System - Database Recreation")
    print("=" * 60)
    print("⚠️  This will recreate the database with correct schema")
    print("   Your data will be backed up but you may need to restore it manually")
    print()
    
    response = input("Do you want to continue? (y/N): ")
    if response.lower() != 'y':
        print("❌ Operation cancelled")
        return False
    
    # Recreate database
    if recreate_database():
        print("\n✅ Database recreation successful!")
        
        # Try to restore sample data
        restore_sample_data()
        
        print("\n🎉 Database is now ready with correct schema!")
        print("💡 Guest bookings (without user accounts) are now supported!")
        print("🚀 You can now start the server: python start_server.py")
        
        return True
    else:
        print("\n❌ Database recreation failed!")
        return False

if __name__ == "__main__":
    main() 