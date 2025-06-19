from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, IntegerField, DateField, SelectField, DecimalField, BooleanField, TimeField, FieldList, FormField
from wtforms.validators import DataRequired, Email, Length, NumberRange, EqualTo, ValidationError, Optional
from models import User, RoomType
from datetime import date, datetime

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[DataRequired()])

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    phone = StringField('Phone Number', validators=[Length(max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please choose a different one.')

class BookingForm(FlaskForm):
    check_in_date = DateField('Check-in Date', validators=[DataRequired()])
    check_out_date = DateField('Check-out Date', validators=[DataRequired()])
    check_in_time = SelectField('Check-in Time', 
                               choices=[('08:00', '8:00 AM'), ('09:00', '9:00 AM'), ('10:00', '10:00 AM'), 
                                        ('11:00', '11:00 AM'), ('12:00', '12:00 PM'), ('13:00', '1:00 PM'),
                                        ('14:00', '2:00 PM'), ('15:00', '3:00 PM'), ('16:00', '4:00 PM'),
                                        ('17:00', '5:00 PM'), ('18:00', '6:00 PM'), ('19:00', '7:00 PM'),
                                        ('20:00', '8:00 PM')],
                               default='14:00')
    check_out_time = SelectField('Check-out Time',
                                choices=[('08:00', '8:00 AM'), ('09:00', '9:00 AM'), ('10:00', '10:00 AM'),
                                         ('11:00', '11:00 AM'), ('12:00', '12:00 PM'), ('13:00', '1:00 PM'),
                                         ('14:00', '2:00 PM')],
                                default='12:00')
    num_guests = IntegerField('Number of Guests', validators=[DataRequired(), NumberRange(min=1, max=10)])
    special_requests = TextAreaField('Special Requests')
    
    def validate_check_in_date(self, check_in_date):
        if check_in_date.data < date.today():
            raise ValidationError('Check-in date cannot be in the past.')
    
    def validate_check_out_date(self, check_out_date):
        if hasattr(self, 'check_in_date') and self.check_in_date.data:
            if check_out_date.data < self.check_in_date.data:
                raise ValidationError('Check-out date cannot be before check-in date.')

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[DataRequired(), Length(max=200)])
    message = TextAreaField('Message', validators=[DataRequired()])

class RoomImageForm(FlaskForm):
    image_url = StringField('Image URL', validators=[DataRequired(), Length(max=500)])
    alt_text = StringField('Alt Text', validators=[Optional(), Length(max=255)])
    is_primary = BooleanField('Primary Image')

class RoomTypeForm(FlaskForm):
    name = StringField('Room Type Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description')
    price_per_night = DecimalField('Price per Night', validators=[DataRequired(), NumberRange(min=0)])
    max_occupancy = IntegerField('Max Occupancy', validators=[DataRequired(), NumberRange(min=1)])
    amenities = TextAreaField('Amenities (one per line)')
    image_url = StringField('Legacy Image URL (optional)', validators=[Optional(), Length(max=255)])
    images = FieldList(FormField(RoomImageForm), min_entries=1, max_entries=10)
    is_active = BooleanField('Active')

class RoomForm(FlaskForm):
    room_number = StringField('Room Number', validators=[DataRequired(), Length(max=20)])
    room_type_id = SelectField('Room Type', coerce=int, validators=[DataRequired()])
    floor = IntegerField('Floor', validators=[NumberRange(min=1)])
    is_available = BooleanField('Available', default=True)
    
    def __init__(self, *args, **kwargs):
        super(RoomForm, self).__init__(*args, **kwargs)
        self.room_type_id.choices = [(rt.id, rt.name) for rt in RoomType.query.filter_by(is_active=True).all()]

class FacilityForm(FlaskForm):
    name = StringField('Facility Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description')
    icon = StringField('Icon Class', validators=[Length(max=50)])
    is_active = BooleanField('Active', default=True)

class TestimonialForm(FlaskForm):
    guest_name = StringField('Guest Name', validators=[DataRequired(), Length(max=100)])
    rating = SelectField('Rating', choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')], coerce=int, validators=[DataRequired()])
    comment = TextAreaField('Comment', validators=[DataRequired()])
    is_featured = BooleanField('Featured')
    is_active = BooleanField('Active', default=True)

class ResortClosureForm(FlaskForm):
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    reason = StringField('Reason', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description')
    is_active = BooleanField('Active', default=True)
    
    def validate_end_date(self, end_date):
        if hasattr(self, 'start_date') and self.start_date.data:
            if end_date.data < self.start_date.data:
                raise ValidationError('End date must be after start date.')

class CalendarSettingsForm(FlaskForm):
    setting_key = StringField('Setting Key', validators=[DataRequired(), Length(max=100)])
    setting_value = TextAreaField('Setting Value', validators=[DataRequired()])
    description = TextAreaField('Description')

class GuestDetailsForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(max=20)])
    special_requests = TextAreaField('Special Requests')
