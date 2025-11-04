# Golden Test Q026-Q041 Deployment Manifest
**Generated:** 2025-11-03  
**Package:** AWS D1.1:2025 Canonical Exam Items  
**Status:** ✅ All files created and ready for deployment

---

## 📦 Complete File Inventory

### Golden Test JSON Files (16 items)
```
c:\ClauseBot_API_Deploy\clausebot\data\golden\
├── README_DEPLOY.md ..................... Deployment guide
├── golden-Q026.json ..................... Clause 5 - Preheat Table 5.8 (A514)
├── golden-Q027.json ..................... Clause 8 - PAUT Annex H
├── golden-Q028.json ..................... Clause 6 - CVN Table 6.7
├── golden-Q029.json ..................... Clause 8 - Inspector quals 8.14.6.2
├── golden-Q030.json ..................... Clause 6 - PJP reorg 6.12
├── golden-Q031.json ..................... Clause 8 - Geometric unsharpness
├── golden-Q032.json ..................... Clause 8 - Digital RT procedures
├── golden-Q033.json ..................... Clause 5 - Shielding gas Table 5.7
├── golden-Q034.json ..................... Clause 4 - LRFD 4.7
├── golden-Q035.json ..................... Clause 6 - Waveform essential vars
├── golden-Q036.json ..................... Clause 5 - Preheat minimum values
├── golden-Q037.json ..................... Clause 6 - Visual hold time
├── golden-Q038.json ..................... Clause 6 - PQR requalification
├── golden-Q039.json ..................... Clause 5 - A5 series filler metals
├── golden-Q040.json ..................... Clause 8 - Digital RT records
└── golden-Q041.json ..................... Clause 8 - UT attenuation factor
```

### Operational Scripts & Docs
```
c:\ClauseBot_API_Deploy\clausebot\ops\
├── PR_BODY.md ........................... GitHub PR description template
├── ingest_golden_Q026_Q041.sql .......... PostgreSQL/Supabase ingestion script
└── release-golden-Q026-Q041.sh .......... Complete automation script

c:\ClauseBot_API_Deploy\clausebot\scripts\
└── validator_curl_batch.sh .............. Batch validator for Q026-Q041
```

---

## ✅ SSOT Metadata Compliance

**All 16 items include:**
- ✅ `nlm_source_id` - NotebookLM tracking ID (format: NLM-AWS-D11-2025-Qxxx-001)
- ✅ `nlm_timestamp` - Content version timestamp (2025-11-03T00:00:00Z)
- ✅ `sme_reviewer_initials` - Set to "TBD" (assign during PR review)
- ✅ `cms_tag` - Hardcoded "source:notebooklm"
- ✅ `code_reference_primary` - AWS D1.1:2025 clause citation
- ✅ `exam_db_category` - Exam classification
- ✅ `cwi_competency` - CWI training alignment

---

## 🎯 Strategic Coverage Summary

### Clause Distribution
| Clause | Count | Topics |
|--------|-------|--------|
| Clause 4 (Design) | 1 | LRFD provisions |
| Clause 5 (Materials) | 4 | Preheat, shielding gas, filler metals |
| Clause 6 (Qualification) | 5 | CVN, PJP, waveform, hold time, requalification |
| Clause 8 (Inspection) | 6 | PAUT, inspector quals, digital RT, UT |

### Difficulty Distribution
- Easy: 1 item (Q033)
- Medium: 9 items (Q026, Q027, Q028, Q030, Q032, Q033, Q034, Q036, Q037, Q039)
- Hard: 6 items (Q029, Q031, Q035, Q038, Q040, Q041)

---

## 🚀 Quick Start Deployment

### Option 1: Automated Release (Recommended)
```bash
# Navigate to repo root
cd c:\ClauseBot_API_Deploy\clausebot

# Configure reviewers (optional - edit script or set env vars)
export REVIEWERS="sme-lead qa-lead"
export ASSIGNEE="dev-lead"

# Run release automation
bash ops/release-golden-Q026-Q041.sh
```

**This will:**
1. ✅ Create feature branch `golden/Q026-Q041`
2. ✅ Validate JSON syntax for all files
3. ✅ Commit all 20 files
4. ✅ Push to remote
5. ✅ Create draft PR with reviewers assigned

---

### Option 2: Manual Deployment

