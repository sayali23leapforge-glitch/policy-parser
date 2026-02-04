# Render Deployment Guide - Auto Dashboard Policy Parser

## 🚀 Complete Deployment Instructions

This guide will help you deploy your entire project to Render's Web Service.

---

## **Step 1: Prepare Your GitHub Repository**

### 1.1 Ensure Git is Initialized (Already Done)
Your project already has Git initialized (`.git/` folder exists).

### 1.2 Push to GitHub
Replace `YOUR_USERNAME` and `YOUR_REPO` with your actual credentials:

```powershell
# Navigate to your project directory
cd "d:\Auto dashboard"

# Add all files to staging
git add .

# Commit changes
git commit -m "Deploy to Render: Complete Auto Dashboard Policy Parser"

# Push to GitHub (if remote is already set up)
git push origin main

# OR if you need to add remote first:
git remote add origin https://github.com/sayali23leapforge-glitch/policy-parser.git
git branch -M main
git push -u origin main
```

---

## **Step 2: Create Render Account & Project**

### 2.1 Sign Up / Log In
1. Go to [render.com](https://render.com)
2. Sign in with GitHub (recommended for easy deployment)
3. Click **"New +"** button → Select **"Web Service"**

### 2.2 Connect GitHub Repository
1. Select **"Connect a repository"**
2. Choose your repository: `policy-parser`
3. Click **"Connect"**

### 2.3 Configure Web Service

| Setting | Value |
|---------|-------|
| **Name** | `auto-dashboard-parser` |
| **Environment** | `Python 3` |
| **Region** | Choose closest to your users |
| **Branch** | `main` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn -w 4 -b 0.0.0.0:$PORT backend.app:app` |
| **Instance Type** | Free (or Starter $7/month) |

---

## **Step 3: Set Environment Variables**

Add these in Render Dashboard → **Environment**:

```plaintext
VITE_SUPABASE_URL=your_supabase_url_here
VITE_SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_key_here
META_APP_ID=your_meta_app_id
META_APP_SECRET=your_meta_app_secret
META_PAGE_ID=your_meta_page_id
META_PAGE_ACCESS_TOKEN=your_meta_page_token
META_LEAD_FORM_ID=your_lead_form_id
META_WEBHOOK_VERIFY_TOKEN=your_webhook_verify_token
FB_PIXEL_ID=your_fb_pixel_id
ZOHO_CLIENT_ID=your_zoho_client_id
ZOHO_CLIENT_SECRET=your_zoho_client_secret
ZOHO_REDIRECT_URI=https://your-render-url.onrender.com/auth/zoho/callback
PYTHON_VERSION=3.13.1
FLASK_PORT=5000
```

### ⚠️ Important: Get Your Render URL First
After deployment starts, Render will give you a URL like: `https://auto-dashboard-parser.onrender.com`

Update `ZOHO_REDIRECT_URI` with your actual Render URL.

---

## **Step 4: Deploy**

### Option A: Automatic Deployment (Recommended)
- Render automatically deploys when you push to `main` branch
- Check deployment status in Render Dashboard → **Deployments** tab

### Option B: Manual Trigger
1. Go to Render Dashboard
2. Click your service
3. Click **"Manual Deploy"** → **"Deploy latest commit"**

---

## **Step 5: Verify Deployment**

Once deployment completes (green ✓):

```bash
# Test your API endpoint
curl https://your-service.onrender.com/api/health

# Expected response:
# { "status": "ok", "environment": "production" }
```

### Check Logs
- Render Dashboard → **Logs** tab
- Look for: `🚀 Flask app running`

---

## **Step 6: Update Frontend URLs**

If you have a frontend, update API calls:

```javascript
// Before (localhost)
const API_URL = 'http://localhost:5000'

// After (Render)
const API_URL = 'https://auto-dashboard-parser.onrender.com'
```

Update this in your HTML files and JavaScript:
- `index.html`
- `Auto dashboard.html`
- `coverpage.html`
- `property.html`

---

## **Step 7: Configure Webhooks (If Using Meta)**

In Meta/Facebook Settings:

1. Go to **Settings** → **Webhooks**
2. Set Webhook URL: `https://your-service.onrender.com/meta/webhook`
3. Verify Token: Use your `META_WEBHOOK_VERIFY_TOKEN`
4. Subscribe to: `leads`, `page`

---

## **Troubleshooting**

### ❌ Build Failed
**Solution:** Check logs, ensure all dependencies in `requirements.txt` are compatible with Python 3.13

```bash
# Test locally first
pip install -r requirements.txt
python -m gunicorn --chdir backend app:app --bind 0.0.0.0:5000
```

### ❌ Port Binding Error
**Solution:** Use `$PORT` environment variable (already configured in `render.yaml`)

### ❌ Module Import Errors
**Solution:** Ensure relative imports in backend are correct:
```python
from .pdf_parser import parse_mvr_pdf
from .routes import blueprint
```

### ❌ Supabase Connection Failed
**Solution:** Verify:
- `VITE_SUPABASE_URL` is correct (ends with `.co`)
- `VITE_SUPABASE_SERVICE_ROLE_KEY` is the SERVICE ROLE KEY (not anon key)

### ❌ Static Files Not Loading
**Solution:** Render serves from root directory. Ensure paths are relative:
```python
app = Flask(__name__, static_folder='..', static_url_path='')
```

---

## **After Deployment**

### Auto-Redeploy on GitHub Push
✅ Already enabled by default. Just push to `main` and Render auto-deploys!

### Monitor Uptime
- Render Dashboard → **Monitoring** tab
- Set up alerts if needed

### Scale Up (Optional)
If free tier is too slow:
1. Click **"Instance Type"**
2. Choose **"Starter"** ($7/month) or higher
3. Render handles scaling automatically

---

## **Quick Command Reference**

```powershell
# Git commands
git status                  # Check changed files
git add .                   # Stage all files
git commit -m "message"     # Commit changes
git push origin main        # Push to GitHub

# Local testing before deployment
python run.py               # Test Flask locally
# Visit http://localhost:5000
```

---

## **Your Deployment URL**

After successful deployment, your app will be available at:

🎯 **`https://auto-dashboard-parser.onrender.com`**

(Replace with your actual Render service name if different)

---

## **Need Help?**

- **Render Docs:** https://render.com/docs
- **Flask Deployment:** https://flask.palletsprojects.com/deployment/
- **Supabase Docs:** https://supabase.com/docs
- **Check GitHub Actions:** Your repo's **Actions** tab for CI/CD logs

---

## **Security Checklist** ✅

- [ ] `.env.local` is in `.gitignore` (not committed)
- [ ] `.env.production` is in `.gitignore`
- [ ] All secrets are added in Render Dashboard, not in code
- [ ] HTTPS is used for all API calls
- [ ] CORS is properly configured
- [ ] Webhook tokens are strong and secret

---

**Last Updated:** February 4, 2026

Good luck with your deployment! 🚀
