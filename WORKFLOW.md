# ClauseBot Enterprise Daily Workflow

## 🚀 One-Command Daily Startup

```powershell
.\scripts\start_local.ps1
```

**What this does:**
- ✅ Activates Python venv automatically
- ✅ Loads `.env` file (if present)
- ✅ Installs/updates dependencies (idempotent)
- ✅ Runs comprehensive preflight checks
- ✅ Starts API server on `http://localhost:8081`

## 📝 Development Workflow (If Code Changes Needed)

```powershell
# Make your edits to clausebot_api/main.py, clausebot_api/airtable_data_source.py, etc.

# Commit and push
git add clausebot_api/*
git commit -m "feat: your update description"
git push origin main
```

**Automated Deployment:**
- 🔄 **Render** auto-deploys backend on push to `main`
- 🔄 **Vercel** auto-deploys frontend on push to `main`
- ⏱️ **No manual intervention required**

## 🔍 Daily Validation Scripts

### Local Environment Check
```powershell
.\scripts\preflight.ps1
```
**Validates:**
- Git repository status and sync
- Python environment and dependencies
- Package entrypoints (`clausebot_api/main.py`, `airtable_data_source.py`)
- Environment variables (`AIRTABLE_*`)
- Direct Airtable API connectivity
- Port availability (8081)

### Production Health Check
```powershell
.\scripts\verify_prod.ps1
```
**Tests:**
- Backend health endpoints
- Airtable connection status
- Quiz API functionality
- Error handling (503/422 responses)
- Stress testing with high question counts

### Platform Independence Check
```powershell
.\scripts\verify_independence.ps1
```
**Verifies:**
- ClauseBot operates independently from other services
- No cross-service dependencies or shared secrets
- Dedicated Airtable data sources
- Proper CORS configuration
- Independent deployment and rollback capabilities

## 🌐 Production Verification

### Frontend Test
Visit: https://miltmonndt.com
- Run a quiz to verify end-to-end functionality
- Test different categories (Fundamentals, Visual Inspection)

### Backend API Test
```powershell
# Basic health
(Invoke-WebRequest 'https://clausebot-api.onrender.com/health').Content

# Airtable connectivity
(Invoke-WebRequest 'https://clausebot-api.onrender.com/health/airtable').Content

# Quiz functionality
(Invoke-WebRequest 'https://clausebot-api.onrender.com/v1/quiz?count=5&category=Fundamentals').Content
```

## 🛡️ Long-Term Stability Practices

### Environment Management
- ✅ Update Render/Vercel environment variables **only** for:
  - Secret rotation (PAT renewal)
  - Domain changes
  - New feature flags
- ❌ **Never** expose PAT or secrets in Git commits
- ✅ Use Render dashboard for production secrets

### Code Stability
- ✅ Keep package names and paths stable (`clausebot_api/`)
- ✅ Maintain consistent entry points
- ✅ Use validation scripts to catch configuration drift

### Monitoring
- 📊 Review Render/Vercel dashboard logs **weekly** (not daily unless errors)
- 🚨 Use validation scripts to catch problems before users do
- 📈 Monitor 422 error rates (indicates low question inventory)

## 🚨 Problem Resolution Map

| Error | Cause | Fix |
|-------|-------|-----|
| **401 Airtable** | PAT wrong/missing scope | Update `AIRTABLE_API_KEY` in Render dashboard |
| **404 Airtable** | Wrong base/table | Verify `AIRTABLE_BASE_ID`/`AIRTABLE_TABLE` |
| **200 but empty** | View/formula filters everything | Check `AIRTABLE_VIEW` and Active field |
| **CORS error** | Frontend blocked | Set `CORS_ALLOW_ORIGINS` in Render |
| **ModuleNotFoundError** | Import path issue | Verify `clausebot_api/` structure |
| **Non-fast-forward push** | Git sync issue | Run `git pull --rebase origin main` |
| **Port in use** | Stale process | Kill old uvicorn (preflight shows PID) |

## 📊 Expected Results

### ✅ Healthy System
- **Preflight:** All green checkmarks
- **Production:** `status: "connected"` from `/health/airtable`
- **Quiz API:** Returns real questions or clean 422 errors
- **Frontend:** Loads and functions without console errors

### 🚨 Problem Indicators
- **Red errors** in validation scripts
- **503/422 responses** from production API
- **CORS errors** in browser console
- **Empty question responses** despite available data

## 🎯 Enterprise Benefits

- **Boringly reliable:** No surprises, predictable operations
- **Observable truth:** Clear visibility into system health
- **Automated validation:** Problems caught before user impact
- **Zero configuration drift:** Consistent environment management
- **One-command startup:** Minimal daily overhead

---

## 🔗 Quick Links

- **Production API:** https://clausebot-api.onrender.com
- **Production Frontend:** https://miltmonndt.com
- **GitHub Repository:** https://github.com/miltmon/clausebot-api
- **Render Dashboard:** https://dashboard.render.com
- **Vercel Dashboard:** https://vercel.com/dashboard

---

*ClauseBot: Enterprise-grade welding education platform with "truth or fail" philosophy*
