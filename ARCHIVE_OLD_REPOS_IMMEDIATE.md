# IMMEDIATE ACTION: Archive Old ClauseBot Repositories

**Created:** October 26, 2025  
**Priority:** 🔴 **CRITICAL**  
**Reason:** Audit revealed old repos causing false negative findings

---

## 🚨 **PROBLEM IDENTIFIED**

External audit found:
- ✅ **CORRECT:** Old `clausebot-api` repo shows 100% CI/CD failures
- ✅ **CORRECT:** Old `clausebotai` repo shows all tests failing
- ❌ **INCORRECT CONCLUSION:** Production is broken

**Root Cause:** Old repos not archived after Oct 25 monorepo migration

---

## 📋 **REPOSITORIES TO ARCHIVE**

### **1. clausebot-api** (Old Backend)
**URL:** https://github.com/miltmon/clausebot-api  
**Status:** Deprecated Oct 25, 2025  
**Replacement:** `github.com/miltmon/clausebot` (backend/ directory)

### **2. clausebotai** (Old Frontend)
**URL:** https://github.com/miltmon/clausebotai  
**Status:** Deprecated Oct 25, 2025  
**Replacement:** `github.com/miltmon/clausebot` (frontend/ directory)

---

## ⚡ **IMMEDIATE ACTIONS (Do Now)**

### **Step 1: Update README Files (Before Archiving)**

#### **clausebot-api README Update**
```markdown
# ⚠️ REPOSITORY ARCHIVED - MOVED TO MONOREPO

**This repository has been deprecated and archived.**

## New Location
**All development moved to:** https://github.com/miltmon/clausebot

**Backend code location:** `backend/` directory in new monorepo

**Migration Date:** October 25, 2025

## Why Archived?
ClauseBot consolidated backend and frontend into a single monorepo for:
- Unified CI/CD pipeline
- Coordinated deployments
- Simplified maintenance
- Single source of truth

## Current Production Services
- **Backend API:** https://clausebot-api.onrender.com
- **Frontend:** https://clausebot.vercel.app
- **Health:** https://clausebot-api.onrender.com/health

## For Developers
- Clone new monorepo: `git clone https://github.com/miltmon/clausebot.git`
- Backend: `cd clausebot/backend`
- Documentation: See monorepo README

---

**This repository is archived for historical reference only.**  
**No further updates will be made here.**
```

#### **clausebotai README Update**
```markdown
# ⚠️ REPOSITORY ARCHIVED - MOVED TO MONOREPO

**This repository has been deprecated and archived.**

## New Location
**All development moved to:** https://github.com/miltmon/clausebot

**Frontend code location:** `frontend/` directory in new monorepo

**Migration Date:** October 25, 2025

## Why Archived?
ClauseBot consolidated backend and frontend into a single monorepo for:
- Unified CI/CD pipeline
- Coordinated deployments
- Simplified maintenance
- Single source of truth

## Current Production Services
- **Frontend:** https://clausebot.vercel.app
- **Backend API:** https://clausebot-api.onrender.com
- **Health Dashboard:** https://clausebot.vercel.app/health

## For Developers
- Clone new monorepo: `git clone https://github.com/miltmon/clausebot.git`
- Frontend: `cd clausebot/frontend`
- Documentation: See monorepo README

---

