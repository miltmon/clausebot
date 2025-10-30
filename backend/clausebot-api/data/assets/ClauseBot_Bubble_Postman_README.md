# ClauseBot → Bubble Dashboard Integration Test Kit

**Status:** Production Ready Test Suite
**Purpose:** Complete API validation for Bubble dashboard integration
**Date:** August 28, 2025

---

## 🎯 **Overview**

This test kit provides comprehensive validation of the ClauseBot API endpoints that will be consumed by the Bubble WeldKnowledge Dashboard. All endpoints are tested with real-world scenarios and expected response validation.

---

## 📦 **Package Contents**

### **1. Postman Environment**
**File:** `ClauseBot_Bubble_Postman_Environment.json`
```json
{
  "name": "ClauseBot Local (Bubble Dashboard)",
  "values": [
    {"key": "base_url", "value": "http://localhost:8080"},
    {"key": "api_key", "value": "your-dashboard-readonly-key"},
    {"key": "window", "value": "24h"},
    {"key": "interval", "value": "1h"},
    {"key": "start", "value": "2025-08-01T00:00:00Z"},
    {"key": "end", "value": "2025-08-28T23:59:59Z"}
  ]
}
```

### **2. Postman Collection**
**File:** `ClauseBot_Bubble_Postman_Collection.json`
- **7 Core Endpoints** with comprehensive test coverage
- **Built-in assertions** for status codes, response structure, data validation
- **Environment variable integration** for flexible testing scenarios

---

## 🔗 **API Endpoints Covered**

### **Health & System Status**
```http
GET {{base_url}}/metrics/health
Tests:
- Status code is 200
- Response has JSON body
- Contains required fields: status, database, ai_services
- Database status is "connected"
- AI services show claude and openai availability
```

### **Dashboard Summary Metrics**
```http
GET {{base_url}}/metrics/summary?window={{window}}
Tests:
- Status code is 200
- Response contains summary statistics
- Fields include: total_queries, avg_response_time, active_users, top_standards
- All numeric fields are valid numbers
- Response time metrics are reasonable (< 5000ms)
```

### **Top Clauses Analytics**
```http
GET {{base_url}}/metrics/top-clauses?window={{window}}&limit=10
Tests:
- Status code is 200
- Returns array of clause usage statistics
- Each item contains: clause_id, standard, query_count, avg_confidence
- Query counts are positive integers
- Confidence scores are between 0.0 and 1.0
```

### **Time Series Data**
```http
GET {{base_url}}/metrics/timeseries?start={{start}}&end={{end}}&interval={{interval}}
Tests:
- Status code is 200
- Returns time-ordered data points
- Each point has: timestamp, queries, avg_response_time, unique_users
- Timestamps are valid ISO 8601 format
- Data is chronologically ordered
```

### **User Engagement Leaderboard**
```http
GET {{base_url}}/metrics/leaderboard?window={{window}}&type=engagement
Tests:
- Status code is 200
- Returns ranked user engagement data
- Fields include: user_id, query_count, avg_session_time, standards_accessed
- Rankings are properly ordered
- All counts are non-negative
```

### **Conversion Funnel Analysis**
```http
GET {{base_url}}/metrics/funnel?window={{window}}
Tests:
- Status code is 200
- Contains funnel stage data
- Stages: visitors, queries, standards_accessed, enterprise_interest
- Each stage has count and conversion_rate fields
- Conversion rates are between 0.0 and 1.0
- Funnel shows logical progression (visitors >= queries >= conversions)
```

### **Query Logs Export**
```http
GET {{base_url}}/metrics/query-logs?start={{start}}&end={{end}}&format=json
Tests:
- Status code is 200
- Returns array of query log entries
- Each entry contains: timestamp, query, standard, response_time, user_id
- Timestamps are valid and within requested range
- Response times are positive numbers
```

---

## 🚀 **Quick Start Guide**

### **Step 1: Import Test Kit**
1. **Open Postman** → Click **Import** button
2. **Import Environment:** Drag `ClauseBot_Bubble_Postman_Environment.json`
3. **Import Collection:** Drag `ClauseBot_Bubble_Postman_Collection.json`
4. **Select Environment:** Choose "ClauseBot Local (Bubble Dashboard)"

### **Step 2: Configure Environment**
```bash
# Ensure ClauseBot is running
.\clausebot.bat up

# Verify health endpoint
curl http://localhost:8080/health

# Set your API key in Postman environment
api_key: "your-dashboard-readonly-key-here"
```

### **Step 3: Run Test Suite**
1. **Start with Health Check:** Send `/metrics/health` request first
2. **Run Individual Tests:** Test each endpoint manually
3. **Run Complete Suite:** Use "Run Collection" to execute all tests
4. **Review Results:** Check test results and response data

---

