#!/usr/bin/env python3
"""
Resort Booking System - Server Startup Script
This script properly sets environment variables and starts the Flask server.
"""

import os
import sys

def setup_environment():
    """Set up required environment variables"""
    print("🔧 Setting up environment variables...")
    
    # Environment variables are now loaded via .env file in app.py
    # No need to set them explicitly here, but keep function for future expansion if needed.
    print("✅ Environment variables configuration deferred to .env and app.py")

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'flask', 'flask_sqlalchemy', 'flask_login', 
        'flask_mail', 'flask_wtf', 'wtforms', 'python-dotenv', 'stripe', 'gunicorn', 'sqlalchemy', 'bcrypt', 'PyMySQL'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("📦 Install them with: pip install -r requirements.txt")
        return False
    
    print("✅ All required packages are installed")
    return True

def start_server():
    """Start the Flask development server"""
    try:
        # Import Flask app after environment is set up
        from app import app
        import routes  # Import routes to register them
        
        print("✅ Flask app imported successfully")
        
        # Create database tables if they don't exist
        with app.app_context():
            from app import db
            db.create_all()
            print("✅ Database tables created/verified")
        
        # Display server information
        print("\n" + "="*60)
        print("🚀 RESORT BOOKING SYSTEM - SERVER STARTING")
        print("="*60)
        print("📍 Main Website:      http://localhost:5000")
        print("🔧 Admin Panel:       http://localhost:5000/admin")
        print("📅 Calendar Example:  http://localhost:5000/booking-calendar/1")
        print("🏨 Room Details:      http://localhost:5000/room/1")
        print("📊 API Example:       http://localhost:5000/api/date-info/1/2025-06-20")
        print("="*60)
        print("🔑 Login Credentials:")
        print("   Admin: admin / admin123")
        print("   User:  john_doe / password123")
        print("="*60)
        print("💡 Press Ctrl+C to stop the server")
        print("="*60)
        
        # Start the Flask development server
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=True
        )
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("🔍 Make sure you're in the correct directory and all files exist")
        return False
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("🔍 Check the error details above for troubleshooting")
        return False

def main():
    """Main function to start the resort booking system"""
    print("🏨 Resort Booking System - Starting Up...")
    print("="*60)
    
    # Step 1: Check dependencies
    # if not check_dependencies():
    #     sys.exit(1)
    
    # Step 2: Set up environment
    setup_environment()
    
    # Step 3: Start server
    print("🚀 Starting Flask development server...")
    start_server()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
        print("Thank you for using Resort Booking System!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1) 