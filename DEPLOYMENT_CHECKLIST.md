# Pre-Deployment Checklist for Render

## ✅ Required Files Present

- [x] `Procfile` - Web server startup configuration
- [x] `render.yaml` - Render service configuration  
- [x] `requirements.txt` - Python dependencies
- [x] `runtime.txt` - Python version specification
- [x] `.gitignore` - Excludes sensitive files
- [x] `run.py` - Entry point for backend
- [x] `backend/app.py` - Flask application
- [x] `backend/pdf_parser.py` - PDF parsing logic
- [x] `backend/__init__.py` - Package initialization
- [x] HTML Frontend Files:
  - [x] `index.html`
  - [x] `Auto dashboard.html`
  - [x] `coverpage.html`
  - [x] `property.html`
  - [x] `PAC form.html`

## 🔍 Configuration Status

### Procfile
```
web: gunicorn --chdir backend app:app --bind 0.0.0.0:$PORT
```
✅ Correctly configured to run from backend directory

### render.yaml
```yaml
- Build Command: pip install -r requirements.txt
- Start Command: gunicorn -w 4 -b 0.0.0.0:$PORT backend.app:app
- Python Version: 3.11.0
```
✅ All settings optimized for Render

### requirements.txt
Contains all necessary dependencies:
- ✅ Flask 3.0.0
- ✅ Flask-CORS 4.0.0
- ✅ PyPDF2 3.0.1
- ✅ supabase 2.13.0
- ✅ python-dotenv 1.0.0
- ✅ gunicorn 21.2.0
- ✅ requests 2.31.0
- ✅ pdfminer.six
- ✅ Pillow
- ✅ pdfplumber

### runtime.txt
✅ Python 3.13.1 specified

### .gitignore
✅ Correctly excludes:
- .env files (sensitive)
- *.pdf (large files)
- __pycache__ (compiled files)
- .venv (virtual environment)

## 🔐 Security Checklist

### Environment Variables Needed in Render

Set these in Render Dashboard > Environment:

```
VITE_SUPABASE_URL=                          ⚠️ NOT IN CODE
VITE_SUPABASE_SERVICE_ROLE_KEY=            ⚠️ NOT IN CODE
META_APP_ID=                               ⚠️ NOT IN CODE
META_APP_SECRET=                           ⚠️ NOT IN CODE
META_PAGE_ID=                              ⚠️ NOT IN CODE
META_PAGE_ACCESS_TOKEN=                    ⚠️ NOT IN CODE
META_LEAD_FORM_ID=                         ⚠️ NOT IN CODE
META_WEBHOOK_VERIFY_TOKEN=                 ⚠️ NOT IN CODE
FB_PIXEL_ID=                               ⚠️ NOT IN CODE
ZOHO_CLIENT_ID=                            ⚠️ NOT IN CODE
ZOHO_CLIENT_SECRET=                        ⚠️ NOT IN CODE
ZOHO_REDIRECT_URI=                         (Set after getting Render URL)
PYTHON_VERSION=3.13.1
FLASK_PORT=5000
```

## 📁 File Structure

```
d:\Auto dashboard\
├── backend/
│   ├── __init__.py              ✅
│   ├── app.py                   ✅ (1627 lines - Main Flask app)
│   ├── pdf_parser.py            ✅
│   └── requirements.txt          ✅
├── .git/                         ✅ (Repository initialized)
├── .gitignore                    ✅
├── Procfile                      ✅
├── render.yaml                   ✅
├── requirements.txt              ✅
├── runtime.txt                   ✅
├── run.py                        ✅
├── Auto dashboard.html           ✅
├── coverpage.html                ✅
├── property.html                 ✅
├── index.html                    ✅
├── PAC form.html                 ✅
└── [other HTML & static files]   ✅
```

## 🚀 Deployment Steps

### 1. Push to GitHub
```powershell
cd "d:\Auto dashboard"
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### 2. Create Render Service
- Go to render.com
- Click "New +" → "Web Service"
- Connect GitHub repo `sayali23leapforge-glitch/policy-parser`
- Select branch: `main`

### 3. Configure Render Settings

| Setting | Value |
|---------|-------|
| Name | auto-dashboard-parser |
| Environment | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn -w 4 -b 0.0.0.0:$PORT backend.app:app` |
| Instance Type | Free (Starter $7/mo recommended) |

### 4. Add Environment Variables
Copy all the environment variables listed above into Render Dashboard

### 5. Deploy
Click "Create Web Service" - Render will automatically build and deploy!

## 🧪 Local Testing (Before Deploying)

```powershell
# Ensure dependencies are installed
pip install -r requirements.txt

# Test Flask app locally
python run.py

# Visit http://localhost:5000
# Should see HTML pages loading
```

## ⚠️ Known Issues & Solutions

### Issue: Import Error "No module named 'backend'"
**Solution:** Procfile correctly uses `--chdir backend app:app`

### Issue: Static files not found
**Solution:** Flask configured with `static_folder='..'` to serve HTML files

### Issue: PDF parsing fails
**Solution:** Ensure PyPDF2, pdfminer.six, and pdfplumber are in requirements.txt ✅

### Issue: Supabase connection fails
**Solution:** Verify `VITE_SUPABASE_URL` ends with `.co` and key is SERVICE ROLE type ✅

## 📊 Expected Performance

- **Build Time:** 3-5 minutes
- **Startup Time:** 30-60 seconds
- **Cold Start:** After 15 minutes of inactivity (free tier)

For always-on service, upgrade to Starter plan ($7/mo).

## ✨ After Deployment

### Your live URL will be:
🎯 **https://auto-dashboard-parser.onrender.com**

### Update webhook URLs:
- Meta/Facebook settings
- Zoho OAuth redirect
- Any external services

### Monitor:
- Render Dashboard > Logs
- Render Dashboard > Monitoring
- Set up email alerts for failures

## 📋 Final Checklist

- [ ] `.env.local` file is NOT in git
- [ ] All secrets are in Render Environment, not in code
- [ ] `requirements.txt` has all dependencies
- [ ] `Procfile` is correct
- [ ] `render.yaml` is configured
- [ ] `runtime.txt` specifies Python version
- [ ] GitHub repository is up to date
- [ ] Backend imports are using relative paths
- [ ] Flask CORS is enabled
- [ ] Supabase credentials are ready
- [ ] Meta/Facebook tokens are ready

---

**Status:** ✅ **READY FOR DEPLOYMENT**

All files are configured correctly. You can now deploy to Render!

See `RENDER_DEPLOYMENT_GUIDE.md` for detailed step-by-step instructions.
