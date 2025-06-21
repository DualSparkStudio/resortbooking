import os
import stripe
import razorpay
from datetime import date, datetime
from flask import current_app, url_for, request
from flask_mail import Message
from app import mail, db
from models import Room, Booking
import uuid
from werkzeug.utils import secure_filename

# Configure Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

# Configure Razorpay
RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET')

if RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET:
    razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
else:
    razorpay_client = None

def check_room_availability(room_type_id, check_in_date, check_out_date, exclude_booking_id=None):
    """Check if rooms of a specific type are available for the given dates"""
    # Get all rooms of this type
    rooms = Room.query.filter_by(room_type_id=room_type_id, is_available=True).all()
    
    if not rooms:
        return []
    
    available_rooms = []
    
    for room in rooms:
        # Check if this room has any conflicting bookings
        # Allow same-day checkout/checkin: existing checkout = new checkin is allowed
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

def get_app_domain():
    """Get the application domain for URLs"""
    # Try to get domain from request context first
    if request:
        return request.url_root.rstrip('/')
    
    # Fallback to environment variables
    domain = os.environ.get('RENDER_EXTERNAL_URL')  # Render.com
    if domain:
        return domain
    
    domain = os.environ.get('RAILWAY_STATIC_URL')  # Railway
    if domain:
        return f'https://{domain}'
    
    domain = os.environ.get('HEROKU_APP_NAME')  # Heroku
    if domain:
        return f'https://{domain}.herokuapp.com'
    
    # Replit fallback
    domain = os.environ.get('REPLIT_DEV_DOMAIN')
    if not domain:
        domains = os.environ.get('REPLIT_DOMAINS', '').split(',')
        domain = domains[0] if domains else 'localhost:5000'
    
    if not domain.startswith('http'):
        if 'localhost' in domain or '127.0.0.1' in domain:
            domain = f'http://{domain}'
        else:
            domain = f'https://{domain}'
    
    return domain

def create_stripe_checkout_session(booking, stripe_secret_key, stripe_publishable_key):
    """Create a Stripe checkout session for a booking"""
    try:
        # Set Stripe API key for this request
        stripe.api_key = stripe_secret_key

        if not stripe.api_key:
            current_app.logger.error("Stripe API key not configured in settings")
            return None
        
        # Get the application domain
        domain = get_app_domain()
        
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

def create_razorpay_order(booking):
    """Create a Razorpay order for a booking"""
    try:
        if not razorpay_client:
            current_app.logger.error("Razorpay client not configured")
            return None
        
        # Calculate amount in paise (smallest currency unit)
        amount_in_paise = int(booking.total_amount * 100)
        
        # Create order data with all required fields
        order_data = {
            'amount': amount_in_paise,  # Amount in paise (required)
            'currency': 'INR',  # Currency code (required)
            'receipt': f'booking_{booking.id}_{int(datetime.now().timestamp())}',  # Unique receipt ID (required)
            'payment_capture': 1,  # Auto-capture payment (1 = auto, 0 = manual)
            'notes': {
                'booking_id': str(booking.id),
                'room_number': booking.room.room_number,
                'room_type': booking.room.room_type.name,
                'check_in': booking.check_in_date.isoformat(),
                'check_out': booking.check_out_date.isoformat(),
                'guest_name': f"{booking.first_name} {booking.last_name}",
                'guest_email': booking.email
            }
        }
        
        # Log the order creation attempt
        current_app.logger.info(f"Creating Razorpay order for booking {booking.id}")
        current_app.logger.info(f"Order data: amount={amount_in_paise} paise (₹{booking.total_amount}), currency=INR")
        current_app.logger.info(f"Receipt ID: {order_data['receipt']}")
        
        # Create the order
        order = razorpay_client.order.create(data=order_data)
        
        # Log successful order creation
        current_app.logger.info(f"Razorpay order created successfully: {order['id']}")
        current_app.logger.info(f"Order status: {order.get('status', 'unknown')}")
        current_app.logger.info(f"Order amount: {order.get('amount', 'unknown')} paise")
        
        # Update booking with Razorpay order ID
        booking.razorpay_order_id = order['id']
        booking.payment_gateway = 'razorpay'
        db.session.commit()
        
        current_app.logger.info(f"Booking {booking.id} updated with Razorpay order ID: {order['id']}")
        
        return order
        
    except razorpay.errors.BadRequestError as e:
        current_app.logger.error(f"Razorpay BadRequestError: {str(e)}")
        current_app.logger.error(f"Error code: {getattr(e, 'code', 'unknown')}")
        current_app.logger.error(f"Error description: {getattr(e, 'description', 'unknown')}")
        return None
    except razorpay.errors.AuthenticationError as e:
        current_app.logger.error(f"Razorpay AuthenticationError: {str(e)}")
        current_app.logger.error("Check your Razorpay API keys")
        return None
    except Exception as e:
        current_app.logger.error(f"Unexpected error creating Razorpay order: {str(e)}")
        current_app.logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        current_app.logger.error(f"Full traceback: {traceback.format_exc()}")
        return None

