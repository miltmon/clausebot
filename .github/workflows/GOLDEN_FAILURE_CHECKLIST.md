# Golden Dataset Validation Failure - Triage Checklist

**Purpose:** Rapid triage guide for golden validation workflow failures  
**SLA:** Begin triage within 2 hours of failure notification

---

## 🚨 Immediate Actions (First 5 Minutes)

1. **Download Artifacts**
   - Go to failed workflow run
   - Download `golden-validation-reports` artifact
   - Extract ZIP and open CSV file in spreadsheet app

2. **Check Pass Rate**
   ```
   Pass rate < 70% → P1 (urgent)
   Pass rate 70-89% → P2 (review required)
   Pass rate ≥ 90% → False alarm (investigate threshold)
   ```

3. **Classify Failure Type**
   - [ ] **Retrieval failure** (wrong clauses returned)
   - [ ] **Infrastructure failure** (timeouts, 5xx errors)
   - [ ] **Data quality issue** (golden dataset needs update)

---

## 📊 Failure Classification & Response

### Type A: Retrieval Failures (Wrong Clauses)

**Symptoms:**
- `reason = "expected_clause_not_in_topk"`
- Queries return irrelevant clauses
- Pass rate dropped after code change

**Triage Steps:**
1. Open CSV, filter for `passed=False`, `reason=expected_clause_not_in_topk`
2. Count failures by `category` (e.g., "preheat", "inspection")
3. Identify pattern:
   - **Single category affected** → Likely embedding/chunking issue for that topic
   - **All categories affected** → Likely retrieval algorithm regression
   - **Edge cases only** → Likely similarity threshold too strict

**Immediate Fix:**
```bash
# Re-run one failing test manually to debug
python ops/golden-validate.py \
  --golden ops/golden_dataset/golden.json \
  --api-base https://clausebot-api.onrender.com \
  --topk 10 \
  --pass-rate 0.0 \
  --tag debug

# Check if increasing top-k helps
# If yes → retrieval ranking issue
# If no → embeddings or data issue
```

**Remediation Options:**
1. **Lower similarity thresholds** in `golden.json` for affected tests
2. **Re-ingest clauses** with improved chunking
3. **Revert recent changes** if regression identified
4. **Update golden dataset** if expectations incorrect

---

### Type B: Infrastructure Failures (Timeouts, Errors)

**Symptoms:**
- `reason = "error_timeout"` or `reason = "error_exception"`
- Multiple tests with high latency (>10s)
- HTTP 5xx errors in response

**Triage Steps:**
1. Check Render service status: https://dashboard.render.com/
2. Check OpenAI API status: https://status.openai.com/
3. Check Supabase status: https://status.supabase.com/
4. Review Render logs for stack traces

**Diagnostic Commands:**
```bash
# Test API health directly
curl https://clausebot-api.onrender.com/health
curl https://clausebot-api.onrender.com/v1/chat/compliance/health

# Check Supabase clause count
# (via SQL editor or Supabase dashboard)
SELECT count(*) FROM clause_embeddings;
```

**Remediation Options:**
1. **If Render down** → Wait for recovery or switch regions
2. **If OpenAI rate limited** → Implement backoff, lower request rate
3. **If Supabase slow** → Check query plans, add indexes
4. **If persistent** → Disable RAG (`RAG_ENABLED=false`)

---

### Type C: Data Quality Issues (Golden Dataset Outdated)

**Symptoms:**
- Tests pass locally but fail in CI
- Expected clauses don't exist in ingested data
- New standard version deployed

**Triage Steps:**
1. Check if recent ingestion ran successfully
2. Verify `clause_embeddings` contains expected clause IDs:
   ```sql
   SELECT clause_id FROM clause_embeddings 
   WHERE section IN ('4.2.3', 'Table 4.1', ...);
   ```
3. Compare golden dataset version to ingested standard version

**Remediation Options:**
1. **Update golden dataset** to match ingested data
2. **Re-ingest correct standard** version
3. **Archive outdated tests** and create new ones

