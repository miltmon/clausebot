# 🎯 Skyvern Package Value Verification Checklist

**Package:** Skyvern OpenAI + Aurora + S3 Runtime  
**Purpose:** Verify 5 core value propositions are working as designed  
**Audience:** Reviewers, maintainers, security auditors

---

## ✅ **HOW TO USE THIS CHECKLIST**

1. **Run each verification** in order (some depend on previous steps)
2. **Tick the checkbox** when the outcome matches expectations
3. **Document any issues** in the "Notes" section at bottom
4. **All 5 must pass** before approving for production use

---

## 1️⃣ **Privacy-First LLM Usage & Redaction** (Compliance-Safe)

**Value:** Prevents accidental leakage of PII/API keys to the model and enforces vendor contract constraints (no training/retention).

### Verification Steps

**Setup:**
```bash
cd infra/skyvern-package/Node
npm install
node server.js &
SERVER_PID=$!
sleep 2
```

**Test A: Email Redaction**
```bash
curl -X POST http://localhost:3000/extract \
  -H "Content-Type: application/json" \
  -d '{
    "pageObj": {"title": "Contact: john.doe@example.com"},
    "selectors": [{"name": "email"}],
    "task": "Extract contact",
    "schema": {"type": "object"}
  }'
```

**Expected:** Response logs show `[REDACTED:EMAIL]` instead of actual email

**Test B: API Key Redaction**
```bash
curl -X POST http://localhost:3000/extract \
  -H "Content-Type: application/json" \
  -d '{
    "pageObj": {"key": "sk-1234567890abcdef"},
    "selectors": [{"name": "key"}],
    "task": "Extract key",
    "schema": {"type": "object"}
  }'
```

**Expected:** Response logs show `[REDACTED:API_KEY]` instead of actual key

**Cleanup:**
```bash
kill $SERVER_PID
```

### Acceptance Criteria

- [ ] Email addresses are redacted in request logs
- [ ] API keys (sk-, pk-) are redacted in request logs
- [ ] Redacted content is NOT sent to LLM API
- [ ] Original data is preserved in response (redaction is log-only)
- [ ] Middleware logs show redaction count

**Pass/Fail:** ⬜ Pass  ⬜ Fail

---

## 2️⃣ **Encrypted, Auditable Artifact Storage + Lifecycle**

**Value:** S3 + KMS + retention worker provides encrypted outputs, clear retention policies, and automatic purge so audit data doesn't linger.

### Verification Steps

**Setup:**
```bash
cd infra/skyvern-package/Node
# Ensure .env has: AWS_REGION, OBJECT_STORE_BUCKET, AWS_KMS_KEY_ARN (or IAM role)
```

**Test A: Upload with Encryption**
```javascript
// In Node REPL or test file
const { uploadJSON } = require('./s3Storage');

uploadJSON('test-artifact.json', { test: 'data', timestamp: Date.now() })
  .then(result => console.log('Upload result:', result));
```

**Expected:** Upload succeeds with KMS encryption metadata

**Test B: Verify S3 Object Metadata**
```bash
aws s3api head-object \
  --bucket YOUR-BUCKET \
  --key test-artifact.json \
  --query '{Encryption:ServerSideEncryption,KMSKey:SSEKMSKeyId}'
```

**Expected:** 
```json
{
  "Encryption": "aws:kms",
  "KMSKey": "arn:aws:kms:REGION:ACCOUNT:key/YOUR-KEY-ID"
}
```

**Test C: Retention Worker (Dry Run)**
```bash
cd ../Python
export DRY_RUN=true
export RETENTION_DAYS=90
python retention_worker.py
```

**Expected:** Worker logs show:
- Connected to Aurora
- Found N objects older than 90 days
- DRY RUN: Would delete [list of keys]
- No actual deletions occurred

### Acceptance Criteria

- [ ] S3 uploads use `ServerSideEncryption=aws:kms`
- [ ] KMS key ARN matches configured value
- [ ] Retention worker connects to Aurora successfully
- [ ] Worker correctly identifies objects > retention period
- [ ] Dry run mode prevents actual deletions
- [ ] Deletion logs are written to database

**Pass/Fail:** ⬜ Pass  ⬜ Fail

