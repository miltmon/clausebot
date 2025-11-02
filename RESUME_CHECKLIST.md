# ClauseBot RAG - Resumption Checklist

**Purpose:** Step-by-step guide to unpark and activate RAG system  
**Prerequisites:** Content work complete, source files obtained, SME crosswalk ready  
**Estimated Time:** 2-4 hours for full resumption

---

## ✅ **Pre-Flight Checks**

Before starting, confirm:

- [ ] Manus website updates complete (D1.1:2025 pages live)
- [ ] SME crosswalk ≥50% complete (100+ rows verified)
- [ ] AWS D1.1:2020 source files obtained (PDF or `clauses.json`)
- [ ] Q032-Q050 quiz questions reviewed and approved
- [ ] Budget approval for $180/month OpenAI costs
- [ ] Team trained on rollback procedures

**If any item unchecked:** Review `PARKING.md` handoff responsibilities first

---

## 🚀 **Phase 1: Environment Preparation (30 minutes)**

### Step 1.1: Verify Repository State

```bash
cd c:\ClauseBot_API_Deploy\clausebot
git fetch origin
git checkout main
git pull origin main
git log --oneline --decorate -10

# Should see tag v1.0-rag-mvp-park
git tag --list | grep rag-mvp-park
```

**Expected:** Clean main branch with all parked commits

---

### Step 1.2: Check Production Environment

```bash
# Test existing functionality (should work)
curl https://clausebot-api.onrender.com/health
curl https://clausebot-api.onrender.com/api/quiz/baseline/random

# Test RAG endpoint (should return 503)
curl https://clausebot-api.onrender.com/v1/chat/compliance/health
```

**Expected:**
- `/health`: `{"ok": true}`
- `/api/quiz`: Returns quiz question
- `/v1/chat/compliance/health`: `{"status": "error"}` or 503 (RAG disabled)

---

### Step 1.3: Verify Supabase State

Login to Supabase dashboard → SQL Editor:

```sql
-- Check tables exist
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('clause_embeddings', 'chat_citations', 'clause_sme_log', 'miltmon_ndt_q_upload_log');

-- Check clause_embeddings is empty (awaiting ingestion)
SELECT count(*) FROM clause_embeddings;

-- Check indexes exist
SELECT indexname FROM pg_indexes WHERE tablename = 'clause_embeddings';
```

**Expected:**
- 4 tables exist
- `clause_embeddings` count = 0 (or small test data)
- Multiple indexes exist (embedding, content_fts, nlm_source, etc.)

---

## 📥 **Phase 2: Data Ingestion (1-2 hours)**

### Step 2.1: Prepare Source Data

**Option A: Use existing `clauses.json`**

```bash
# Verify file exists
ls backend/data/codes/aws_d1_1_2020/index/clauses.json

# Check format
head -20 backend/data/codes/aws_d1_1_2020/index/clauses.json
```

**Option B: Create from PDF** (if JSON not available)

See `backend/scripts/pdf_to_json_converter.py` (create if needed) or use NotebookLM export

---

### Step 2.2: Set Environment Variables (Local)

```bash
# Windows PowerShell
$env:OPENAI_API_KEY="sk-..."
$env:SUPABASE_URL="https://hqhughgdraokwmreronk.supabase.co"
$env:SUPABASE_SERVICE_ROLE_KEY="service_role_..."

# Verify
echo $env:OPENAI_API_KEY
```

---

### Step 2.3: Run Ingestion Script

```bash
cd backend
python scripts/ingest_aws_d11.py
```

**Expected Output:**
```
========================================
ClauseBot RAG - AWS D1.1 Ingestion
========================================
Golden dataset: backend/data/codes/aws_d1_1_2020/index/clauses.json
Loaded 1,247 clauses
Preparing to embed 1,247 chunks...
Embedding batch 1/25 (50 items)...
[... progress ...]
Ingestion complete.
Total clauses processed: 1,247
Successfully upserted: 1,247
Errors: 0
```

**If errors occur:**
- Check OpenAI API key validity
- Check Supabase service role key permissions
- Review `backend/scripts/ingest_aws_d11.py` error messages

