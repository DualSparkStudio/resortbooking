from datetime import datetime, date, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import hashlib
from app import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    bookings = db.relationship('Booking', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def generate_password_reset_token(self):
        """Generate a secure password reset token"""
        # Generate a random token
        token = secrets.token_urlsafe(32)
        
        # Create a timestamp (rounded to minute for consistency)
        timestamp = int(datetime.utcnow().timestamp())
        
        # Create token data and hash
        token_data = f"{token}:{timestamp}:{self.id}"
        token_hash = hashlib.sha256(token_data.encode()).hexdigest()
        
        # Return token in format: token|hash|timestamp (using | to avoid : conflicts)
        return f"{token}|{token_hash}|{timestamp}"
    
    def verify_password_reset_token(self, token_string, expiry_hours=1):
        """Verify a password reset token and check if it's still valid"""
        try:
            # Split the token using | separator
            parts = token_string.split('|')
            if len(parts) != 3:
                return False
            
            token, token_hash, timestamp_str = parts
            timestamp = int(timestamp_str)
            
            # Check if token is expired
            current_time = int(datetime.utcnow().timestamp())
            if current_time - timestamp > expiry_hours * 3600:  # 3600 seconds = 1 hour
                return False
            
            # Verify the hash (note: token_data uses : separator for hashing)
            token_data = f"{token}:{timestamp}:{self.id}"
            expected_hash = hashlib.sha256(token_data.encode()).hexdigest()
            
            return token_hash == expected_hash
            
        except Exception:
            return False
    
    @staticmethod
    def get_user_by_reset_token(token_string):
        """Get user by reset token without exposing user ID in token"""
        # This is a simple implementation - in production you might want to store tokens in database
        # For now, we'll try to match against all users (not ideal for large user bases)
        users = User.query.all()
        for user in users:
            if user.verify_password_reset_token(token_string):
                return user
        return None
    
    def __repr__(self):
        return f'<User {self.username}>'

class RoomType(db.Model):
    __tablename__ = 'room_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price_per_night = db.Column(db.Numeric(10, 2), nullable=False)
    max_occupancy = db.Column(db.Integer, nullable=False)
    amenities = db.Column(db.Text)  # JSON string of amenities
    image_url = db.Column(db.String(255))  # Keep for backward compatibility
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    rooms = db.relationship('Room', backref='room_type', lazy=True)
    images = db.relationship('RoomTypeImage', backref='room_type', lazy=True, cascade='all, delete-orphan')
    
    def get_primary_image(self):
        """Get the primary image or fall back to image_url"""
        primary_image = RoomTypeImage.query.filter_by(room_type_id=self.id, is_primary=True).first()
        if primary_image:
            return primary_image.image_url
        elif self.images:
            return self.images[0].image_url
        else:
            return self.image_url
    
    def get_all_images(self):
        """Get all image URLs for this room type"""
        image_urls = [img.image_url for img in self.images]
        if self.image_url and self.image_url not in image_urls:
            image_urls.append(self.image_url)
        return image_urls
    
    @property
    def amenities_list(self):
        """Get amenities as a list for template rendering"""
        if self.amenities:
            return [line.strip() for line in self.amenities.split('\n') if line.strip()]
        return []
    
    def __repr__(self):
        return f'<RoomType {self.name}>'

class RoomTypeImage(db.Model):
    __tablename__ = 'room_type_images'
    
    id = db.Column(db.Integer, primary_key=True)
    room_type_id = db.Column(db.Integer, db.ForeignKey('room_types.id'), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    alt_text = db.Column(db.String(255))
    is_primary = db.Column(db.Boolean, default=False)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<RoomTypeImage {self.room_type_id}:{self.image_url[:50]}>'

class Room(db.Model):
    __tablename__ = 'rooms'
    
    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(20), unique=True, nullable=False)
    room_type_id = db.Column(db.Integer, db.ForeignKey('room_types.id'), nullable=False)
    floor = db.Column(db.Integer)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    bookings = db.relationship('Booking', backref='room', lazy=True)
    
    def __repr__(self):
        return f'<Room {self.room_number}>'

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Now nullable for guests
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    check_in_date = db.Column(db.Date, nullable=False)
    check_out_date = db.Column(db.Date, nullable=False)
    check_in_time = db.Column(db.String(10), default="14:00")  # Default check-in time (2 PM)
    check_out_time = db.Column(db.String(10), default="12:00")  # Default check-out time (12 PM)
    num_guests = db.Column(db.Integer, nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    booking_status = db.Column(db.String(20), default='pending')  # pending, confirmed, cancelled, completed
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, failed, refunded
    payment_gateway = db.Column(db.String(20), default='stripe')  # stripe, razorpay
    stripe_session_id = db.Column(db.String(255))
    razorpay_order_id = db.Column(db.String(255))
    razorpay_payment_id = db.Column(db.String(255))
    special_requests = db.Column(db.Text)
    # Guest fields
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_duration_days(self):
        return (self.check_out_date - self.check_in_date).days
    
    def __repr__(self):
        return f'<Booking {self.id}>'

class Facility(db.Model):
    __tablename__ = 'facilities'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))  # Font Awesome icon class
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Facility {self.name}>'

class Testimonial(db.Model):
    __tablename__ = 'testimonials'
    
    id = db.Column(db.Integer, primary_key=True)
    guest_name = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.Text, nullable=False)
    is_featured = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Testimonial {self.guest_name}>'

class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ContactMessage {self.subject}>'

class ResortClosure(db.Model):
    __tablename__ = 'resort_closures'
    
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ResortClosure {self.reason} ({self.start_date} - {self.end_date})>'

class CalendarSettings(db.Model):
    __tablename__ = 'calendar_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(100), unique=True, nullable=False)
    setting_value = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<CalendarSettings {self.setting_key}>'
