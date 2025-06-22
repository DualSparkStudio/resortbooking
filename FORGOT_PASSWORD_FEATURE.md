# Forgot Password Feature - Resort Booking System

## Overview
Comprehensive password reset functionality that allows users and admins to securely recover their accounts via email verification.

## ✅ Features Implemented

### 1. **Password Reset Forms**
- **ForgotPasswordForm** - Email validation and user lookup
- **ResetPasswordForm** - Secure password reset with confirmation
- **Form Validation** - Email existence check and password strength requirements

### 2. **User Model Enhancements**
- **Token Generation** - Cryptographically secure tokens using `secrets` module
- **Token Verification** - 1-hour expiry with SHA256 hash validation
- **User Lookup** - Safe token-to-user mapping without exposing user IDs

### 3. **Email Functionality**
- **Professional Email Template** - HTML formatted with resort branding
- **Secure Link Generation** - Domain-aware reset URLs
- **Security Warnings** - Clear expiration and usage instructions
- **Error Handling** - Graceful fallback when email not configured

### 4. **Routes Implementation**
- **`/forgot-password`** - Email submission and token generation
- **`/reset-password/<token>`** - Token validation and password update
- **Security Measures** - No account information disclosure, CSRF protection

### 5. **User Interface**
- **Forgot Password Page** - Clean, guided interface with process visualization
- **Reset Password Page** - Secure form with password visibility toggles
- **Login Integration** - Prominent "Forgot Password?" link
- **Admin Profile Integration** - Password reset option in admin panel

## 🔐 Security Features

### Token Security
- **Cryptographically Secure** - Uses `secrets.token_urlsafe(32)`
- **Time-Limited** - 1-hour expiration for safety
- **Hash Verification** - SHA256 ensures token integrity
- **Single-Use Design** - Tokens become invalid after password reset

### Email Security
- **No Information Disclosure** - Doesn't reveal if email exists
- **Professional Formatting** - Reduces spam likelihood
- **Clear Security Instructions** - Expiration warnings and usage guidelines

### Password Security
- **Minimum 6 Characters** - Enforced password length
- **Secure Hashing** - Uses Flask-Bcrypt for storage
- **Confirmation Required** - Prevents typos in new passwords
- **Strength Guidelines** - Visual tips for strong passwords

## 📧 Email Configuration

Add these environment variables to your `.env` file:

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

## 🚀 How to Use

### For All Users (Regular & Admin)
1. **Access Reset Form**
   - From login page: Click "Forgot Password?" link
   - From admin profile: Click "Forgot Password?" button

2. **Submit Email Address**
   - Enter your registered email address
   - System validates email format and existence

3. **Check Your Email**
   - Look for password reset email (check spam folder)
   - Email contains secure reset link valid for 1 hour

4. **Reset Password**
   - Click the reset link in email
   - Enter and confirm your new password
   - Password must be at least 6 characters

5. **Login with New Password**
   - Use new credentials to access your account
   - Admins are redirected to admin dashboard

## 💡 Benefits

- **Self-Service Recovery** - No support tickets needed
- **Enhanced Security** - Token-based verification system
- **24/7 Availability** - Automated password recovery process
- **Professional Experience** - Industry-standard implementation
- **Admin Support** - Comprehensive solution for all user types 