**This repository is archived for historical reference only.**  
**No further updates will be made here.**
```

---

### **Step 2: Disable GitHub Actions (Before Archiving)**

#### **For clausebot-api:**
1. Go to: https://github.com/miltmon/clausebot-api/settings/actions
2. Click: **"Disable Actions for this repository"**
3. Confirm

#### **For clausebotai:**
1. Go to: https://github.com/miltmon/clausebotai/settings/actions
2. Click: **"Disable Actions for this repository"**
3. Confirm

**Result:** Stops "failing" CI/CD runs that confuse auditors

---

### **Step 3: Disable Webhooks (Optional)**

#### **For clausebot-api:**
1. Go to: https://github.com/miltmon/clausebot-api/settings/hooks
2. For each webhook, click **"Delete"**

#### **For clausebotai:**
1. Go to: https://github.com/miltmon/clausebotai/settings/hooks
2. For each webhook, click **"Delete"**

---

### **Step 4: Archive Repositories**

#### **Archive clausebot-api:**
1. Go to: https://github.com/miltmon/clausebot-api/settings
2. Scroll to: **"Danger Zone"**
3. Click: **"Archive this repository"**
4. Type repository name to confirm
5. Click: **"I understand, archive this repository"**

**Expected Result:**
- Repo marked as archived (read-only)
- Yellow banner: "This repository has been archived"
- No new commits/PRs/issues possible

#### **Archive clausebotai:**
1. Go to: https://github.com/miltmon/clausebotai/settings
2. Scroll to: **"Danger Zone"**
3. Click: **"Archive this repository"**
4. Type repository name to confirm
5. Click: **"I understand, archive this repository"**

---

### **Step 5: Add Topics/Labels (After Archiving)**

#### **For both repos, add topics:**
```
deprecated
archived
moved-to-monorepo
clausebot-legacy
```

**How:**
1. Click "About" (gear icon) on main repo page
2. Add topics in the field
3. Save

---

## ✅ **VERIFICATION CHECKLIST**

After completing above steps, verify:

### **clausebot-api Verification:**
- [ ] README shows deprecation notice
- [ ] GitHub Actions disabled
- [ ] Repository archived (yellow banner visible)
- [ ] Topics added (deprecated, archived)
- [ ] Webhooks disabled (optional)
- [ ] Repo is read-only (cannot push)

### **clausebotai Verification:**
- [ ] README shows deprecation notice
- [ ] GitHub Actions disabled
- [ ] Repository archived (yellow banner visible)
- [ ] Topics added (deprecated, archived)
- [ ] Webhooks disabled (optional)
- [ ] Repo is read-only (cannot push)

### **New Monorepo Verification:**
- [ ] https://github.com/miltmon/clausebot is active
- [ ] Latest commit is Oct 25+ (post-migration)
- [ ] backend/ directory exists
- [ ] frontend/ directory exists
- [ ] CI/CD status checked (if applicable)

---

## 📊 **EXPECTED RESULTS**

### **Before Archiving:**
```
User searches "clausebot github"
├─ Finds clausebot-api (100% CI/CD failures)
├─ Finds clausebotai (all tests failing)
└─ Concludes: "Production is broken" ❌ FALSE
```

### **After Archiving:**
```
User searches "clausebot github"
├─ Finds clausebot (active monorepo)
├─ Sees old repos marked "ARCHIVED"
├─ Reads deprecation notice → goes to monorepo
└─ Checks monorepo status → sees actual production state ✅
```

---

## 🎯 **SUCCESS CRITERIA**

**You'll know it worked when:**

1. ✅ Old repo pages show yellow "ARCHIVED" banner
2. ✅ README files clearly state "MOVED TO MONOREPO"
3. ✅ GitHub Actions no longer run (shows "disabled")
4. ✅ Search results clearly distinguish old vs new repos
5. ✅ Future audits check correct repository

---

## 🚨 **ROLLBACK PLAN**

**If you need to unarchive (emergency):**

1. Go to archived repo settings
2. Scroll to "Danger Zone"
3. Click "Unarchive this repository"
4. Re-enable Actions if needed

**Note:** Only unarchive if there's a critical need (e.g., recover missing code)

---

## 📞 **SUPPORT**

**Questions during archival:**
- GitHub Docs: https://docs.github.com/en/repositories/archiving-a-github-repository
- Monorepo Status: See `MONOREPO_COMPLETE.md`
- Truth Check: See `TRUTH_CHECK_REPORT_2025-10-26.md`

---

## ⏱️ **TIME ESTIMATE**

- **Step 1 (Update READMEs):** 5 minutes
- **Step 2 (Disable Actions):** 2 minutes
- **Step 3 (Disable Webhooks):** 2 minutes (optional)
- **Step 4 (Archive Repos):** 3 minutes
- **Step 5 (Add Topics):** 2 minutes
- **Verification:** 3 minutes

**Total:** ~15-20 minutes

---

## 🎊 **IMPACT**

**Archiving these repos will:**
- ✅ Eliminate audit confusion
- ✅ Make it clear which repo is active
- ✅ Stop "failing" CI/CD runs
- ✅ Improve search result clarity
- ✅ Reduce support questions
- ✅ Complete the monorepo migration

---

**Created:** October 26, 2025  
**Urgency:** IMMEDIATE (triggered by external audit)  
**Owner:** DevOps / Repository Admin  
**Estimated Completion:** Today (15-20 minutes)

---

**DO THIS NOW** to prevent future false audit findings and complete the monorepo migration properly.

