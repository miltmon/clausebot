# ClauseBot API - Disable Stub Mode in Render

**Date:** October 23, 2025  
**Issue:** Production serving stub data instead of real Airtable questions  
**Root Cause:** `QUIZ_STUB=1` environment variable active in Render  
**Impact:** Users receiving test data, not real AWS D1.1 welding content

---

## **Current State**

**Verification Output (10/23/2025 16:15 PT):**
```json
{
  "count": 1,
  "source": "stub",           // ❌ Should be "airtable"
  "category": "Fundamentals",
  "items": [{
    "q": "Quiz endpoint test - is the routing working?",  // ❌ Test data
    "source": "stub"
  }]
}
```

**Code Location:** `clausebot_api/routes/quiz.py:37`
```python
if os.getenv("QUIZ_STUB", "0") == "1":
    return {"count": 1, "category": cat, "source": "stub", "items": [stub_item]}
```

---

## **Fix Procedure**

### **Step 1: Access Render Dashboard**

1. Navigate to: https://dashboard.render.com/web/srv-d37fjc0gjchc73c8gfs0
2. Login with Miltmon credentials
3. Select **clausebot-api** service

### **Step 2: Modify Environment Variables**

1. Click **"Environment"** tab in left sidebar
2. Locate `QUIZ_STUB` variable
3. **Option A (Recommended):** Click "Delete" next to `QUIZ_STUB`
4. **Option B (Alternative):** Edit value to `0` (instead of `1`)
5. Click **"Save Changes"**

### **Step 3: Trigger Redeploy**

1. Render will auto-prompt: **"Redeploy required for changes to take effect"**
2. Click **"Manual Deploy" → "Deploy latest commit"**
3. Wait 2-3 minutes for deployment to complete
4. Monitor deployment logs for:
   ```
   [startup] quiz default category = Fundamentals
   ```

### **Step 4: Verify Fix**

Run verification script from PowerShell:
```powershell
cd c:\Users\miltm\MiltmonNDT_Workspace
.\verify_clausebot.ps1
```

**Expected Output:**
```
[3/4] /v1/quiz?category=Fundamentals&count=3
  Count: 3                    ✅ Matches request
  Source: airtable            ✅ NOT "stub"
  Category: Fundamentals

  Sample Question:
    Q: [Real AWS D1.1 welding question]   ✅ Real content
    Correct: [A/B/C/D]
    Clause: [Actual AWS D1.1 reference]
    Explanation: [Real technical explanation]
```

**Quick Test via cURL:**
```powershell
$q = Invoke-RestMethod "https://clausebot-api.onrender.com/v1/quiz?category=Fundamentals&count=5"
Write-Host "Source: $($q.source)"  # Should show "airtable"
Write-Host "Count: $($q.count)"    # Should show 5
```

---

## **Success Criteria**

- [ ] `QUIZ_STUB` removed or set to `0` in Render
- [ ] Redeploy completed successfully
- [ ] `/v1/quiz` returns `"source": "airtable"`
- [ ] Questions contain real AWS D1.1 welding content
- [ ] Requested count matches returned count
- [ ] All questions have complete data (q, a[], correct, clause_ref, explanation)

---

## **Rollback Plan**

If real Airtable data causes issues:

1. Re-enable stub mode: Set `QUIZ_STUB=1` in Render
2. Redeploy
3. Investigate Airtable data quality issues
4. Fix field mappings if needed
5. Re-test with stub mode disabled

---

## **Post-Fix Documentation**

Once verified, update:
1. `CONSOLIDATION_RECEIPTS.md` - Add production verification receipt
2. `scripts/verify_prod.ps1` - Update to check for stub mode
3. Create deployment timestamp record

---

## **Contact**

**Service:** clausebot-api  
**Render URL:** https://clausebot-api.onrender.com  
**Dashboard:** https://dashboard.render.com/web/srv-d37fjc0gjchc73c8gfs0  
**Repository:** https://github.com/miltmon/clausebot-api  
**Last Commit:** 684583b (field mapping fixes)

---

**Status:** ⏳ AWAITING RENDER ENVIRONMENT VARIABLE CHANGE