def verify_razorpay_payment(payment_id, order_id, signature):
    """Verify Razorpay payment signature"""
    try:
        if not razorpay_client:
            current_app.logger.error("Razorpay client not configured for payment verification")
            return False
        
        # Log verification attempt
        current_app.logger.info(f"Verifying Razorpay payment signature")
        current_app.logger.info(f"Payment ID: {payment_id}")
        current_app.logger.info(f"Order ID: {order_id}")
        current_app.logger.info(f"Signature present: {'Yes' if signature else 'No'}")
        
        # Prepare verification parameters
        params_dict = {
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }
        
        # Verify the payment signature
        current_app.logger.info("Calling Razorpay signature verification...")
        razorpay_client.utility.verify_payment_signature(params_dict)
        
        current_app.logger.info("Payment signature verification successful")
        return True
        
    except razorpay.errors.SignatureVerificationError as e:
        current_app.logger.error(f"Razorpay signature verification failed: {str(e)}")
        current_app.logger.error("This indicates the payment may be fraudulent or tampered with")
        return False
    except razorpay.errors.BadRequestError as e:
        current_app.logger.error(f"Razorpay BadRequestError during verification: {str(e)}")
        current_app.logger.error(f"Error code: {getattr(e, 'code', 'unknown')}")
        return False
    except Exception as e:
        current_app.logger.error(f"Unexpected error verifying Razorpay payment: {str(e)}")
        current_app.logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        current_app.logger.error(f"Full traceback: {traceback.format_exc()}")
        return False

def send_booking_confirmation_email(booking, mail_settings, app_domain):
    """Send booking confirmation email to user or guest"""
    try:
        # Configure mail settings for this send operation
        current_app.config.update(
            MAIL_SERVER=mail_settings['MAIL_SERVER'],
            MAIL_PORT=mail_settings['MAIL_PORT'],
            MAIL_USE_TLS=mail_settings['MAIL_USE_TLS'],
            MAIL_USERNAME=mail_settings['MAIL_USERNAME'],
            MAIL_PASSWORD=mail_settings['MAIL_PASSWORD'],
            MAIL_DEFAULT_SENDER=mail_settings['MAIL_DEFAULT_SENDER']
        )
        mail.init_app(current_app)

        # Handle both user bookings and guest bookings
        if booking.user:
            # Registered user booking
            recipient_email = booking.user.email
            guest_name = booking.user.get_full_name()
        else:
            # Guest booking
            recipient_email = booking.email
            guest_name = f"{booking.first_name} {booking.last_name}"

        msg = Message(
            subject='Booking Confirmation - Luxury Resort',
            recipients=[recipient_email],
            html=f"""
            <h2>Booking Confirmation</h2>
            <p>Dear {guest_name},</p>
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

def send_contact_notification_email(contact_message, admin_email, mail_settings):
    """Send notification email for new contact message"""
    try:
        # Configure mail settings for this send operation
        current_app.config.update(
            MAIL_SERVER=mail_settings['MAIL_SERVER'],
            MAIL_PORT=mail_settings['MAIL_PORT'],
            MAIL_USE_TLS=mail_settings['MAIL_USE_TLS'],
            MAIL_USERNAME=mail_settings['MAIL_USERNAME'],
            MAIL_PASSWORD=mail_settings['MAIL_PASSWORD'],
            MAIL_DEFAULT_SENDER=mail_settings['MAIL_DEFAULT_SENDER']
        )
        mail.init_app(current_app)
        
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

def allowed_file(filename):
    """Check if the file has an allowed extension"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_image(file, upload_folder, prefix="image"):
    """
    Save an uploaded image file with a secure filename
    Returns the relative URL path to the saved file
    """
    if not file or not file.filename:
        return None
    
    if not allowed_file(file.filename):
        raise ValueError("File type not allowed. Please use PNG, JPG, JPEG, GIF, or WEBP files.")
    
    # Secure the filename and add unique identifier
    filename = secure_filename(file.filename)
    unique_filename = f"{prefix}_{uuid.uuid4().hex[:8]}_{filename}"
    
    # Save the file to the upload folder
    file_path = os.path.join(upload_folder, unique_filename)
    file.save(file_path)
    
    # Return the relative URL path
    return f"/static/uploads/{unique_filename}"
