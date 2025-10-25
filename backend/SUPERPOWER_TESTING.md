# 🚀 ClauseBot API Superpower Testing Guide

## Quick Start Testing

### 1. Environment Setup
```powershell
# Copy template and fill in your credentials
copy env.template .env
# Edit .env with your actual API keys and database credentials
```

### 2. Local Development Server
```powershell
cd C:\ClauseBot_API_Deploy\clausebot-api
.\.venv\Scripts\Activate.ps1
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### 3. Test Core Superpowers

#### 🤖 AI Provider Router
```powershell
# Test AI assistance
curl -X POST "http://127.0.0.1:8000/api/assist" -H "Content-Type: application/json" -d '{"prompt": "What is the difference between MIG and TIG welding?"}'

# Check available providers
curl "http://127.0.0.1:8000/api/assist/providers"

# Get current provider config
curl "http://127.0.0.1:8000/api/config/provider"
```

#### 💰 Cost Management
```powershell
# Estimate costs for different models
curl "http://127.0.0.1:8000/api/costs/estimate?provider_model=openai/gpt-4&monthly_calls=1000&avg_in=100&avg_out=200"

# Compare model costs
curl "http://127.0.0.1:8000/api/costs/compare?monthly_calls=1000&avg_in=100&avg_out=200"

# Check budget status
curl "http://127.0.0.1:8000/api/costs/budget/alert"
```

#### 🏥 Enhanced Health Monitoring
```powershell
# Basic health check
curl "http://127.0.0.1:8000/health"

# Detailed health with latencies
curl "http://127.0.0.1:8000/api/health/detailed"

# Real-time metrics snapshot
curl "http://127.0.0.1:8000/api/metrics/snapshot"
```

#### 🔧 CURSOR Integration
```powershell
# Enhanced incident reporting
curl -X POST "http://127.0.0.1:8000/api/cursor/incident" -H "Content-Type: application/json" -d '{
  "incident_type": "Chrome_Hang",
  "severity": "medium",
  "confidence": 0.85,
  "system_context": {
    "chrome_processes": 12,
    "gpu_name": "Intel Arc A770"
  }
}'
```

### 4. Comprehensive Testing Suite
```powershell
# Run the comprehensive test suite
.\test_dual_database.ps1 -ApiBase "http://127.0.0.1:8000" -Verbose

# Test CURSOR integration
.\ops\validation\cursor_dual_db_validator.ps1 -ApiBase "http://127.0.0.1:8000"
```

## Production Deployment Testing

### 1. Environment Variables for Render
Set these in your Render dashboard:
- `MODEL_PROVIDER`, `MODEL_NAME`
- `OPENAI_API_KEY` (or your chosen provider key)
- `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`
- `AIRTABLE_API_KEY`, `AIRTABLE_BASE_ID`
- `ALLOWED_ORIGINS`

### 2. Database Schema Setup
Run the SQL in your Supabase SQL editor:
```sql
-- Execute the contents of supabase_schema.sql
-- This creates incidents table, model_usage table, and all indexes
```

### 3. Airtable Table Setup
Create table with fields:
- `title` (Single line text)
- `source` (Single select: cursor/windsurf/exa/manual)
- `severity` (Single select: low/medium/high/critical)
- `confidence` (Number, precision 2)
- `supabase_id` (Single line text)
- `payload_json` (Long text)

### 4. Production Validation
```powershell
# Test production deployment
.\ops\validation\cursor_dual_db_validator.ps1 -ApiBase "https://clausebot-api.onrender.com" -FullValidation

# Send test incident to production
.\ops\validation\cursor_incident_sender.ps1 -IncidentType "Production_Test" -Severity "low" -ApiBase "https://clausebot-api.onrender.com"
```

## Superpower Feature Matrix

| Feature | Endpoint | Status | Description |
|---------|----------|--------|-------------|
| 🤖 AI Assistance | `/api/assist` | ✅ Ready | Multi-provider AI with cost tracking |
| 💰 Cost Estimation | `/api/costs/*` | ✅ Ready | Real-time cost analysis and budgeting |
| 🏥 Health Monitoring | `/api/health/detailed` | ✅ Ready | Service-by-service health with latencies |
| 📊 Metrics Dashboard | `/api/metrics/snapshot` | ✅ Ready | 24-hour incident and performance stats |
| 🔧 CURSOR Integration | `/api/cursor/incident` | ✅ Ready | Enhanced system context capture |
| 🛡️ Webhook Security | `/api/integrations/exa` | ✅ Ready | HMAC verification and payload sanitization |
| 📱 Firebase Realtime | Auto-publish | ✅ Ready | Live incident broadcasting |
| 🔍 Dual-DB Search | `/api/search` | ✅ Ready | Supabase primary, Airtable fallback |

## Expected Response Times
- Health checks: < 100ms
- AI assistance: < 2000ms (depends on provider)
- Database operations: < 500ms
- Cost calculations: < 50ms
- Metrics snapshots: < 200ms

## Troubleshooting

### Common Issues
1. **AI Provider Errors**: Check API keys in `.env`
2. **Database Connection**: Verify Supabase/Airtable credentials
3. **CORS Issues**: Update `ALLOWED_ORIGINS` environment variable
4. **Cost Tracking**: Ensure `model_usage` table exists in Supabase

### Debug Commands
```powershell
# Check environment variables
Get-Content .env

# Test database connections individually
curl "http://127.0.0.1:8000/health"

# View detailed logs
uvicorn main:app --reload --log-level debug
```

## Success Criteria
✅ All health checks return green  
✅ AI assistance responds within 2 seconds  
✅ Cost estimates are accurate  
✅ Dual-database writes succeed  
✅ CURSOR integration captures system context  
✅ Metrics show real-time data  

**Ready for enterprise deployment! 🚀**
