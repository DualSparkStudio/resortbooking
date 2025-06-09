import os
import stripe
from datetime import date, datetime
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import func
from app import app, db, login_manager
from models import User, RoomType, Room, Booking, Facility, Testimonial, ContactMessage
from forms import LoginForm, RegistrationForm, BookingForm, ContactForm, RoomTypeForm, RoomForm, FacilityForm, TestimonialForm
from utils import check_room_availability, calculate_booking_total, create_stripe_checkout_session, send_booking_confirmation_email, send_contact_notification_email

# Configure Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    # Get featured testimonials
    testimonials = Testimonial.query.filter_by(is_featured=True, is_active=True).limit(3).all()
    # Get active facilities
    facilities = Facility.query.filter_by(is_active=True).limit(6).all()
    # Get room types for quick booking
    room_types = RoomType.query.filter_by(is_active=True).limit(3).all()
    
    return render_template('index.html', testimonials=testimonials, facilities=facilities, room_types=room_types)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/rooms')
def rooms():
    room_types = RoomType.query.filter_by(is_active=True).all()
    return render_template('rooms.html', room_types=room_types)

@app.route('/room/<int:room_type_id>')
def room_detail(room_type_id):
    room_type = RoomType.query.get_or_404(room_type_id)
    return render_template('room_detail.html', room_type=room_type)

