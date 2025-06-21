#!/usr/bin/env python3
"""
Environment Setup Script for Resort Booking System
This script helps create the .env file with proper configuration.
"""

import os
import secrets
from pathlib import Path

def generate_secret_key():
    """Generate a secure secret key"""
    return secrets.token_urlsafe(32)

def create_env_file():
    """Create a .env file with default configuration"""
    print("🔧 Creating .env file...")
    
    # Get the current directory
    current_dir = Path(__file__).parent
    env_file = current_dir / '.env'
    
    # Generate a secure secret key
    secret_key = generate_secret_key()
    
    # Default environment configuration
    env_content = f"""# Flask Configuration
SESSION_SECRET={secret_key}

# Database Configuration (using SQLite for local development)
# Leave empty to use default SQLite database
DATABASE_URL=

# Mail Configuration (optional for local development)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_DEFAULT_SENDER=

# Admin Configuration
ADMIN_EMAIL=admin@resort.com

# Stripe Configuration (optional for local testing)
STRIPE_SECRET_KEY=
STRIPE_PUBLISHABLE_KEY=

# Razorpay Configuration (optional)
RAZORPAY_KEY_ID=
RAZORPAY_KEY_SECRET=
"""
    
    # Write the .env file
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print(f"✅ .env file created: {env_file}")
        print(f"🔑 Generated secure secret key")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def show_setup_instructions():
    """Show setup instructions"""
    print("\n📋 SETUP INSTRUCTIONS:")
    print("=" * 50)
    print("1. The .env file has been created with default values")
    print("2. For basic local development, you don't need to change anything")
    print("3. To enable email notifications, update the MAIL_* variables")
    print("4. To enable Stripe payments, add your Stripe keys")
    print("5. Run the database fix: python fix_database.py")
    print("6. Start the server: python start_server.py")
    print("\n🔐 SECURITY NOTE:")
    print("- Never commit the .env file to version control")
    print("- Change the SESSION_SECRET in production")
    print("- Use environment variables in production deployments")

def main():
    """Main function to set up environment"""
    print("🏨 Resort Booking System - Environment Setup")
    print("=" * 50)
    
    # Check if .env already exists
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        response = input("⚠️  .env file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("❌ Setup cancelled")
            return
    
    # Create .env file
    if create_env_file():
        show_setup_instructions()
        print("\n✅ Environment setup completed!")
    else:
        print("\n❌ Environment setup failed!")

if __name__ == "__main__":
    main() 