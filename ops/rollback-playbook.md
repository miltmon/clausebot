# ClauseBot RAG - Emergency Rollback Playbook

**Purpose:** Step-by-step emergency procedures for rolling back RAG deployment

**Last Updated:** 2025-11-02

---

## 🚨 When to Use This Playbook

Use this playbook when:
- RAG endpoint returning 5xx errors consistently
- Citation accuracy dropping below 70%
- OpenAI costs spiking unexpectedly
- Database queries timing out
- Golden validation failing with <80% pass rate for >24 hours

---

## ⚡ INSTANT DISABLE (30 seconds)

**Use Case:** RAG is causing production issues, need immediate disable

### Steps

1. **Login to Render Dashboard**
   - Navigate to: https://dashboard.render.com/
   - Select service: `clausebot-api`

2. **Disable Feature Flag**
   - Go to: Environment → Environment Variables
   - Find: `RAG_ENABLED`
   - Change value: `false`
   - Click: **Save**

3. **Trigger Redeploy**
   - Click: **Manual Deploy** → **Deploy Latest Commit**
   - Wait: ~60 seconds for deployment
   - **Result:** RAG endpoint returns 503, existing endpoints unaffected

4. **Verify**
   ```bash
   curl https://clausebot-api.onrender.com/v1/chat/compliance/health
   # Should show: "rag_enabled": false
   ```

**Blast Radius:** ZERO - Existing quiz/health endpoints remain operational

---

## 🔄 CODE REVERT (5 minutes)

**Use Case:** RAG code is buggy, need to revert commits

### Prerequisites
- Identify problematic commit SHA
- Git access to repository

### Steps

1. **Identify Last Good Commit**
   ```bash
   git log --oneline -20
   # Find commit before RAG merge
   ```

2. **Create Revert**
   ```bash
   git revert <bad-commit-sha>
   # Or revert multiple commits:
   git revert <sha1> <sha2> <sha3>
   ```

3. **Push Revert**
   ```bash
   git push origin main
   ```

4. **Monitor Render Deployment**
   - Render auto-deploys on push to main
   - Check logs: https://dashboard.render.com/
   - Expected time: 3-5 minutes

5. **Verify**
   ```bash
   ./ops/smoke-script.sh
   ```

**Recovery Time:** 5-10 minutes

---

## 🗄️ DATABASE ROLLBACK (if needed)

**Use Case:** Corrupted embeddings, need to restore database state

### Option 1: Clear RAG Tables Only (Safe)

```sql
-- Run in Supabase SQL Editor
TRUNCATE TABLE chat_citations CASCADE;
TRUNCATE TABLE clause_embeddings CASCADE;
```

**Impact:** Removes all RAG data, preserves existing app data

### Option 2: Restore from Backup

1. **Login to Supabase Dashboard**
   - Navigate to: https://supabase.com/dashboard/project/<your-project>

2. **Access Backups**
   - Go to: Database → Backups
   - Select: Latest backup before issue

3. **Restore**
   - Click: **Restore**
   - Confirm: Read warning about data loss
   - Wait: 5-15 minutes

4. **Re-run Ingestion** (if needed)
   ```bash
   python backend/scripts/ingest_aws_d11.py
   ```

---

## 📊 ROLLBACK CHECKLIST

Use this checklist to ensure complete rollback:

### Immediate Actions (0-5 minutes)
- [ ] Disable `RAG_ENABLED` in Render
- [ ] Verify existing endpoints still work
- [ ] Post incident notice in Slack (if configured)
- [ ] Save logs/screenshots for post-mortem

### Stabilization (5-30 minutes)
- [ ] Identify root cause (check logs)
- [ ] Decide: instant disable vs code revert
- [ ] Execute appropriate rollback procedure
- [ ] Run smoke tests
- [ ] Monitor error rates for 15 minutes

### Post-Incident (30+ minutes)
- [ ] Document incident in GitHub issue
- [ ] Schedule post-mortem meeting
- [ ] Update golden dataset if needed
- [ ] Review rollback effectiveness
- [ ] Plan fix and redeployment

---

## 🔍 Troubleshooting Common Issues

### Issue: "RAG still responding after disable"

**Cause:** Browser/CDN cache

**Fix:**
```bash
# Hard refresh endpoint
curl -H "Cache-Control: no-cache" https://clausebot-api.onrender.com/v1/chat/compliance/health
```

### Issue: "Revert failed to deploy"

**Cause:** Merge conflict or build error

**Fix:**
1. Check Render logs for build errors
2. Fix issues locally
3. Force push if needed:
   ```bash
   git push origin main --force-with-lease
   ```

### Issue: "Database restore too slow"

**Cause:** Large database, long restore time

**Fix:**
1. Use TRUNCATE instead (instant)
2. Re-ingest from source data
3. Consider smaller ingestion batches

### Issue: "Golden validation still failing after rollback"

**Cause:** Golden dataset expectations misaligned

**Fix:**
1. Review failed tests:
   ```bash
   cat ops/reports/golden-report-*.csv
   ```
2. Update `golden.json` expected_clauses
3. Re-run validation

---

## 📞 Escalation Paths

### P0 - Production Down (RAG breaking existing functionality)
- **Action:** Instant disable + notify on-call SRE
- **Contact:** [PagerDuty link]
- **SLA:** 30-minute response

### P1 - RAG Degraded (RAG not working, existing app OK)
- **Action:** Disable + notify RAG team
- **Contact:** [Slack: @rag-team]
- **SLA:** 2-hour response

### P2 - Quality Issue (Low accuracy, no outage)
- **Action:** Monitor + schedule review
- **Contact:** [Email: qa-lead@example.com]
- **SLA:** Next business day

---

## 🧪 Post-Rollback Validation

After any rollback, run these checks:

```bash
# 1. Smoke tests
./ops/smoke-script.sh

# 2. Existing functionality
curl https://clausebot-api.onrender.com/health
curl https://clausebot-api.onrender.com/api/quiz/baseline/random

# 3. Verify RAG disabled
curl https://clausebot-api.onrender.com/v1/chat/compliance
# Should return: 503 Service Unavailable

# 4. Check logs for errors
# Render Dashboard → Logs → Filter last 15 minutes
```

---

## 📝 Incident Report Template

After rollback, document using this template:

```
## RAG Rollback Incident - [DATE]

**Severity:** [P0/P1/P2]
**Duration:** [Start time] - [End time]
**Rollback Method:** [Instant disable / Code revert / DB restore]

### Timeline
- [HH:MM] Issue detected
- [HH:MM] Rollback initiated
- [HH:MM] Service restored
- [HH:MM] Root cause identified

### Root Cause
[Brief description]

### Impact
- Affected endpoints: [list]
- User impact: [none / degraded / down]
- Duration: [X minutes]

### Action Items
- [ ] Fix root cause
- [ ] Update monitoring
- [ ] Update rollback playbook
- [ ] Schedule post-mortem

### Lessons Learned
[What went well, what to improve]
```

---

## 🔗 Related Documentation

- **Deployment Runbook:** `backend/DEPLOYMENT_RUNBOOK_CURSOR.md`
- **Team Responsibilities:** `backend/TEAM_RESPONSIBILITIES.md`
- **Failure Checklist:** `.github/workflows/GOLDEN_FAILURE_CHECKLIST.md`
- **Smoke Tests:** `ops/smoke-script.sh`

---

**Remember:** Fast rollback is better than perfect diagnosis. Disable first, debug later.

