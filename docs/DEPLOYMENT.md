# ClauseBot Deployment Guide

**Created:** October 25, 2025  
**Purpose:** Unified deployment guide for monorepo

---

## **Architecture**

**Monorepo Structure:**
```
clausebot/
├── backend/   → Render (Python/FastAPI)
└── frontend/  → Vercel (React/Vite)
```

**Production URLs:**
- Backend API: https://clausebot-api.onrender.com
- Frontend: https://clausebot.miltmonndt.com

---

## **Backend Deployment (Render)**

### **Service Configuration**
1. **Connect Repository:** Link to `github.com/miltmon/clausebot` (or new repo)
2. **Settings:**
   - Name: `clausebot-api`
   - Environment: `Python 3`
   - Region: `Oregon (US West)`
   - Branch: `main`
   - **Root Directory:** `backend`
   - Build Command: (auto-detected or `pip install -r requirements.txt`)
   - Start Command: `uvicorn clausebot_api.main:app --host 0.0.0.0 --port $PORT`

### **Environment Variables**
```env
AIRTABLE_API_KEY=<your_key>
AIRTABLE_BASE_ID=appJQ23u70iwOl5Nn
AIRTABLE_TABLE=Questions
AIRTABLE_VIEW=Grid view
ENABLE_CATEGORY_FILTER=0
EXCLUDE_NEEDS_VALIDATION=1
```

### **Health Check**
- Path: `/health`
- Interval: 10s
- Timeout: 5s
- Unhealthy threshold: 3
- Grace period: 30s

---

## **Frontend Deployment (Vercel)**

### **Project Configuration**
1. **Import Repository:** Connect to monorepo
2. **Settings:**
   - Framework Preset: `Vite`
   - **Root Directory:** `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install`

### **Environment Variables**
```env
VITE_API_BASE=https://clausebot-api.onrender.com
VITE_GA_ID=G-XXXXXXXX
```

### **Domain**
- Production: `clausebot.miltmonndt.com`
- Preview: `*.vercel.app`

---

## **Post-Deployment Verification**

### **Automated Tests**
```powershell
# From monorepo root
.\scripts\smoke.ps1
```

### **Manual Checks**
1. Backend health: https://clausebot-api.onrender.com/health
2. Airtable health: https://clausebot-api.onrender.com/health/airtable
3. Quiz endpoint: https://clausebot-api.onrender.com/v1/quiz?count=5
4. Frontend loads: https://clausebot.miltmonndt.com
5. No `/blank` routes (should redirect to `/`)
6. Module-1 redirect works: `/module-1` → `/modules/1`

---

## **CI/CD Pipeline**

**GitHub Actions:** `.github/workflows/monorepo.yml`

**Triggers:**
- Push to `main` → Full test + build
- Pull requests → Test only

**Jobs:**
1. Backend: Python tests, linting, health check simulation
2. Frontend: npm build, type checking, linting
3. Integration: Production API health check

---

## **Troubleshooting**

### **Backend Issues**
- **503 Errors:** Check Render logs, verify Airtable env vars
- **Cold Starts:** First request may take 30-60s (free tier)
- **CORS Errors:** Verify frontend URL in CORS whitelist

### **Frontend Issues**
- **Build Failures:** Check Node version (20+), clear cache
- **API Connection:** Verify `VITE_API_BASE` environment variable
- **Routing Issues:** Check `vercel.json` redirects

### **Deployment Failures**
```bash
# Check local build
cd backend && pytest
cd frontend && npm run build

# Verify GitHub Actions
# Check: https://github.com/<user>/<repo>/actions
```

---

## **Rollback Procedure**

### **Backend (Render)**
1. Go to Render Dashboard → clausebot-api → Manual Deploy
2. Select previous successful commit
3. Click "Deploy"

### **Frontend (Vercel)**
1. Go to Vercel Dashboard → clausebot → Deployments
2. Find last working deployment
3. Click "Promote to Production"

---

## **Migration from Old Repos**

**Archived Repositories:**
- `clausebot-api` → Backend code integrated into `backend/`
- `clausebotai` → Frontend code integrated into `frontend/`

**Benefits:**
- Single CI/CD pipeline
- Coordinated releases
- Simplified maintenance
- No more confusion between repos

---

## **Next Steps**

1. ✅ Monorepo created
2. ⏳ Connect Render (point to `backend/`)
3. ⏳ Connect Vercel (point to `frontend/`)
4. ⏳ Run smoke tests
5. ⏳ Archive old repos
6. ⏳ Update documentation links

---

**Last Updated:** October 25, 2025  
**Maintained by:** MiltmonNDT Platform Team

