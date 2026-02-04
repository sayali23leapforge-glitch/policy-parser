# ZohoSigner Backend - Quick Start Guide

## ⚡ 5-Minute Setup

### Step 1: Create Database Table
1. Go to [Supabase Console](https://app.supabase.com)
2. Open your project's SQL Editor
3. Copy and paste the entire contents of `ZOHO_FORMS_SCHEMA.sql`
4. Click "Run"

### Step 2: Verify Environment
Check `.env.local` has:
```
VITE_SUPABASE_URL=your_url
VITE_SUPABASE_SERVICE_ROLE_KEY=your_key
FLASK_PORT=5000
```

### Step 3: Start Backend
```bash
cd d:/Auto\ dashboard
python backend/app.py
```

You should see:
```
* Running on http://0.0.0.0:5000
* Restarting with reloader
```

### Step 4: Test the Form
1. Open `zoho signer auto.html` in your browser
2. Click "Auto Signer" tab
3. Select a form (e.g., "PAC Form (Auto)")
4. Upload a PDF
5. Fill in signer info:
   - Name: "Test Client"
   - Email: "test@example.com"
6. Click "Process"
7. You should see: "Form Submitted - Form ID: [UUID]"

### Step 5: Verify Data
In Supabase SQL Editor, run:
```sql
SELECT form_id, signer_email, status, created_at 
FROM zoho_forms 
ORDER BY created_at DESC 
LIMIT 5;
```

You should see your submission!

---

## 📁 What Was Added

### Backend Code
- `backend/app.py` - Added 3 new routes (lines ~1350+):
  - `POST /process-form` - Main form processor
  - `POST /zoho-webhook` - Placeholder for Zoho webhooks
  - `GET /oauth/callback` - Placeholder for OAuth

### Database
- `ZOHO_FORMS_SCHEMA.sql` - SQL to create `zoho_forms` table

### Frontend
- `zoho signer auto.html` - Updated to send data to backend:
  - `submitFormToBackend()` - New function
  - `executeAutoSignerAction()` - Updated to call backend

### Documentation
- `ZOHO_BACKEND_SETUP.md` - Complete setup guide
- `ZOHO_IMPLEMENTATION_CHECKLIST.md` - Implementation details
- `ZOHO_QUICK_START.md` - This file

---

## 🎯 What Happens When User Clicks "Process"

1. **Frontend** collects:
   - PDF file (from upload)
   - Form name
   - Signer name/email
   - Broker name/email

2. **Sends to backend**: `POST /process-form`

3. **Backend**:
   - Validates PDF
   - Generates UUID (form_id)
   - Saves PDF to `/uploads/`
   - Inserts record in `zoho_forms` table
   - Returns `form_id` + status

4. **Frontend**:
   - Shows success notification
   - Displays form_id

---

## ✅ Verification Checklist

- [ ] Backend starts without errors
- [ ] Can upload PDF without errors
- [ ] Form submission shows success message
- [ ] Form ID is displayed
- [ ] Check `/uploads/` folder - PDF is there
- [ ] Check Supabase - row exists in `zoho_forms` table
- [ ] Row has correct email, form name, status

---

## 🔧 If Something Goes Wrong

**Backend won't start:**
```bash
pip install -r backend/requirements.txt
```

**"Table zoho_forms does not exist":**
- Run ZOHO_FORMS_SCHEMA.sql in Supabase

**"File not saved":**
- Check `/uploads/` folder exists
- Check write permissions on folder

**"No response from backend":**
- Is backend running? (should see `Running on http://0.0.0.0:5000`)
- Is frontend trying to connect? (check browser console for errors)
- Is FLASK_PORT correct in `.env.local`?

---

## 🎓 Next Steps (Not Yet Implemented)

When ready, implement:
1. **Zoho API Integration** - Send forms to Zoho for signing
2. **Webhook Handler** - Receive completion notifications from Zoho
3. **OAuth2** - Authenticate with Zoho API
4. **Email Notifications** - Notify when signatures complete

See `ZOHO_BACKEND_SETUP.md` for details.

---

## 📞 File Locations

| File | Purpose |
|------|---------|
| `backend/app.py` | Backend routes |
| `ZOHO_FORMS_SCHEMA.sql` | Database schema |
| `zoho signer auto.html` | Frontend form |
| `ZOHO_BACKEND_SETUP.md` | Full documentation |
| `/uploads/` | Uploaded PDFs |

---

That's it! You're ready to test the ZohoSigner backend. 🎉
