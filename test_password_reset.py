#!/usr/bin/env python3
"""
Test Password Reset Functionality
This script helps test the password reset feature
"""

import os
import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app, db
from models import User

def test_password_reset():
    """Test password reset token generation and verification"""
    app = create_app()
    
    with app.app_context():
        # Find a test user (admin)
        user = User.query.filter_by(username='admin').first()
        if not user:
            print("❌ Admin user not found. Please ensure the database is set up.")
            return False
        
        print(f"🧪 Testing password reset for user: {user.email}")
        
        # Generate reset token
        token = user.generate_password_reset_token()
        print(f"🔑 Generated token: {token}")
        
        # Verify token
        if user.verify_password_reset_token(token):
            print("✅ Token verification successful")
        else:
            print("❌ Token verification failed")
            return False
        
        # Test token URL
        print(f"🔗 Reset URL: http://localhost:5000/reset-password/{token}")
        print("📝 You can use this URL to test password reset directly")
        
        # Test user lookup by token
        found_user = User.get_user_by_reset_token(token)
        if found_user and found_user.id == user.id:
            print("✅ User lookup by token successful")
        else:
            print("❌ User lookup by token failed")
            return False
        
        return True

def check_mail_config():
    """Check if mail configuration is set up"""
    print("📧 Checking mail configuration...")
    
    env_file = Path(__file__).parent / '.env'
    if not env_file.exists():
        print("❌ No .env file found")
        print("💡 Create .env file with mail settings (see PASSWORD_RESET_SETUP.md)")
        return False
    
    # Check for required mail settings
    required_settings = ['MAIL_SERVER', 'MAIL_USERNAME', 'MAIL_PASSWORD', 'MAIL_DEFAULT_SENDER']
    
    with open(env_file, 'r') as f:
        content = f.read()
    
    missing = []
    for setting in required_settings:
        if setting not in content or f"{setting}=" not in content:
            missing.append(setting)
        else:
            # Check if it has a value
            for line in content.split('\n'):
                if line.startswith(f"{setting}=") and len(line.split('=', 1)[1].strip()) > 0:
                    break
            else:
                missing.append(setting)
    
    if missing:
        print(f"❌ Missing mail settings: {missing}")
        print("💡 Update .env file with your email credentials")
        return False
    else:
        print("✅ Mail configuration appears complete")
        return True

def main():
    print("🧪 Password Reset Test")
    print("=" * 40)
    
    # Check mail configuration
    mail_ok = check_mail_config()
    
    # Test password reset functionality
    if test_password_reset():
        print("\n✅ All password reset tests passed!")
        
        if mail_ok:
            print("\n🔗 To test the full flow:")
            print("1. Start the Flask app: python app.py")
            print("2. Go to: http://localhost:5000/login")
            print("3. Click 'Forgot Password?'")
            print("4. Enter: admin@resort.com")
            print("5. Check your email for the reset link")
        else:
            print("\n⚠️  Email not configured - you can still test:")
            print("1. Start the Flask app: python app.py")
            print("2. Go to: http://localhost:5000/login")
            print("3. Click 'Forgot Password?'")
            print("4. Enter: admin@resort.com")
            print("5. Check server logs for the reset token")
            print("6. Use the token in the reset URL shown above")
    else:
        print("\n❌ Password reset tests failed!")
        print("💡 Make sure the database is set up and admin user exists")

if __name__ == "__main__":
    main() 