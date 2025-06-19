#!/usr/bin/env python3
"""
Script to add multiple sample images to existing room types
Run this after the main sample data has been created
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import RoomType, RoomTypeImage

def add_sample_images():
    """Add multiple images to existing room types"""
    
    with app.app_context():
        print("Adding sample images to room types...")
        
        # Sample images for different room types
        sample_images = {
            'Deluxe Ocean Suite': [
                'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
                'https://images.unsplash.com/photo-1566195992011-5f6b21e539aa?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
                'https://images.unsplash.com/photo-1631049035634-f04a8d2d5e66?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
                'https://images.unsplash.com/photo-1596394516093-501ba68a0ba6?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
                'https://images.unsplash.com/photo-1571896349842-33c89424de2d?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80'
            ],
            'Garden Villa': [
                'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
                'https://images.unsplash.com/photo-1564013799919-ab600027ffc6?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
                'https://images.unsplash.com/photo-1540518614846-7eded433c457?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
                'https://images.unsplash.com/photo-1578662996442-48f60103fc96?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
                'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80'
            ],
            'Presidential Suite': [
                'https://images.unsplash.com/photo-1596394516093-501ba68a0ba6?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
                'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
                'https://images.unsplash.com/photo-1618773928121-c32242e63f39?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
                'https://images.unsplash.com/photo-1611892440504-42a792e24d32?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
                'https://images.unsplash.com/photo-1590490360182-c33d57733427?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
                'https://images.unsplash.com/photo-1631049552057-403cdb8f0658?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80'
            ]
        }
        
        for room_name, image_urls in sample_images.items():
            room_type = RoomType.query.filter_by(name=room_name).first()
            if room_type:
                print(f"Adding images to {room_name}...")
                
                # Clear existing images first
                RoomTypeImage.query.filter_by(room_type_id=room_type.id).delete()
                
                # Add new images
                for i, image_url in enumerate(image_urls):
                    room_image = RoomTypeImage(
                        room_type_id=room_type.id,
                        image_url=image_url,
                        alt_text=f'{room_name} - Image {i+1}',
                        is_primary=(i == 0),  # First image is primary
                        sort_order=i
                    )
                    db.session.add(room_image)
                
                print(f"  Added {len(image_urls)} images")
            else:
                print(f"Room type '{room_name}' not found, skipping...")
        
        db.session.commit()
        print("Sample images added successfully!")

if __name__ == '__main__':
    add_sample_images()