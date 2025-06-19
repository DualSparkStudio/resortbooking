import os
import stripe
from datetime import date, datetime, timedelta
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import joinedload
from app import app, db, login_manager
from models import User, RoomType, Room, Booking, Facility, Testimonial, ContactMessage, ResortClosure, CalendarSettings, RoomTypeImage
from forms import LoginForm, RegistrationForm, BookingForm, ContactForm, RoomTypeForm, RoomForm, FacilityForm, TestimonialForm, ResortClosureForm, CalendarSettingsForm, GuestDetailsForm
from utils import check_room_availability, calculate_booking_total, create_stripe_checkout_session, send_booking_confirmation_email, send_contact_notification_email

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
        
        # Get mail settings from environment variables for now
        mail_settings = {
            'MAIL_SERVER': os.environ.get('MAIL_SERVER'),
            'MAIL_PORT': int(os.environ.get('MAIL_PORT', 587)),
            'MAIL_USE_TLS': os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1'],
            'MAIL_USERNAME': os.environ.get('MAIL_USERNAME'),
            'MAIL_PASSWORD': os.environ.get('MAIL_PASSWORD'),
            'MAIL_DEFAULT_SENDER': os.environ.get('MAIL_DEFAULT_SENDER')
        }
        admin_email = os.environ.get('ADMIN_EMAIL', 'admin@resort.com')
        
        # Send notification email
        send_contact_notification_email(contact_message, admin_email, mail_settings)
        
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
    
    # Pre-fill form with URL parameters if provided
    if request.method == 'GET':
        check_in = request.args.get('check_in')
        check_out = request.args.get('check_out')
        if check_in:
            try:
                form.check_in_date.data = datetime.strptime(check_in, '%Y-%m-%d').date()
            except ValueError:
                pass
        if check_out:
            try:
                form.check_out_date.data = datetime.strptime(check_out, '%Y-%m-%d').date()
            except ValueError:
                pass
    
    if form.validate_on_submit():
        # Save booking info in session and redirect to guest details page
        session['pending_booking'] = {
                'room_type_id': room_type_id,
                'check_in_date': form.check_in_date.data.isoformat(),
                'check_out_date': form.check_out_date.data.isoformat(),
                'check_in_time': form.check_in_time.data,
                'check_out_time': form.check_out_time.data,
                'num_guests': form.num_guests.data,
        }
        return redirect(url_for('guest_details'))
    elif request.method == 'POST':
        flash('Please correct the errors in the form below.', 'danger')
    
    return render_template('booking.html', form=form, room_type=room_type)

@app.route('/guest-details', methods=['GET', 'POST'])
def guest_details():
    pending = session.get('pending_booking')
    if not pending:
        flash('Please select your stay details first.', 'warning')
        return redirect(url_for('index'))
    room_type = RoomType.query.get_or_404(pending['room_type_id'])
    
    # Calculate nights and total for template display
    check_in_date = datetime.fromisoformat(pending['check_in_date']).date()
    check_out_date = datetime.fromisoformat(pending['check_out_date']).date()
    nights = (check_out_date - check_in_date).days
    total_amount = calculate_booking_total(room_type, check_in_date, check_out_date)
    
    form = GuestDetailsForm()
    if form.validate_on_submit():
        # Check room availability again
        available_rooms = check_room_availability(
            room_type.id,
            datetime.fromisoformat(pending['check_in_date']).date(),
            datetime.fromisoformat(pending['check_out_date']).date()
        )
        if not available_rooms:
            flash('Sorry, no rooms are available for the selected dates.', 'warning')
            return redirect(url_for('book_room', room_type_id=room_type.id))
        total_amount = calculate_booking_total(room_type, datetime.fromisoformat(pending['check_in_date']).date(), datetime.fromisoformat(pending['check_out_date']).date())
        booking = Booking(
            user_id=None,
            room_id=available_rooms[0].id,
            check_in_date=datetime.fromisoformat(pending['check_in_date']).date(),
            check_out_date=datetime.fromisoformat(pending['check_out_date']).date(),
            check_in_time=pending['check_in_time'],
            check_out_time=pending['check_out_time'],
            num_guests=pending['num_guests'],
            total_amount=total_amount,
            special_requests=form.special_requests.data,
            booking_status='confirmed',
            payment_status='paid',
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            phone=form.phone.data
        )
        db.session.add(booking)
        db.session.commit()
        # Send confirmation email
        mail_settings = {
            'MAIL_SERVER': os.environ.get('MAIL_SERVER'),
            'MAIL_PORT': int(os.environ.get('MAIL_PORT', 587)),
            'MAIL_USE_TLS': os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1'],
            'MAIL_USERNAME': os.environ.get('MAIL_USERNAME'),
            'MAIL_PASSWORD': os.environ.get('MAIL_PASSWORD'),
            'MAIL_DEFAULT_SENDER': os.environ.get('MAIL_DEFAULT_SENDER')
        }
        app_domain = os.environ.get('REPLIT_DEV_DOMAIN') or os.environ.get('REPLIT_DOMAINS', '').split(',')[0] or 'localhost:5000'
        if not app_domain.startswith('http'):
            if 'localhost' in app_domain or '127.0.0.1' in app_domain:
                app_domain = f'http://{app_domain}'
            else:
                app_domain = f'https://{app_domain}'
        send_booking_confirmation_email(booking, mail_settings, app_domain)
        session.pop('pending_booking', None)
        flash('Your booking has been confirmed! A confirmation email has been sent.', 'success')
        return redirect(url_for('booking_success_fallback', booking_id=booking.id))
    elif request.method == 'POST':
        flash('Please correct the errors in the form below.', 'danger')
    return render_template('guest_details.html', form=form, room_type=room_type, pending=pending, nights=nights, total_amount=total_amount)