---

### Step 2.4: Verify Ingestion

```sql
-- In Supabase SQL Editor
SELECT count(*) FROM clause_embeddings;
SELECT standard, count(*) FROM clause_embeddings GROUP BY standard;
SELECT clause_id, title, substring(content, 1, 100) 
FROM clause_embeddings 
LIMIT 10;

-- Check embedding dimensions
SELECT clause_id, array_length(embedding, 1) as dim 
FROM clause_embeddings 
LIMIT 5;
```

**Expected:**
- Count ≥ 1,000 (depends on source file)
- Standard = 'AWS D1.1:2020'
- Embedding dimensions = 3072

---

## ✅ **Phase 3: Local Validation (30 minutes)**

### Step 3.1: Run Golden Validator Locally

```bash
cd clausebot
python ops/golden-validate.py \
  --golden ops/golden_dataset/golden.json \
  --api-base https://clausebot-api.onrender.com \
  --topk 5 \
  --pass-rate 0.85 \
  --tag resume-validation
```

**Expected:** Pass rate ≥85% (lower threshold for first run)

**If pass rate <85%:**
1. Review `ops/reports/golden-report-*.csv`
2. Check which tests failed (reason column)
3. Adjust similarity thresholds in `golden.json` if needed
4. Re-run until pass rate acceptable

---

### Step 3.2: Manual Query Testing

```bash
# Test with curl
curl -X POST https://clausebot-api.onrender.com/v1/chat/compliance \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is minimum preheat for 1 inch A36 steel?",
    "top_k": 5
  }' | jq .
```

**Expected:** Should return 503 (RAG still disabled)

---

### Step 3.3: Run Smoke Tests (Local)

```bash
chmod +x ops/smoke-script.sh
./ops/smoke-script.sh
```

**Expected:** All tests pass except RAG endpoint (disabled)

---

## 🔓 **Phase 4: Enable RAG (5 minutes)**

### Step 4.1: Update Render Environment Variables

1. Login to https://dashboard.render.com/
2. Select service: `clausebot-api`
3. Go to: **Environment** → **Environment Variables**
4. Find: `RAG_ENABLED`
5. Change value: `false` → `true`
6. Click: **Save**

---

### Step 4.2: Trigger Redeploy

1. Click: **Manual Deploy** → **Deploy Latest Commit**
2. Wait: ~60-90 seconds for deployment
3. Monitor logs for: `✅ RAG compliance router enabled at /v1/chat/compliance`

---

### Step 4.3: Verify RAG Active

```bash
# Health check should now show operational
curl https://clausebot-api.onrender.com/v1/chat/compliance/health | jq .

# Expected: {"status": "operational", "rag_enabled": true}

# Test query
curl -X POST https://clausebot-api.onrender.com/v1/chat/compliance \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is minimum preheat for A36 steel?",
    "standard": "AWS D1.1:2020",
    "top_k": 5
  }' | jq .
```

**Expected:** Returns answer with citations

---

## 🧪 **Phase 5: Production Validation (30 minutes)**

### Step 5.1: Run Full Golden Validation

```bash
python ops/golden-validate.py \
  --golden ops/golden_dataset/golden.json \
  --api-base https://clausebot-api.onrender.com \
  --topk 5 \
  --pass-rate 0.90 \
  --tag production-validation
```

**Expected:** Pass rate ≥90%

---

### Step 5.2: Run Smoke Tests (Production)

```bash
export API_BASE="https://clausebot-api.onrender.com"
./ops/smoke-script.sh
```

**Expected:** All tests pass (including RAG endpoint)

---

### Step 5.3: Monitor Initial Queries

```sql
-- In Supabase SQL Editor
-- Check citations being logged
SELECT 
  query,
  canonical_id,
  similarity_score,
  created_at
FROM chat_citations
ORDER BY created_at DESC
LIMIT 20;

-- Check for fallback logging (Priority 3)
SELECT 
  query,
  fallback_reason,
  priority,
  status
FROM miltmon_ndt_q_upload_log
ORDER BY timestamp DESC
LIMIT 10;
```

