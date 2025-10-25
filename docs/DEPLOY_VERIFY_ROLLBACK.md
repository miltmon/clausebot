# ClauseBot Deploy/Verify/Rollback Runbook

**Last Updated:** October 25, 2025  
**Audience:** DevOps, On-call Engineers, Future Maintainers

---

## 🚀 DEPLOY

### Automatic Deployment (Standard)

**Trigger:**
```bash
git push origin main
```

**What Happens:**
1. GitHub Actions CI/CD triggers automatically
2. Backend job:
   - Writes buildinfo.txt with REPO/SHA/DATE
   - Installs dependencies
   - Verifies critical files exist
   - Runs tests and linting
3. Frontend job:
   - Installs dependencies (npm ci)
   - Runs linting and type checks
   - Builds production bundle
   - Performs link checking
4. Integration job:
   - Tests production API health
   - Verifies CORS preflight
5. Render auto-deploys backend (on main branch push)
6. Vercel auto-deploys frontend (on main branch push)

**Expected Duration:**
- CI/CD: ~50-60 seconds
- Render deploy: 2-3 minutes
- Vercel deploy: 60-90 seconds
- **Total:** 4-5 minutes

---

### Manual Deployment (Emergency/Testing)

**Render (Backend):**
1. Go to: https://dashboard.render.com/web/srv-d37fjc0gjchc73c8gfs0
2. Click "Manual Deploy" tab
3. Click "Deploy latest commit"
4. Monitor logs for success

**Vercel (Frontend):**
1. Go to: https://vercel.com/miltmonllc/clausebot
2. Click "Deployments" tab
3. Find desired commit
4. Click "Redeploy"

---

## ✅ VERIFY

### Automated Verification Script

```powershell
cd c:\ClauseBot_API_Deploy\clausebot
.\scripts\verify-full-stack.ps1 -FrontendUrl "https://clausebot.vercel.app"
```

**Expected Output:**
```
Results: 8/8 checks passed (100%)
🎉 DEPLOYMENT SUCCESSFUL - ALL SYSTEMS OPERATIONAL!
```

---

### Manual Verification Checklist

#### Backend Health Checks

```powershell
# Basic health
Invoke-RestMethod https://clausebot-api.onrender.com/health
# Expected: {"ok": true, "service": "clausebot-api", "version": "0.1.0"}

# Build info (verify correct repo/SHA/date)
Invoke-RestMethod https://clausebot-api.onrender.com/buildinfo
# Expected: {"REPO": "miltmon/clausebot", "SHA": "abc1234...", "DATE": "2025-10-25T..."}

# Airtable connection
Invoke-RestMethod https://clausebot-api.onrender.com/health/airtable
# Expected: {"status": "connected", "configured": true}

# Quiz baseline
Invoke-RestMethod https://clausebot-api.onrender.com/health/quiz/baseline
# Expected: {"status": "connected", "eligible_in_sample": 93}
```

#### Frontend Checks

```powershell
# Homepage loads
(Invoke-WebRequest https://clausebot.vercel.app -UseBasicParsing).StatusCode
# Expected: 200

# /blank redirect
try { Invoke-WebRequest "https://clausebot.vercel.app/blank" -MaximumRedirection 0 } catch { $_.Exception.Response.StatusCode.value__ }
# Expected: 307 or 308

# /module-1 redirect
try { Invoke-WebRequest "https://clausebot.vercel.app/module-1" -MaximumRedirection 0 } catch { $_.Exception.Response.StatusCode.value__ }
# Expected: 308 or 301
```

#### CORS Verification

```powershell
# Preflight check
curl -i -X OPTIONS https://clausebot-api.onrender.com/health `
  -H "Origin: https://clausebot.vercel.app" `
  -H "Access-Control-Request-Method: GET" `
  | Select-String "access-control-allow-origin"
# Expected: access-control-allow-origin: https://clausebot.vercel.app
```

#### Browser Console Check

1. Open: https://clausebot.vercel.app
2. Open DevTools (F12) → Console tab
3. Verify: No CORS errors
4. Verify: No 404 errors
5. Verify: GA4 events firing (if configured)

---

## 🔄 ROLLBACK

### When to Rollback

**Immediate rollback if:**
- ❌ `/health` endpoints return 5xx errors
- ❌ Frontend shows critical errors in console
- ❌ CORS errors preventing frontend/backend communication
- ❌ Database connection failures
- ❌ User-facing functionality broken

**Investigate first if:**
- ⚠️ Linting warnings in CI
- ⚠️ TypeScript type warnings
- ⚠️ Link checker warnings
- ⚠️ Performance degradation (but app functional)

---

### Rollback Procedure - Backend (Render)

**Option 1: Via Dashboard (Fastest)**

1. Go to: https://dashboard.render.com/web/srv-d37fjc0gjchc73c8gfs0/events
2. Find the last known-good deploy
3. Click the "Rollback" button next to that deploy
4. Confirm rollback
5. Wait 2-3 minutes for deploy to complete
6. Verify with health checks

**Option 2: Via Git Revert**

```bash
# Identify bad commit
git log --oneline -5

# Revert the commit (creates new commit)
git revert <bad-commit-sha>

