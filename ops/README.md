# ClauseBot Ops Toolkit

**Purpose:** Operational test artifacts that protect production (smoke script, rollback playbook, sampling helpers)

---

## What's in this folder

* `smoke-script.sh` — Idempotent, single-step smoke test used by CI
* `rollback-playbook.md` — Operator playbook for emergency rollback
* `golden-validate.py` — Golden dataset validator for RAG accuracy
* `golden_dataset/golden.json` — Curated test queries with expected clauses
* `README.md` — This file

---

## Quick maintenance & local usage

```bash
# Make scripts executable
chmod +x ops/smoke-script.sh

# Export environment variables (securely)
export API_BASE="https://clausebot-api.onrender.com"
export SUPABASE_URL="https://hqhughgdraokwmreronk.supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="service_role_..."

# Run smoke script
./ops/smoke-script.sh

# Run golden validation
python ops/golden-validate.py --golden ops/golden_dataset/golden.json --pass-rate 0.90
```

---

## How to extend the smoke suite

Keep smoke tests lightweight and fast (<120s). For richer validation, add separate scripts and call from CI as separate steps.

### Pattern for new checks
```
ops/
├── smoke-script.sh           # quick sanity checks
├── golden-validate.py        # golden dataset validator
├── citation-sample-audit.sh  # exports sample for human review (future)
└── reports/                  # QA artifacts
```

---

## Golden dataset validation

### Purpose
Use curated queries with expected canonical clause IDs to prevent retrieval regressions.

### Golden dataset format
```json
{
  "tests": [
    {
      "id": "gd-001",
      "query": "What is minimum preheat for A36 steel?",
      "standard": "AWS D1.1:2020",
      "expected_clauses": ["4.2.3", "Table 4.1"],
      "min_similarity": 0.70
    }
  ]
}
```

### Validator behavior
- POSTs each query to `/v1/chat/compliance`
- Compares returned citations to expected_clauses
- Pass if ANY expected clause in top-K (configurable tolerance)
- Outputs JSON + CSV reports
- Returns non-zero exit code on failure (CI-friendly)

---

## Citation accuracy sampling

### Workflow
1. Sample N recent queries from `chat_citations`
2. Export CSV with query, answer, clause_content, citation_id
3. QA/SME labels: supporting | not_supporting | ambiguous
4. Store labels in DB for metrics and tuning

### Helper script (future)
`ops/citation-sample-audit.sh` will automate steps 1-2

---

## CI integration

* Smoke tests run on every push to main via `post-deploy-smoke.yml`
* Golden validation runs nightly via `golden-validation.yml`
* Keep golden tests fast (<2 min total)
* Heavy tests (100+ queries) should be separate nightly jobs

---

## Metrics & thresholds

Track:
* `smoke_pass_rate` — target: 100%
* `golden_pass_rate` — target: ≥95%
* `citation_accuracy` — target: ≥90% (human-reviewed)
* `avg_rag_latency` — target: <3s

Set alerts:
* `smoke_pass_rate < 100%` → page SRE
* `golden_pass_rate < 90%` → QA review
* `citation_accuracy < 85%` → consider disabling RAG

---

## Security & secrets

* Never hardcode secrets in scripts
* Use environment variables and GitHub Secrets
* Limit access to `SUPABASE_SERVICE_ROLE_KEY`
* Rotate keys regularly

---

## Troubleshooting

**Smoke script fails with 503 from /v1/chat/compliance**
* Check `RAG_ENABLED` env var in Render
* Verify recent deployment succeeded

**Golden validation failures**
* Confirm ingestion: `SELECT count(*) FROM clause_embeddings;`
* Check similarity thresholds in golden.json
* Review retrieval logic for edge cases

**Supabase errors in CI**
* Verify `SUPABASE_SERVICE_ROLE_KEY` permissions
* Check project not paused

---

## Ownership & contacts

* **Ops Owner:** [Add name/Slack]
* **QA Owner:** [Add name/Slack]
* **SRE/On-call:** [Add contact]

---

## Maintenance cadence

* **Daily:** Smoke tests via CI
* **Weekly:** Golden dataset review
* **Monthly:** Citation accuracy sampling
* **Quarterly:** Archive logs, rotate secrets

---

For detailed deployment procedures, see:
* `../backend/DEPLOYMENT_RUNBOOK_CURSOR.md`
* `../backend/TEAM_RESPONSIBILITIES.md`
* `.github/workflows/GOLDEN_FAILURE_CHECKLIST.md`