## 📊 **Expected Test Results**

### **Successful Test Run Output:**
```
✅ Health Check                    - All tests passed (5/5)
✅ Dashboard Summary              - All tests passed (4/4)
✅ Top Clauses Analytics          - All tests passed (5/5)
✅ Time Series Data               - All tests passed (4/4)
✅ User Engagement Leaderboard    - All tests passed (4/4)
✅ Conversion Funnel Analysis     - All tests passed (6/6)
✅ Query Logs Export              - All tests passed (5/5)

Total: 33/33 tests passed
Collection run completed in 2.3 seconds
```

### **Sample Response Validation:**
```json
// Health Check Response
{
  "status": "healthy",
  "database": "connected",
  "ai_services": {"claude": true, "openai": true},
  "timestamp": "2025-08-28T16:30:45.123Z",
  "version": "1.0.0"
}

// Dashboard Summary Response
{
  "window": "24h",
  "total_queries": 1247,
  "avg_response_time_ms": 234,
  "active_users": 89,
  "top_standards": ["AWS_D1.1", "ASME_IX", "API_1104"],
  "success_rate": 0.98
}
```

---

## 🔧 **Advanced Configuration**

### **Environment Variables Explained:**
| Variable | Purpose | Example Value |
|----------|---------|---------------|
| `base_url` | ClauseBot API root | `http://localhost:8080` |
| `api_key` | Dashboard authentication | `cb_dash_readonly_abc123` |
| `window` | Time window for metrics | `24h`, `7d`, `30d` |
| `interval` | Time series interval | `1h`, `6h`, `1d` |
| `start` | Query start time | `2025-08-01T00:00:00Z` |
| `end` | Query end time | `2025-08-28T23:59:59Z` |

### **Custom Test Scenarios:**
```javascript
// Example custom test for response time validation
pm.test("Response time is acceptable", function () {
    const responseTime = pm.response.responseTime;
    pm.expect(responseTime).to.be.below(1000); // Less than 1 second
});

// Example custom test for data freshness
pm.test("Data is recent", function () {
    const jsonData = pm.response.json();
    const lastUpdate = new Date(jsonData.timestamp);
    const now = new Date();
    const ageMinutes = (now - lastUpdate) / (1000 * 60);
    pm.expect(ageMinutes).to.be.below(60); // Less than 1 hour old
});
```

---

## 🎪 **Bubble Dashboard Integration Workflow**

### **Pre-Integration Validation:**
1. **Run Full Test Suite** → Ensure all endpoints return valid data
2. **Verify Response Formats** → Confirm JSON structure matches Bubble expectations
3. **Test Error Scenarios** → Validate graceful handling of invalid requests
4. **Performance Validation** → Ensure response times meet dashboard requirements

### **Post-Integration Monitoring:**
1. **Health Check Automation** → Set up scheduled health monitoring
2. **Performance Tracking** → Monitor dashboard load impact on API
3. **Error Rate Monitoring** → Track and alert on API failures
4. **Usage Analytics** → Measure dashboard engagement and API utilization

---

## 🚀 **Next Steps: Enhanced Testing Options**

### **Option A: curl Smoke Script**
```bash
# Quick validation script for CI/CD
#!/bin/bash
echo "Running ClauseBot smoke test..."
curl -f http://localhost:8080/health || exit 1
curl -f http://localhost:8080/metrics/summary?window=1h || exit 1
echo "✅ Smoke test passed"
```

### **Option B: Supabase Mirror Cron**
```javascript
// Automated data sync to Supabase for Bubble consumption
const syncMetrics = async () => {
  const metrics = await fetch('http://localhost:8080/metrics/summary?window=24h');
  const data = await metrics.json();

  await supabase
    .from('clausebot_metrics')
    .upsert({
      timestamp: new Date().toISOString(),
      ...data
    });
};

// Run every hour
setInterval(syncMetrics, 60 * 60 * 1000);
```

---

## ✅ **Validation Checklist**

### **Before Bubble Integration:**
- [ ] All 7 endpoint tests pass
- [ ] Response times < 1 second average
- [ ] Data formats match Bubble requirements
- [ ] Error handling works gracefully
- [ ] API key authentication functional

### **During Integration:**
- [ ] CORS headers configured for Bubble domain
- [ ] Rate limiting appropriate for dashboard usage
- [ ] Error messages helpful for debugging
- [ ] Performance maintains under dashboard load

### **Post Integration:**
- [ ] End-to-end dashboard functionality verified
- [ ] Real user data flowing correctly
- [ ] No API performance degradation
- [ ] Monitoring and alerting active

---

**Commander, this test kit provides bulletproof validation for the Bubble dashboard integration. Every endpoint is thoroughly tested, and the framework is ready for both development and production use! 🎯⚡🛡️**
