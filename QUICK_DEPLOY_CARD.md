# ⚡ QUICK REFERENCE - Render Deployment

## 🚀 DEPLOY IN 5 MINUTES

### Step 1: Git Push (1 min)
```powershell
cd "d:\Auto dashboard"
git add .
git commit -m "Deploy to Render"
git push origin main
```

### Step 2: Create Service on Render (2 min)
- Go to **render.com**
- Click **"New +"** → **"Web Service"**
- Select **GitHub repo**: `sayali23leapforge-glitch/policy-parser`
- Select **branch**: `main`

### Step 3: Configure (1 min)
| Setting | Value |
|---------|-------|
| **Name** | auto-dashboard-parser |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn -w 4 -b 0.0.0.0:$PORT backend.app:app` |

### Step 4: Add Environment Variables (1 min)
Copy these into Render dashboard:
```
VITE_SUPABASE_URL=your_url
VITE_SUPABASE_SERVICE_ROLE_KEY=your_key
META_APP_ID=your_id
META_APP_SECRET=your_secret
META_PAGE_ID=your_page_id
META_PAGE_ACCESS_TOKEN=your_token
META_LEAD_FORM_ID=your_form_id
META_WEBHOOK_VERIFY_TOKEN=your_token
FB_PIXEL_ID=your_pixel_id
ZOHO_CLIENT_ID=your_zoho_id
ZOHO_CLIENT_SECRET=your_zoho_secret
ZOHO_REDIRECT_URI=https://auto-dashboard-parser.onrender.com/auth/zoho/callback
PYTHON_VERSION=3.13.1
```

### Step 5: Deploy! (instant)
Click **"Create Web Service"** → Wait 3-5 min → LIVE! 🎉

---

## 🔗 YOUR LIVE URL
```
https://auto-dashboard-parser.onrender.com
```

---

## ✅ VERIFY DEPLOYMENT

After it goes live, check:

```bash
# Browser check
https://auto-dashboard-parser.onrender.com  ✓ Loads
https://auto-dashboard-parser.onrender.com/dashboard  ✓ Dashboard
https://auto-dashboard-parser.onrender.com/coverpage  ✓ Cover page

# API check
curl https://auto-dashboard-parser.onrender.com/api/health
# Should return: { "status": "ok" }
```

---

## 🛠️ USEFUL COMMANDS

```powershell
# Test locally before deploying
python run.py  # Visit http://localhost:5000

# Verify deployment setup
python verify_deployment.py

# Check git status
git status

# View git logs
git log --oneline -5
```

---

## 📊 MONITORING

After deployment, monitor:
- **Render Dashboard** → **Logs tab** - Check for errors
- **Render Dashboard** → **Monitoring** - View metrics
- **Response time** - Should be <500ms
- **Error rate** - Should be ~0%

---

## 🔐 SECURITY CHECKLIST

✅ `.env` files in `.gitignore` (not committed)  
✅ All secrets in Render environment variables  
✅ No API keys in source code  
✅ HTTPS enabled (automatic)  
✅ CORS configured  

---

## 🆘 IF SOMETHING BREAKS

### Build Failed
1. Check Render **Logs** tab
2. Fix locally: `python run.py`
3. Push again: `git push origin main`

### Can't Connect
1. Verify URL: `https://auto-dashboard-parser.onrender.com`
2. Check Render **Monitoring** tab
3. Restart service (manual deploy button)

### Environment Variables Not Working
1. Click Render service
2. Scroll to **Environment** tab
3. Verify values are correct
4. Click **Manual Deploy** to refresh

### PDF Upload Fails
1. Check file size (<10MB)
2. Verify PyPDF2 installed: `requirements.txt` ✓
3. Check Render logs for error

---

## 💰 PRICING

| Plan | Cost | Status | Speed |
|------|------|--------|-------|
| Free | $0/mo | Sleeps after 15 min | Slow start |
| Starter | $7/mo | Always on | Fast 🚀 |

**Recommended:** Start Free, upgrade to Starter if needed.

---

## 📚 FULL DOCUMENTATION

1. **DEPLOYMENT_READY.md** - Complete overview
2. **RENDER_DEPLOYMENT_GUIDE.md** - Step-by-step guide
3. **DEPLOYMENT_CHECKLIST.md** - Verification checklist
4. **DEPLOYMENT_ARCHITECTURE.md** - System design

---

## 🎯 SUCCESS CHECKLIST

- [ ] Project pushed to GitHub
- [ ] Render service created
- [ ] Environment variables added
- [ ] Service status shows "Running" (green)
- [ ] URL loads in browser
- [ ] All pages accessible
- [ ] File upload works
- [ ] No errors in logs

✅ **All done? Congrats, you're live!** 🎉

---

## ⚡ POWER TIPS

1. **Auto-Deploy:** Render auto-deploys on every git push
2. **Logs:** Check Render Dashboard → Logs for debugging
3. **Scale:** Upgrade from Free→Starter for no cold starts
4. **Monitor:** Set up email alerts in Render dashboard
5. **Rollback:** `git revert HEAD && git push` to go back

---

## 📞 SUPPORT

- **Render Docs:** https://render.com/docs
- **Flask Help:** https://flask.palletsprojects.com/
- **Supabase Help:** https://supabase.com/docs
- **GitHub Repo:** `sayali23leapforge-glitch/policy-parser`

---

**Created:** February 4, 2026  
**Status:** ✅ Ready to Deploy  
**Next Step:** Run deployment steps above!

🚀 Let's go live!
