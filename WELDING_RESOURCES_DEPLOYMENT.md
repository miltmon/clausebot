# Welding Resources API - Deployment Guide

## 🎯 Overview

**Feature:** Pro-gated welding resources API providing curated articles on welding symbols and CWI certification

**Endpoints:** 4 new API endpoints
- `GET /v1/welding-symbols` - 25 welding symbols articles
- `GET /v1/cwi-resources` - 28 CWI resources articles  
- `GET /v1/welding-resources/search?q={query}` - Full-text search
- `GET /v1/health/welding-resources` - Health check

**Status:** ✅ Code complete, ready for deployment

---

## 📦 What's Included

### 1. Database Migration
- **File:** `backend/clausebot_api/migrations/20251101_create_welding_resources.sql`
- **Creates:** `welding_resources` table with RLS policies
- **Security:** Pro subscription required for read access

### 2. API Routes
- **File:** `backend/clausebot_api/api/routes/welding_resources.py`
- **Registered in:** `backend/clausebot_api/main.py`
- **Dependencies:** Supabase Python SDK

### 3. Data Files
- `backend/data/webset-articles_weld_and_welding_symbols.csv` (25 articles)
- `backend/data/webset-articles_asme_aws_cwi_welding_resources.csv` (28 articles)

### 4. Ingestion Script
- **File:** `backend/scripts/ingest_welding_data.py`
- **Purpose:** Load CSV data into database

---

## 🚀 Deployment Steps

### Step 1: Merge PR to Main

```bash
# Option A: Via GitHub UI
# Visit: https://github.com/miltmon/clausebot/pull/new/feat/welding-resources-api
# Click "Create pull request" → "Merge"

# Option B: Via CLI
gh pr create --title "feat(welding): add welding resources API" --body "Pro feature implementation complete"
gh pr merge --merge
```

### Step 2: Run Database Migration

**Connect to Supabase:**
```bash
# Get connection string from Supabase dashboard
# Project: hqhughgdraokwmreronk
# Settings → Database → Connection String (PostgreSQL)

# Run migration
psql "postgresql://postgres:[YOUR-PASSWORD]@db.hqhughgdraokwmreronk.supabase.co:5432/postgres" \
  -f backend/clausebot_api/migrations/20251101_create_welding_resources.sql
```

**Or via Supabase SQL Editor:**
1. Open https://supabase.com/dashboard/project/hqhughgdraokwmreronk/sql
2. Copy contents of `20251101_create_welding_resources.sql`
3. Paste and run

**Expected output:**
```
CREATE TABLE
CREATE INDEX (4x)
ALTER TABLE
CREATE POLICY (2x)
CREATE FUNCTION
CREATE TRIGGER
COMMENT (6x)
```

### Step 3: Run Data Ingestion

**Set environment variables:**
```bash
export SUPABASE_URL="https://hqhughgdraokwmreronk.supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="[YOUR-SERVICE-ROLE-KEY]"
```

**Run ingestion script:**
```bash
cd C:\ClauseBot_API_Deploy\clausebot
python backend/scripts/ingest_welding_data.py
```

**Expected output:**
```
============================================================
WELDING RESOURCES DATA INGESTION
============================================================

🔌 Connecting to Supabase...
   ✅ Connected

📖 Reading webset-articles_weld_and_welding_symbols.csv...
   Found 25 valid records
💾 Inserting into database...
   ✅ Inserted/updated 25 records

📖 Reading webset-articles_asme_aws_cwi_welding_resources.csv...
   Found 28 valid records
💾 Inserting into database...
   ✅ Inserted/updated 28 records

============================================================
✅ INGESTION COMPLETE: 53 total records
============================================================

🔍 Verifying data in database...
   Welding Symbols: 25 articles
   CWI Resources: 28 articles
   Total: 53 articles

✅ Verification complete!
```

### Step 4: Verify Render Deployment

Render will auto-deploy when main branch is updated.

**Check deployment:**
- Visit: https://dashboard.render.com/web/srv-d37fjc0gjchc73c8gfs0
- Wait for "Live" status
- Check logs for successful startup

**Test endpoints:**
```bash
# Health check
curl https://clausebot-api.onrender.com/v1/health/welding-resources

# Expected response:
{
  "status": "ok",
  "welding_symbols_count": 25,
  "cwi_resources_count": 28,
  "total_count": 53
}

# Get welding symbols
curl https://clausebot-api.onrender.com/v1/welding-symbols | jq '.total'
# Expected: 25

# Get CWI resources
curl https://clausebot-api.onrender.com/v1/cwi-resources | jq '.total'
# Expected: 28

# Search
curl "https://clausebot-api.onrender.com/v1/welding-resources/search?q=fillet" | jq '.total'
# Expected: > 0
```

### Step 5: Verify in Swagger UI

Visit: https://clausebot-api.onrender.com/docs

**Expected new endpoints:**
- `GET /v1/welding-symbols`
- `GET /v1/cwi-resources`
- `GET /v1/welding-resources/search`
- `GET /v1/health/welding-resources`

---

## ✅ Success Criteria

- [ ] PR merged to main
- [ ] Database migration completed (no errors)
- [ ] Data ingestion completed (53 articles)
- [ ] Render deployment live
- [ ] Health endpoint returns `total_count: 53`
- [ ] Swagger UI shows 4 new endpoints
- [ ] Search endpoint returns results

---

## 🔧 Troubleshooting

### Migration fails with "relation already exists"
```sql
-- Safe to ignore - table already created
-- Verify with: SELECT COUNT(*) FROM welding_resources;
```

### Ingestion fails with "permission denied"
```bash
# Check service role key is correct
echo $SUPABASE_SERVICE_ROLE_KEY | cut -c1-20
# Should start with "eyJ..."

# Verify RLS policies exist
psql "..." -c "SELECT * FROM pg_policies WHERE tablename='welding_resources';"
```

### Endpoints return 500 error
```bash
# Check Render logs
curl https://api.render.com/v1/services/srv-d37fjc0gjchc73c8gfs0/logs

# Common causes:
# - Missing SUPABASE_URL env var
# - Missing SUPABASE_SERVICE_ROLE_KEY env var
# - Table doesn't exist (run migration)
```

---

## 📊 Monitoring

**Dashboard queries:**
```sql
-- Count by category
SELECT category, COUNT(*) 
FROM welding_resources 
GROUP BY category;

-- Recent additions
SELECT title, category, created_at 
FROM welding_resources 
ORDER BY created_at DESC 
LIMIT 10;

-- Search test
SELECT COUNT(*) 
FROM welding_resources 
WHERE to_tsvector('english', title || ' ' || COALESCE(description, '')) 
  @@ to_tsquery('english', 'fillet');
```

---

## 🎉 Launch Checklist

- [x] Code complete
- [x] Committed to GitHub
- [x] Branch pushed
- [ ] PR created
- [ ] PR merged
- [ ] Migration executed
- [ ] Data ingested
- [ ] Render deployed
- [ ] Endpoints verified
- [ ] Ready for Nov 10 launch

---

**Questions?** Check Render logs or Supabase SQL editor for debugging.

