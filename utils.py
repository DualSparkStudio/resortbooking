import os
import stripe
from datetime import date, datetime
from flask import current_app, url_for
from flask_mail import Message
from app import mail, db
from models import Room, Booking

# Configure Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

def check_room_availability(room_type_id, check_in_date, check_out_date, exclude_booking_id=None):
    """Check if rooms of a specific type are available for the given dates"""
    # Get all rooms of this type
    rooms = Room.query.filter_by(room_type_id=room_type_id, is_available=True).all()
    
    if not rooms:
        return []
    
    available_rooms = []
    
    for room in rooms:
        # Check if this room has any conflicting bookings
        query = Booking.query.filter(
            Booking.room_id == room.id,
            Booking.booking_status.in_(['confirmed', 'pending']),
            Booking.check_in_date < check_out_date,
            Booking.check_out_date > check_in_date
        )
        
        if exclude_booking_id:
            query = query.filter(Booking.id != exclude_booking_id)
        
        conflicting_bookings = query.count()
        
        if conflicting_bookings == 0:
            available_rooms.append(room)
    
    return available_rooms

def calculate_booking_total(room_type, check_in_date, check_out_date):
    """Calculate total cost for a booking"""
    nights = (check_out_date - check_in_date).days
    return float(room_type.price_per_night) * nights

def create_stripe_checkout_session(booking):
    """Create a Stripe checkout session for a booking"""
    try:
        # Determine the domain for redirect URLs
        domain = os.environ.get('REPLIT_DEV_DOMAIN')
        if not domain:
            domains = os.environ.get('REPLIT_DOMAINS', '').split(',')
            domain = domains[0] if domains else 'localhost:5000'
        
        if not domain.startswith('http'):
            domain = f'https://{domain}'
        
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f'Room Booking - {booking.room.room_type.name}',
                        'description': f'Room {booking.room.room_number} from {booking.check_in_date} to {booking.check_out_date}',
                    },
                    'unit_amount': int(booking.total_amount * 100),  # Stripe expects cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f'{domain}/booking-success?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=f'{domain}/booking-cancel',
            metadata={
                'booking_id': str(booking.id)
            }
        )
        
        # Update booking with Stripe session ID
        booking.stripe_session_id = session.id
        db.session.commit()
        
        return session
    except Exception as e:
        current_app.logger.error(f"Error creating Stripe session: {str(e)}")
        return None

def send_booking_confirmation_email(booking):
    """Send booking confirmation email to user"""
    try:
        msg = Message(
            subject='Booking Confirmation - Luxury Resort',
            recipients=[booking.user.email],
            html=f"""
            <h2>Booking Confirmation</h2>
            <p>Dear {booking.user.get_full_name()},</p>
            <p>Your booking has been confirmed! Here are the details:</p>
            <ul>
                <li><strong>Booking ID:</strong> {booking.id}</li>
                <li><strong>Room:</strong> {booking.room.room_type.name} - Room {booking.room.room_number}</li>
                <li><strong>Check-in:</strong> {booking.check_in_date.strftime('%B %d, %Y')}</li>
                <li><strong>Check-out:</strong> {booking.check_out_date.strftime('%B %d, %Y')}</li>
                <li><strong>Guests:</strong> {booking.num_guests}</li>
                <li><strong>Total Amount:</strong> ${booking.total_amount}</li>
            </ul>
            {f'<p><strong>Special Requests:</strong> {booking.special_requests}</p>' if booking.special_requests else ''}
            <p>We look forward to welcoming you to our resort!</p>
            <p>Best regards,<br>Luxury Resort Team</p>
            """
        )
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Error sending confirmation email: {str(e)}")
        return False

def send_contact_notification_email(contact_message):
    """Send notification email for new contact message"""
    try:
        admin_email = os.environ.get('ADMIN_EMAIL', 'admin@resort.com')
        msg = Message(
            subject=f'New Contact Message: {contact_message.subject}',
            recipients=[admin_email],
            html=f"""
            <h2>New Contact Message</h2>
            <p><strong>From:</strong> {contact_message.name} ({contact_message.email})</p>
            <p><strong>Subject:</strong> {contact_message.subject}</p>
            <p><strong>Message:</strong></p>
            <p>{contact_message.message}</p>
            <p><strong>Received:</strong> {contact_message.created_at.strftime('%B %d, %Y at %I:%M %p')}</p>
            """
        )
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Error sending contact notification email: {str(e)}")
        return False

def format_currency(amount):
    """Format amount as currency"""
    return f"${amount:,.2f}"

def get_star_rating_html(rating):
    """Generate HTML for star rating display"""
    stars = []
    for i in range(1, 6):
        if i <= rating:
            stars.append('<i class="fas fa-star text-warning"></i>')
        else:
            stars.append('<i class="far fa-star text-muted"></i>')
    return ' '.join(stars)
