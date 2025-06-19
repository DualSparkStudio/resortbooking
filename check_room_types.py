#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import RoomType, RoomTypeImage

def check_room_types():
    with app.app_context():
        print("Checking existing room types...")
        
        room_types = RoomType.query.all()
        
        if not room_types:
            print("No room types found!")
            return
            
        for room_type in room_types:
            images_count = RoomTypeImage.query.filter_by(room_type_id=room_type.id).count()
            print(f"- ID: {room_type.id}, Name: '{room_type.name}', Images: {images_count}")
            print(f"  Legacy image_url: {room_type.image_url}")
            print(f"  Primary image: {room_type.get_primary_image()}")
            print()

if __name__ == '__main__':
    check_room_types() 