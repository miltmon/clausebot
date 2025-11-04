# Golden Tests Q026–Q041: D1.1:2025 Canonical Release

## Overview
Adds 16 canonical golden test items (Q026-Q041) fully aligned to AWS D1.1:2025 code updates and ClauseBot validator/SSOT ingestion pipeline.

**Compliance:** All items include complete NLM/SSOT metadata (`source:notebooklm` tagged)

---

## Strategic Coverage

### Clause 4 (Design)
- **Q034:** LRFD provisions (new Clause 4.7)

### Clause 5 (Preheat & Materials)
- **Q026:** Preheat Table 5.8 - A514 steel requirements
- **Q033:** Shielding gas compositions (Table 5.7)
- **Q036:** Updated preheat values for new steel grades
- **Q039:** A5 series filler metal reference updates

### Clause 6 (Qualification)
- **Q028:** CVN consolidation into Table 6.7
- **Q030:** PJP groove weld reorganization (6.12)
- **Q035:** Waveform control essential variables (6.8.1)
- **Q037:** Visual inspection hold time (6.5.3)
- **Q038:** PQR requalification triggers (6.7)

### Clause 8 (Inspection & NDT)
- **Q027:** PAUT normative Annex H
- **Q029:** Inspector qualification updates (8.14.6.2)
- **Q031:** Geometric unsharpness (Ug) methodology
- **Q032:** Digital radiography procedures (8.17.20)
- **Q040:** Digital RT records retention (8.17.21)
- **Q041:** UT attenuation factor methodology (8.18)

---

## Artifacts Included

### JSON Golden Test Files
```
data/golden/
├── golden-Q026.json through golden-Q041.json
└── README_DEPLOY.md
```

### SSOT Metadata (Per Item)
- ✅ `nlm_source_id` - NotebookLM tracking ID
- ✅ `nlm_timestamp` - Content version timestamp
- ✅ `sme_reviewer_initials` - Currently "TBD" (to be assigned)
- ✅ `cms_tag` - Hardcoded "source:notebooklm"
- ✅ `code_reference_primary` - AWS D1.1:2025 clause citation
- ✅ `exam_db_category` - Exam classification
- ✅ `cwi_competency` - CWI training alignment

---

## Review Checklist

### Technical Validation
- [ ] All JSON files parse correctly (`jq empty golden-Q*.json`)
- [ ] Schema compliance verified (id, version, metadata present)
- [ ] Rationale fields complete and accurate
- [ ] Citations reference correct D1.1:2025 clauses

### Validator QA
- [ ] Run validator batch script: `bash scripts/validator_curl_batch.sh`
- [ ] Confirm 16/16 PASS result
- [ ] Review any similarity threshold warnings

### SME Sign-Off
- [ ] SME reviews technical accuracy of rationale
- [ ] SME verifies clause citations against D1.1:2025 PDF
- [ ] SME updates `sme_reviewer_initials` from "TBD" to initials
- [ ] SME commits changes to this PR branch

### QA/Staging
- [ ] Run staging ingest: `psql $SUPABASE_STAGING_URL -f ops/ingest_golden_Q026_Q041.sql`
- [ ] Verify row counts match expected (16 rows)
- [ ] Spot-check 3-5 items in staging DB for data integrity

---

## Deployment Instructions

**Full workflow documented in:** `data/golden/README_DEPLOY.md`

**Quick commands:**
```bash
# 1. Validate JSON syntax
for f in data/golden/golden-Q*.json; do jq empty "$f" && echo "✓ $f"; done

# 2. Run validator
bash scripts/validator_curl_batch.sh

# 3. After SME approval, ingest to staging
psql $SUPABASE_STAGING_URL -f ops/ingest_golden_Q026_Q041.sql

# 4. Promote to production (post-QA)
psql $SUPABASE_PROD_URL -c "INSERT INTO golden_tests SELECT * FROM golden_tests_staging WHERE id BETWEEN 'Q026' AND 'Q041' ON CONFLICT (id) DO UPDATE SET content = EXCLUDED.content, updated_at = NOW();"
```

---

## Rollback Plan

**If critical issues discovered:**
```bash
# 1. Revert git commit
git revert <commit-sha>
git push origin main

# 2. Remove from production DB
psql $SUPABASE_PROD_URL -c "DELETE FROM golden_tests WHERE id BETWEEN 'Q026' AND 'Q041';"

# 3. Document issue in ops/rollback log
```

---

## Related Documentation
- **Deployment Guide:** `data/golden/README_DEPLOY.md`
- **Crosswalk CSV:** `docs/crosswalk/aws_d11_2020_to_2025.csv`
- **Validator Script:** `scripts/validator_curl_batch.sh`
- **Ingest SQL:** `ops/ingest_golden_Q026_Q041.sql`

---

## Contacts & Escalation
- **Technical Issues:** Platform team (<2 hour response)
- **Content Questions:** SME lead (TBD - assign during review)
- **Validator Failures:** QA team + reference `ops/golden-validate.py`
- **DB Issues:** DevOps + `DEPLOYMENT_RUNBOOK_CURSOR.md`

---

**Status:** Ready for SME review & validator QA  
**Target Merge:** After all checkboxes complete  
**Production Go-Live:** Post-QA sign-off