```bash
# 1. Create branch
cd c:\ClauseBot_API_Deploy\clausebot
git checkout -b golden/Q026-Q041

# 2. Validate JSON
for f in data/golden/golden-Q*.json; do 
  jq empty "$f" && echo "✓ $f" || echo "✗ $f FAILED"
done

# 3. Stage files
git add data/golden/*.json
git add data/golden/README_DEPLOY.md
git add ops/PR_BODY.md
git add ops/ingest_golden_Q026_Q041.sql
git add scripts/validator_curl_batch.sh
git add ops/release-golden-Q026-Q041.sh

# 4. Commit
git commit -m "feat(golden-tests): add Q026-Q041 canonical items (D1.1:2025)"

# 5. Push
git push -u origin golden/Q026-Q041

# 6. Create PR (via GitHub web UI or CLI)
gh pr create --draft --body-file ops/PR_BODY.md
```

---

## 🔍 Validation & QA

### Step 1: Validator Check
```bash
# Set validator URL (if different from default)
export VALIDATOR_URL="https://clausebot-api.onrender.com/v1/golden/validate"

# Run batch validator
bash scripts/validator_curl_batch.sh

# Expected output: ✅ ALL TESTS PASSED (16/16)
```

### Step 2: SME Review
1. Assign SME reviewer in PR
2. SME verifies:
   - Technical accuracy of rationale
   - Correct clause citations
   - Expected answers match code
3. SME updates `sme_reviewer_initials` from "TBD" to initials
4. SME commits changes to PR branch

### Step 3: Staging Ingest
```bash
# Set database URL
export SUPABASE_STAGING_URL="postgresql://..."

# Run ingestion
psql $SUPABASE_STAGING_URL -f ops/ingest_golden_Q026_Q041.sql

# Verify row count (expect 16)
psql $SUPABASE_STAGING_URL -c "SELECT COUNT(*) FROM golden_tests_staging WHERE id BETWEEN 'Q026' AND 'Q041';"
```

### Step 4: Production Promotion
```bash
# After QA sign-off
export SUPABASE_PROD_URL="postgresql://..."

# Promote to production
psql $SUPABASE_PROD_URL -c "
INSERT INTO golden_tests 
SELECT * FROM golden_tests_staging 
WHERE id BETWEEN 'Q026' AND 'Q041'
ON CONFLICT (id) DO UPDATE SET 
  content = EXCLUDED.content, 
  updated_at = NOW();
"
```

---

## 🔄 Rollback Procedure

**If critical issues discovered:**

```bash
# 1. Revert git commit
git revert <commit-sha>
git push origin main

# 2. Remove from production DB
psql $SUPABASE_PROD_URL -c "DELETE FROM golden_tests WHERE id BETWEEN 'Q026' AND 'Q041';"

# 3. Document in audit log
# (See ops/ingest_golden_Q026_Q041.sql for audit table)
```

---

## 📞 Support & Escalation

| Issue Type | Contact | Response Time |
|------------|---------|---------------|
| Technical/Script Errors | Platform team | <2 hours |
| Content/Accuracy Questions | SME lead | 1-2 business days |
| Validator Failures | QA team | <4 hours |
| Database Issues | DevOps | <2 hours |

**References:**
- Deployment Guide: `data/golden/README_DEPLOY.md`
- Crosswalk CSV: `docs/crosswalk/aws_d11_2020_to_2025.csv`
- Main Parking Doc: `PARKING.md`
- Resume Checklist: `RESUME_CHECKLIST.md`

---

## ✅ Completion Checklist

### Pre-Deployment
- [x] All 16 JSON files created
- [x] All JSON files validate with `jq`
- [x] SSOT metadata present in all items
- [x] README_DEPLOY.md completed
- [x] PR_BODY.md template created
- [x] Ingest SQL script ready
- [x] Validator script ready
- [x] Release automation script ready

### Deployment Phase
- [ ] Feature branch created
- [ ] All files committed and pushed
- [ ] Draft PR created with reviewers
- [ ] Validator run (16/16 PASS)
- [ ] SME review completed
- [ ] SME initials updated
- [ ] Staging ingest successful
- [ ] QA sign-off obtained

### Production Phase
- [ ] PR merged to main
- [ ] Production ingest completed
- [ ] Verification queries passed
- [ ] Audit log entry created
- [ ] Team notified

---

## 🎉 Package Complete!

**Status:** ✅ **ALL FILES CREATED AND READY**

**Next Action:** Run `bash ops/release-golden-Q026-Q041.sh` or follow manual deployment steps above.

**Questions?** Reference `data/golden/README_DEPLOY.md` for detailed workflow.

---

**Package Generated:** 2025-11-03  
**Total Files:** 20 (16 JSON + 4 operational)  
**Total Lines:** ~2,500+ (documentation + code + data)  
**Compliance:** 100% SSOT metadata coverage

