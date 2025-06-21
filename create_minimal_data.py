#!/usr/bin/env python3
"""
Create Minimal Data Script for Resort Booking System
This script creates minimal data needed for testing guest bookings.
"""

from datetime import date, datetime
from app import app, db
from models import User, RoomType, Room, Facility

def create_minimal_data():
    """Create minimal data for testing"""
    print("🏨 Creating minimal data for testing...")
    
    with app.app_context():
        # Create admin user if not exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@resort.com',
                first_name='Admin',
                last_name='User',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print("✅ Created admin user")
        
        # Create room types if not enough exist
        room_types = RoomType.query.count()
        if room_types < 3:
            # Standard Room
            standard = RoomType(
                name='Standard Room',
                description='Comfortable room with modern amenities',
                price_per_night=150.00,
                max_occupancy=2,
                amenities='Free WiFi\nAir Conditioning\nFlat Screen TV\nMini Fridge',
                is_active=True
            )
            db.session.add(standard)
            
            # Deluxe Room
            deluxe = RoomType(
                name='Deluxe Room',
                description='Spacious room with ocean view',
                price_per_night=250.00,
                max_occupancy=3,
                amenities='Free WiFi\nAir Conditioning\nFlat Screen TV\nMini Fridge\nOcean View\nBalcony',
                is_active=True
            )
            db.session.add(deluxe)
            
            # Suite
            suite = RoomType(
                name='Luxury Suite',
                description='Premium suite with all luxury amenities',
                price_per_night=450.00,
                max_occupancy=4,
                amenities='Free WiFi\nAir Conditioning\nFlat Screen TV\nMini Fridge\nOcean View\nBalcony\nJacuzzi\nKitchenette',
                is_active=True
            )
            db.session.add(suite)
            
            db.session.commit()
            print("✅ Created room types")
        
        # Create rooms if not enough exist
        rooms = Room.query.count()
        if rooms < 6:
            room_types = RoomType.query.all()
            room_number = 101
            
            for room_type in room_types:
                for i in range(2):  # 2 rooms per type
                    room = Room(
                        room_number=str(room_number),
                        room_type_id=room_type.id,
                        floor=int(str(room_number)[0]),
                        is_available=True
                    )
                    db.session.add(room)
                    room_number += 1
            
            db.session.commit()
            print("✅ Created rooms")
        
        # Create basic facilities
        facilities = Facility.query.count()
        if facilities < 3:
            facilities_data = [
                ('Swimming Pool', 'Olympic-size outdoor pool with poolside service', 'fas fa-swimming-pool'),
                ('Spa & Wellness', 'Full-service spa with massage and wellness treatments', 'fas fa-spa'),
                ('Restaurant', 'Fine dining restaurant with international cuisine', 'fas fa-utensils'),
                ('Fitness Center', '24/7 fitness center with modern equipment', 'fas fa-dumbbell'),
                ('Beach Access', 'Private beach access with complimentary chairs and umbrellas', 'fas fa-umbrella-beach'),
                ('Conference Rooms', 'Modern conference facilities for business meetings', 'fas fa-presentation-screen')
            ]
            
            for name, desc, icon in facilities_data:
                facility = Facility(
                    name=name,
                    description=desc,
                    icon=icon,
                    is_active=True
                )
                db.session.add(facility)
            
            db.session.commit()
            print("✅ Created facilities")
        
        # Print summary
        users = User.query.count()
        room_types = RoomType.query.count()
        rooms = Room.query.count()
        facilities = Facility.query.count()
        
        print(f"\n📊 Data Summary:")
        print(f"   Users: {users}")
        print(f"   Room Types: {room_types}")
        print(f"   Rooms: {rooms}")
        print(f"   Facilities: {facilities}")
        
        print("\n✅ Minimal data creation completed!")
        print("🔑 Admin login: admin / admin123")

if __name__ == "__main__":
    create_minimal_data() 