# Push to trigger new deploy
git push origin main
```

**Expected Rollback Time:** 2-4 minutes

---

### Rollback Procedure - Frontend (Vercel)

**Option 1: Via Dashboard (Fastest)**

1. Go to: https://vercel.com/miltmonllc/clausebot/deployments
2. Find the last known-good deployment
3. Click the "..." menu → "Promote to Production"
4. Confirm promotion
5. Wait ~30 seconds
6. Verify frontend loads correctly

**Option 2: Via Git Revert**

```bash
# Same as backend
git revert <bad-commit-sha>
git push origin main
```

**Expected Rollback Time:** 30-60 seconds

---

### Rollback Procedure - Both Simultaneously

If a commit affected both backend and frontend:

```bash
# Revert the problematic commit
git revert <bad-commit-sha>
git push origin main

# Both platforms will auto-deploy the reverted state
# Monitor Render (2-3 min) and Vercel (30-60 sec)
```

---

## 📊 POST-ROLLBACK

### Verification After Rollback

1. Run full verification script
2. Check `/buildinfo` to confirm correct SHA
3. Verify user-facing functionality
4. Check monitoring dashboards for normal metrics

### Root Cause Analysis

After successful rollback:

1. **Review the failed deploy:**
   - Check Render logs: https://dashboard.render.com/web/srv-d37fjc0gjchc73c8gfs0/logs
   - Check Vercel logs: https://vercel.com/miltmonllc/clausebot/deployments
   - Review GitHub Actions logs

2. **Document the incident:**
   - What broke?
   - What commit caused it?
   - How was it detected?
   - How long was the issue present?
   - What was the fix?

3. **Prevent recurrence:**
   - Add CI checks if possible
   - Update documentation
   - Consider additional testing

---

## 🚨 EMERGENCY CONTACTS

**Platforms:**
- Render Dashboard: https://dashboard.render.com
- Vercel Dashboard: https://vercel.com/miltmonllc
- GitHub Repository: https://github.com/miltmon/clausebot

**Monitoring:**
- Health Endpoint: https://clausebot-api.onrender.com/health
- Frontend: https://clausebot.vercel.app

**Documentation:**
- This runbook: `docs/DEPLOY_VERIFY_ROLLBACK.md`
- Troubleshooting: `RENDER_TROUBLESHOOTING.md`
- Migration history: `MIGRATION_SUCCESS_REPORT.md`

---

## 📝 DEPLOYMENT LOG TEMPLATE

```markdown
## Deployment - [DATE]

**Deployer:** [NAME]
**Commit:** [SHA]
**Type:** [Routine/Hotfix/Rollback]

### Changes
- [Description of what changed]

### Verification
- [ ] All health checks passing
- [ ] /buildinfo shows correct SHA
- [ ] Frontend loads without errors
- [ ] CORS functioning correctly
- [ ] No console errors
- [ ] Redirects working

### Issues Encountered
[None / Description]

### Resolution Time
[X minutes]

### Status
✅ Success / ❌ Rolled Back
```

---

## 🎯 SUCCESS CRITERIA

**A deployment is successful when:**
- ✅ All health endpoints return 200 OK
- ✅ `/buildinfo` shows expected SHA and date
- ✅ Frontend loads without console errors
- ✅ All redirects function correctly
- ✅ CORS allows frontend/backend communication
- ✅ Automated verification passes 8/8 checks
- ✅ No user-reported issues within 24 hours

---

## 🔧 COMMON ISSUES & SOLUTIONS

### Issue: "Build failed on Render"
**Symptoms:** Deploy shows "Build failed" status  
**Check:** Render logs for error messages  
**Common Causes:**
- Missing dependencies in requirements.txt
- Python syntax errors
- Missing environment variables
- Docker build failure

**Solution:**
1. Check logs for specific error
2. Fix in code
3. Commit and push
4. Monitor new deploy

---

### Issue: "Vercel build failed"
**Symptoms:** Deploy shows "Failed" status in Vercel  
**Check:** Vercel deployment logs  
**Common Causes:**
- TypeScript errors
- Missing dependencies
- Environment variable not set
- Build command failure

**Solution:**
1. Check logs for specific error
2. Fix in code or configuration
3. Commit and push
4. Monitor new deploy

---

### Issue: "CORS errors in browser"
**Symptoms:** Console shows "blocked by CORS policy"  
**Check:** Backend CORS configuration  
**Solution:**
1. Verify `backend/clausebot_api/main.py` includes correct origins
2. Check `allow_origin_regex` includes Vercel pattern
3. Redeploy backend if changes needed
4. Verify with CORS preflight check

---

### Issue: "Health endpoint returns 503"
**Symptoms:** `/health/airtable` or `/health/quiz` returns 503  
**Check:** Airtable connection and environment variables  
**Common Causes:**
- Invalid AIRTABLE_API_KEY
- Network connectivity issues
- Airtable API rate limiting

**Solution:**
1. Verify environment variables in Render
2. Check Airtable API status
3. Review Render logs for connection errors
4. Consider implementing retry logic

---

**Last Updated:** October 25, 2025  
**Version:** 1.0  
**Next Review:** December 1, 2025