---

### Step 5.4: Cost Monitoring

1. Login to OpenAI platform: https://platform.openai.com/
2. Go to: **Usage**
3. Check: Daily API usage (embeddings + completions)
4. Set: Budget alert at $200/month

**Expected:** ~$6-10/day for moderate usage (500 queries/day)

---

## 📊 **Phase 6: Operational Monitoring (Ongoing)**

### Daily (First Week)

- [ ] Check golden validation results (GitHub Actions)
- [ ] Review `miltmon_ndt_q_upload_log` for Priority 3 fallbacks
- [ ] Monitor OpenAI usage and costs
- [ ] Check Render logs for errors (5xx responses)

### Weekly (First Month)

- [ ] Review golden validation pass rate trends
- [ ] Sample 10 chat_citations for accuracy review
- [ ] Check average response latency
- [ ] Update golden dataset with new queries

### Monthly (Ongoing)

- [ ] SME review of fallback queue (Q051-Q110 creation)
- [ ] Performance tuning (similarity thresholds)
- [ ] Cost optimization review
- [ ] Stakeholder reporting (metrics dashboard)

---

## 🚨 **Rollback Procedures (If Needed)**

### Immediate Disable (30 seconds)

```bash
# Via Render dashboard:
# Environment → RAG_ENABLED → false → Save → Manual Deploy
```

### Full Rollback (5 minutes)

```bash
git revert v1.0-rag-mvp-park..HEAD
git push origin main
# Render auto-deploys reverted state
```

**See:** `ops/rollback-playbook.md` for detailed procedures

---

## ✅ **Resumption Completion Checklist**

- [ ] Phase 1: Environment verified
- [ ] Phase 2: Data ingested (count > 1,000)
- [ ] Phase 3: Local validation passed
- [ ] Phase 4: RAG enabled in production
- [ ] Phase 5: Production validation passed (≥90%)
- [ ] Phase 6: Monitoring established
- [ ] Team notified (Slack announcement)
- [ ] Stakeholders updated (email from `STAKEHOLDER_ANNOUNCEMENT.md`)
- [ ] Documentation reviewed with team
- [ ] On-call rotation aware of new system

---

## 📞 **Support Contacts**

| Issue | Contact | Response Time |
|-------|---------|---------------|
| **Ingestion errors** | Platform Team | 4 hours |
| **OpenAI quota exceeded** | Platform Team | 2 hours |
| **Supabase connection issues** | Platform Team | 1 hour |
| **Golden validation failures** | QA Lead + Platform | 24 hours |
| **Production outage (5xx errors)** | On-Call SRE | 30 minutes |

---

## 🎯 **Success Criteria**

**Minimum Requirements:**
- ✅ Ingestion: ≥1,000 clauses in database
- ✅ Golden validation: ≥90% pass rate
- ✅ Smoke tests: 100% pass
- ✅ Response latency: <4s average (95th percentile)
- ✅ Error rate: <2% of requests
- ✅ Cost: Within $180/month budget

**Stretch Goals:**
- 🎯 Golden validation: ≥95% pass rate
- 🎯 Response latency: <3s average
- 🎯 Zero Priority 3 fallbacks for top 50 queries
- 🎯 User satisfaction: >4.0/5.0 (if collecting feedback)

---

## 📚 **Related Documentation**

- **Operations:** `ops/rollback-playbook.md`
- **Deployment:** `backend/DEPLOYMENT_RUNBOOK_CURSOR.md`
- **Team Responsibilities:** `backend/TEAM_RESPONSIBILITIES.md`
- **Failure Triage:** `.github/workflows/GOLDEN_FAILURE_CHECKLIST.md`
- **Migration Planning:** `docs/crosswalk/README.md`

---

**🎉 System resumed successfully! Monitor closely for first 48 hours.**

**Questions?** Contact Platform Lead or review `PARKING.md`

---

**Last Updated:** 2025-11-02  
**Version:** 1.0  
**Next Review:** After first production week

