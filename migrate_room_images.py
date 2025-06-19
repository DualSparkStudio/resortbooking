import os
import sys
import sqlite3
from datetime import datetime

def migrate_room_images():
    """
    Create room_type_images table for multiple images support
    """
    print("Starting room images migration...")
    
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
        
        # Check if table already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='room_type_images'")
        if cursor.fetchone():
            print("room_type_images table already exists.")
            return
        
        # Create room_type_images table
        print("Creating room_type_images table...")
        cursor.execute('''
            CREATE TABLE room_type_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_type_id INTEGER NOT NULL,
                image_url VARCHAR(500) NOT NULL,
                alt_text VARCHAR(255),
                is_primary BOOLEAN DEFAULT 0,
                sort_order INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (room_type_id) REFERENCES room_types(id) ON DELETE CASCADE
            )
        ''')
        
        # Create index for better performance
        cursor.execute('''
            CREATE INDEX idx_room_type_images_room_type_id ON room_type_images(room_type_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX idx_room_type_images_is_primary ON room_type_images(is_primary)
        ''')
        
        # Migrate existing image_url data from room_types to room_type_images
        print("Migrating existing image URLs...")
        cursor.execute("SELECT id, image_url FROM room_types WHERE image_url IS NOT NULL AND image_url != ''")
        room_types_with_images = cursor.fetchall()
        
        for room_type_id, image_url in room_types_with_images:
            cursor.execute('''
                INSERT INTO room_type_images (room_type_id, image_url, alt_text, is_primary, sort_order, created_at)
                VALUES (?, ?, ?, 1, 0, ?)
            ''', (room_type_id, image_url, f"Main image for room type {room_type_id}", datetime.now()))
            print(f"Migrated image for room type {room_type_id}: {image_url}")
        
        # Commit changes and close connection
        conn.commit()
        conn.close()
        
        print("Migration completed successfully.")
        print(f"Migrated {len(room_types_with_images)} existing room type images.")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    migrate_room_images() 