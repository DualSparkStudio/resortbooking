# Gmail App Password Setup for Password Reset

## 🚨 IMPORTANT: You Need Gmail App Password

The `.env` file is configured but you need to replace `YOUR-GMAIL-APP-PASSWORD-HERE` with your actual Gmail App Password.

## 📧 Step-by-Step Gmail Setup

### Step 1: Enable 2-Factor Authentication
1. **Go to:** [Google Account Settings](https://myaccount.google.com/)
2. **Click:** "Security" in the left sidebar
3. **Find:** "2-Step Verification" 
4. **Enable it** if not already enabled (required for App Passwords)

### Step 2: Generate App Password
1. **Still in Security settings**
2. **Find:** "App passwords" (may be under "2-Step Verification")
3. **Click:** "App passwords"
4. **Select:** "Mail" from the dropdown
5. **Click:** "Generate"
6. **Copy the 16-character password** (format: `abcd efgh ijkl mnop`)

### Step 3: Update .env File
Replace `YOUR-GMAIL-APP-PASSWORD-HERE` with your actual app password:

**Open `.env` file and change this line:**
```
MAIL_PASSWORD=YOUR-GMAIL-APP-PASSWORD-HERE
```

**To this (with your actual app password):**
```
MAIL_PASSWORD=abcd efgh ijkl mnop
```

### Step 4: Restart the App
```bash
# Stop the current Flask app (Ctrl+C if running)
# Then restart:
python app.py
```

## 🧪 Test the Password Reset

After setting up the app password:

1. **Go to:** http://localhost:5000/login
2. **Click:** "Forgot Password?"
3. **Enter:** yashkaranjule230@gmail.com
4. **Check Gmail inbox** for the reset email
5. **Click the reset link** in the email

## 🔧 Alternative: Quick Test Setup

If you want to test immediately without Gmail setup, you can use a temporary email service:

**Option 1: Use Mailtrap (Recommended for Testing)**
```env
MAIL_SERVER=smtp.mailtrap.io
MAIL_PORT=2525
MAIL_USE_TLS=true
MAIL_USERNAME=your-mailtrap-username
MAIL_PASSWORD=your-mailtrap-password
MAIL_DEFAULT_SENDER=test@example.com
```

**Option 2: Keep Using Console Logging**
The current system logs reset tokens to console, so you can:
1. Try password reset
2. Copy the URL from Flask console logs
3. Use it directly in browser

## 📞 Troubleshooting

### "Authentication failed" Error:
- Make sure you're using App Password, not regular Gmail password
- Verify 2-Factor Authentication is enabled
- Double-check the app password was copied correctly

### "Connection timeout" Error:
- Check internet connection
- Some networks block SMTP ports
- Try using port 465 with SSL instead

### Still Not Working?
- Use the console logging method (check Flask terminal for reset URLs)
- Or use admin reset: Login as admin → Users → Edit user → Set new password

## 🎯 Expected Result

After proper setup, password reset will:
✅ Send professional HTML email to user
✅ Include secure reset link
✅ Work automatically without console logging
✅ Provide excellent user experience

The system is ready - just needs your Gmail App Password! 