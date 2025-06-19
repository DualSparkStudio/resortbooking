import os
import sys
import sqlite3

def migrate_database():
    """
    Add check_in_time and check_out_time columns to the bookings table
    """
    print("Starting database migration...")
    
    # Find the database file
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'resort_booking.db')
    print(f"Database path: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        sys.exit(1)
    
    try:
        # Connect to the SQLite database directly
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(bookings)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add check_in_time column if it doesn't exist
        if 'check_in_time' not in columns:
            print("Adding check_in_time column to bookings table...")
            cursor.execute('ALTER TABLE bookings ADD COLUMN check_in_time VARCHAR(10) DEFAULT "14:00"')
            print("Added check_in_time column.")
        else:
            print("check_in_time column already exists.")
        
        # Add check_out_time column if it doesn't exist
        if 'check_out_time' not in columns:
            print("Adding check_out_time column to bookings table...")
            cursor.execute('ALTER TABLE bookings ADD COLUMN check_out_time VARCHAR(10) DEFAULT "12:00"')
            print("Added check_out_time column.")
        else:
            print("check_out_time column already exists.")
        
        # Commit changes and close connection
        conn.commit()
        conn.close()
        
        print("Migration completed successfully.")
    except Exception as e:
        print(f"Error during migration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    migrate_database() 