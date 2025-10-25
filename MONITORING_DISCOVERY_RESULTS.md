# ClauseBot API Monitoring - Route Discovery Results

**Date:** October 25, 2025  
**Purpose:** Discover actual available routes for monitoring configuration

---

## 🔍 DISCOVERY METHOD

### OpenAPI Spec Analysis
```powershell
$API = "https://clausebot-api.onrender.com"
$spec = Invoke-RestMethod "$API/openapi.json"
$spec.paths | Where-Object { $_ -match 'quiz|cross' }
```

### Route Probing
Tested 12 candidate routes with direct HTTP requests.

---

## ✅ AVAILABLE ROUTES - QUIZ

### Content Endpoints (2864 bytes response)

**Route 1: `/v1/quiz`**
- **Status:** ✅ 200 OK
- **Size:** 2864 bytes
- **Purpose:** Primary quiz content delivery
- **Monitoring:** ✅ RECOMMENDED
- **Keyword:** `"items"` or `"count"`

**Route 2: `/api/quiz`**
- **Status:** ✅ 200 OK  
- **Size:** 2864 bytes (identical to /v1/quiz)
- **Purpose:** Legacy/alias endpoint
- **Monitoring:** Not needed (use /v1/quiz instead)

### Health Endpoints

**Route 3: `/health/quiz`**
- **Status:** ✅ 200 OK
- **Size:** 56 bytes
- **Purpose:** Simple quiz service health check
- **Response:** `{"quiz": "ready", "default_category": "..."}`
- **Monitoring:** ✅ GOOD for simple health

**Route 4: `/health/quiz/baseline`**
- **Status:** ✅ 200 OK
- **Size:** 101 bytes
- **Purpose:** Quiz data baseline metrics
- **Response:** `{"status": "connected", "configured": true, "sample_size": 100, "eligible_in_sample": 93}`
- **Monitoring:** ✅ EXCELLENT for data quality

**Route 5: `/health/quiz/detailed`**
- **Status:** ✅ 200 OK
- **Size:** 490 bytes
- **Purpose:** Detailed quiz data distribution
- **Response:** Includes total, eligible, production_ready counts
- **Monitoring:** ✅ BEST for comprehensive health

---

## ❌ NON-EXISTENT ROUTES - CROSSWALK

### All Tested (404 Not Found)

- `/crosswalk` → 404
- `/v1/crosswalk` → 404
- `/api/crosswalk` → 404
- `/health/crosswalk` → 404
- `/crosswalk/stats` → 404
- `/v1/crosswalk/stats` → 404

**Conclusion:** NO crosswalk endpoints exist in current API deployment.

---

## 🎯 MONITORING RECOMMENDATIONS

### Option A: Current Working Endpoints (Fast - Use Today)

**4 Monitors:**
1. ✅ API Health: `/health` (infrastructure)
2. ✅ Frontend: `https://clausebot.vercel.app/` (infrastructure)
3. ✅ Quiz Content: `/v1/quiz` (content delivery)
4. ✅ Quiz Health: `/health/quiz/detailed` (data quality)

**Pros:**
- All endpoints verified working (200 OK)
- Good coverage of infrastructure + content
- Can deploy to UptimeRobot immediately
- No code changes required

