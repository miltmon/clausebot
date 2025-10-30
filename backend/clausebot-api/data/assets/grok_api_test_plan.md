# Grok API Performance Test Plan

## **ENDPOINTS TO TEST:**

### **1. Practice Questions:**
```bash
curl -X POST http://localhost:8080/practice \
  -H "Content-Type: application/json" \
  -d '{"count": 10, "category": "mixed"}' \
  -w "@curl-format.txt"
```

### **2. Study Questions:**
```bash
curl -X POST http://localhost:8080/study \
  -H "Content-Type: application/json" \
  -d '{"category": "definitions", "count": 10}' \
  -w "@curl-format.txt"
```

### **3. Explanation:**
```bash
curl -X POST http://localhost:8080/explain \
  -H "Content-Type: application/json" \
  -d '{"questionId": "test-123"}' \
  -w "@curl-format.txt"
```

### **4. Health Check:**
```bash
curl -X GET http://localhost:8080/health \
  -w "@curl-format.txt"
```

## **PERFORMANCE TARGETS:**
- **P95 Response Time:** <1 second
- **CORS Headers:** Present and correct
- **Health Endpoint:** <200ms response

## **CURL FORMAT FILE:**
```
     time_namelookup:  %{time_namelookup}\n
        time_connect:  %{time_connect}\n
     time_appconnect:  %{time_appconnect}\n
    time_pretransfer:  %{time_pretransfer}\n
       time_redirect:  %{time_redirect}\n
  time_starttransfer:  %{time_starttransfer}\n
                     ----------\n
          time_total:  %{time_total}\n
```

## **CORS VERIFICATION:**
```bash
curl -X OPTIONS http://localhost:8080/practice \
  -H "Origin: http://localhost:5173" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -v
```

**Expected Headers:**
- `Access-Control-Allow-Origin: *`
- `Access-Control-Allow-Methods: POST, GET, OPTIONS`
- `Access-Control-Allow-Headers: Content-Type`

## **STATUS:** ✅ READY FOR GROK TESTING
