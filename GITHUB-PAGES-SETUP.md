# 🚀 GitHub Pages Setup Guide

## ✅ What I've Created for You

Your repository is now **GitHub Pages ready** with a static landing page that showcases your Flask project.

### 📁 Files Added/Modified:

1. **`index.html`** - Beautiful static landing page
2. **`_config.yml`** - Jekyll configuration for GitHub Pages
3. **`.github/workflows/static.yml`** - GitHub Actions for auto-deployment
4. **`README.md`** - Updated with deployment information

## 🎯 How to Enable GitHub Pages

### Step 1: Push Your Changes
```bash
git add .
git commit -m "Add GitHub Pages static site"
git push origin main
```

### Step 2: Enable GitHub Pages
1. Go to your GitHub repository
2. Click **Settings** tab
3. Scroll down to **Pages** section
4. Under **Source**, select:
   - **Deploy from a branch**
   - Branch: **main**
   - Folder: **/ (root)**
5. Click **Save**

### Step 3: Wait for Deployment
- GitHub will automatically build and deploy your site
- Check the **Actions** tab to see deployment progress
- Your site will be available at: `https://yourusername.github.io/repository-name`

## 📋 What the GitHub Pages Site Shows

### ✅ Static Landing Page Features:
- **Project showcase** with beautiful design
- **Technology stack** overview
- **Deployment instructions** for the Flask app
- **Clear explanation** of GitHub Pages limitations
- **Links to deployment platforms** (Render, Railway, Heroku)

### ❌ What It Cannot Do:
- Run the Flask application
- Handle bookings or payments
- Access the database
- Process forms or authentication

## 🔄 Two-Part Solution

### 1. GitHub Pages (Static Demo)
- **Purpose**: Project portfolio and documentation
- **Shows**: What your project does and how to deploy it
- **URL**: `https://yourusername.github.io/resort-booking`

### 2. Flask App (Live Application)
- **Purpose**: Actual working booking system
- **Deploy to**: Render.com, Railway, Heroku, or PythonAnywhere
- **URL**: `https://your-app-name.onrender.com`

## 🎨 Customizing Your GitHub Pages Site

To customize the static landing page:

1. **Update GitHub repository URL** in `index.html`:
   ```html
   <a href="https://github.com/YOURUSERNAME/YOURREPO" class="btn btn-outline-light btn-lg">
   ```

2. **Add your deployed app URL** in `index.html`:
   ```javascript
   const liveAppUrl = 'https://your-app-name.onrender.com';
   ```

3. **Update repository name** in `_config.yml`:
   ```yaml
   url: "https://yourusername.github.io"
   baseurl: "/your-repo-name"
   ```

## 🚨 Important Reminders

### GitHub Pages Limitations:
- ❌ **No Python/Flask support**
- ❌ **No server-side processing**
- ❌ **No database connections**
- ❌ **No payment processing**
- ✅ **Only static HTML/CSS/JavaScript**

### Solution:
- Use GitHub Pages for **project showcase**
- Deploy Flask app on **Render.com** (free) for actual functionality
- Link between the two in your landing page

## 📝 Next Steps

1. **Enable GitHub Pages** using steps above
2. **Deploy Flask app** to Render.com using `deployment-guide.md`
3. **Update links** in `index.html` to point to your live app
4. **Share both URLs**:
   - Portfolio: `https://yourusername.github.io/resort-booking`
   - Live App: `https://your-app.onrender.com`

## 🎉 Success!

You now have:
- ✅ A beautiful GitHub Pages portfolio site
- ✅ Deployment configurations for Flask app
- ✅ Clear separation between demo and live app
- ✅ Professional project presentation

Your GitHub Pages site will showcase your Flask project beautifully while directing users to the actual deployed application! 