@app.route('/booking-success-fallback/<int:booking_id>')
def booking_success_fallback(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    # For guest bookings (user_id is None), allow access
    # For user bookings, ensure user can only view their own booking
    if booking.user_id is not None:
        if not current_user.is_authenticated or booking.user_id != current_user.id:
            flash('Access denied.', 'danger')
            return redirect(url_for('index'))
    
    return render_template('booking_confirmation.html', booking=booking)

@app.route('/booking-success')
def booking_success():
    session_id = request.args.get('session_id')
    if not session_id:
        flash('Invalid booking session.', 'danger')
        return redirect(url_for('index'))
    
    try:
        # Find the booking
        booking = Booking.query.filter_by(stripe_session_id=session_id).first()
        if not booking:
            flash('Booking not found.', 'danger')
            return redirect(url_for('index'))

        # Get mail settings and app domain from environment variables for now
        mail_settings = {
            'MAIL_SERVER': os.environ.get('MAIL_SERVER'),
            'MAIL_PORT': int(os.environ.get('MAIL_PORT', 587)),
            'MAIL_USE_TLS': os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1'],
            'MAIL_USERNAME': os.environ.get('MAIL_USERNAME'),
            'MAIL_PASSWORD': os.environ.get('MAIL_PASSWORD'),
            'MAIL_DEFAULT_SENDER': os.environ.get('MAIL_DEFAULT_SENDER')
        }
        app_domain = os.environ.get('REPLIT_DEV_DOMAIN') or os.environ.get('REPLIT_DOMAINS', '').split(',')[0] or 'localhost:5000'
        if not app_domain.startswith('http'):
            if 'localhost' in app_domain or '127.0.0.1' in app_domain:
                app_domain = f'http://{app_domain}'
            else:
                app_domain = f'https://{app_domain}'
        
        # Retrieve the session from Stripe
        # We need the stripe secret key for this
        stripe_secret_key = os.environ.get('STRIPE_SECRET_KEY')
        if not stripe_secret_key:
            current_app.logger.error("Stripe Secret Key not configured for retrieving session.")
            flash('Payment verification failed due to configuration error.', 'danger')
            return redirect(url_for('index'))
        stripe.api_key = stripe_secret_key

        stripe_session = stripe.checkout.Session.retrieve(session_id)
        
        # Update booking status
        if stripe_session.payment_status == 'paid':
            booking.payment_status = 'paid'
            booking.booking_status = 'confirmed'
            db.session.commit()
            
            # Send confirmation email
            send_booking_confirmation_email(booking, mail_settings, app_domain)
            
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
    
    # Handle export request
    if request.args.get('export') == 'true':
        return export_bookings()
    
    # Handle filters
    status_filter = request.args.get('status')
    payment_filter = request.args.get('payment_status')
    
    query = Booking.query
    
    if status_filter:
        query = query.filter(Booking.booking_status == status_filter)
    
    if payment_filter:
        query = query.filter(Booking.payment_status == payment_filter)
    
    bookings = query.order_by(Booking.created_at.desc()).all()
    return render_template('admin/bookings.html', bookings=bookings)

@app.route('/admin/bookings/confirm/<int:booking_id>', methods=['POST'])
@login_required
def admin_confirm_booking(booking_id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    booking = Booking.query.get_or_404(booking_id)
    booking.booking_status = 'confirmed'
    booking.payment_status = 'paid'
    db.session.commit()
    
    flash(f'Booking #{booking.id} has been confirmed.', 'success')
    return redirect(url_for('admin_bookings'))

@app.route('/admin/bookings/cancel/<int:booking_id>', methods=['POST'])
@login_required
def admin_cancel_booking(booking_id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    booking = Booking.query.get_or_404(booking_id)
    booking.booking_status = 'cancelled'
    db.session.commit()
    
    flash(f'Booking #{booking.id} has been cancelled.', 'success')
    return redirect(url_for('admin_bookings'))

@app.route('/admin/bookings/complete/<int:booking_id>', methods=['POST'])
@login_required
def admin_complete_booking(booking_id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    booking = Booking.query.get_or_404(booking_id)
    booking.booking_status = 'completed'
    db.session.commit()
    
    flash(f'Booking #{booking.id} has been marked as completed.', 'success')
    return redirect(url_for('admin_bookings'))

def export_bookings():
    """Export bookings to CSV"""
    import csv
    from io import StringIO
    from flask import make_response
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Booking ID', 'Guest Name', 'Email', 'Room Type', 'Room Number',
        'Check-in', 'Check-out', 'Guests', 'Total Amount', 'Booking Status',
        'Payment Status', 'Created At'
    ])
    
    # Write data
    bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    for booking in bookings:
        writer.writerow([
            booking.id,
            booking.user.get_full_name(),
            booking.user.email,
            booking.room.room_type.name,
            booking.room.room_number,
            booking.check_in_date.strftime('%Y-%m-%d'),
            booking.check_out_date.strftime('%Y-%m-%d'),
            booking.num_guests,
            float(booking.total_amount),
            booking.booking_status,
            booking.payment_status,
            booking.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=bookings_export.csv'
    
    return response

@app.route('/admin/bookings/bulk-action', methods=['POST'])
@login_required
def admin_bulk_booking_action():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    action = request.form.get('action')
    booking_ids = request.form.getlist('booking_ids')
    
    if not booking_ids:
        flash('No bookings selected.', 'warning')
        return redirect(url_for('admin_bookings'))
    
    success_count = 0
    
    for booking_id in booking_ids:
        booking = Booking.query.get(booking_id)
        if booking:
            if action == 'bulk_confirm':
                booking.booking_status = 'confirmed'
                booking.payment_status = 'paid'
                success_count += 1
            elif action == 'bulk_cancel':
                booking.booking_status = 'cancelled'
                success_count += 1
            elif action == 'bulk_complete':
                booking.booking_status = 'completed'
                success_count += 1
    
    if success_count > 0:
        db.session.commit()
        action_name = action.replace('bulk_', '').replace('_', ' ').title()
        flash(f'{success_count} booking(s) {action_name.lower()}ed successfully.', 'success')
    else:
        flash('No bookings were updated.', 'warning')
    
    return redirect(url_for('admin_bookings'))

@app.route('/admin/users', methods=['GET', 'POST'])
@login_required
def admin_users():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    # Handle POST requests for adding new users or bulk actions
    if request.method == 'POST':
        # Check if this is a bulk action
        action = request.form.get('action')
        if action and action.startswith('bulk_'):
            user_ids = request.form.getlist('user_ids')
            if not user_ids:
                flash('No users selected.', 'warning')
                return redirect(url_for('admin_users'))
            
            # Handle different bulk actions
            if action == 'bulk_delete':
                success_count = 0
                failed_count = 0
                failed_users = []
                
                for user_id in user_ids:
                    try:
                        user_id = int(user_id)
                        # Don't delete current user
                        if user_id == current_user.id:
                            continue
                        
                        user = User.query.get(user_id)
                        if user:
                            # Check if user has active bookings
                            active_bookings = [b for b in user.bookings if b.booking_status in ['confirmed', 'pending']]
                            
                            if active_bookings:
                                failed_count += 1
                                failed_users.append(f"{user.get_full_name()} ({len(active_bookings)} active bookings)")
                            else:
                                try:
                                    db.session.delete(user)
                                    success_count += 1
                                except Exception as e:
                                    failed_count += 1
                                    failed_users.append(f"{user.get_full_name()} (database error)")
                    except (ValueError, TypeError):
                        continue
                
                if success_count > 0:
                    db.session.commit()
                    flash(f'{success_count} user(s) deleted successfully.', 'success')
                
                if failed_count > 0:
                    flash(f'{failed_count} user(s) could not be deleted: {", ".join(failed_users)}', 'warning')
                
                if success_count == 0 and failed_count == 0:
                    flash('No users were selected for deletion.', 'warning')
                
                return redirect(url_for('admin_users'))
            
            # Handle bulk export
            elif action == 'bulk_export':
                # Create CSV export for selected users
                import csv
                from io import StringIO
                from flask import make_response
                
                selected_users = []
                for user_id in user_ids:
                    try:
                        user_id = int(user_id)
                        user = User.query.get(user_id)
                        if user:
                            selected_users.append(user)
                    except (ValueError, TypeError):
                        continue
                
                if not selected_users:
                    flash('No valid users selected for export.', 'warning')
                    return redirect(url_for('admin_users'))
                
                output = StringIO()
                writer = csv.writer(output)
                
                # Write header
                writer.writerow(['ID', 'Username', 'First Name', 'Last Name', 'Email', 'Phone', 'Is Admin', 'Created At', 'Total Bookings'])
                
                # Write user data
                for user in selected_users:
                    writer.writerow([
                        user.id,
                        user.username,
                        user.first_name,
                        user.last_name,
                        user.email,
                        user.phone or '',
                        'Yes' if user.is_admin else 'No',
                        user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                        len(user.bookings)
                    ])
                
                # Create response
                output.seek(0)
                response = make_response(output.getvalue())
                response.headers['Content-Type'] = 'text/csv'
                response.headers['Content-Disposition'] = f'attachment; filename=selected_users_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
                
                return response
        
        # If not a bulk action, handle adding new user
        username = request.form.get('username')
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone = request.form.get('phone')
        password = request.form.get('password')
        is_admin = 'is_admin' in request.form
        
        # Validate form data
        if not username or not email or not first_name or not last_name or not password:
            flash('All required fields must be filled.', 'danger')
            return redirect(url_for('admin_users'))
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return redirect(url_for('admin_users'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists.', 'danger')
            return redirect(url_for('admin_users'))
        
        # Create new user
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            is_admin=is_admin
        )
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('User added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding user: {str(e)}', 'danger')
        
        return redirect(url_for('admin_users'))
    
    # Handle GET requests with search/filter parameters
    search_query = request.args.get('search', '')
    user_type = request.args.get('user_type', '')
    date_filter = request.args.get('date_filter', '')
    
    # Start with base query
    query = User.query
    
    # Apply filters
    if search_query:
        query = query.filter(
            or_(
                User.username.ilike(f'%{search_query}%'),
                User.email.ilike(f'%{search_query}%'),
                User.first_name.ilike(f'%{search_query}%'),
                User.last_name.ilike(f'%{search_query}%')
            )
        )
    
    if user_type == 'admin':
        query = query.filter_by(is_admin=True)
    elif user_type == 'regular':
        query = query.filter_by(is_admin=False)
    
    if date_filter:
        today = date.today()
        if date_filter == 'today':
            query = query.filter(func.date(User.created_at) == today)
        elif date_filter == 'week':
            start_of_week = today - timedelta(days=today.weekday())
            query = query.filter(func.date(User.created_at) >= start_of_week)
        elif date_filter == 'month':
            start_of_month = date(today.year, today.month, 1)
            query = query.filter(func.date(User.created_at) >= start_of_month)
    
    # Get users with applied filters and eager load bookings
    users = query.options(
        joinedload(User.bookings).joinedload(Booking.room).joinedload(Room.room_type)
    ).order_by(User.created_at.desc()).all()
    
    # Handle export request
    if request.args.get('export') == 'true':
        # Create CSV export
        import csv
        from io import StringIO
        from flask import make_response
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['ID', 'Username', 'First Name', 'Last Name', 'Email', 'Phone', 'Is Admin', 'Created At', 'Total Bookings'])
        
        # Write user data
        for user in users:
            writer.writerow([
                user.id,
                user.username,
                user.first_name,
                user.last_name,
                user.email,
                user.phone or '',
                'Yes' if user.is_admin else 'No',
                user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                len(user.bookings)
            ])
        
        # Create response
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=users_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return response
    
    return render_template('admin/users.html', users=users)

@app.route('/admin/users/edit/<int:id>', methods=['POST'])
@login_required
def admin_edit_user(id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(id)
    
    # Get form data
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    username = request.form.get('username')
    phone = request.form.get('phone')
    is_admin = 'is_admin' in request.form
    
    # Validate required fields
    if not first_name or not last_name or not email or not username:
        flash('All required fields must be filled.', 'danger')
        return redirect(url_for('admin_users'))
    
    # Check if email already exists for another user
    existing_email_user = User.query.filter(User.email == email, User.id != id).first()
    if existing_email_user:
        flash('Email already exists for another user.', 'danger')
        return redirect(url_for('admin_users'))
    
    # Check if username already exists for another user
    existing_username_user = User.query.filter(User.username == username, User.id != id).first()
    if existing_username_user:
        flash('Username already exists for another user.', 'danger')
        return redirect(url_for('admin_users'))
    
    # Update user details
    user.first_name = first_name
    user.last_name = last_name
    user.email = email
    user.username = username
    user.phone = phone
    user.is_admin = is_admin
    
    # Update password if provided
    new_password = request.form.get('password')
    if new_password and len(new_password) >= 6:
        user.set_password(new_password)
    
    try:
        db.session.commit()
        flash('User updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating user: {str(e)}', 'danger')
    
    return redirect(url_for('admin_users'))

@app.route('/admin/users/delete/<int:id>', methods=['POST'])
@login_required
def admin_delete_user(id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    # Don't allow deleting self
    if id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin_users'))
    
    user = User.query.get_or_404(id)
    
    # Check if user has active bookings (confirmed or pending)
    active_bookings = [b for b in user.bookings if b.booking_status in ['confirmed', 'pending']]
    
    if active_bookings:
        flash(f'Cannot delete user "{user.get_full_name()}" because they have {len(active_bookings)} active booking(s). Please cancel or complete their bookings first.', 'danger')
        return redirect(url_for('admin_users'))
    
    # If user has completed or cancelled bookings, we can still delete them
    # but we need to handle the foreign key constraint
    try:
        # Delete the user (this will cascade to bookings if configured properly)
        db.session.delete(user)
        db.session.commit()
        flash(f'User "{user.get_full_name()}" deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        # If cascade delete fails, provide more specific error
        if 'foreign key constraint' in str(e).lower():
            flash(f'Cannot delete user "{user.get_full_name()}" due to database constraints. Please contact system administrator.', 'danger')
        else:
            flash(f'Error deleting user: {str(e)}', 'danger')
    
    return redirect(url_for('admin_users'))

@app.route('/admin/users/toggle-admin/<int:id>', methods=['POST'])
@login_required
def admin_toggle_user_admin(id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    # Don't allow removing admin from self
    if id == current_user.id:
        flash('You cannot change your own admin status.', 'danger')
        return redirect(url_for('admin_users'))
    
    user = User.query.get_or_404(id)
    user.is_admin = not user.is_admin
    db.session.commit()
    
    status = 'granted' if user.is_admin else 'revoked'
    flash(f'Admin privileges {status} for {user.get_full_name()}.', 'success')
    return redirect(url_for('admin_users'))

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
    
    if request.method == 'POST':
        # Handle our custom form data from JavaScript
        try:
            # Basic room type data
            room_type = RoomType(
                name=request.form.get('name'),
                description=request.form.get('description'),
                price_per_night=float(request.form.get('price_per_night', 0)),
                max_occupancy=int(request.form.get('max_occupancy', 1)),
                amenities=request.form.get('amenities'),
                image_url=request.form.get('image_url', ''),
                is_active=request.form.get('is_active') == 'on'
            )
            db.session.add(room_type)
            db.session.flush()  # Get the ID without committing
            
            # Handle multiple images
            from models import RoomTypeImage
            image_urls = request.form.getlist('image_urls[]')
            uploaded_files = request.files.getlist('images')
            
            # Process URL images
            for i, url in enumerate(image_urls):
                if url.strip():
                    room_image = RoomTypeImage(
                        room_type_id=room_type.id,
                        image_url=url.strip(),
                        alt_text=f'{room_type.name} image {i+1}',
                        is_primary=(i == 0),  # First image is primary
                        sort_order=i
                    )
                    db.session.add(room_image)
            
            # Process uploaded files (would need file handling logic here)
            for i, file in enumerate(uploaded_files):
                if file and file.filename:
                    # For now, just save the filename - in production you'd upload to cloud storage
                    # This is a placeholder - implement actual file upload logic
                    filename = f"room_type_{room_type.id}_{i}_{file.filename}"
                    # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    
                    room_image = RoomTypeImage(
                        room_type_id=room_type.id,
                        image_url=f"/static/uploads/{filename}",  # Placeholder path
                        alt_text=f'{room_type.name} image {len(image_urls) + i + 1}',
                        is_primary=(len(image_urls) == 0 and i == 0),  # Primary if no URLs
                        sort_order=len(image_urls) + i
                    )
                    db.session.add(room_image)
            
            db.session.commit()
            return jsonify({'success': True, 'message': 'Room type added successfully!'})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 400
    
    # GET request - return the form page
    return redirect(url_for('admin_rooms'))

@app.route('/admin/room-types/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_edit_room_type(id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    room_type = RoomType.query.get_or_404(id)
    
    if request.method == 'POST':
        # Handle our custom form data from JavaScript
        try:
            # Update basic room type fields
            room_type.name = request.form.get('name')
            room_type.description = request.form.get('description')
            room_type.price_per_night = float(request.form.get('price_per_night', 0))
            room_type.max_occupancy = int(request.form.get('max_occupancy', 1))
            room_type.amenities = request.form.get('amenities')
            room_type.image_url = request.form.get('image_url', '')
            room_type.is_active = request.form.get('is_active') == 'on'
            
            # Handle existing images to keep
            from models import RoomTypeImage
            keep_images = request.form.get('keepImages', '').split(',')
            keep_images = [img.strip() for img in keep_images if img.strip()]
            
            # Delete images that are not in the keep list
            if keep_images:
                RoomTypeImage.query.filter_by(room_type_id=room_type.id)\
                    .filter(~RoomTypeImage.image_url.in_(keep_images)).delete(synchronize_session=False)
            else:
                # Delete all existing images if no keep list
                RoomTypeImage.query.filter_by(room_type_id=room_type.id).delete()
            
            # Add new images from URLs
            new_image_urls = request.form.getlist('new_image_urls[]')
            uploaded_files = request.files.getlist('new_images')
            
            # Get current max sort order
            max_sort_order = 0
            existing_images = RoomTypeImage.query.filter_by(room_type_id=room_type.id).all()
            if existing_images:
                max_sort_order = max(img.sort_order for img in existing_images)
            
            # Process new URL images
            for i, url in enumerate(new_image_urls):
                if url.strip():
                    room_image = RoomTypeImage(
                        room_type_id=room_type.id,
                        image_url=url.strip(),
                        alt_text=f'{room_type.name} image',
                        is_primary=False,  # Don't automatically set as primary
                        sort_order=max_sort_order + i + 1
                    )
                    db.session.add(room_image)
            
            # Process uploaded files
            for i, file in enumerate(uploaded_files):
                if file and file.filename:
                    # For now, just save the filename - in production you'd upload to cloud storage
                    filename = f"room_type_{room_type.id}_{max_sort_order + len(new_image_urls) + i}_{file.filename}"
                    # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    
                    room_image = RoomTypeImage(
                        room_type_id=room_type.id,
                        image_url=f"/static/uploads/{filename}",  # Placeholder path
                        alt_text=f'{room_type.name} image',
                        is_primary=False,  # Don't automatically set as primary
                        sort_order=max_sort_order + len(new_image_urls) + i + 1
                    )
                    db.session.add(room_image)
            
            # Ensure there's at least one primary image
            primary_image = RoomTypeImage.query.filter_by(room_type_id=room_type.id, is_primary=True).first()
            if not primary_image:
                first_image = RoomTypeImage.query.filter_by(room_type_id=room_type.id).first()
                if first_image:
                    first_image.is_primary = True
            
            db.session.commit()
            return jsonify({'success': True, 'message': 'Room type updated successfully!'})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 400
    
    # GET request - redirect to admin rooms page
    return redirect(url_for('admin_rooms'))

@app.route('/admin/room-types/delete/<int:id>', methods=['POST'])
@login_required
def admin_delete_room_type(id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    room_type = RoomType.query.get_or_404(id)
    
    # Check if there are rooms of this type
    if room_type.rooms:
        flash(f'Cannot delete room type "{room_type.name}" because it has {len(room_type.rooms)} rooms associated with it. Delete the rooms first.', 'danger')
        return redirect(url_for('admin_room_types'))
    
    # Check if there are bookings for this room type
    has_bookings = False
    for room in room_type.rooms:
        if room.bookings:
            has_bookings = True
            break
    
    if has_bookings:
        flash(f'Cannot delete room type "{room_type.name}" because it has bookings associated with it.', 'danger')
        return redirect(url_for('admin_room_types'))
    
    try:
        db.session.delete(room_type)
        db.session.commit()
        flash(f'Room type "{room_type.name}" deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting room type: {str(e)}', 'danger')
    
    return redirect(url_for('admin_room_types'))

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

@app.route('/admin/rooms/delete/<int:id>', methods=['POST'])
@login_required
def admin_delete_room(id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    room = Room.query.get_or_404(id)
    
    # Check if there are any bookings for this room
    if Booking.query.filter_by(room_id=id).count() > 0:
        flash('Cannot delete room. There are bookings associated with this room.', 'danger')
        return redirect(url_for('admin_rooms'))
    
    db.session.delete(room)
    db.session.commit()
    flash('Room deleted successfully!', 'success')
    return redirect(url_for('admin_rooms'))

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

@app.route('/admin/facilities/delete/<int:id>', methods=['POST'])
@login_required
def admin_delete_facility(id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    facility = Facility.query.get_or_404(id)
    db.session.delete(facility)
    db.session.commit()
    flash('Facility deleted successfully!', 'success')
    return redirect(url_for('admin_facilities'))

@app.route('/admin/resort-closures')
@login_required
def admin_resort_closures():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    closures = ResortClosure.query.order_by(ResortClosure.start_date.desc()).all()
    return render_template('admin/resort_closures.html', closures=closures)

@app.route('/admin/resort-closures/add', methods=['GET', 'POST'])
@login_required
def admin_add_resort_closure():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    form = ResortClosureForm()
    if form.validate_on_submit():
        closure = ResortClosure(
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            reason=form.reason.data,
            description=form.description.data,
            is_active=form.is_active.data
        )
        db.session.add(closure)
        db.session.commit()
        flash('Resort closure added successfully!', 'success')
        return redirect(url_for('admin_resort_closures'))
    
    return render_template('admin/resort_closure_form.html', form=form, title='Add Resort Closure')

@app.route('/admin/resort-closures/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_edit_resort_closure(id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    closure = ResortClosure.query.get_or_404(id)
    form = ResortClosureForm(obj=closure)
    
    if form.validate_on_submit():
        form.populate_obj(closure)
        db.session.commit()
        flash('Resort closure updated successfully!', 'success')
        return redirect(url_for('admin_resort_closures'))
    
    return render_template('admin/resort_closure_form.html', form=form, closure=closure, title='Edit Resort Closure')

@app.route('/admin/resort-closures/delete/<int:id>', methods=['POST'])
@login_required
def admin_delete_resort_closure(id):
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    closure = ResortClosure.query.get_or_404(id)
    db.session.delete(closure)
    db.session.commit()
    flash('Resort closure deleted successfully!', 'success')
    return redirect(url_for('admin_resort_closures'))

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
        # Handle both user and guest bookings
        if booking.user:
            guest_name = booking.user.get_full_name()
        else:
            guest_name = f"{booking.first_name} {booking.last_name}"
        
        calendar_data.append({
            'title': f'Room {booking.room.room_number} - {guest_name}',
            'start': booking.check_in_date.isoformat(),
            'end': booking.check_out_date.isoformat(),
            'color': '#38a169' if booking.booking_status == 'confirmed' else '#ed8936',
            'room_number': booking.room.room_number,
            'guest_name': guest_name,
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

# New enhanced booking calendar route
@app.route('/booking-calendar/<int:room_type_id>')
def booking_calendar(room_type_id):
    room_type = RoomType.query.get_or_404(room_type_id)
    
    # Get calendar data for the next 6 months
    start_date = datetime.now().date()
    end_date = start_date + timedelta(days=180)
    
    # Get all rooms of this type
    total_rooms = Room.query.filter_by(room_type_id=room_type_id, is_available=True).count()
    
    # Get bookings grouped by date
    bookings = db.session.query(Booking).join(Room).filter(
        Room.room_type_id == room_type_id,
        Booking.check_in_date <= end_date,
        Booking.check_out_date >= start_date,
        Booking.booking_status.in_(['confirmed', 'pending'])
    ).all()
    
    # Get resort closures
    closures = ResortClosure.query.filter(
        ResortClosure.start_date <= end_date,
        ResortClosure.end_date >= start_date,
        ResortClosure.is_active == True
    ).all()
    
    # Convert to calendar format
    calendar_data = []
    
    # Create a dictionary to track occupancy by date
    daily_occupancy = {}
    
    # Calculate daily occupancy
    for booking in bookings:
        current_date = booking.check_in_date
        while current_date < booking.check_out_date:
            if current_date not in daily_occupancy:
                daily_occupancy[current_date] = {
                    'confirmed': 0,
                    'pending': 0
                }
            
            if booking.booking_status == 'confirmed':
                daily_occupancy[current_date]['confirmed'] += 1
            elif booking.booking_status == 'pending':
                daily_occupancy[current_date]['pending'] += 1
            
            current_date += timedelta(days=1)
    
    # Add individual booking events (for display purposes)
    for booking in bookings:
        # Only show confirmed bookings as events to maintain privacy
        if booking.booking_status == 'confirmed':
            calendar_data.append({
                'title': 'Booked',
                'start': booking.check_in_date.isoformat(),
                'end': booking.check_out_date.isoformat(),
                'color': '#c1502e',  # Warm terracotta for booked
                'backgroundColor': 'rgba(193, 80, 46, 0.2)',
                'borderColor': '#c1502e',
                'type': 'booking',
                'room_number': booking.room.room_number,
                'status': booking.booking_status,
                'textColor': '#ffffff'
            })
    
    # Add closures
    for closure in closures:
        calendar_data.append({
            'title': f'Resort Closed - {closure.reason}',
            'start': closure.start_date.isoformat(),
            'end': (closure.end_date + timedelta(days=1)).isoformat(),  # Add 1 day for end date
            'color': '#6c757d',
            'backgroundColor': 'rgba(108, 117, 125, 0.3)',
            'borderColor': '#6c757d',
            'type': 'closure',
            'reason': closure.reason,
            'description': closure.description,
            'textColor': '#ffffff'
        })
    
    return render_template('booking_calendar.html', 
                         room_type=room_type, 
                         calendar_data=calendar_data,
                         total_rooms=total_rooms)

# API endpoint for date information
@app.route('/api/date-info/<int:room_type_id>/<date_str>')
def get_date_info(room_type_id, date_str):
    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
    
    room_type = RoomType.query.get_or_404(room_type_id)
    
    # Check if resort is closed
    closure = ResortClosure.query.filter(
        ResortClosure.start_date <= target_date,
        ResortClosure.end_date >= target_date,
        ResortClosure.is_active == True
    ).first()
    
    if closure:
        return jsonify({
            'resort_closed': True,
            'closure_reason': closure.reason,
            'closure_description': closure.description
        })
    
    # Get room availability for this date
    total_rooms = Room.query.filter_by(room_type_id=room_type_id, is_available=True).count()
    
    booked_rooms = db.session.query(Booking).join(Room).filter(
        Room.room_type_id == room_type_id,
        Booking.check_in_date <= target_date,
        Booking.check_out_date > target_date,
        Booking.booking_status == 'confirmed'
    ).count()
    
    pending_rooms = db.session.query(Booking).join(Room).filter(
        Room.room_type_id == room_type_id,
        Booking.check_in_date <= target_date,
        Booking.check_out_date > target_date,
        Booking.booking_status == 'pending'
    ).count()
    
    available_rooms = total_rooms - booked_rooms - pending_rooms
    
    return jsonify({
        'resort_closed': False,
        'total_rooms': total_rooms,
        'available_rooms': max(0, available_rooms),
        'booked_rooms': booked_rooms,
        'pending_rooms': pending_rooms,
        'price_per_night': float(room_type.price_per_night)
    })

# API endpoint for admin calendar bookings
@app.route('/admin/api/calendar-bookings')
@login_required
def admin_calendar_bookings():
    if not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid date format'}), 400
    
    # Get all bookings within the date range
    bookings = db.session.query(Booking).options(
        joinedload(Booking.room).joinedload(Room.room_type),
        joinedload(Booking.user)
    ).filter(
        Booking.check_in_date <= end_date,
        Booking.check_out_date >= start_date
    ).all()
    
    calendar_events = []
    
    for booking in bookings:
        # Get guest name
        if booking.user:
            guest_name = booking.user.get_full_name()
        else:
            guest_name = f"{booking.first_name} {booking.last_name}"
        
        # Create calendar event
        event = {
            'id': f'booking-{booking.id}',
            'title': f"{guest_name} - {booking.room.room_type.name}",
            'start': booking.check_in_date.isoformat(),
            'end': booking.check_out_date.isoformat(),
            'extendedProps': {
                'booking_id': booking.id,
                'status': booking.booking_status,
                'guest_name': guest_name,
                'room_type': booking.room.room_type.name,
                'room_number': booking.room.room_number,
                'num_guests': booking.num_guests,
                'total_amount': float(booking.total_amount),
                'payment_status': booking.payment_status,
                'special_requests': booking.special_requests
            },
            'backgroundColor': get_status_color(booking.booking_status),
            'borderColor': get_status_color(booking.booking_status),
            'textColor': '#ffffff'
        }
        
        calendar_events.append(event)
    
    return jsonify(calendar_events)

def get_status_color(status):
    """Get color for booking status"""
    colors = {
        'confirmed': '#28a745',
        'pending': '#ffc107', 
        'cancelled': '#dc3545',
        'completed': '#17a2b8'
    }
    return colors.get(status, '#6c757d')

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
