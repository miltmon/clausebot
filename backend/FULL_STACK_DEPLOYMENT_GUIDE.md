# 🚀 ClauseBot Full-Stack Deployment Guide

## 📋 Overview

This guide covers deploying ClauseBot's **full-stack infrastructure** with:
- ✅ FastAPI web service (main API)
- ✅ Background worker (RQ for async jobs)
- ✅ Cron job (nightly Airtable → Supabase sync)
- ✅ Valkey/Redis cache (sub-50ms lookups)
- ✅ Environment variable groups (DRY config)

**Architecture:**
```
┌─────────────────┐
│   Vercel/CDN    │  Frontend (React)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  clausebot-api  │  Web Service (FastAPI)
│   (Render)      │  ├─ /health, /quiz, /v1/*
└────────┬────────┘  └─ Cache: 300s TTL
         │
         ├──────────────┐
         │              │
         ▼              ▼
┌──────────────┐  ┌──────────────┐
│ clausebot-kv │  │   Supabase   │
│  (Valkey)    │  │  (Postgres)  │
│   Cache      │  │  Source DB   │
└──────────────┘  └──────┬───────┘
         ▲               ▲
         │               │
         └───────┬───────┘
                 │
         ┌───────┴────────┐
         │                │
    ┌────▼─────┐   ┌─────▼──────┐
    │  worker  │   │ nightly-sync│
    │  (RQ)    │   │   (cron)    │
    └──────────┘   └─────────────┘
         │                │
         └────────┬───────┘
                  │
            ┌─────▼──────┐
            │  Airtable  │
            │   Source   │
            └────────────┘
```

---

## 🎯 Prerequisites

