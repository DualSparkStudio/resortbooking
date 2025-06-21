#!/usr/bin/env python3
"""
Database Schema Migration Script for Resort Booking System
This script updates the existing database to match the current model definitions.
"""

import sqlite3
import os
from pathlib import Path

def get_database_path():
    """Get the path to the SQLite database"""
    current_dir = Path(__file__).parent
    db_path = current_dir / 'instance' / 'resort_booking.db'
    return str(db_path)

def check_column_exists(cursor, table_name, column_name):
    """Check if a column exists in a table"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [column[1] for column in cursor.fetchall()]
    return column_name in columns

def migrate_bookings_table(cursor):
    """Migrate the bookings table to add missing columns"""
    print("🔄 Migrating bookings table...")
    
    # List of columns that should exist in the bookings table
    required_columns = [
        ('payment_gateway', 'VARCHAR(20)', 'stripe'),
        ('stripe_session_id', 'VARCHAR(255)', None),
        ('razorpay_order_id', 'VARCHAR(255)', None),
        ('razorpay_payment_id', 'VARCHAR(255)', None),
        ('first_name', 'VARCHAR(50)', None),
        ('last_name', 'VARCHAR(50)', None),
        ('email', 'VARCHAR(120)', None),
        ('phone', 'VARCHAR(20)', None),
        ('updated_at', 'DATETIME', 'CURRENT_TIMESTAMP')
    ]
    
    added_columns = []
    
    for column_name, column_type, default_value in required_columns:
        if not check_column_exists(cursor, 'bookings', column_name):
            try:
                if default_value:
                    cursor.execute(f"ALTER TABLE bookings ADD COLUMN {column_name} {column_type} DEFAULT '{default_value}'")
                else:
                    cursor.execute(f"ALTER TABLE bookings ADD COLUMN {column_name} {column_type}")
                added_columns.append(column_name)
                print(f"  ✅ Added column: {column_name}")
            except sqlite3.Error as e:
                print(f"  ⚠️  Failed to add column {column_name}: {e}")
    
    if added_columns:
        print(f"  📊 Added {len(added_columns)} columns to bookings table")
    else:
        print("  ✅ Bookings table already up to date")
    
    return added_columns

def migrate_room_type_images_table(cursor):
    """Create room_type_images table if it doesn't exist"""
    print("🔄 Checking room_type_images table...")
    
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS room_type_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_type_id INTEGER NOT NULL,
                image_url VARCHAR(500) NOT NULL,
                alt_text VARCHAR(255),
                is_primary BOOLEAN DEFAULT 0,
                sort_order INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (room_type_id) REFERENCES room_types (id)
            )
        """)
        print("  ✅ room_type_images table created/verified")
        return True
    except sqlite3.Error as e:
        print(f"  ❌ Failed to create room_type_images table: {e}")
        return False

def migrate_other_tables(cursor):
    """Create other missing tables if they don't exist"""
    print("🔄 Checking other tables...")
    
    tables = [
        ("facilities", """
            CREATE TABLE IF NOT EXISTS facilities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                icon VARCHAR(50),
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """),
        ("testimonials", """
            CREATE TABLE IF NOT EXISTS testimonials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guest_name VARCHAR(100) NOT NULL,
                rating INTEGER NOT NULL,
                comment TEXT NOT NULL,
                is_featured BOOLEAN DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """),
        ("contact_messages", """
            CREATE TABLE IF NOT EXISTS contact_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(120) NOT NULL,
                subject VARCHAR(200) NOT NULL,
                message TEXT NOT NULL,
                is_read BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """),
        ("resort_closures", """
            CREATE TABLE IF NOT EXISTS resort_closures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                reason VARCHAR(200) NOT NULL,
                description TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """),
        ("calendar_settings", """
            CREATE TABLE IF NOT EXISTS calendar_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setting_key VARCHAR(100) NOT NULL UNIQUE,
                setting_value TEXT NOT NULL,
                description TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
    ]
    
    created_tables = []
    for table_name, create_sql in tables:
        try:
            cursor.execute(create_sql)
            created_tables.append(table_name)
            print(f"  ✅ {table_name} table created/verified")
        except sqlite3.Error as e:
            print(f"  ⚠️  Failed to create {table_name} table: {e}")
    
    return created_tables

def update_user_table(cursor):
    """Update users table to ensure all columns exist"""
    print("🔄 Checking users table...")
    
    # Check if is_admin column exists
    if not check_column_exists(cursor, 'users', 'is_admin'):
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0")
            print("  ✅ Added is_admin column to users table")
        except sqlite3.Error as e:
            print(f"  ⚠️  Failed to add is_admin column: {e}")
    else:
        print("  ✅ Users table already up to date")

def backup_database(db_path):
    """Create a backup of the database before migration"""
    backup_path = db_path + '.backup'
    try:
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✅ Database backup created: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"⚠️  Failed to create backup: {e}")
        return None

def main():
    """Main migration function"""
    print("🏨 Resort Booking System - Database Schema Migration")
    print("=" * 60)
    
    # Get database path
    db_path = get_database_path()
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        print("   Run python fix_database.py first to create the database")
        return False
    
    print(f"📁 Database location: {db_path}")
    
    # Create backup
    backup_path = backup_database(db_path)
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n🔄 Starting schema migration...")
        
        # Migrate tables
        migrate_bookings_table(cursor)
        migrate_room_type_images_table(cursor)
        update_user_table(cursor)
        migrate_other_tables(cursor)
        
        # Commit changes
        conn.commit()
        
        print("\n✅ Database migration completed successfully!")
        
        # Test the migration by importing models
        print("\n🧪 Testing migration...")
        try:
            from app import app, db
            with app.app_context():
                from models import Booking, User, RoomType
                
                # Test a simple query
                booking_count = Booking.query.count()
                user_count = User.query.count()
                room_type_count = RoomType.query.count()
                
                print(f"  ✅ Migration test successful!")
                print(f"  📊 Bookings: {booking_count}")
                print(f"  📊 Users: {user_count}")
                print(f"  📊 Room Types: {room_type_count}")
                
        except Exception as e:
            print(f"  ❌ Migration test failed: {e}")
            print("  🔄 You may need to restart the server")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        if backup_path and os.path.exists(backup_path):
            print(f"💾 Database backup available at: {backup_path}")
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Your database is now up to date!")
        print("🚀 You can now start the server: python start_server.py")
    else:
        print("\n❌ Migration failed. Check the error messages above.") 