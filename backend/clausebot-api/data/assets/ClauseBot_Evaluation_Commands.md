# ClauseBot Evaluation Command Sequence
**Purpose:** Verify ClauseBot deployment meets FABTECH demo performance standards
**Target Metrics:** ≥85% accuracy, ≤1.0s p95 latency, Min 10 prompts scored

---

## 🔍 **Step 1: Run ClauseBot Smoke Test**

### Primary Evaluation Command:
```powershell
# Navigate to ClauseBot core directory
cd .\clausebot_core

# Run comprehensive smoke test
.\Smoke-Test.ps1 -Verbose
```

### Alternative Commands:
```powershell
# Option 1: Main workspace smoke test (basic connectivity)
.\clausebot_smoke_test.ps1 -BaseUrl "http://localhost:8080" -TimeoutSeconds 30 -Verbose

# Option 2: Integration verification (comprehensive)
.\Verify-ClauseBot-Integration-v1.ps1

# Option 3: Python-based smoke test
python smoke_test.py

# Option 4: Simple Python smoke test
python smoke_test_simple.py
```

---

## 🔍 **Step 2: Performance Evaluation**

### Expected Test Results:
1. **Health Check** ✅
   - Service status: "healthy"
   - Database: "connected"
   - AI services: Claude/OpenAI available

2. **Response Time Metrics** ✅
   - Average response time: <1000ms
   - p95 latency: ≤1.0s
   - No timeout errors

3. **Accuracy Validation** ✅
   - AI model confidence scores ≥85%
   - Query processing success rate: 100%
   - No error responses for standard queries

---

## 🔍 **Step 3: Quick Verification Steps**

### PowerShell Commands to Run:
```powershell
# 1. Check ClauseBot service status
curl http://localhost:8080/health | ConvertFrom-Json

# 2. Test metrics endpoint
curl "http://localhost:8080/metrics/summary?window=1h" | ConvertFrom-Json

# 3. Verify AI response time
Measure-Command { curl -Method POST -Uri "http://localhost:8080/ask" -Body '{"query":"What is AWS D1.1?"}' -ContentType "application/json" }

# 4. Check database connection
curl "http://localhost:8080/metrics/top-clauses?window=1h&limit=5" | ConvertFrom-Json
```

---

## 🎯 **Success Criteria (FABTECH Ready)**

### Green Quality Gates:
- [ ] **Health Check**: All services operational
- [ ] **Response Time**: <1000ms average, <1s p95
- [ ] **Accuracy**: ≥85% AI confidence scores
- [ ] **Stability**: No crashes during 10+ queries
- [ ] **Database**: Connected and responsive
- [ ] **AI Services**: Claude/OpenAI both available

### Demo-Critical Endpoints:
- [ ] `/health` - Returns healthy status
- [ ] `/ask` - Processes queries in <1s
- [ ] `/metrics/summary` - Returns valid analytics
- [ ] `/metrics/top-clauses` - Returns clause data

---

## 🚨 **Troubleshooting**

### If Tests Fail:
```powershell
# Check if ClauseBot is running
Get-Process | Where-Object {$_.Name -like "*clause*"}

# Check port 8080 availability
netstat -an | Select-String ":8080"

# Review logs
Get-Content .\logs\clausebot.log -Tail 50

# Restart ClauseBot service
.\scripts\clausebot_services_management.ps1 -Action Restart
```

### If Performance is Poor:
1. **Check system resources**
2. **Verify database connection pooling**
3. **Confirm AI API keys are valid**
4. **Test with reduced query complexity**

---

## 📊 **Expected Output Example**

### Successful Smoke Test:
```
🔥 ClauseBot Smoke Test Starting...
Target: http://localhost:8080
Timeout: 30 seconds

✅ Health Check
✅ Metrics Summary
✅ Top Clauses Analytics
✅ Time Series Data
✅ Conversion Funnel
✅ Ask Endpoint (POST)

🎯 Smoke Test Results:
Passed: 6/6 tests
✅ All smoke tests passed! ClauseBot is operational.
```

### Performance Metrics:
```json
{
  "status": "healthy",
  "database": "connected",
  "ai_services": {
    "claude": true,
    "openai": true
  },
  "metrics": {
    "avg_response_time_ms": 450,
    "p95_response_time_ms": 890,
    "total_queries": 1247,
    "avg_confidence": 0.89
  }
}
```

---

## ✅ **Post-Evaluation Actions**

### If All Tests Pass:
1. **Update demo script** with confirmed performance metrics
2. **Archive test results** for FABTECH evidence
3. **Proceed to Stripe checkout hardening** (next todo)
4. **Schedule final pre-FABTECH validation**

### If Tests Fail:
1. **Document specific failures**
2. **Implement performance optimizations**
3. **Re-run evaluation until green**
4. **Update FABTECH demo fallback procedures**

---

**Ready to execute?** Start with the primary smoke test command and validate all green checkmarks before proceeding to FABTECH demo.
