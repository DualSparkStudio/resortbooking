#!/usr/bin/env python3
"""
Database Fix Script for Resort Booking System
This script fixes common database initialization issues.
"""

import os
import sys
from pathlib import Path

def fix_database_path():
    """Ensure the instance directory exists and has proper permissions"""
    print("🔧 Fixing database path issues...")
    
    # Get the current directory
    current_dir = Path(__file__).parent
    instance_dir = current_dir / 'instance'
    
    # Create instance directory if it doesn't exist
    instance_dir.mkdir(exist_ok=True)
    print(f"✅ Instance directory created/verified: {instance_dir}")
    
    # Check if database file exists
    db_path = instance_dir / 'resort_booking.db'
    if db_path.exists():
        print(f"✅ Database file exists: {db_path}")
        print(f"📊 Database size: {db_path.stat().st_size} bytes")
    else:
        print(f"⚠️  Database file doesn't exist yet: {db_path}")
        print("   It will be created when the app starts")
    
    # Set environment variable for database URL
    os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'
    print(f"✅ Database URL set: sqlite:///{db_path}")
    
    return db_path

def initialize_database():
    """Initialize the database with tables"""
    print("🗄️  Initializing database...")
    
    try:
        # Import Flask app components
        from app import app, db
        
        # Create application context
        with app.app_context():
            # Import all models to ensure they're registered
            import models
            
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Check if we have any data
            from models import User, RoomType, Room
            
            user_count = User.query.count()
            room_type_count = RoomType.query.count()
            room_count = Room.query.count()
            
            print(f"📊 Database statistics:")
            print(f"   Users: {user_count}")
            print(f"   Room Types: {room_type_count}")
            print(f"   Rooms: {room_count}")
            
            if user_count == 0 and room_type_count == 0:
                print("⚠️  Database is empty. Consider running create_sample_data.py")
                
        return True
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False

def main():
    """Main function to fix database issues"""
    print("🏨 Resort Booking System - Database Fix")
    print("=" * 50)
    
    # Step 1: Fix database path
    db_path = fix_database_path()
    
    # Step 2: Initialize database
    if initialize_database():
        print("\n✅ Database fix completed successfully!")
        print(f"📁 Database location: {db_path}")
        print("🚀 You can now start the server with: python start_server.py")
    else:
        print("\n❌ Database fix failed!")
        print("🔍 Check the error messages above for troubleshooting")

if __name__ == "__main__":
    main() 