@app.route('/facilities')
def facilities():
    facilities = Facility.query.filter_by(is_active=True).all()
    return render_template('facilities.html', facilities=facilities)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        contact_message = ContactMessage(
            name=form.name.data,
            email=form.email.data,
            subject=form.subject.data,
            message=form.message.data
        )
        db.session.add(contact_message)
        db.session.commit()
        
        # Send notification email
        send_contact_notification_email(contact_message)
        
        flash('Thank you for your message! We will get back to you soon.', 'success')
        return redirect(url_for('contact'))
    
    return render_template('contact.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone=form.phone.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.created_at.desc()).all()
    return render_template('dashboard.html', bookings=bookings)

@app.route('/book/<int:room_type_id>', methods=['GET', 'POST'])
def book_room(room_type_id):
    room_type = RoomType.query.get_or_404(room_type_id)
    form = BookingForm()
    
    if form.validate_on_submit():
        # Check if user is logged in
        if not current_user.is_authenticated:
            session['booking_data'] = {
                'room_type_id': room_type_id,
                'check_in_date': form.check_in_date.data.isoformat(),
                'check_out_date': form.check_out_date.data.isoformat(),
                'num_guests': form.num_guests.data,
                'special_requests': form.special_requests.data
            }
            flash('Please log in to complete your booking.', 'info')
            return redirect(url_for('login', next=url_for('book_room', room_type_id=room_type_id)))
        
        # Check room availability
        available_rooms = check_room_availability(
            room_type_id, 
            form.check_in_date.data, 
            form.check_out_date.data
        )
        
        if not available_rooms:
            flash('Sorry, no rooms are available for the selected dates.', 'warning')
            return render_template('booking.html', form=form, room_type=room_type)
        
        # Calculate total cost
        total_amount = calculate_booking_total(room_type, form.check_in_date.data, form.check_out_date.data)
        
        # Create booking
        booking = Booking(
            user_id=current_user.id,
            room_id=available_rooms[0].id,  # Assign first available room
            check_in_date=form.check_in_date.data,
            check_out_date=form.check_out_date.data,
            num_guests=form.num_guests.data,
            total_amount=total_amount,
            special_requests=form.special_requests.data
        )
        db.session.add(booking)
        db.session.commit()
        
        # Create Stripe checkout session
        stripe_session = create_stripe_checkout_session(booking)
        if stripe_session:
            return redirect(stripe_session.url, code=303)
        else:
            flash('There was an error processing your payment. Please try again.', 'danger')
            db.session.delete(booking)
            db.session.commit()
    
    # Handle returning from login with booking data
    if not current_user.is_authenticated and 'booking_data' in session:
        booking_data = session.pop('booking_data')
        if booking_data['room_type_id'] == room_type_id:
            form.check_in_date.data = datetime.fromisoformat(booking_data['check_in_date']).date()
            form.check_out_date.data = datetime.fromisoformat(booking_data['check_out_date']).date()
            form.num_guests.data = booking_data['num_guests']
            form.special_requests.data = booking_data['special_requests']
    
    return render_template('booking.html', form=form, room_type=room_type)

@app.route('/booking-success')
def booking_success():
    session_id = request.args.get('session_id')
    if not session_id:
        flash('Invalid booking session.', 'danger')
        return redirect(url_for('index'))
    
    try:
        # Retrieve the session from Stripe
        stripe_session = stripe.checkout.Session.retrieve(session_id)
        
        # Find the booking
        booking = Booking.query.filter_by(stripe_session_id=session_id).first()
        if not booking:
            flash('Booking not found.', 'danger')
            return redirect(url_for('index'))
        
        # Update booking status
        if stripe_session.payment_status == 'paid':
            booking.payment_status = 'paid'
            booking.booking_status = 'confirmed'
            db.session.commit()
            
            # Send confirmation email
            send_booking_confirmation_email(booking)
            
            return render_template('booking_confirmation.html', booking=booking)
        else:
            flash('Payment was not completed successfully.', 'warning')
            return redirect(url_for('dashboard'))
            
    except Exception as e:
        app.logger.error(f"Error processing booking success: {str(e)}")
        flash('There was an error processing your booking.', 'danger')
        return redirect(url_for('index'))

@app.route('/booking-cancel')
def booking_cancel():
    flash('Your booking was cancelled. You can try again anytime.', 'info')
    return render_template('cancel.html')

@app.route('/cancel-booking/<int:booking_id>')
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    # Check if user owns this booking
    if booking.user_id != current_user.id:
        flash('You can only cancel your own bookings.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Check if booking can be cancelled
    if booking.booking_status in ['cancelled', 'completed']:
        flash('This booking cannot be cancelled.', 'warning')
        return redirect(url_for('dashboard'))
    
    # Cancel the booking
    booking.booking_status = 'cancelled'
    db.session.commit()
    
    flash('Your booking has been cancelled.', 'success')
    return redirect(url_for('dashboard'))

# Admin Routes
@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    # Get statistics
    stats = {
        'total_bookings': Booking.query.count(),
        'total_users': User.query.count(),
        'total_rooms': Room.query.count(),
        'pending_bookings': Booking.query.filter_by(booking_status='pending').count(),
        'confirmed_bookings': Booking.query.filter_by(booking_status='confirmed').count(),
        'recent_bookings': Booking.query.order_by(Booking.created_at.desc()).limit(5).all()
    }
    
    return render_template('admin/dashboard.html', stats=stats)

@app.route('/admin/rooms')
@login_required
def admin_rooms():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    room_types = RoomType.query.all()
    rooms = Room.query.all()
    return render_template('admin/rooms.html', room_types=room_types, rooms=rooms)

@app.route('/admin/bookings')
@login_required
def admin_bookings():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    return render_template('admin/bookings.html', bookings=bookings)

@app.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/room-types')
@login_required
def admin_room_types():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    room_types = RoomType.query.all()
    return render_template('admin/room_types.html', room_types=room_types)

@app.route('/admin/room-types/add', methods=['GET', 'POST'])
@login_required
def admin_add_room_type():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    form = RoomTypeForm()
    if form.validate_on_submit():
        room_type = RoomType(
            name=form.name.data,
            description=form.description.data,
            price_per_night=form.price_per_night.data,
            max_occupancy=form.max_occupancy.data,
            amenities=form.amenities.data,
            image_url=form.image_url.data,
            is_active=form.is_active.data
        )
        db.session.add(room_type)
        db.session.commit()
        flash('Room type added successfully!', 'success')
        return redirect(url_for('admin_room_types'))
    
    return render_template('admin/room_type_form.html', form=form, title='Add Room Type')

@app.route('/admin/room-types/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_edit_room_type(id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    room_type = RoomType.query.get_or_404(id)
    form = RoomTypeForm(obj=room_type)
    
    if form.validate_on_submit():
        form.populate_obj(room_type)
        db.session.commit()
        flash('Room type updated successfully!', 'success')
        return redirect(url_for('admin_room_types'))
    
    return render_template('admin/room_type_form.html', form=form, room_type=room_type, title='Edit Room Type')

@app.route('/admin/rooms/add', methods=['GET', 'POST'])
@login_required
def admin_add_room():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    form = RoomForm()
    if form.validate_on_submit():
        room = Room(
            room_number=form.room_number.data,
            room_type_id=form.room_type_id.data,
            floor=form.floor.data,
            is_available=form.is_available.data
        )
        db.session.add(room)
        db.session.commit()
        flash('Room added successfully!', 'success')
        return redirect(url_for('admin_rooms'))
    
    return render_template('admin/room_form.html', form=form, title='Add Room')

@app.route('/admin/rooms/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_edit_room(id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    room = Room.query.get_or_404(id)
    form = RoomForm(obj=room)
    
    if form.validate_on_submit():
        form.populate_obj(room)
        db.session.commit()
        flash('Room updated successfully!', 'success')
        return redirect(url_for('admin_rooms'))
    
    return render_template('admin/room_form.html', form=form, room=room, title='Edit Room')

@app.route('/admin/facilities')
@login_required
def admin_facilities():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    facilities = Facility.query.all()
    return render_template('admin/facilities.html', facilities=facilities)

@app.route('/admin/facilities/add', methods=['GET', 'POST'])
@login_required
def admin_add_facility():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    form = FacilityForm()
    if form.validate_on_submit():
        facility = Facility(
            name=form.name.data,
            description=form.description.data,
            icon=form.icon.data,
            is_active=form.is_active.data
        )
        db.session.add(facility)
        db.session.commit()
        flash('Facility added successfully!', 'success')
        return redirect(url_for('admin_facilities'))
    
    return render_template('admin/facility_form.html', form=form, title='Add Facility')

@app.route('/admin/facilities/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_edit_facility(id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    facility = Facility.query.get_or_404(id)
    form = FacilityForm(obj=facility)
    
    if form.validate_on_submit():
        form.populate_obj(facility)
        db.session.commit()
        flash('Facility updated successfully!', 'success')
        return redirect(url_for('admin_facilities'))
    
    return render_template('admin/facility_form.html', form=form, facility=facility, title='Edit Facility')

@app.route('/room-calendar/<int:room_type_id>')
def room_calendar(room_type_id):
    room_type = RoomType.query.get_or_404(room_type_id)
    
    # Get all bookings for this room type in the next 3 months
    from datetime import datetime, timedelta
    start_date = datetime.now().date()
    end_date = start_date + timedelta(days=90)
    
    bookings = db.session.query(Booking).join(Room).filter(
        Room.room_type_id == room_type_id,
        Booking.check_in_date <= end_date,
        Booking.check_out_date >= start_date,
        Booking.booking_status.in_(['confirmed', 'pending'])
    ).all()
    
    # Convert bookings to calendar format
    calendar_data = []
    for booking in bookings:
        calendar_data.append({
            'title': f'Room {booking.room.room_number} - {booking.user.get_full_name()}',
            'start': booking.check_in_date.isoformat(),
            'end': booking.check_out_date.isoformat(),
            'color': '#38a169' if booking.booking_status == 'confirmed' else '#ed8936',
            'room_number': booking.room.room_number,
            'guest_name': booking.user.get_full_name(),
            'status': booking.booking_status
        })
    
    return render_template('room_calendar.html', room_type=room_type, calendar_data=calendar_data)

@app.route('/create-admin-user')
def create_admin_user():
    # Check if admin already exists
    admin_user = User.query.filter_by(username='admin').first()
    if admin_user:
        return "Admin user already exists"
    
    # Create admin user
    admin = User(
        username='admin',
        email='admin@luxuryresort.com',
        first_name='Resort',
        last_name='Administrator',
        phone='+1-555-0123'
    )
    admin.is_admin = True
    admin.set_password('admin123')  # Change this password after first login
    
    db.session.add(admin)
    db.session.commit()
    
    return "Admin user created successfully! Username: admin, Password: admin123"

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# Context processors
@app.context_processor
def utility_processor():
    def format_currency(amount):
        return f"${amount:,.2f}"
    
    def get_star_rating(rating):
        stars = []
        for i in range(1, 6):
            if i <= rating:
                stars.append('<i class="fas fa-star text-warning"></i>')
            else:
                stars.append('<i class="far fa-star text-muted"></i>')
        return ' '.join(stars)
    
    return dict(format_currency=format_currency, get_star_rating=get_star_rating)
