# 🏗️ Deployment Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         YOUR LOCAL MACHINE                       │
│                     (d:\Auto dashboard)                          │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Source Code                                              │   │
│  │ ├── backend/                                             │   │
│  │ │   ├── app.py (Flask application)                       │   │
│  │ │   ├── pdf_parser.py (PDF extraction)                   │   │
│  │ │   └── __init__.py (exports app, socketio)              │   │
│  │ ├── HTML Pages                                           │   │
│  │ │   ├── index.html                                       │   │
│  │ │   ├── Auto dashboard.html                              │   │
│  │ │   ├── coverpage.html                                   │   │
│  │ │   └── property.html                                    │   │
│  │ ├── Configuration                                        │   │
│  │ │   ├── Procfile                                         │   │
│  │ │   ├── render.yaml                                      │   │
│  │ │   ├── requirements.txt                                 │   │
│  │ │   └── runtime.txt                                      │   │
│  │ └── .gitignore (excludes secrets)                        │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           ↓                                      │
│                    git add . && git push                         │
│                           ↓                                      │
└─────────────────────────────────────────────────────────────────┘
                            ↓
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                      GITHUB REPOSITORY                           │
│            sayali23leapforge-glitch/policy-parser               │
│                                                                   │
│  Branch: main                                                    │
│  Auto webhook trigger enabled                                   │
└─────────────────────────────────────────────────────────────────┘
                            ↓
                            ↓
                    (Automatic trigger)
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                      RENDER.COM SERVICE                          │
│                  auto-dashboard-parser                           │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ BUILD STEP (3-5 minutes)                                 │   │
│  │ 1. Clone repository                                      │   │
│  │ 2. pip install -r requirements.txt                       │   │
│  │ 3. Setup static assets                                   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           ↓                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ START COMMAND                                            │   │
│  │ gunicorn -w 4 -b 0.0.0.0:$PORT backend.app:app          │   │
│  │                                                          │   │
│  │ ✓ Allocates port dynamically                            │   │
│  │ ✓ Starts 4 worker processes                             │   │
│  │ ✓ Loads Flask app from backend module                   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           ↓                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ RUNNING SERVICE                                          │   │
│  │ https://auto-dashboard-parser.onrender.com              │   │
│  │                                                          │   │
│  │ Environment Variables Loaded:                           │   │
│  │ ├── VITE_SUPABASE_URL                                   │   │
│  │ ├── VITE_SUPABASE_SERVICE_ROLE_KEY                      │   │
│  │ ├── META_* tokens                                       │   │
│  │ ├── ZOHO_* credentials                                  │   │
│  │ └── FB_PIXEL_ID                                         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ FLASK APPLICATION                                        │   │
│  │                                                          │   │
│  │ Routes:                                                  │   │
│  │ ├── GET  / (index.html)                                 │   │
│  │ ├── GET  /dashboard (Auto dashboard.html)               │   │
│  │ ├── POST /api/parse-quote (PDF parsing)                 │   │
│  │ ├── POST /meta/webhook (Facebook leads)                 │   │
│  │ ├── GET  /api/health (status check)                     │   │
│  │ └── WebSocket /socket (real-time updates)               │   │
│  │                                                          │   │
│  │ External Services:                                       │   │
│  │ ├── Supabase (Database)                                 │   │
│  │ ├── Meta/Facebook (Lead API)                            │   │
│  │ └── Zoho (CRM integration)                              │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ SSL/HTTPS                                                │   │
│  │ ✓ Automatic certificate                                 │   │
│  │ ✓ Auto renewal                                          │   │
│  │ ✓ All traffic encrypted                                 │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                            ↓
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                    END USERS / CLIENTS                           │
│                                                                   │
│  Browser → https://auto-dashboard-parser.onrender.com           │
│                                                                   │
│  Features:                                                       │
│  ├── Upload PDF/JSON quotes                                     │
│  ├── Auto-parse policy data                                     │
│  ├── Generate cover page summary                                │
│  ├── Manage property information                                │
│  ├── Submit PAC forms                                           │
│  └── Real-time updates via WebSocket                            │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### Upload & Processing Flow
```
User Upload File (PDF/JSON)
        ↓
Frontend: POST /api/parse-quote
        ↓
Backend: pdf_parser.py
├── Extract text from PDF
├── Parse policy information
└── Return structured JSON
        ↓
Frontend: Display extracted data
        ↓
Supabase: Save to database
        ↓
User: View/Edit form
```

### Real-Time Updates Flow
```
Backend Event (new lead/update)
        ↓
SocketIO Emit Event
        ↓
Browser WebSocket Connection
        ↓
Real-time UI Update
```

### Webhook Integration Flow
```
Meta/Facebook Server
        ↓
POST /meta/webhook
        ↓
Verify Signature (Security)
        ↓
Process Lead Data
        ↓
Store in Supabase
        ↓
Emit to Connected Clients
```

---

## File Routing

```
RENDER SERVER
│
├── GET / 
│   └── Serves: index.html
│
├── GET /dashboard
│   └── Serves: Auto dashboard.html
│
├── GET /coverpage
│   └── Serves: coverpage.html
│
├── GET /property
│   └── Serves: property.html
│
├── POST /api/parse-quote
│   └── Calls: backend/pdf_parser.py
│       ├── parse_mvr_pdf()
│       ├── parse_dash_pdf()
│       └── parse_quote_pdf()
│
├── POST /api/save-data
│   └── Saves to: Supabase (database)
│
├── POST /meta/webhook
│   └── Receives: Facebook lead events
│
├── GET /api/health
│   └── Returns: Status JSON
│
└── WebSocket /socket
    └── Real-time: SocketIO events
```

---

## Deployment Timeline

