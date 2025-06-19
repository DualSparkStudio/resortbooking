import os
from datetime import date, datetime, timedelta

# Set environment variables BEFORE importing app
os.environ['SESSION_SECRET'] = 'your-secret-key-here-for-development'
os.environ['DATABASE_URL'] = 'sqlite:///resort_booking.db'

from app import app, db
from models import User, RoomType, Room, Booking, Facility, Testimonial, ResortClosure

def create_sample_data():
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Check if data already exists
        if User.query.first():
            print("Sample data already exists!")
            return
        
        print("Creating sample data...")
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@luxuryresort.com',
            first_name='Resort',
            last_name='Administrator',
            phone='+1-555-0123',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create sample users
        user1 = User(
            username='john_doe',
            email='john@example.com',
            first_name='John',
            last_name='Doe',
            phone='+1-555-0001'
        )
        user1.set_password('password123')
        db.session.add(user1)
        
        user2 = User(
            username='jane_smith',
            email='jane@example.com',
            first_name='Jane',
            last_name='Smith',
            phone='+1-555-0002'
        )
        user2.set_password('password123')
        db.session.add(user2)
        
        # Create room types
        deluxe_suite = RoomType(
            name='Deluxe Ocean Suite',
            description='Spacious suite with panoramic ocean views, private balcony, and luxury amenities.',
            price_per_night=450.00,
            max_occupancy=4,
            amenities='Ocean view, Private balcony, King bed, Marble bathroom, Mini bar, WiFi',
            image_url='https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
            is_active=True
        )
        db.session.add(deluxe_suite)
        
        garden_villa = RoomType(
            name='Garden Villa',
            description='Private villa surrounded by tropical gardens with outdoor shower and terrace.',
            price_per_night=350.00,
            max_occupancy=2,
            amenities='Garden view, Private terrace, Queen bed, Outdoor shower, Kitchenette, WiFi',
            image_url='https://images.unsplash.com/photo-1631049307264-da0ec9d70304?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
            is_active=True
        )
        db.session.add(garden_villa)
        
        presidential_suite = RoomType(
            name='Presidential Suite',
            description='Ultimate luxury with private terrace, jacuzzi, and personal butler service.',
            price_per_night=850.00,
            max_occupancy=6,
            amenities='Ocean view, Private terrace, Jacuzzi, Butler service, Full kitchen, WiFi',
            image_url='https://images.unsplash.com/photo-1596394516093-501ba68a0ba6?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
            is_active=True
        )
        db.session.add(presidential_suite)
        
        db.session.commit()
        
        # Create rooms
        rooms_data = [
            ('101', deluxe_suite.id, 1),
            ('102', deluxe_suite.id, 1),
            ('103', deluxe_suite.id, 1),
            ('201', garden_villa.id, 2),
            ('202', garden_villa.id, 2),
            ('301', presidential_suite.id, 3),
        ]
        
        for room_number, room_type_id, floor in rooms_data:
            room = Room(
                room_number=room_number,
                room_type_id=room_type_id,
                floor=floor,
                is_available=True
            )
            db.session.add(room)
        
        db.session.commit()
        
        # Create sample bookings
        today = date.today()
        
        # Booking 1: Confirmed booking for next week
        booking1 = Booking(
            user_id=user1.id,
            room_id=1,  # Room 101
            check_in_date=today + timedelta(days=7),
            check_out_date=today + timedelta(days=10),
            num_guests=2,
            total_amount=1350.00,
            booking_status='confirmed',
            payment_status='paid'
        )
        db.session.add(booking1)
        
        # Booking 2: Pending booking for next month
        booking2 = Booking(
            user_id=user2.id,
            room_id=4,  # Room 201
            check_in_date=today + timedelta(days=30),
            check_out_date=today + timedelta(days=33),
            num_guests=2,
            total_amount=1050.00,
            booking_status='pending',
            payment_status='pending'
        )
        db.session.add(booking2)
        
        # Create resort closures
        closure1 = ResortClosure(
            start_date=today + timedelta(days=60),
            end_date=today + timedelta(days=62),
            reason='Maintenance',
            description='Annual maintenance and deep cleaning of all facilities.',
            is_active=True
        )
        db.session.add(closure1)
        
        closure2 = ResortClosure(
            start_date=today + timedelta(days=90),
            end_date=today + timedelta(days=91),
            reason='Staff Training',
            description='Mandatory staff training and team building activities.',
            is_active=True
        )
        db.session.add(closure2)
        
        # Create facilities
        facilities_data = [
            ('Swimming Pool', 'Olympic-sized infinity pool with ocean views', 'fas fa-swimming-pool'),
            ('Spa & Wellness', 'Full-service spa with massage and wellness treatments', 'fas fa-spa'),
            ('Fitness Center', '24/7 state-of-the-art fitness facility', 'fas fa-dumbbell'),
            ('Restaurant', 'Fine dining with international cuisine', 'fas fa-utensils'),
            ('Beach Access', 'Private beach with water sports equipment', 'fas fa-umbrella-beach'),
            ('Concierge Service', '24/7 concierge and room service', 'fas fa-concierge-bell'),
        ]
        
        for name, description, icon in facilities_data:
            facility = Facility(
                name=name,
                description=description,
                icon=icon,
                is_active=True
            )
            db.session.add(facility)
        
        # Create testimonials
        testimonials_data = [
            ('Sarah Johnson', 5, 'Absolutely amazing experience! The staff was incredible and the views were breathtaking.', True),
            ('Michael Chen', 5, 'Perfect getaway destination. Every detail was thoughtfully planned and executed.', True),
            ('Emily Rodriguez', 4, 'Beautiful resort with excellent amenities. Will definitely return!', True),
        ]
        
        for guest_name, rating, comment, is_featured in testimonials_data:
            testimonial = Testimonial(
                guest_name=guest_name,
                rating=rating,
                comment=comment,
                is_featured=is_featured,
                is_active=True
            )
            db.session.add(testimonial)
        
        db.session.commit()
        print("Sample data created successfully!")
        print("Admin login: admin / admin123")
        print("User login: john_doe / password123")

if __name__ == '__main__':
    create_sample_data() 