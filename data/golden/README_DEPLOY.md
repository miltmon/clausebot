# Golden Test Deployment Guide: Q026-Q041
## AWS D1.1:2025 Canonical Exam Items - NLM SSOT Compliant

### Overview
This package contains 16 canonical golden test items (Q026-Q041) for ClauseBot exam database validation and D1.1:2025 curriculum integration.

**Strategic Coverage:**
- **Clause 4 (Design):** LRFD provisions, joint design
- **Clause 5 (Preheat/Materials):** Table 5.8 updates, filler metal changes
- **Clause 6 (Qualification):** CVN consolidation, waveform tech, PJP reorg
- **Clause 8 (Inspection):** PAUT (Annex H), digital radiography, inspector quals

**Metadata Compliance:**
- ✅ `nlm_source_id` - NotebookLM source tracking
- ✅ `nlm_timestamp` - Content version control
- ✅ `sme_reviewer_initials` - SME approval tracking (currently "TBD")
- ✅ `cms_tag` - Hardcoded "source:notebooklm"

---

### Deployment Workflow

#### Phase 1: Repository Integration (15 min)
```bash
# 1. Create feature branch
git checkout -b golden/Q026-Q041

# 2. Copy JSON files (already in place if using this README)
# Files: golden-Q026.json through golden-Q041.json

# 3. Validate JSON syntax
for f in data/golden/golden-Q*.json; do
  jq empty "$f" && echo "✓ $f" || echo "✗ $f INVALID"
done

# 4. Commit and push
git add data/golden/golden-Q*.json data/golden/README_DEPLOY.md
git commit -m "feat(golden-tests): add Q026-Q041 canonical items (D1.1:2025)"
git push -u origin golden/Q026-Q041
```

#### Phase 2: Pull Request & Review (1-2 days)
```bash
# Create PR via GitHub CLI
gh pr create \
  --title "feat(golden-tests): add Q026-Q041 canonical items" \
  --body-file ops/PR_BODY.md \
  --label "golden-tests,examdb,nlm-canonical" \
  --reviewer sme-lead,qa-lead \
  --draft

# Reviewers check:
# - [ ] JSON schema validity
# - [ ] SSOT metadata present
# - [ ] Clause citations accurate
# - [ ] Rationale complete
```

#### Phase 3: Validator QA (30 min)
```bash
# Run golden validator endpoint
bash scripts/validator_curl_batch.sh

# Expected: 16/16 PASS
```

#### Phase 4: SME Sign-Off (2-3 days)
- SME reviews each item for technical accuracy
- SME updates `sme_reviewer_initials` from "TBD" to actual initials
- SME commits changes to PR branch

#### Phase 5: Staging Ingest (1 hour)
```bash
# Connect to staging DB
psql $SUPABASE_STAGING_URL -f ops/ingest_golden_Q026_Q041.sql

# Verify row counts
psql $SUPABASE_STAGING_URL -c "
SELECT COUNT(*) FROM golden_tests_staging WHERE id BETWEEN 'Q026' AND 'Q041';
"
# Expected: 16 rows
```

#### Phase 6: Production Promotion (30 min)
```bash
# After QA sign-off, promote to production
psql $SUPABASE_PROD_URL -c "
INSERT INTO golden_tests
SELECT * FROM golden_tests_staging
WHERE id BETWEEN 'Q026' AND 'Q041'
ON CONFLICT (id) DO UPDATE SET
  content = EXCLUDED.content,
  metadata = EXCLUDED.metadata,
  updated_at = NOW();
"

# Verify
psql $SUPABASE_PROD_URL -c "
SELECT id, metadata->>'nlm_source_id', metadata->>'sme_reviewer_initials'
FROM golden_tests
WHERE id BETWEEN 'Q026' AND 'Q041'
ORDER BY id;
"
```

---

### Rollback Procedure
```bash
# If issues discovered post-merge
git revert <commit-sha>
git push origin main

# Remove from production DB
psql $SUPABASE_PROD_URL -c "
DELETE FROM golden_tests WHERE id BETWEEN 'Q026' AND 'Q041';
"
```

---

### File Manifest
```
data/golden/
├── README_DEPLOY.md (this file)
├── golden-Q026.json (Clause 5 - Preheat Table 5.8)
├── golden-Q027.json (Clause 8 - PAUT Annex H)
├── golden-Q028.json (Clause 6 - CVN Table 6.7)
├── golden-Q029.json (Clause 8 - Inspector quals 8.14.6.2)
├── golden-Q030.json (Clause 6 - PJP reorg 6.12)
├── golden-Q031.json (Clause 8 - Digital RT geometric unsharpness)
├── golden-Q032.json (Clause 8 - Digital RT procedures)
├── golden-Q033.json (Clause 5 - Shielding gas Table 5.7)
├── golden-Q034.json (Clause 4 - LRFD 4.7)
├── golden-Q035.json (Clause 6 - Waveform essential variables)
├── golden-Q036.json (Clause 5 - Preheat minimum values)
├── golden-Q037.json (Clause 6 - Visual inspection hold time)
├── golden-Q038.json (Clause 6 - PQR requalification triggers)
├── golden-Q039.json (Clause 5 - Filler metal A5 series changes)
├── golden-Q040.json (Clause 8 - Digital RT records)
└── golden-Q041.json (Clause 8 - UT attenuation factor)
```

---

### Support & Escalation
- **Technical Issues:** Platform team (<2 hour response)
- **Content Questions:** SME team (see `sme_reviewer_initials`)
- **Validator Failures:** QA team + reference `ops/golden-validate.py`
- **DB/Ingest Issues:** DevOps + reference `DEPLOYMENT_RUNBOOK_CURSOR.md`

---

**Status:** Ready for deployment  
**Last Updated:** 2025-11-03  
**Maintained By:** Platform Engineering + SME Content Team