```
Timeline (Total: 3-5 minutes from push to live)

Time   Event                          Status
────   ─────────────────────────────  ──────────
0:00   Push to GitHub                 ✓ Trigger
0:05   Render detects change          ✓ Notification
0:10   Clone repository               ⟳ Building
1:30   Install dependencies           ⟳ Building
2:45   Build complete                 ✓ Ready
3:00   Start gunicorn server          ⟳ Starting
3:15   Server listening on port       ✓ Available
       All routes responding          ✓ LIVE
3:30   Render health check passes     ✓ GREEN
```

---

## Environment Setup

### Development (Local)
```
http://localhost:5000
├── Backend: Backend/app.py (debug mode)
├── Frontend: HTML files (in root)
├── Database: Supabase (cloud)
├── Secrets: .env.local (local)
└── Logs: console output
```

### Production (Render)
```
https://auto-dashboard-parser.onrender.com
├── Backend: Gunicorn (4 workers)
├── Frontend: Served by Gunicorn + Flask
├── Database: Supabase (cloud)
├── Secrets: Environment variables (Render dashboard)
├── Logs: Render dashboard → Logs tab
├── SSL: Automatic Let's Encrypt
└── Monitoring: Render dashboard → Monitoring
```

---

## Scaling Architecture

### Current Setup
```
Render Web Service
├── Instance: Free / Starter
├── RAM: 512MB / 1GB
├── vCPU: Shared
├── Workers: 4 (gunicorn)
└── Cold start: 30-60s (free tier only)
```

### Growth Path
```
Step 1: Free Tier
└── Good for: Testing, low traffic
    Cost: $0/month
    Limitation: Sleeps after 15 min inactivity

Step 2: Starter Tier
└── Good for: Production, consistent traffic
    Cost: $7/month
    Benefit: Always on, no cold starts

Step 3: Standard Tier
└── Good for: High traffic
    Cost: $25/month
    Benefit: 1GB RAM, auto-scaling

Step 4: Pro Tier
└── Good for: Enterprise
    Cost: $75+/month
    Benefit: Full auto-scaling, load balancing
```

---

## Security Architecture

```
HTTPS/SSL
    │
    ↓
Render Edge (DDoS protection)
    │
    ↓
Flask CORS (Cross-origin validation)
    │
    ↓
Route Handlers
    ├── POST /meta/webhook
    │   └── Verify HMAC signature (security)
    │
    ├── POST /api/parse-quote
    │   └── Validate file type
    │
    └── All other routes
        └── Rate limiting (optional)
    │
    ↓
Supabase
    ├── Row-level security (RLS)
    ├── Role-based access (RBAC)
    └── Encrypted secrets
    │
    ↓
External APIs
    ├── Meta: Bearer token
    ├── Zoho: OAuth2
    └── Supabase: Service role key (never exposed)
```

---

## Monitoring & Alerting

### What to Monitor
```
Render Dashboard → Monitoring Tab

1. Response Time (Target: <500ms)
2. Error Rate (Target: <1%)
3. Memory Usage (Target: <80%)
4. CPU Usage (Target: <50%)
5. Active Instances (Should be 1)
6. Request Count (Trend analysis)
```

### Logs Access
```
Render Dashboard → Logs Tab

Types:
├── Build Logs (deployment issues)
├── Runtime Logs (application output)
└── Error Logs (exceptions)

Search: grep "ERROR" or "Exception"
Tail: Real-time log streaming
```

---

## Disaster Recovery

### If Deployment Fails
```
1. Check Render Logs → Logs tab
2. Common issues:
   ├── Module not found → requirements.txt missing
   ├── Port error → $PORT not in config
   ├── Import error → backend/__init__.py
   └── Env var missing → Check Render env vars

3. Fix locally:
   ├── python run.py (test)
   ├── git commit
   ├── git push origin main

4. Render auto-redeploys
```

### If Service Goes Down
```
1. Render automatically restarts (unless fatal)
2. Check status: render.com → service page
3. Manual restart:
   ├── Click service
   ├── Click "Manual Deploy"
   ├── Select "Deploy latest commit"

4. Investigate:
   ├── Render Logs
   ├── Recent commits
   ├── Environment variables
```

### Rollback Strategy
```
If new code breaks production:

1. Revert last commit:
   git revert HEAD
   git push origin main

2. Render auto-deploys previous version

3. Investigate issue:
   - Check logs
   - Test locally
   - Fix and re-deploy
```

---

## Performance Optimization

### Current Setup
```
Metrics:
├── Server response: ~100-200ms
├── Page load: ~1-2s
├── PDF parsing: 2-10s (depends on file size)
└── Database query: ~100-500ms
```

### If Performance Degrades
```
Step 1: Upgrade instance
- Free → Starter ($7/mo): Huge improvement

Step 2: Optimize code
- Cache results
- Lazy load assets
- Compress images

Step 3: Database optimization
- Add indexes in Supabase
- Query optimization
- Connection pooling
```

---

## Success Criteria ✅

After deployment, verify:

```
☑ Service status: Green (running)
☑ Response time: <1000ms
☑ Error rate: 0%
☑ SSL certificate: Valid (🔒 in browser)
☑ All pages load: / ✓ /dashboard ✓ /coverpage ✓
☑ API endpoints: /api/health ✓
☑ File upload: PDF/JSON ✓
☑ WebSocket: Real-time updates ✓
☑ Database: Supabase connected ✓
☑ Webhooks: Meta integration ✓
```

Once all checks pass: 🎉 **DEPLOYMENT SUCCESSFUL**

---

**Generated:** February 4, 2026  
**For:** Auto Dashboard Policy Parser  
**Target Platform:** Render Web Service  
**Status:** Ready for Production