---

## 3️⃣ **Least-Privilege Auth & No Hardcoded Secrets**

**Value:** Using RDS IAM tokens and role-based AWS access removes long-lived DB/AWS keys from source, shrinking blast radius.

### Verification Steps

**Test A: RDS IAM Token Generation**
```bash
cd infra/skyvern-package/Python
export RDS_IAM=true
export DB_HOST=your-aurora-cluster.region.rds.amazonaws.com
export DB_PORT=5432
export DB_USER=iam_user
export DB_NAME=postgres

python -c "
from retention_worker import generate_rds_iam_token
token = generate_rds_iam_token()
print(f'Token generated: {token[:20]}...')
print(f'Token length: {len(token)} chars')
"
```

**Expected:**
```
Token generated: your-cluster.region...
Token length: 500+ chars
```

**Test B: Connect with IAM Token**
```bash
python retention_worker.py --test-connection
```

**Expected:** 
```
✓ Generated RDS IAM token
✓ Connected to Aurora database
✓ Connection test passed
```

**Test C: Verify No Hardcoded Secrets**
```bash
cd infra/skyvern-package
grep -r "AKIA\|sk-\|password" . --exclude=".env.example" --exclude="*.md"
```

**Expected:** No matches (only `.env.example` should have placeholders)

**Test D: IAM Role Test (if using EC2/ECS/GitHub Actions)**
```bash
# On runner with IAM role attached
aws sts get-caller-identity
```

**Expected:** Shows role ARN, not access key user

### Acceptance Criteria

- [ ] RDS IAM token generation succeeds
- [ ] Connection to Aurora works with generated token
- [ ] Token expires after 15 minutes (test re-generation)
- [ ] No hardcoded AWS keys in codebase
- [ ] No database passwords in codebase
- [ ] IAM role assumed correctly (if applicable)
- [ ] Boto3 uses default credential chain (no explicit keys)

**Pass/Fail:** ⬜ Pass  ⬜ Fail

---

## 4️⃣ **Shift-Left Secret Scanning + Repo Hygiene**

**Value:** Automated trufflehog/git-secrets + pre-commit hooks stop secrets before they land in history — fewer emergency key rotations.

### Verification Steps

**Test A: Pre-commit Hooks (Local)**
```bash
cd infra/skyvern-package

# Install pre-commit
pip install pre-commit
pre-commit install

# Create test file with fake secret
echo "aws_access_key_id = AKIAIOSFODNN7EXAMPLE" > test-secret.txt
git add test-secret.txt

# Try to commit
git commit -m "test: should fail"
```

**Expected:** Commit blocked with message about detected secret

**Cleanup:**
```bash
git reset HEAD test-secret.txt
rm test-secret.txt
```

**Test B: CI Secret Scan**
```bash
# Check PR #4 CI run
gh run list --repo miltmon/clausebot --branch feature/skyvern-openai-aura-s3-package --limit 1
gh run view <RUN_ID> --log | grep -i "trufflehog\|secret"
```

**Expected:** CI passes with "No secrets found"

**Test C: Manual Trufflehog Scan**
```bash
# Scan current branch
docker run --rm -v $(pwd):/src trufflesecurity/trufflehog:latest git file:///src --only-verified
```

**Expected:** `No verified secrets found`

**Test D: Git-secrets Scan**
```bash
# Install git-secrets (if not already)
# macOS: brew install git-secrets
# Linux: see https://github.com/awslabs/git-secrets

cd infra/skyvern-package
git secrets --scan
```

**Expected:** No secrets detected

### Acceptance Criteria

- [ ] Pre-commit hooks installed and working
- [ ] Hooks block commits with secrets
- [ ] CI workflow includes trufflehog scan
- [ ] CI workflow includes git-secrets scan
- [ ] All scans pass with zero findings
- [ ] `.env` is in `.gitignore`
- [ ] Only `.env.example` is committed (no real values)

**Pass/Fail:** ⬜ Pass  ⬜ Fail

---

## 5️⃣ **Portable, Reviewable Infra Pattern**

**Value:** Self-contained package with `.env.example`, vendor-swap notes, and testable components makes onboarding, audits, and provider swaps fast and low-risk.

### Verification Steps

