# Bubble WeldKnowledge Dashboard ↔ ClauseBot Integration Contract v1.0

**Status:** Draft for Commander Review
**Target:** Connect Bubble WeldKnowledge Dashboard to local ClauseBot API
**Date:** August 28, 2025

---

## 🎯 **Integration Overview**

The **Bubble WeldKnowledge Dashboard** (https://miltmon-80193.bubbleapps.io/version-test/) will consume ClauseBot API endpoints to provide real-time welding standards interpretation and compliance verification.

### **Key Dashboard Sections to Integrate:**
- **Standards** → ASME Codes, AWS Standards, API Standards
- **Tools** → WPS Management, NDT Records, Compliance
- **Learning Resources** → AI-powered clause explanations

---

## 🔗 **API Integration Points**

### **1. Standards Query Integration**

**Bubble Dashboard Flow:**
```
User clicks "ASME Standards" →
Bubble calls ClauseBot /ask →
Display interpreted results in dashboard
```

**ClauseBot API Call:**
```http
POST http://localhost:8080/ask
Content-Type: application/json

{
  "query": "What are the acceptance criteria for groove welds in ASME IX?",
  "codes": ["ASME_IX"],
  "top_k": 3,
  "client": {
    "app_version": "bubble-dashboard-1.0",
    "session_id": "bubble-user-session-id",
    "dashboard_section": "asme_standards"
  }
}
```

**Expected Response for Bubble:**
```json
{
  "request_id": "uuid-here",
  "mode": "live",
  "answer": "ASME IX QW-302 specifies acceptance criteria for groove welds...",
  "citations": ["ASME IX QW-302.1", "ASME IX QW-302.2"],
  "normalized_clause_ids": ["ASME_IX:QW-302.1", "ASME_IX:QW-302.2"],
  "latency_ms": 245,
  "safety_flags": [],
  "bubble_display": {
    "formatted_answer": "ASME IX QW-302 specifies acceptance criteria...",
    "citation_links": [
      {"text": "ASME IX QW-302.1", "section": "asme_standards"},
      {"text": "ASME IX QW-302.2", "section": "asme_standards"}
    ],
    "confidence_level": "high"
  }
}
```

---

### **2. WPS Management Integration**

**Bubble Dashboard Use Case:**
User uploads WPS document → ClauseBot validates against standards → Results display in dashboard

**API Endpoint:** `/validate-wps` (new endpoint needed)
```http
POST http://localhost:8080/validate-wps
Content-Type: multipart/form-data

{
  "wps_document": [uploaded file],
  "standards_to_check": ["AWS_D1.1", "ASME_IX"],
  "validation_level": "full",
  "client": {
    "app_version": "bubble-dashboard-1.0",
    "user_id": "bubble-user-id"
  }
}
```

---

### **3. NDT Records Integration**

**Bubble Dashboard Use Case:**
User queries NDT acceptance criteria → ClauseBot provides standards-based guidance

**API Call Pattern:**
```json
{
  "query": "What are the acceptance criteria for magnetic particle testing per ASME V?",
  "codes": ["ASME_V"],
  "context": {
    "ndt_method": "magnetic_particle",
    "material_type": "carbon_steel",
    "application": "pressure_vessel"
  }
}
```

---

### **4. Compliance Verification Integration**

**Bubble Dashboard Use Case:**
Automated compliance checking → ClauseBot cross-references multiple standards

**API Call Pattern:**
```json
{
  "query": "Verify compliance for 1/2 inch fillet weld undercut of 1/16 inch per AWS D1.1",
  "codes": ["AWS_D1.1"],
  "validation_mode": true,
  "context": {
    "weld_type": "fillet",
    "weld_size": "1/2_inch",
    "defect_type": "undercut",
    "defect_measurement": "1/16_inch"
  }
}
```

---

## 🛠️ **Bubble-Specific Data Mappings**

### **Dashboard Display Fields**

| Bubble Field | ClauseBot Response Field | Format |
|--------------|-------------------------|---------|
| `standard_name` | `citations[0]` | "AWS D1.1" |
| `clause_reference` | `normalized_clause_ids[0]` | "AWS_D1_1:6.7.1" |
| `interpretation` | `answer` | Rich text |
| `confidence_score` | `confidence_level` | "high/medium/low" |
| `last_updated` | `timestamp` | ISO 8601 |
| `citation_count` | `citations.length` | Integer |

### **Bubble Workflow Triggers**

1. **Standards Page Load** → Bulk query for common standards info
2. **Search Box Entry** → Real-time `/ask` calls as user types
3. **Document Upload** → `/validate-wps` or `/validate-pqr` calls
4. **Compliance Check** → Batch validation calls

---

## 🔧 **Implementation Requirements**

### **ClauseBot API Enhancements Needed:**

1. **CORS Configuration**
   ```python
   # Add to clausebot_main_app.py
   origins = [
       "https://miltmon-80193.bubbleapps.io",
       "http://localhost:3000",  # for testing
   ]
   ```

2. **New Endpoints:**
   - `POST /validate-wps` - WPS document validation
   - `POST /validate-pqr` - PQR document validation
   - `GET /standards-summary` - Quick standards overview for dashboard

3. **Enhanced Response Format:**
   ```python
   # Add bubble_display object to all responses
   "bubble_display": {
       "formatted_answer": "HTML-formatted response",
       "citation_links": [...],
       "confidence_level": "high|medium|low",
       "suggested_actions": [...]
   }
   ```

### **Bubble Dashboard Configuration:**

1. **API Connector Setup:**
   - Base URL: `http://localhost:8080` (dev) or `https://clausebot-api.miltmonndt.com` (prod)
   - Headers: `Authorization: Bearer [api-key]`
   - Timeout: 30 seconds

2. **Data Types:**
   ```
   ClauseBotResponse:
     - answer (text)
     - citations (list of texts)
     - confidence_level (text)
     - latency_ms (number)
   ```

3. **Error Handling:**
   - API timeout → Show cached results
   - API error → Show "Contact support" message
   - No results → Show "No standards found" with suggestion

---

## 📊 **Mock Data Payloads for Testing**

### **ASME Standards Query:**
```json
{
  "request_id": "test-asme-001",
  "mode": "demo",
  "answer": "ASME IX QW-302 specifies that groove weld acceptance criteria include complete joint penetration with no cracks, complete fusion, and profile within specified tolerances.",
  "citations": ["ASME IX QW-302.1", "ASME IX QW-302.2"],
  "normalized_clause_ids": ["ASME_IX:QW-302.1", "ASME_IX:QW-302.2"],
  "latency_ms": 156,
  "bubble_display": {
    "formatted_answer": "<strong>ASME IX QW-302</strong> specifies that groove weld acceptance criteria include:<ul><li>Complete joint penetration</li><li>No cracks</li><li>Complete fusion</li><li>Profile within specified tolerances</li></ul>",
    "citation_links": [
      {"text": "ASME IX QW-302.1", "url": "/standards/asme-ix#QW-302.1"},
      {"text": "ASME IX QW-302.2", "url": "/standards/asme-ix#QW-302.2"}
    ],
    "confidence_level": "high"
  }
}
```

### **AWS Standards Query:**
```json
{
  "request_id": "test-aws-001",
  "mode": "demo",
  "answer": "AWS D1.1 Table 6.1 specifies maximum allowable undercut of 1/32 inch for any member regardless of thickness.",
  "citations": ["AWS D1.1 Table 6.1"],
  "normalized_clause_ids": ["AWS_D1_1:6.1"],
  "latency_ms": 134,
  "bubble_display": {
    "formatted_answer": "<strong>AWS D1.1 Table 6.1</strong> specifies:<br/>Maximum allowable undercut: <strong>1/32 inch</strong> for any member regardless of thickness.",
    "citation_links": [
      {"text": "AWS D1.1 Table 6.1", "url": "/standards/aws-d1-1#table-6-1"}
    ],
    "confidence_level": "high"
  }
}
```

---

## ✅ **Integration Checklist**

### **Phase 1: Basic Integration**
- [ ] Configure CORS for Bubble domain
- [ ] Test `/ask` endpoint from Bubble
- [ ] Implement basic error handling
- [ ] Add `bubble_display` formatting

### **Phase 2: Enhanced Features**
- [ ] Add `/validate-wps` endpoint
- [ ] Implement bulk standards queries
- [ ] Add confidence scoring
- [ ] Create dashboard-specific response formatting

### **Phase 3: Advanced Integration**
- [ ] Real-time search suggestions
- [ ] Document upload processing
- [ ] Compliance verification workflows
- [ ] Analytics and usage tracking

---

## 🚀 **Next Steps**

1. **Commander Review** - Approve integration approach
2. **CORS Configuration** - Update ClauseBot API for Bubble domain
3. **Mock Testing** - Test API calls from Bubble with mock responses
4. **Live Integration** - Connect Bubble dashboard to local ClauseBot
5. **User Acceptance Testing** - Validate end-to-end workflows

---

**Commander, this integration will transform the Bubble WeldKnowledge Dashboard into a true AI-powered compliance platform! 🎯⚡🛡️**
