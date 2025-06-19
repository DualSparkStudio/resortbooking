# Resort Booking System - Deployment Guide

## ❌ GitHub Pages Limitation

**GitHub Pages cannot host this Flask application** because it only supports static websites (HTML, CSS, JavaScript). Flask requires a Python server environment.

## ✅ Recommended Hosting Platforms

### 1. Render.com (FREE - Recommended)

**Why Render?**
- Free tier with 512MB RAM
- Automatic HTTPS
- PostgreSQL database included
- GitHub auto-deployment
- No credit card required

**Steps to Deploy:**

1. **Prepare Repository:**
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Sign up at render.com** and connect your GitHub account

3. **Create New Web Service:**
   - Choose your repository
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn --bind 0.0.0.0:$PORT app:app`

4. **Create PostgreSQL Database:**
   - Add new PostgreSQL database
   - Copy connection string

5. **Set Environment Variables:**
   ```
   DATABASE_URL=<your-postgres-connection-string>
   SESSION_SECRET=<generate-random-32-char-string>
   STRIPE_SECRET_KEY=<your-stripe-secret-key>
   STRIPE_PUBLISHABLE_KEY=<your-stripe-publishable-key>
   MAIL_USERNAME=<your-email>
   MAIL_PASSWORD=<your-email-app-password>
   MAIL_DEFAULT_SENDER=<your-email>
   ADMIN_EMAIL=<admin-email>
   ```

6. **Deploy** - Render will automatically build and deploy

### 2. Railway.app (FREE)

**Steps:**
1. Connect GitHub repository
2. Add PostgreSQL plugin
3. Set environment variables
4. Deploy automatically

### 3. Heroku (Limited Free)

**Requirements:**
- Add `Procfile`: `web: gunicorn app:app`
- Add Heroku Postgres add-on
- Configure environment variables

### 4. PythonAnywhere (FREE)

**Steps:**
1. Upload code to PythonAnywhere
2. Configure WSGI file
3. Set up MySQL database
4. Configure environment variables

## Environment Variables Setup

Create these environment variables in your hosting platform:

```bash
# Required
DATABASE_URL=postgresql://user:pass@host:5432/db_name
SESSION_SECRET=your-secret-key-32-characters-long

# Stripe (for payments)
STRIPE_SECRET_KEY=sk_live_or_test_key
STRIPE_PUBLISHABLE_KEY=pk_live_or_test_key

# Email (Gmail example)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
ADMIN_EMAIL=admin@yourresort.com
```

## Gmail App Password Setup

1. Enable 2-Factor Authentication on Gmail
2. Go to Google Account Settings > Security
3. Generate App Password for "Mail"
4. Use this password (not your regular password)

## Domain Setup

After deployment:
1. Get your app URL (e.g., `your-app.onrender.com`)
2. Update Stripe webhook URLs
3. Test all functionality
4. Optional: Connect custom domain

## Database Migration

Your app will automatically create tables on first run. For production data:

1. **Create Admin User:**
   Visit: `https://your-app-url.com/create-admin-user`

2. **Add Sample Data:**
   Use the admin panel to add room types, facilities, etc.

## Security Checklist

- ✅ Use strong SESSION_SECRET (32+ characters)
- ✅ Use HTTPS (automatic on most platforms)
- ✅ Set FLASK_ENV=production
- ✅ Never commit .env files
- ✅ Use Stripe live keys for production
- ✅ Enable email notifications

## Alternative: Convert to Static Site (JAMstack)

If you absolutely need GitHub Pages, you would need to completely rebuild as:
- **Frontend:** React/Vue/Vanilla JS
- **Backend:** Serverless functions (Vercel, Netlify)
- **Database:** Headless CMS (Strapi, Sanity) or Firebase
- **Payments:** Stripe Elements with serverless

This would require rewriting 80%+ of the current codebase.

## Cost Comparison

| Platform | Free Tier | Database | Custom Domain |
|----------|-----------|----------|---------------|
| Render.com | 512MB RAM | PostgreSQL | ✅ |
| Railway | 512MB RAM | PostgreSQL | ✅ |
| Heroku | 512MB RAM | PostgreSQL | ✅ |
| PythonAnywhere | 512MB RAM | MySQL | ❌ |
| GitHub Pages | Static Only | ❌ | ✅ |

**Recommendation:** Use Render.com for the easiest deployment experience. 