**Test A: Swap to Mock LLM Endpoint**
```bash
cd infra/skyvern-package/Node

# Update .env
echo "LLM_API_URL=http://localhost:8000/v1/completions" >> .env

# Start mock server (in another terminal)
# Simple mock using Python
python3 -m http.server 8000 &
MOCK_PID=$!

# Run extraction test
node -e "
const { callLLM } = require('./llmClient');
callLLM('test prompt', {})
  .then(r => console.log('Response:', r))
  .catch(e => console.log('Error (expected):', e.message));
"

kill $MOCK_PID
```

**Expected:** Client attempts to call mock endpoint (fails gracefully with timeout/error, but proves URL is configurable)

**Test B: Run Unit Tests**
```bash
cd infra/skyvern-package/Node
npm test
```

**Expected:** All tests pass

**Test C: Documentation Completeness**
```bash
cd infra/skyvern-package

# Check README has key sections
grep -E "Quick Start|Environment Variables|IAM Permissions|Troubleshooting" README.md

# Check .env.example is complete
cat .env.example | grep -E "OPENAI_API_KEY|AWS_REGION|DB_HOST"
```

**Expected:** All sections present, all required env vars documented

**Test D: Zero External Dependencies for Reading**
```bash
# Verify someone can audit without running code
ls -la infra/skyvern-package/
cat infra/skyvern-package/README.md
cat infra/skyvern-package/.env.example
cat infra/skyvern-package/schema.sql
```

**Expected:** All key files are readable text (no compiled artifacts required)

**Test E: Swap to Anthropic (Optional)**
```bash
# Update llmClient.js to use Claude API
# Change base URL and model name
# No business logic changes should be needed

# Verify tests still pass with minimal modifications
npm test
```

**Expected:** Swap requires only config changes, no logic rewrites

### Acceptance Criteria

- [ ] LLM endpoint URL is configurable via .env
- [ ] Unit tests run and pass
- [ ] README documents all environment variables
- [ ] README includes quick start guide
- [ ] README includes IAM policy example
- [ ] README includes troubleshooting section
- [ ] `.env.example` includes all required variables with placeholders
- [ ] Schema.sql is readable SQL (not ORM-generated gibberish)
- [ ] Package is self-contained (no parent repo dependencies)
- [ ] Swapping LLM vendor requires only config changes

**Pass/Fail:** ⬜ Pass  ⬜ Fail

---

## 📊 **VERIFICATION SUMMARY**

| # | Value Proposition | Pass/Fail | Notes |
|---|-------------------|-----------|-------|
| 1 | Privacy-First LLM & Redaction | ⬜ | |
| 2 | Encrypted Storage + Lifecycle | ⬜ | |
| 3 | Least-Privilege Auth (IAM) | ⬜ | |
| 4 | Secret Scanning + Hygiene | ⬜ | |
| 5 | Portable Infra Pattern | ⬜ | |

**Overall Status:** ⬜ **All Pass** (ready for production)  
**Overall Status:** ⬜ **Some Fail** (needs fixes - see notes)

---

## 📝 **NOTES & ISSUES**

Document any failures, warnings, or observations here:

```
[Your notes here]


```

---

## ✅ **APPROVAL CHECKLIST**

Before approving this PR for merge:

- [ ] All 5 verification tests pass
- [ ] CI is green (no secret findings)
- [ ] Repository secrets configured (or IAM role plan documented)
- [ ] Aurora IAM user created and tested
- [ ] S3 bucket + KMS key exist and permissions verified
- [ ] README reviewed and accurate
- [ ] Follow-up issue created for monitoring/OIDC setup
- [ ] At least 1 maintainer assigned

**Approved by:** ________________  
**Date:** ________________

---

## 🚀 **NEXT STEPS AFTER VERIFICATION**

1. **If all pass:** Approve PR, merge to main, deploy to staging
2. **If any fail:** Document in Notes, create issues, fix and re-test
3. **After merge:** Run verification again in staging environment
4. **After staging:** Run verification in production
5. **Ongoing:** Add smoke tests to CI/CD pipeline for continuous verification

---

**Questions?** Open an issue: `gh issue create --repo miltmon/clausebot --label skyvern,infra`

