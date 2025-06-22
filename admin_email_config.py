#!/usr/bin/env python3
"""
Admin Email Configuration System
Allows admins to configure email settings through the web interface
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from flask import current_app
from models import db

class EmailConfig:
    """Handle email configuration for multi-tenant system"""
    
    @staticmethod
    def get_email_providers():
        """Get list of supported email providers with their settings"""
        return {
            'gmail': {
                'name': 'Gmail',
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'use_tls': True,
                'instructions': 'Use your Gmail address and App Password (requires 2FA)',
                'help_url': 'https://support.google.com/accounts/answer/185833'
            },
            'outlook': {
                'name': 'Outlook/Hotmail',
                'smtp_server': 'smtp-mail.outlook.com',
                'smtp_port': 587,
                'use_tls': True,
                'instructions': 'Use your Outlook/Hotmail email and password',
                'help_url': 'https://support.microsoft.com/en-us/office/pop-imap-and-smtp-settings-for-outlook-com-d088b986-291d-42b8-9564-9c414e2aa040'
            },
            'yahoo': {
                'name': 'Yahoo Mail',
                'smtp_server': 'smtp.mail.yahoo.com',
                'smtp_port': 587,
                'use_tls': True,
                'instructions': 'Use your Yahoo email and App Password (requires 2FA)',
                'help_url': 'https://help.yahoo.com/kb/generate-third-party-passwords-sln15241.html'
            },
            'custom': {
                'name': 'Custom SMTP Server',
                'smtp_server': '',
                'smtp_port': 587,
                'use_tls': True,
                'instructions': 'Enter your custom SMTP server details',
                'help_url': ''
            }
        }
    
    @staticmethod
    def test_email_connection(smtp_server, smtp_port, use_tls, username, password):
        """Test email connection without sending actual email"""
        try:
            if use_tls:
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(smtp_server, smtp_port)
            
            server.login(username, password)
            server.quit()
            return True, "Connection successful!"
        
        except smtplib.SMTPAuthenticationError:
            return False, "Authentication failed. Check your email and password."
        except smtplib.SMTPConnectError:
            return False, "Cannot connect to email server. Check server settings."
        except smtplib.SMTPException as e:
            return False, f"SMTP error: {str(e)}"
        except Exception as e:
            return False, f"Connection error: {str(e)}"
    
    @staticmethod
    def send_test_email(smtp_server, smtp_port, use_tls, username, password, sender_email, test_recipient):
        """Send a test email to verify configuration"""
        try:
            # Create test message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = test_recipient
            msg['Subject'] = "Test Email - Resort Booking System"
            
            body = """
            <h2>Email Configuration Test</h2>
            <p>Congratulations! Your email configuration is working correctly.</p>
            <p>Your Resort Booking System can now send:</p>
            <ul>
                <li>Password reset emails</li>
                <li>Booking confirmations</li>
                <li>Contact form notifications</li>
            </ul>
            <p><strong>This is a test email - no action required.</strong></p>
            <hr>
            <p><small>Resort Booking System - Email Configuration Test</small></p>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            if use_tls:
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(smtp_server, smtp_port)
            
            server.login(username, password)
            server.send_message(msg)
            server.quit()
            
            return True, "Test email sent successfully!"
        
        except Exception as e:
            return False, f"Failed to send test email: {str(e)}"
    
    @staticmethod
    def save_email_config(smtp_server, smtp_port, use_tls, username, password, sender_email):
        """Save email configuration to environment/database"""
        try:
            # Update environment variables in current session
            os.environ['MAIL_SERVER'] = smtp_server
            os.environ['MAIL_PORT'] = str(smtp_port)
            os.environ['MAIL_USE_TLS'] = 'true' if use_tls else 'false'
            os.environ['MAIL_USERNAME'] = username
            os.environ['MAIL_PASSWORD'] = password
            os.environ['MAIL_DEFAULT_SENDER'] = sender_email
            
            # Update Flask app config
            if current_app:
                current_app.config['MAIL_SERVER'] = smtp_server
                current_app.config['MAIL_PORT'] = smtp_port
                current_app.config['MAIL_USE_TLS'] = use_tls
                current_app.config['MAIL_USERNAME'] = username
                current_app.config['MAIL_PASSWORD'] = password
                current_app.config['MAIL_DEFAULT_SENDER'] = sender_email
            
            # Save to .env file for persistence
            env_file = Path(__file__).parent / '.env'
            
            # Read existing .env content
            env_content = ""
            if env_file.exists():
                with open(env_file, 'r') as f:
                    env_content = f.read()
            
            # Update or add email configuration
            email_config = f"""
# Email Configuration (Auto-configured by admin)
MAIL_SERVER={smtp_server}
MAIL_PORT={smtp_port}
MAIL_USE_TLS={'true' if use_tls else 'false'}
MAIL_USERNAME={username}
MAIL_PASSWORD={password}
MAIL_DEFAULT_SENDER={sender_email}
"""
            
            # Remove old email configuration
            lines = env_content.split('\n')
            filtered_lines = []
            skip_next = False
            
            for line in lines:
                if line.startswith('MAIL_') or line.strip() == '# Email Configuration (Auto-configured by admin)':
                    continue
                filtered_lines.append(line)
            
            # Add new email configuration
            updated_content = '\n'.join(filtered_lines) + email_config
            
            # Write updated .env file
            with open(env_file, 'w') as f:
                f.write(updated_content)
            
            return True, "Email configuration saved successfully!"
        
        except Exception as e:
            return False, f"Failed to save configuration: {str(e)}"
    
    @staticmethod
    def get_current_config():
        """Get current email configuration"""
        return {
            'smtp_server': os.environ.get('MAIL_SERVER', ''),
            'smtp_port': int(os.environ.get('MAIL_PORT', 587)),
            'use_tls': os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true',
            'username': os.environ.get('MAIL_USERNAME', ''),
            'sender_email': os.environ.get('MAIL_DEFAULT_SENDER', ''),
            'is_configured': bool(os.environ.get('MAIL_SERVER') and os.environ.get('MAIL_USERNAME'))
        }
    
    @staticmethod
    def get_email_status():
        """Get email system status for admin dashboard"""
        config = EmailConfig.get_current_config()
        
        if not config['is_configured']:
            return {
                'status': 'not_configured',
                'message': 'Email system not configured',
                'color': 'warning'
            }
        
        # Test connection
        success, message = EmailConfig.test_email_connection(
            config['smtp_server'],
            config['smtp_port'],
            config['use_tls'],
            config['username'],
            os.environ.get('MAIL_PASSWORD', '')
        )
        
        if success:
            return {
                'status': 'working',
                'message': 'Email system working correctly',
                'color': 'success'
            }
        else:
            return {
                'status': 'error',
                'message': f'Email system error: {message}',
                'color': 'danger'
            } 