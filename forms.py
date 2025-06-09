from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, IntegerField, DateField, SelectField, DecimalField, BooleanField
from wtforms.validators import DataRequired, Email, Length, NumberRange, EqualTo, ValidationError
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
    num_guests = IntegerField('Number of Guests', validators=[DataRequired(), NumberRange(min=1, max=10)])
    special_requests = TextAreaField('Special Requests')
    
    def validate_check_in_date(self, check_in_date):
        if check_in_date.data < date.today():
            raise ValidationError('Check-in date cannot be in the past.')
    
    def validate_check_out_date(self, check_out_date):
        if hasattr(self, 'check_in_date') and self.check_in_date.data:
            if check_out_date.data <= self.check_in_date.data:
                raise ValidationError('Check-out date must be after check-in date.')

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[DataRequired(), Length(max=200)])
    message = TextAreaField('Message', validators=[DataRequired()])

class RoomTypeForm(FlaskForm):
    name = StringField('Room Type Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description')
    price_per_night = DecimalField('Price per Night', validators=[DataRequired(), NumberRange(min=0)])
    max_occupancy = IntegerField('Max Occupancy', validators=[DataRequired(), NumberRange(min=1)])
    amenities = TextAreaField('Amenities (one per line)')
    image_url = StringField('Image URL', validators=[Length(max=255)])
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
