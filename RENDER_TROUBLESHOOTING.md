# Render Deployment Troubleshooting Guide

**Date:** October 25, 2025
**Issue:** Deployment failed after monorepo migration
**Commit:** `c14d194` - "fix: add CORS regex for Vercel previews + integrate GA4"

---

## Quick Diagnosis Checklist

Go to: https://dashboard.render.com/web/srv-d37fjc0gjchc73c8gfs0/settings

### ✅ Required Configuration

**Build & Deploy Section:**
- [ ] **Repository**: `miltmon/clausebot` (NOT `clausebot-api`)
- [ ] **Branch**: `main`
- [ ] **Root Directory**: `backend` (exactly this, no slashes)
- [ ] **Build Command**: Empty (uses Dockerfile)
- [ ] **Docker Command**: Empty (uses Dockerfile CMD)

**Environment Section:**
- [ ] **Plan**: Starter or higher
- [ ] **Environment**: Docker
- [ ] **Auto-Deploy**: Enabled (optional)

**Health Check:**
- [ ] **Path**: `/health`
- [ ] **Interval**: 10s
- [ ] **Timeout**: 5s

---

## Common Error Patterns

### Error: "Could not find requirements.txt"

**Cause:** Root Directory not set to `backend`

**Fix:**
1. Set Root Directory to `backend` (no slashes)
2. Save changes
3. Manual deploy

---

### Error: "Repository not found" or "Failed to clone"

**Cause:** Still pointing to old `clausebot-api` repo

**Fix:**
1. Build & Deploy → Repository → Edit
2. Select `miltmon/clausebot`
3. Save changes
4. Manual deploy

---

### Error: "COPY failed: no such file or directory"

**Cause:** Docker build context is wrong directory

**Fix:**
1. Verify Root Directory = `backend`
2. Check Dockerfile COPY paths:
   - `COPY clausebot_api ./clausebot_api` ✅
   - `COPY data ./data` ✅
   - `COPY config ./config` ✅
3. Ensure these directories exist in `backend/`

---

### Error: "ModuleNotFoundError: No module named 'clausebot_api'"

**Cause:** Package not installed or PYTHONPATH wrong

**Fix:**
1. Verify Dockerfile has: `RUN pip install -e .`
2. Verify pyproject.toml exists in backend/
3. Check Render environment variable `PYTHONPATH` not set (Docker handles this)

---

### Error: "Health check failed"

**Cause:** Service started but `/health` endpoint not responding

**Fix:**
1. Check if service is listening on correct port
2. Verify `uvicorn clausebot_api.main:app --host 0.0.0.0 --port $PORT`
3. Check Render environment variable `PORT` is set

---

## Successful Deploy Log Example

```
==> Cloning repository from https://github.com/miltmon/clausebot
==> Checking out commit c14d194 in branch main
==> Using root directory: backend
==> Building Docker image from Dockerfile
==> Step 1/12 : FROM python:3.11-slim AS base
==> Step 2/12 : ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
==> Step 3/12 : WORKDIR /app
...
==> Successfully built Docker image
==> Starting container
==> Service is listening on port 8081
==> Health check passed: GET /health returned 200
==> Your service is live 🎉
```

---

## Manual Verification Commands

After deployment succeeds, verify with:

```powershell
# Health check
Invoke-RestMethod https://clausebot-api.onrender.com/health

# Airtable connection
Invoke-RestMethod https://clausebot-api.onrender.com/health/airtable

# Quiz baseline
Invoke-RestMethod https://clausebot-api.onrender.com/health/quiz/baseline
```

Expected responses:
```json
{"ok": true, "service": "clausebot-api", "version": "0.1.0"}
{"ok": true, "airtable_connection": "healthy"}
{"total_records": 121, "eligible_count": 114}
```

---

## Render Dashboard Quick Links

- **Service Settings:** https://dashboard.render.com/web/srv-d37fjc0gjchc73c8gfs0/settings
- **Events/Logs:** https://dashboard.render.com/web/srv-d37fjc0gjchc73c8gfs0/events
- **Environment Variables:** https://dashboard.render.com/web/srv-d37fjc0gjchc73c8gfs0/env
- **Manual Deploy:** https://dashboard.render.com/web/srv-d37fjc0gjchc73c8gfs0/deploys

---

## Next Steps After Successful Deploy

1. ✅ Verify `/health` endpoint responds
2. ✅ Verify `/health/airtable` endpoint responds
3. ✅ Test quiz endpoint with: `https://clausebot-api.onrender.com/api/quiz?count=3`
4. ✅ Proceed with Vercel frontend deployment
5. ✅ Run comprehensive smoke tests

---

**Last Updated:** 2025-10-25 09:30 AM PDT

