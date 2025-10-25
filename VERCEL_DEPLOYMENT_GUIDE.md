# Vercel Frontend Deployment Guide - ClauseBot Monorepo

**Date:** October 25, 2025 at 10:05 AM PDT  
**Backend Status:** ✅ LIVE on Render (miltmon/clausebot)  
**Frontend Status:** ⏳ AWAITING DEPLOYMENT

---

## ✅ PRE-DEPLOYMENT VERIFICATION

**All prerequisites confirmed:**
- ✅ `frontend/package-lock.json` exists and synced
- ✅ `frontend/vercel.json` with redirects configured
- ✅ Monorepo structure correct on GitHub
- ✅ Backend API operational at https://clausebot-api.onrender.com
- ✅ CORS configured for `*.vercel.app` domains

---

## 🚀 DEPLOYMENT STEPS (5 Minutes)

### Step 1: Open Vercel Import Page

**URL:** https://vercel.com/new

**Action:** Click to open in browser

---

### Step 2: Import Repository

**Search for:** `miltmon/clausebot`

**Action:** Click **"Import"** button next to the repository

**Note:** If you don't see it, you may need to:
- Refresh Vercel's GitHub app permissions
- Or use "Import from Git" and connect to GitHub

---

### Step 3: Configure Project Settings

**CRITICAL CONFIGURATION:**

| Setting | Value | Notes |
|---------|-------|-------|
| **Project Name** | `clausebot` | Or your preference |
| **Framework Preset** | `Vite` | Should auto-detect |
| **Root Directory** | `frontend` | ⚠️ **MUST CLICK "EDIT" AND TYPE THIS** |
| **Build Command** | `npm run build` | Auto-detected |
| **Output Directory** | `dist` | Auto-detected |
| **Install Command** | `npm ci` | Recommended |

**⚠️ CRITICAL:** The **Root Directory** field defaults to empty. You MUST:
1. Click the **"Edit"** button next to Root Directory
2. Type: `frontend`
3. Confirm the change

---

### Step 4: Add Environment Variables

**Click "Environment Variables" dropdown**

**Add Variable 1:**
```
Name: VITE_API_BASE
Value: https://clausebot-api.onrender.com
Environments: ☑ Production  ☑ Preview  ☐ Development
```

**Add Variable 2:**
```
Name: VITE_GA_ID
Value: [YOUR GA4 MEASUREMENT ID]
Environments: ☑ Production  ☐ Preview  ☐ Development
```

**To find your GA4 ID:**
- Format: `G-XXXXXXXXXX`
- Found in: Google Analytics → Admin → Property Settings → Measurement ID

---

### Step 5: Deploy

**Action:** Click the **"Deploy"** button

**Monitor Build Logs:**

You should see:
```
▲ Cloning miltmon/clausebot (Branch: main)
▲ Using root directory: frontend
▲ Installing dependencies (npm ci)
▲ Building application (npm run build)
▲ Uploading build outputs
✓ Build completed in 60-90s
✓ Deployment Ready
```

**Expected Duration:** 60-120 seconds

---

## 📋 DEPLOYMENT URL FORMAT

**Vercel will provide a URL like:**
```
https://clausebot-[random-hash].vercel.app
```

**Examples:**
- `https://clausebot-abc123xyz.vercel.app`
- `https://clausebot-git-main-miltmonllc.vercel.app`

**Copy this entire URL!**

---

## 🧪 QUICK SELF-VERIFICATION

**Before reporting back, quickly test:**

### Test 1: Homepage Loads
```
Open: https://clausebot-[your-hash].vercel.app/
Expected: Page loads without errors (200 OK)
```

### Test 2: Blank Redirect
```
Open: https://clausebot-[your-hash].vercel.app/blank
Expected: Redirects to / (308 redirect)
```

### Test 3: Console Check
```
1. Open browser DevTools (F12)
2. Go to Console tab
3. Reload page
4. Expected: No red errors about API or CORS
```

---

## 📊 REPORT BACK TEMPLATE

**After deployment completes, paste this:**

```
✅ VERCEL DEPLOYMENT COMPLETE

Deployment URL: https://clausebot-[paste-your-hash].vercel.app
Status: [Live/Failed]
Build Time: [XX seconds]

Quick Tests:
- Homepage loads: [Yes/No]
- /blank redirects: [Yes/No]  
- Console errors: [None/List them]
```

---

## 🚨 TROUBLESHOOTING

### Error: "Root directory not found"
**Fix:** Make sure you clicked "Edit" and typed `frontend` exactly

### Error: "package.json not found"
**Fix:** Root directory is wrong - should be `frontend`, not empty or `/frontend`

### Error: "Build failed - npm ci"
**Fix:** Check that `package-lock.json` is committed and synced

### Warning: "Environment variable VITE_API_BASE is not set"
**Fix:** Add environment variables in Vercel project settings

### CORS errors in browser console
**Fix:** Backend should already be configured for `*.vercel.app`, but verify:
- Backend has `allow_origin_regex=r"https://.*\.vercel\.app"`
- Commit `c14d194` deployed to Render

---

## 🎯 WHAT HAPPENS NEXT

**Once you provide the Vercel URL, I will:**

1. ✅ **Run Comprehensive Verification:**
   - Frontend loads (200 OK)
   - All redirects working (308/301)
   - CORS functionality
   - API connectivity
   - GA4 tracking

2. ✅ **Provide Archive Scripts:**
   - Archive old `clausebot-api` repository
   - Archive old `clausebotai` repository

3. ✅ **Generate Final Success Report:**
   - Complete deployment receipts
   - Performance metrics
   - Next steps for custom domain (if needed)

4. 🎉 **WEEKEND LOOP CLOSURE CONFIRMED!**

---

## ⏱️ TIMELINE

**Current:** 10:05 AM PDT  
**Expected Completion:** 10:12 AM PDT (7 minutes)

**Breakdown:**
- Vercel configuration: 2 minutes
- Build & deploy: 2 minutes
- Quick self-test: 1 minute
- Report back: 1 minute
- Automated verification: 1 minute

---

**Execute the deployment now and paste your Vercel URL when complete!** 🚀

