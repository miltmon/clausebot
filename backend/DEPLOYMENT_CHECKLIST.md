# ✅ ClauseBot Full-Stack Deployment Checklist

## Pre-Deployment

- [ ] Commit all code changes to GitHub
- [ ] Verify `render.yaml` is in repo root or `backend/` directory
- [ ] Have Render account ready
- [ ] Have all environment secrets ready (see below)

---

## Environment Secrets Required

Copy these from your dashboards:

```bash
# Supabase (https://supabase.com/dashboard)
SUPABASE_URL=https://_________________.supabase.co
SUPABASE_SERVICE_KEY=eyJ_________________________

# Airtable (https://airtable.com/create/tokens)
AIRTABLE_PAT=pat_______________________________
AIRTABLE_BASE_ID=app___________________________
AIRTABLE_CLAUSES_TABLE=tbl___________________
AIRTABLE_EDITIONS_TABLE=tbl_________________(optional)
```

---

## Deployment Steps

### 1. Create Blueprint

- [ ] Render Dashboard → **New +** → **Blueprint**
- [ ] Connect GitHub repo: `clausebot`
- [ ] Branch: `main`
- [ ] Review resources (4 items):
  - [ ] `clausebot-api` (web)
  - [ ] `clausebot-worker` (worker)
  - [ ] `clausebot-nightly-sync` (cron)
  - [ ] `clausebot-kv` (database)
- [ ] Click **Apply**
- [ ] Wait for provisioning (~5-10 min)

### 2. Configure Environment Group

- [ ] Go to **Environment** → **Groups** → `clausebot-shared`
- [ ] Add secrets (6 total):
  - [ ] `SUPABASE_URL`
  - [ ] `SUPABASE_SERVICE_KEY`
  - [ ] `AIRTABLE_PAT`
  - [ ] `AIRTABLE_BASE_ID`
  - [ ] `AIRTABLE_CLAUSES_TABLE`
  - [ ] `AIRTABLE_EDITIONS_TABLE` (if applicable)
- [ ] **Save** → Services will redeploy

---

## Verification (5 min)

### Health Checks

```bash
# 1. Basic health
curl https://clausebot-api.onrender.com/health
# Expected: {"ok": true, "service": "clausebot-api"}

# 2. Cache health
curl https://clausebot-api.onrender.com/health/cache
# Expected: {"ok": true, "enabled": true}

# 3. Quiz endpoint (test cache)
curl "https://clausebot-api.onrender.com/quiz?count=5"
# Expected: JSON with 5 questions

# 4. Quiz again (should be faster - cached)
curl "https://clausebot-api.onrender.com/quiz?count=5"
# Expected: Same JSON, <50ms response time
```

### Service Status

- [ ] **clausebot-api**: Status = "Running" (green)
- [ ] **clausebot-worker**: Logs show "Worker ready"
- [ ] **clausebot-nightly-sync**: Schedule shows next run time
- [ ] **clausebot-kv**: Status = "Available"

---

## Post-Deployment

### Immediate (first 10 minutes)

- [ ] Test quiz endpoint 3-5 times
- [ ] Check `/health/cache` shows hits > 0
- [ ] Verify hit_rate is increasing

### First Hour

- [ ] Check worker logs (no errors)
- [ ] Monitor API response times (<100ms typical)
- [ ] Verify Supabase has recent data

### First Day

- [ ] Wait for cron run (09:00 UTC / 01:00 PT)
- [ ] Check cron logs for success
- [ ] Verify Supabase `synced_at` is fresh
- [ ] Cache hit rate should be >50%

### First Week

- [ ] Cache hit rate should be >70%
- [ ] No cron failures
- [ ] Worker processing jobs successfully
- [ ] API response times stable

---

## Quick Smoke Tests

### Cache is Working
```bash
# Clear a test key
curl -X DELETE https://clausebot-api.onrender.com/admin/cache/clear

# Call quiz twice, second should be faster
time curl "https://clausebot-api.onrender.com/quiz?count=5"  # ~500ms
time curl "https://clausebot-api.onrender.com/quiz?count=5"  # <50ms
```

### Worker is Working
```bash
# Trigger a test job (if you add this endpoint)
curl -X POST https://clausebot-api.onrender.com/jobs/test

# Check logs
# Render Dashboard → clausebot-worker → Logs
# Should show: "Processing job: test"
```

### Sync is Working
```bash
# Trigger manual sync
# Render Dashboard → clausebot-nightly-sync → Manual Run

# Check logs for:
# ✅ SYNC COMPLETE
# quiz_items: XXX records

# Verify in Supabase
SELECT COUNT(*), MAX(synced_at) FROM quiz_items;
```

---

## Rollback Plan (if needed)

If something goes wrong:

1. **Disable auto-deploy** in Blueprint settings
2. **Revert commit** on GitHub
3. **Manual sync** Blueprint to previous version
4. **Verify** health checks pass
5. **Investigate** logs for root cause

---

## Success Indicators

After 24 hours, you should see:

- ✅ `/health` → 200 OK
- ✅ `/health/cache` → hit_rate > 70%
- ✅ Quiz API → <50ms (cached), <1s (uncached)
- ✅ Worker logs → No errors
- ✅ Cron logs → Daily success
- ✅ Supabase → Fresh data daily

---

## Common Issues

| Issue | Check | Fix |
|-------|-------|-----|
| Cache disabled | `/health/cache` shows `enabled: false` | Verify `clausebot-kv` is running |
| High miss rate | `/health/cache` shows hit_rate < 50% | Increase `QUIZ_CACHE_TTL` |
| Slow API | Response time > 1s | Check Airtable API limits |
| Cron not running | No logs at 09:00 UTC | Check schedule, trigger manual run |
| Worker idle | No job logs | Verify `KV_URL` is set |
| Sync failed | Cron logs show error | Check `AIRTABLE_PAT` is valid |

---

## Environment Variables Reference

| Variable | Location | Required | Default | Example |
|----------|----------|----------|---------|---------|
| `SUPABASE_URL` | Env Group | ✅ Yes | - | `https://xyz.supabase.co` |
| `SUPABASE_SERVICE_KEY` | Env Group | ✅ Yes | - | `eyJ...` |
| `AIRTABLE_PAT` | Env Group | ✅ Yes | - | `pat...` |
| `AIRTABLE_BASE_ID` | Env Group | ✅ Yes | - | `app...` |
| `AIRTABLE_CLAUSES_TABLE` | Env Group | ✅ Yes | - | `tbl...` |
| `QUIZ_CACHE_TTL` | render.yaml | No | 300 | `300` (seconds) |
| `SYNC_MODE` | render.yaml | No | full | `airtable_to_supabase` |

---

**Print this checklist and check off items as you complete them!**

---

**Deployment Owner:** Milt Jewell  
**Email:** mjewell@miltmon.com  
**Date:** October 28, 2025