**Cons:**
- No crosswalk monitoring (doesn't exist)
- Quiz content endpoint is slower (3155ms)

---

### Option B: Add Canary Endpoints (Best Practice - 30 min)

**Create dedicated monitoring endpoints:**

**File:** `backend/clausebot_api/routes/canary.py`

```python
"""Canary endpoints optimized for external monitoring."""
from typing import Dict, Any
from fastapi import APIRouter
from clausebot_api.airtable_data_source import get_airtable_health

router = APIRouter()


@router.get("/canary/quiz")
def quiz_canary() -> Dict[str, Any]:
    """
    Lightweight quiz availability check.
    Returns minimal data optimized for monitoring.
    """
    try:
        # Quick check of Airtable connection
        health = get_airtable_health()
        
        return {
            "ok": True,
            "service": "quiz",
            "available": health.get("configured", False),
            "questions": health.get("sample_size", 0)
        }
    except Exception as e:
        return {
            "ok": False,
            "service": "quiz",
            "error": str(e)
        }


@router.get("/canary/api")
def api_canary() -> Dict[str, Any]:
    """
    Comprehensive API health canary.
    Tests all critical services without heavy operations.
    """
    results = {
        "ok": True,
        "services": {}
    }
    
    # Test Airtable
    try:
        airtable = get_airtable_health()
        results["services"]["airtable"] = {
            "ok": airtable.get("configured", False),
            "sample_size": airtable.get("sample_size", 0)
        }
    except Exception as e:
        results["ok"] = False
        results["services"]["airtable"] = {"ok": False, "error": str(e)}
    
    return results
```

**Register in `main.py`:**
```python
from clausebot_api.routes.canary import router as canary_router
app.include_router(canary_router, tags=["monitoring"])
```

**Then monitor:**
1. `/health` (infrastructure)
2. Frontend (infrastructure)
3. `/canary/quiz` (content availability, keyword: `"questions"`)
4. `/canary/api` (comprehensive, keyword: `"services"`)

**Pros:**
- Purpose-built for monitoring (fast, lightweight)
- Clear separation of concerns
- Easy to add more canaries later
- Standard monitoring pattern

**Cons:**
- Requires code change + deploy (30 min)
- One more commit before Nov 2

---

### Option C: Hybrid Approach (Recommended)

**For November 2 (Use what exists):**
1. `/health` → Infrastructure health
2. Frontend → Frontend availability
3. `/v1/quiz` → Content delivery (keyword: `"items"`)
4. `/health/quiz/baseline` → Data quality (keyword: `"eligible_in_sample"`)

**For December (Add canaries):**
- Add canary endpoints in next sprint
- Migrate monitors to canaries
- Add crosswalk canary when that feature ships

**Rationale:**
- Unblocks Nov 2 monitoring setup (today's goal)
- Provides good coverage immediately
- Allows time for proper canary implementation
- Doesn't rush code changes before weekend

---

## 📊 RESPONSE TIME ANALYSIS

| Endpoint | Response Time | Assessment |
|----------|---------------|------------|
| `/health` | 367ms | ✅ Fast |
| Frontend | 163ms | ✅ Fast |
| `/v1/quiz` | 3155ms | ⚠️ Slow but acceptable |
| `/health/quiz/detailed` | 812ms | ✅ Acceptable |
| `/health/quiz/baseline` | 490ms | ✅ Fast |

**Conclusion:** All endpoints respond within acceptable timeframe for monitoring (< 5 seconds).

---

## 🎯 FINAL RECOMMENDATION

### For November 2, 2025 Setup

**Use Option C (Hybrid):**

**Monitor 1: ClauseBot API Health**
```
URL: https://clausebot-api.onrender.com/health
Keyword: "ok"
Purpose: Infrastructure health
```

**Monitor 2: ClauseBot Frontend**
```
URL: https://clausebot.vercel.app/
Keyword: "ClauseBot"
Purpose: Frontend availability
```

**Monitor 3: ClauseBot Quiz Content**
```
URL: https://clausebot-api.onrender.com/v1/quiz
Keyword: "items"
Purpose: Content delivery verification
```

**Monitor 4: ClauseBot Quiz Data Quality**
```
URL: https://clausebot-api.onrender.com/health/quiz/baseline
Keyword: "eligible_in_sample"
Purpose: Data quality metrics
```

**Rationale:**
- ✅ All 4 endpoints verified working
- ✅ Fast deployment (no code changes)
- ✅ Good coverage (infrastructure + content + data quality)
- ✅ Unblocks Nov 2 monitoring setup
- ✅ Can add canaries in December sprint

---

## 📝 CROSSWALK NOTES

**Status:** NO crosswalk endpoints exist in current deployment.

**Options:**
1. **Skip for now** - Focus on quiz monitoring (primary feature)
2. **Add canary** - When crosswalk feature is implemented
3. **Health endpoint** - Add `/health/crosswalk` when feature ships

**Recommendation:** Skip crosswalk monitoring until feature exists. No point monitoring something that doesn't exist.

---

## ✅ ACTION ITEMS

### Immediate (Nov 2 Setup)
- [x] Discovery complete
- [x] Verify all endpoints working
- [ ] Update monitoring guide with verified URLs
- [ ] Update preflight script
- [ ] Execute UptimeRobot setup

### Future (December Sprint)
- [ ] Implement canary endpoints (`/canary/quiz`, `/canary/api`)
- [ ] Migrate monitors to canaries
- [ ] Add crosswalk monitoring when feature ships
- [ ] Document canary pattern for future services

---

**Generated:** October 25, 2025  
**Method:** OpenAPI discovery + HTTP probing  
**Verified:** All recommended endpoints tested and working  
**Status:** ✅ Ready for Nov 2 monitoring deployment

