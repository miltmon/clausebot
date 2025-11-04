#!/usr/bin/env bash
# Golden Test Release Automation
# Creates branch, commits Q026-Q041 files, and opens draft PR

set -euo pipefail

# ========================================
# CONFIGURATION - EDIT BEFORE RUNNING
# ========================================

GIT_REMOTE="${GIT_REMOTE:-origin}"
BASE_BRANCH="${BASE_BRANCH:-main}"
FEATURE_BRANCH="golden/Q026-Q041"
PR_TITLE="feat(golden-tests): add Q026-Q041 canonical items (D1.1:2025)"
PR_BODY_FILE="ops/PR_BODY.md"
PR_LABELS="golden-tests,examdb,nlm-canonical,d1.1-2025"

# Reviewers (GitHub usernames, space-separated)
REVIEWERS="${REVIEWERS:-sme-lead qa-lead}"
ASSIGNEE="${ASSIGNEE:-dev-lead}"

# Files to add
FILES_TO_ADD=(
  "data/golden/README_DEPLOY.md"
  "data/golden/golden-Q026.json"
  "data/golden/golden-Q027.json"
  "data/golden/golden-Q028.json"
  "data/golden/golden-Q029.json"
  "data/golden/golden-Q030.json"
  "data/golden/golden-Q031.json"
  "data/golden/golden-Q032.json"
  "data/golden/golden-Q033.json"
  "data/golden/golden-Q034.json"
  "data/golden/golden-Q035.json"
  "data/golden/golden-Q036.json"
  "data/golden/golden-Q037.json"
  "data/golden/golden-Q038.json"
  "data/golden/golden-Q039.json"
  "data/golden/golden-Q040.json"
  "data/golden/golden-Q041.json"
  "ops/PR_BODY.md"
  "ops/ingest_golden_Q026_Q041.sql"
  "scripts/validator_curl_batch.sh"
)

# ========================================
# DEPENDENCY CHECK
# ========================================

echo "Checking dependencies..."

if ! command -v git >/dev/null 2>&1; then
  echo "ERROR: git is required but not installed."
  exit 1
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "ERROR: GitHub CLI (gh) is required but not installed."
  echo "Install: https://cli.github.com/"
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "ERROR: jq is required but not installed."
  exit 1
fi

# Verify gh auth
if ! gh auth status >/dev/null 2>&1; then
  echo "ERROR: GitHub CLI is not authenticated."
  echo "Run: gh auth login"
  exit 1
fi

echo "✓ All dependencies satisfied"
echo ""

# ========================================
# VERIFY FILES EXIST
# ========================================

echo "Verifying files exist..."
MISSING_FILES=()

for file in "${FILES_TO_ADD[@]}"; do
  if [ ! -f "$file" ]; then
    MISSING_FILES+=("$file")
  fi
done

if [ ${#MISSING_FILES[@]} -gt 0 ]; then
  echo "ERROR: The following files are missing:"
  printf '  - %s\n' "${MISSING_FILES[@]}"
  echo ""
  echo "Generate files first or adjust FILES_TO_ADD array."
  exit 2
fi

echo "✓ All files present"
echo ""

# ========================================
# VALIDATE JSON FILES
# ========================================

echo "Validating JSON syntax..."
JSON_FILES=(data/golden/golden-Q*.json)
INVALID_FILES=()

for file in "${JSON_FILES[@]}"; do
  if ! jq empty "$file" 2>/dev/null; then
    INVALID_FILES+=("$file")
  fi
done

if [ ${#INVALID_FILES[@]} -gt 0 ]; then
  echo "ERROR: Invalid JSON in the following files:"
  printf '  - %s\n' "${INVALID_FILES[@]}"
  exit 3
fi

echo "✓ All JSON files valid"
echo ""

# ========================================
# GIT BRANCH CREATION
# ========================================

echo "Creating feature branch: $FEATURE_BRANCH"

# Fetch latest from remote
git fetch "$GIT_REMOTE"

# Check if branch already exists locally
if git rev-parse --verify "$FEATURE_BRANCH" >/dev/null 2>&1; then
  echo "WARNING: Branch $FEATURE_BRANCH already exists locally."
  read -p "Delete and recreate? (y/N): " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    git branch -D "$FEATURE_BRANCH"
  else
    echo "Aborting."
    exit 4
  fi
fi

# Create branch from base
git checkout -b "$FEATURE_BRANCH" "$GIT_REMOTE/$BASE_BRANCH"

echo "✓ Branch created"
echo ""

# ========================================
# STAGE AND COMMIT FILES
# ========================================

echo "Staging files..."

for file in "${FILES_TO_ADD[@]}"; do
  git add "$file"
  echo "  + $file"
done

echo ""
echo "Committing changes..."

COMMIT_MSG="feat(golden-tests): add Q026-Q041 canonical items (D1.1:2025)

- 16 golden test items covering strategic D1.1:2025 updates
- Full NLM SSOT metadata compliance (source:notebooklm)
- Coverage: Clauses 4, 5, 6, 8 (PAUT, CVN, waveform, digital RT)
- SME initials: TBD (to be assigned during PR review)

Files:
- data/golden/README_DEPLOY.md
- data/golden/golden-Q026.json through Q041.json
- ops/PR_BODY.md
- ops/ingest_golden_Q026_Q041.sql
- scripts/validator_curl_batch.sh"

git commit -m "$COMMIT_MSG"

echo "✓ Changes committed"
echo ""

# ========================================
# PUSH TO REMOTE
# ========================================

echo "Pushing to remote: $GIT_REMOTE/$FEATURE_BRANCH"

git push -u "$GIT_REMOTE" "$FEATURE_BRANCH"

echo "✓ Branch pushed"
echo ""

# ========================================
# CREATE PULL REQUEST
# ========================================

echo "Creating draft pull request..."

# Build reviewer args
REVIEWER_ARGS=()
for reviewer in $REVIEWERS; do
  REVIEWER_ARGS+=(--reviewer "$reviewer")
done

# Create PR
gh pr create \
  --base "$BASE_BRANCH" \
  --head "$FEATURE_BRANCH" \
  --title "$PR_TITLE" \
  --body-file "$PR_BODY_FILE" \
  --label "$PR_LABELS" \
  "${REVIEWER_ARGS[@]}" \
  --assignee "$ASSIGNEE" \
  --draft

echo "✓ Draft PR created"
echo ""

# ========================================
# NEXT STEPS
# ========================================

echo "========================================="
echo "✅ RELEASE PROCESS INITIATED"
echo "========================================="
echo ""
echo "PR created as DRAFT - next steps:"
echo ""
echo "1. Run validator:"
echo "   bash scripts/validator_curl_batch.sh"
echo ""
echo "2. Review validator output (expect 16/16 PASS)"
echo ""
echo "3. Assign SME for content review:"
echo "   - Update sme_reviewer_initials in each JSON file"
echo "   - Commit changes to PR branch"
echo ""
echo "4. After SME approval, mark PR as ready for review"
echo ""
echo "5. After QA sign-off, merge PR"
echo ""
echo "6. Run production ingest:"
echo "   psql \$SUPABASE_PROD_URL -f ops/ingest_golden_Q026_Q041.sql"
echo ""
echo "========================================="
echo "PR URL: $(gh pr view --json url -q .url)"
echo "========================================="

exit 0