---

## 🔍 Detailed Investigation

### Step 1: Identify Top Failures

```bash
# From CSV, sort by best_similarity ascending
# Focus on tests with similarity < 0.50 (very wrong)

grep ",False," ops/reports/golden-report-*.csv | \
  sort -t',' -k7 -n | head -10
```

### Step 2: Manual Query Test

```bash
# Pick one failing test, query manually
curl -X POST https://clausebot-api.onrender.com/v1/chat/compliance \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is minimum preheat for A36 steel?",
    "top_k": 5
  }' | jq .
```

**Analyze:**
- Are returned clauses relevant to query?
- Is similarity score reasonable (>0.60)?
- Does answer include correct citations?

### Step 3: Check Recent Changes

```bash
# Review recent commits
git log --oneline -10

# If recent RAG changes, consider revert
git revert <commit-sha>
```

---

## 🛠️ Quick Fixes (Choose One)

### Fix 1: Lower Similarity Thresholds

Edit `ops/golden_dataset/golden.json`:
```json
{
  "id": "gd-014",
  "min_similarity": 0.60  // Was 0.70, lowered
}
```

**When:** Tests failing with `reason=match_below_similarity_threshold`

### Fix 2: Re-Ingest Clauses

```bash
export OPENAI_API_KEY="sk-..."
export SUPABASE_URL="https://..."
export SUPABASE_SERVICE_ROLE_KEY="service_role_..."

python backend/scripts/ingest_aws_d11.py
```

**When:** Data freshness issue, chunking improved

### Fix 3: Update Golden Dataset

```json
// Change expected_clauses to match current retrieval
{
  "id": "gd-001",
  "expected_clauses": ["4.2.3", "4.2"]  // Removed "Table 4.1"
}
```

**When:** Expectations incorrect, standard changed

### Fix 4: Disable RAG Temporarily

```bash
# Via Render dashboard
RAG_ENABLED=false
# Redeploy
```

**When:** P0 incident, need immediate mitigation

---

## 📞 Escalation Matrix

| Pass Rate | Severity | Owner | Action | SLA |
|-----------|----------|-------|--------|-----|
| <70% | P1 | @rag-team + @oncall-sre | Immediate investigation, consider disable | 2h response |
| 70-85% | P2 | @rag-team | Scheduled investigation | Next day |
| 85-89% | P3 | @qa-lead | Review + tune | Next sprint |
| ≥90% | P4 | @rag-team | Monitor, no action | - |

### Contacts

- **RAG Team Lead:** [Slack: @rag-lead]
- **QA Lead:** [Slack: @qa-lead]
- **On-Call SRE:** [PagerDuty rotation]
- **Platform Lead:** [Slack: @platform-lead]

---

## 📝 Post-Triage Actions

After resolving failure:

1. **Document Root Cause**
   - Create GitHub issue with failure details
   - Link to workflow run and artifacts
   - Tag with `rag-validation` label

2. **Update Monitoring**
   - If new failure mode, add detection
   - Adjust thresholds if needed

3. **Update Runbooks**
   - Add to this checklist if new pattern
   - Update `ops/README.md` with learnings

4. **Communicate**
   - Post summary in team Slack
   - Update stakeholders if P1

---

## 🎯 Success Criteria

Triage complete when:
- [ ] Root cause identified and documented
- [ ] Fix applied and validated
- [ ] Golden validation passing again
- [ ] Team notified of resolution
- [ ] Post-mortem scheduled (if P1)

---

## 📚 Related Documentation

- **Deployment Runbook:** `backend/DEPLOYMENT_RUNBOOK_CURSOR.md`
- **Rollback Playbook:** `ops/rollback-playbook.md`
- **Team Responsibilities:** `backend/TEAM_RESPONSIBILITIES.md`
- **Workflows README:** `.github/workflows/README.md`

---

**Remember:** Golden validation failures are NOT always bad - they may indicate dataset needs updating as the system improves.