1. **GitHub repository** with `clausebot` monorepo
2. **Render account** (https://render.com)
3. **Supabase project** (https://supabase.com)
4. **Airtable account** with Personal Access Token
5. **Environment secrets** (see below)

---

## 📝 Step 1: Prepare Environment Variables

### **Required Secrets (Render Dashboard)**

Create these in Render Dashboard → Environment → `clausebot-shared` group:

```bash
# Supabase (primary database)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=eyJ...your-service-role-key

# Airtable (source data)
AIRTABLE_PAT=pat...your-personal-access-token
AIRTABLE_BASE_ID=appJQ23u70iwOl5Nn
AIRTABLE_CLAUSES_TABLE=tblvvclz8NSpiSVR9
AIRTABLE_EDITIONS_TABLE=tblYourEditionsTable  # Optional
```

### **Public Config (in render.yaml)**

These are already set in `render.yaml` envVarGroup:

```yaml
PLATFORM_VERSION: "AWS D1.1:2025-r1"
CLAUSEBOT_EDITION: "AWS_D1.1:2025"
ALLOW_ORIGINS: "https://clausebot.vercel.app,https://clausebot.miltmonndt.com"
```

---

## 🚢 Step 2: Deploy via Render Blueprint

### **Option A: Create New Blueprint (Recommended)**

1. **Commit** your changes to GitHub:
   ```bash
   cd c:\ClauseBot_API_Deploy\clausebot
   git add backend/render.yaml backend/clausebot_api backend/jobs backend/requirements.txt
   git commit -m "feat: full-stack blueprint with worker, cron, cache"
   git push origin main
   ```

2. **Render Dashboard** → **New +** → **Blueprint**

3. **Connect** your `clausebot` repository

4. **Select branch**: `main` (or your default branch)

5. **Blueprint path**: `backend/render.yaml` (Render auto-detects from root)

6. **Review** the resources Render will create:
   - ✅ `clausebot-api` (web service)
   - ✅ `clausebot-worker` (worker service)
   - ✅ `clausebot-nightly-sync` (cron job)
   - ✅ `clausebot-kv` (Postgres/Key-Value)

7. **Apply** → Wait for provisioning (~5-10 minutes)

### **Option B: Update Existing Blueprint**

If you already have a Blueprint:

1. Push changes to GitHub
2. Render Dashboard → **Your Blueprint** → **Manual Sync**
3. Review changes → **Apply**

---

## 🔧 Step 3: Configure Environment Variable Group

After first deploy, set secrets in the **environment variable group**:

1. Render Dashboard → **Environment** → **Groups**
2. Find `clausebot-shared` group
3. **Add/Edit** each secret:
   - `SUPABASE_URL` → Your Supabase project URL
   - `SUPABASE_SERVICE_KEY` → Service role key (NOT anon key)
   - `AIRTABLE_PAT` → Personal Access Token
   - `AIRTABLE_BASE_ID` → Your base ID
   - `AIRTABLE_CLAUSES_TABLE` → Table name
4. **Save** → Render will redeploy affected services

---

## ✅ Step 4: Verification Checklist

### **4.1 Web Service Health**

```bash
# Basic health
curl https://clausebot-api.onrender.com/health

# Expected:
{
  "ok": true,
  "service": "clausebot-api",
  "edition": "AWS_D1.1:2025"
}
```

### **4.2 Cache Health**

```bash
curl https://clausebot-api.onrender.com/health/cache

# Expected (first time - no hits yet):
{
  "ok": true,
  "enabled": true,
  "ttl_seconds": 300,
  "keyspace_hits": 0,
  "keyspace_misses": 0,
  "hit_rate": 0.0
}
```

### **4.3 Quiz Endpoint (Cache Test)**

```bash
# First call (cache miss - ~500-1000ms)
time curl "https://clausebot-api.onrender.com/quiz?count=5"

# Second call (cache hit - <50ms)
time curl "https://clausebot-api.onrender.com/quiz?count=5"

# Check cache stats again
curl https://clausebot-api.onrender.com/health/cache

# Expected:
{
  "ok": true,
  "keyspace_hits": 1,
  "keyspace_misses": 1,
  "hit_rate": 50.0
}
```

### **4.4 Worker Status**

Render Dashboard → **clausebot-worker** → **Logs**

```
✅ Connected to Valkey/Redis
👂 Listening on queues: default, slow
⚡ Worker ready - waiting for jobs...
```

### **4.5 Cron Job Schedule**

Render Dashboard → **clausebot-nightly-sync** → **Settings**

- Schedule: `0 9 * * *` (09:00 UTC / 01:00 PT)
- Next run: [timestamp]
- Status: Active

**Manual test:**
```bash
# Trigger manual run from Render Dashboard
# Check logs for:
🚀 ClauseBot Airtable → Supabase Sync
✅ SYNC COMPLETE
```

---

## 📊 Step 5: Monitor Cache Performance

### **Cache Metrics Dashboard**

Add to your monitoring:

```bash
# Health check every 60s
watch -n 60 'curl -s https://clausebot-api.onrender.com/health/cache | jq'

# Expected after a few hours:
{
  "ok": true,
  "keyspace_hits": 1234,
  "keyspace_misses": 456,
  "hit_rate": 73.0  # Target: >70%
}
```

### **Cache Tuning**

If hit rate is **<70%**, adjust TTL:

1. Render Dashboard → **clausebot-api** → **Environment**
2. Edit `QUIZ_CACHE_TTL`:
   - Default: `300` (5 min)
   - Low traffic: `600` (10 min)
   - High traffic/static: `900` (15 min)
3. Save → Redeploy

---

## 🔄 Step 6: Verify Nightly Sync

Wait for first cron run (09:00 UTC), then check:

### **Cron Logs**

Render Dashboard → **clausebot-nightly-sync** → **Logs**

```
🚀 ClauseBot Airtable → Supabase Sync
⏰ Started at: 2025-10-28T09:00:00Z
🎯 Mode: airtable_to_supabase

====================================================================
🔄 QUIZ ITEMS SYNC
====================================================================
📥 Fetching Airtable: tblvvclz8NSpiSVR9 (view: viw5Q9YwrJ9Saz8ca)
   ✅ Fetched 250 records
📤 Upserting 250 records to Supabase: quiz_items
   ✅ Batch 1: 100 records
   ✅ Batch 2: 100 records
   ✅ Batch 3: 50 records
   ✅ Total upserted: 250/250

🔥 Warming cache (clearing stale keys)
   ✅ Cleared 12 keys matching cb:/v1/quiz*

====================================================================
✅ SYNC COMPLETE
====================================================================
  quiz_items: 250 records
⏰ Finished at: 2025-10-28T09:00:45Z
```

### **Supabase Verification**

```sql
-- Check sync timestamp
SELECT COUNT(*), MAX(synced_at)
FROM quiz_items;

-- Expected:
-- count: 250
-- max: 2025-10-28 09:00:45+00
```

---

## 🚨 Troubleshooting

### **Problem: KV_URL not set**

**Symptoms:**
```
⚠️  KV_URL not set - cache disabled
```

**Fix:**
1. Verify `clausebot-kv` database exists in Render
2. Check `render.yaml` has `fromService` wiring:
   ```yaml
   - key: KV_URL
     fromService:
       type: pserv
       name: clausebot-kv
       property: connectionString
   ```
3. Redeploy service

### **Problem: Cache connection failed**

**Symptoms:**
```json
{
  "ok": false,
  "enabled": true,
  "error": "Connection refused"
}
```

**Fix:**
1. Check `clausebot-kv` is running (Render Dashboard)
2. Verify service is in same region as database
3. Check Render Private Network is enabled

### **Problem: Worker not processing jobs**

**Symptoms:**
- Jobs enqueued but never complete
- Worker logs show no activity

**Fix:**
1. Check worker logs for connection errors
2. Verify `KV_URL` is set correctly
3. Restart worker service
4. Check job status:
   ```bash
   # Add debug endpoint
   curl https://clausebot-api.onrender.com/jobs/status/{job_id}
   ```

### **Problem: Cron not running**

**Symptoms:**
- No logs at scheduled time
- `synced_at` in Supabase is stale

**Fix:**
1. Check cron is "Active" in Render Dashboard
2. Verify schedule: `0 9 * * *` (09:00 UTC)
3. Check logs for errors during last run
4. Manually trigger test run:
   ```bash
   # In Render Dashboard → clausebot-nightly-sync → Shell
   python -m jobs.airtable_sync
   ```

### **Problem: Airtable sync failed**

**Symptoms:**
```
❌ SYNC FAILED: 401 Unauthorized
```

**Fix:**
1. Verify `AIRTABLE_PAT` is valid:
   ```bash
   curl -H "Authorization: Bearer YOUR_PAT" \
     https://api.airtable.com/v0/meta/bases
   ```
2. Check token has access to base
3. Verify base ID and table names are correct

---

## 🎯 Success Criteria

After deployment, you should have:

- ✅ **API** responding at `/health` with 200 OK
- ✅ **Cache** showing `ok: true` at `/health/cache`
- ✅ **Quiz endpoint** showing **<50ms** response time (cache hits)
- ✅ **Worker** logs showing "Worker ready"
- ✅ **Cron** scheduled for 09:00 UTC daily
- ✅ **Supabase** `quiz_items` table populated
- ✅ **Cache hit rate** >70% after 24 hours

---

## 📈 Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Quiz API (cache hit) | <50ms | `time curl /quiz` |
| Quiz API (cache miss) | <1000ms | First call after sync |
| Cache hit rate | >70% | `/health/cache` |
| Sync duration | <60s | Cron logs |
| Worker queue lag | <5s | RQ dashboard |

---

## 🔧 Maintenance

### **Daily**
- Check `/health/cache` hit rate
- Review error logs (Render Dashboard)
- Verify cron ran successfully

### **Weekly**
- Analyze quiz usage patterns (GA4)
- Review cache TTL effectiveness
- Check Supabase storage usage

### **Monthly**
- Update dependencies (`requirements.txt`)
- Review and optimize worker tasks
- Analyze sync performance trends

---

## 📚 Additional Resources

- [Render Blueprints](https://render.com/docs/blueprint-spec)
- [Render Key-Value (Redis)](https://render.com/docs/key-value)
- [Render Cron Jobs](https://render.com/docs/cronjobs)
- [RQ Documentation](https://python-rq.org/)
- [Valkey/Redis Compatibility](https://valkey.io/)

---

## 🆘 Support

If you encounter issues:

1. Check Render Dashboard logs
2. Review this troubleshooting guide
3. Test endpoints with `curl`
4. Check environment variables in `clausebot-shared` group

**Contact:**
- Email: mjewell@miltmon.com
- SMS: +1-310-755-1124

---

**Last Updated:** October 28, 2025  
**Status:** Production Ready  
**Version:** 1.0.0 (Full-Stack)

