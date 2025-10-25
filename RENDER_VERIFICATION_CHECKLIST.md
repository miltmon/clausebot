# Render Deployment Verification Checklist

**Date:** October 25, 2025 at 9:45 AM PDT  
**Latest Commit:** `81f7b2b` - "feat(system): add /buildinfo endpoint for deployment verification"

---

## ✅ BUILDINFO ENDPOINT ADDED

**New feature deployed in this commit:**
- Added `/buildinfo` endpoint to definitively show which code is live
- CI/CD writes `buildinfo.txt` with REPO, SHA, and DATE
- Endpoint reads this file and returns deployment metadata

**Once deployed, you can verify with:**
```powershell
Invoke-RestMethod https://clausebot-api.onrender.com/buildinfo | ConvertTo-Json
```

---

## 📋 60-SECOND RENDER CHECK (Do This NOW)

### Step 1: Check Render Settings

**Open:** https://dashboard.render.com/web/srv-d37fjc0gjchc73c8gfs0/settings

**Scroll to "Build & Deploy" section and record:**

```
Repository: _________________ (clausebot-api OR clausebot?)
Root Directory: _____________ (empty OR backend?)
Branch: _____________________ (should be main)
```

### Step 2: Check Latest Deploy

**Open:** https://dashboard.render.com/web/srv-d37fjc0gjchc73c8gfs0/events

**Find most recent deploy and record:**

```
Status: _____________________ (Live/Failed/Building)
Commit Hash: ________________ (short SHA like 81f7b2b)
Repository: _________________ (which repo was used?)
Time: _______________________ (when it deployed)
```

---

## 🎯 NEXT STEPS BASED ON YOUR FINDINGS

### IF Repository = `clausebot-api` (OLD REPO)

**Action: Reconnect to Monorepo**

1. **In Render Settings → Build & Deploy:**
   - Click edit icon next to Repository
   - Select: `miltmon/clausebot`
   - Branch: `main`
   - Root Directory: `backend` (exactly this, no slashes)
   - Save Changes

2. **Trigger Manual Deploy:**
   - Go to "Manual Deploy" tab
   - Click "Deploy latest commit"
   - Should deploy commit `81f7b2b`

3. **Wait 2-3 minutes for deploy**

4. **Verify with buildinfo:**
   ```powershell
   Invoke-RestMethod https://clausebot-api.onrender.com/buildinfo
   # Should show: REPO=miltmon/clausebot, SHA=81f7b2b...
   ```

---

### IF Repository = `clausebot` (NEW REPO) ✅

**Scenario A: Already on commit 81f7b2b**
- 🎉 **Migration Complete!**
- Test buildinfo endpoint (should work immediately)
- Proceed to Vercel frontend deployment

**Scenario B: On older commit (348774a or earlier)**
- Trigger manual deploy to get latest commit
- Wait 2-3 minutes
- Test buildinfo endpoint
- Proceed to Vercel frontend deployment

---

## 🧪 VERIFICATION COMMANDS

**After any deploy completes, run these:**

```powershell
# 1. Basic health
(Invoke-WebRequest https://clausebot-api.onrender.com/health -UseBasicParsing).StatusCode
# Expected: 200

# 2. Build info (NEW!)
Invoke-RestMethod https://clausebot-api.onrender.com/buildinfo | ConvertTo-Json
# Expected: 
# {
#   "REPO": "miltmon/clausebot",
#   "SHA": "81f7b2b...",
#   "DATE": "2025-10-25T16:45:00Z"
# }

# 3. Airtable health
(Invoke-WebRequest https://clausebot-api.onrender.com/health/airtable -UseBasicParsing).StatusCode
# Expected: 200

# 4. Quiz baseline
Invoke-RestMethod https://clausebot-api.onrender.com/health/quiz/baseline | ConvertTo-Json
# Expected: status=connected, sample_size, eligible_in_sample
```

---

## 📊 STATUS REPORT TEMPLATE

**After checking Render, paste this:**

```
=== RENDER CURRENT CONFIGURATION ===
Repository: [paste here]
Root Directory: [paste here]
Branch: [paste here]

=== LATEST DEPLOY ===
Status: [paste here]
Commit: [paste here]
Time: [paste here]

=== BUILDINFO ENDPOINT (if live) ===
[paste JSON output or "not yet deployed"]
```

---

## 🚀 FINAL PHASE AFTER VERIFICATION

Once backend shows correct `buildinfo`:
1. ✅ Backend migration confirmed complete
2. 🚀 Deploy Vercel frontend from monorepo
3. ✅ Run comprehensive smoke tests
4. ✅ Archive old `clausebot-api` repository
5. ✅ Archive old `clausebotai` repository
6. 🎉 **WEEKEND DEBUGGING LOOP CLOSED!**

---

**Execute the 60-second check now and report your findings!**

