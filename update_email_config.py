#!/usr/bin/env python3
"""
Update Email Configuration Script
This script helps you update the .env file with your Gmail App Password
"""

import os
from pathlib import Path

def update_email_config():
    """Update the .env file with Gmail App Password"""
    print("🔧 Gmail App Password Setup")
    print("=" * 40)
    
    env_file = Path(__file__).parent / '.env'
    
    if not env_file.exists():
        print("❌ .env file not found!")
        return False
    
    print("📧 Current email configuration:")
    print("   MAIL_USERNAME: yashkaranjule230@gmail.com")
    print("   MAIL_SERVER: smtp.gmail.com")
    print("   MAIL_PORT: 587")
    print()
    
    print("🔑 To complete setup, you need a Gmail App Password:")
    print("1. Go to: https://myaccount.google.com/security")
    print("2. Enable 2-Factor Authentication (if not already)")
    print("3. Go to 'App passwords'")
    print("4. Generate password for 'Mail'")
    print("5. Copy the 16-character password")
    print()
    
    app_password = input("Enter your Gmail App Password (16 characters): ").strip()
    
    if not app_password:
        print("❌ No password entered. Exiting.")
        return False
    
    if len(app_password) < 10:
        print("⚠️  App password seems too short. Gmail app passwords are usually 16 characters.")
        confirm = input("Continue anyway? (y/n): ").strip().lower()
        if confirm != 'y':
            return False
    
    # Read current .env file
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Replace the placeholder password
    updated_content = content.replace(
        'MAIL_PASSWORD=YOUR-GMAIL-APP-PASSWORD-HERE',
        f'MAIL_PASSWORD={app_password}'
    )
    
    # Also update any other placeholder
    updated_content = updated_content.replace(
        'MAIL_PASSWORD=your_app_password',
        f'MAIL_PASSWORD={app_password}'
    )
    
    # Write updated content
    with open(env_file, 'w') as f:
        f.write(updated_content)
    
    print("✅ Email configuration updated!")
    print("🔄 Please restart your Flask app for changes to take effect:")
    print("   python app.py")
    print()
    print("🧪 Test password reset:")
    print("1. Go to: http://localhost:5000/login")
    print("2. Click 'Forgot Password?'")
    print("3. Enter: yashkaranjule230@gmail.com")
    print("4. Check your Gmail inbox!")
    
    return True

def show_current_config():
    """Show current email configuration"""
    env_file = Path(__file__).parent / '.env'
    
    if not env_file.exists():
        print("❌ .env file not found!")
        return
    
    print("📧 Current .env email configuration:")
    print("-" * 40)
    
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    email_lines = [line.strip() for line in lines if line.startswith('MAIL_')]
    
    for line in email_lines:
        if 'MAIL_PASSWORD' in line:
            # Hide password for security
            if 'YOUR-GMAIL-APP-PASSWORD-HERE' in line:
                print(f"   {line} ⚠️  NEEDS SETUP")
            else:
                print(f"   MAIL_PASSWORD=*** (configured) ✅")
        else:
            print(f"   {line}")

def main():
    print("🔧 Email Configuration Helper")
    print("=" * 50)
    
    while True:
        print("\n1. Show current configuration")
        print("2. Update Gmail App Password")
        print("3. Exit")
        
        choice = input("\nChoose an option (1-3): ").strip()
        
        if choice == '1':
            show_current_config()
        elif choice == '2':
            if update_email_config():
                break
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main() 