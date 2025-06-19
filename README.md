# 🏨 Luxury Resort Booking System

A comprehensive full-stack resort booking and management system built with Flask.

## 🚨 Important: GitHub Pages vs Flask Application

### GitHub Pages (This Repository)
- **What it shows**: Static landing page showcasing the project
- **What it can't do**: Run the actual Flask application
- **URL**: `https://yourusername.github.io/resort-booking`

### Flask Application (Requires Deployment)
- **What it does**: Full booking system with database, payments, admin panel
- **Where to deploy**: Render.com, Railway, Heroku, PythonAnywhere
- **URL**: `https://your-app.onrender.com` (after deployment)

## 🎯 Quick Start

### Option 1: View the Static Demo (GitHub Pages)
1. Visit the GitHub Pages URL to see the project showcase
2. This shows what the project does but doesn't run the actual app

### Option 2: Deploy the Full Application
1. Follow the [Deployment Guide](deployment-guide.md)
2. Deploy to Render.com (recommended free option)
3. Get your full Flask app running with database and payments

## 🏗️ Project Architecture

### Backend
- **Framework**: Flask 3.1.1
- **Database**: SQLAlchemy with PostgreSQL/SQLite
- **Authentication**: Flask-Login with BCrypt
- **Payments**: Stripe integration
- **Email**: Flask-Mail

### Frontend
- **Styling**: Bootstrap 5 + custom luxury theme
- **JavaScript**: Vanilla JS with jQuery
- **Design**: Responsive, mobile-first approach

## 📦 Features

### 🌟 Public Website
- Stunning hero carousel with resort imagery
- Room showcases with image galleries
- Facilities and amenities display
- Contact forms with email notifications

### 📅 Booking System
- Real-time room availability checking
- Multi-step booking process
- Guest and registered user support
- Stripe payment integration
- Email confirmations

### 👨‍💼 Admin Dashboard
- Comprehensive booking management
- Room and room type administration
- User management system
- Resort closure scheduling
- Analytics and reporting

### 💳 Payment Processing
- Secure Stripe checkout
- Payment status tracking
- Automated booking confirmations
- Invoice generation ready

## 🚀 Deployment Options

### 1. Render.com (Recommended - FREE)
```bash
# 1. Push to GitHub
git add .
git commit -m "Deploy to Render"
git push origin main

# 2. Connect repo on render.com
# 3. Set environment variables
# 4. Deploy automatically
```

### 2. Railway.app
- Connect GitHub repository
- Add PostgreSQL plugin
- Set environment variables
- Deploy

### 3. Heroku
- Add Heroku Postgres add-on
- Configure environment variables
- Use included Procfile

### 4. PythonAnywhere
- Upload code files
- Configure WSGI
- Set up MySQL database

## ⚙️ Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/db_name

# Security
SESSION_SECRET=your-32-character-secret-key

# Stripe Payments
STRIPE_SECRET_KEY=sk_test_or_live_key
STRIPE_PUBLISHABLE_KEY=pk_test_or_live_key

# Email (Gmail example)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# Admin
ADMIN_EMAIL=admin@yourresort.com
```

## 🛠️ Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/resort-booking.git
   cd resort-booking
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   - Create `.env` file with required variables
   - See `.env.example` for reference

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the app**
   - Open `http://localhost:5000`
   - Create admin user at `/create-admin-user`

## 📁 Project Structure

```
resort-booking/
├── app.py                 # Flask application factory
├── models.py              # Database models
├── routes.py              # Application routes
├── forms.py               # WTForms definitions
├── utils.py               # Utility functions
├── requirements.txt       # Python dependencies
├── render.yaml            # Render.com deployment config
├── Procfile              # Heroku deployment config
├── _config.yml           # GitHub Pages Jekyll config
├── index.html            # Static landing page for GitHub Pages
├── deployment-guide.md   # Detailed deployment instructions
├── templates/            # Jinja2 templates
├── static/               # CSS, JS, images
├── instance/             # SQLite database (development)
└── migrations/           # Database migrations
```

## 🎨 Design Features

- **Luxury Theme**: Calming blues, sage greens, warm terracotta
- **Typography**: Playfair Display + Lato font combination
- **Responsive**: Mobile-first Bootstrap 5 implementation
- **Animations**: Smooth transitions and hover effects
- **UX**: Intuitive booking flow and admin interface

## 🔒 Security Features

- CSRF protection
- Password hashing with BCrypt
- SQL injection prevention
- Secure session management
- Input validation and sanitization

## 📊 Database Schema

- **Users**: Authentication and profiles
- **RoomTypes**: Room categories with images
- **Rooms**: Individual room inventory
- **Bookings**: Reservation management
- **Facilities**: Resort amenities
- **Testimonials**: Guest reviews
- **ContactMessages**: Inquiry management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For deployment help or questions:
- Read the [Deployment Guide](deployment-guide.md)
- Check the GitHub Issues
- Contact: your-email@example.com

---

**Note**: This Flask application requires a Python server environment and cannot run on GitHub Pages alone. Use the included deployment configurations for proper hosting. 