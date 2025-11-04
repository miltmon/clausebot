# PR Workflow Quick Reference Guide

**Purpose:** Standardized git commands for creating feature PRs with proper CI validation gates.

---

## 🚀 Standard Feature PR Workflow

### **1. Create Feature Branch**

```bash
# Ensure you're on latest main
cd c:\ClauseBot_API_Deploy\clausebot
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/your-feature-name

# Example naming conventions:
# feature/rag-integration
# fix/airtable-timeout
# docs/api-specification
# test/golden-Q042-Q050
```

### **2. Make Changes and Commit**

```bash
# Stage your changes
git add <files>

# Commit with conventional commit format
git commit -m "feat: add new quiz validation endpoint"
git commit -m "fix: resolve Airtable connection timeout"
git commit -m "docs: update deployment runbook"
git commit -m "test: add golden tests Q042-Q050"

# Conventional commit prefixes:
# feat: - New feature
# fix: - Bug fix
# docs: - Documentation only
# test: - Adding or updating tests
# refactor: - Code refactoring
# perf: - Performance improvement
# ci: - CI/CD changes
# chore: - Maintenance tasks
```

### **3. Push and Create PR**

```bash
# Push feature branch to origin
git push -u origin feature/your-feature-name

# Create PR via GitHub CLI (recommended)
gh pr create \
  --base main \
  --head feature/your-feature-name \
  --title "feat: Your Feature Title" \
  --body "## Description

Detailed description of changes.

## Changes
- Change 1
- Change 2

## Testing
- [ ] Manual testing completed
- [ ] CI smoke tests pass
- [ ] No new linter errors

## Checklist
- [ ] Code follows project conventions
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No breaking changes (or documented)
" \
  --assignee @me \
  --label "enhancement"

# Or create PR via browser
# GitHub will prompt you after push
```

### **4. Wait for CI Validation**

```bash
# Check CI status
gh pr checks

# View detailed run
gh run list --workflow="CI Smoke Tests ClauseBot"

# Watch live (auto-refresh)
gh run watch
```

### **5. Address Review Feedback**

```bash
# Make requested changes
git add <files>
git commit -m "fix: address PR review comments"
git push

# Amend last commit if needed (before review)
git add <files>
git commit --amend --no-edit
git push --force-with-lease
```

### **6. Merge PR**

```bash
# Merge via CLI (after approval)
gh pr merge --squash --delete-branch

# Or merge via GitHub web UI
# Choose "Squash and merge" for clean history
```

---

## 🧪 Pre-PR Validation Checklist

**Run these locally BEFORE creating PR:**

```bash
# 1. Lint check (if configured)
# flake8 clausebot_api/ (Python)
# eslint frontend/ (JavaScript)

# 2. Local smoke test
curl -fsS http://localhost:8000/health | jq
curl -fsS "http://localhost:8000/v1/quiz?count=1" | jq

# 3. Verify no secrets committed
git diff main --name-only | xargs grep -i "api_key\|secret\|password" || echo "✅ No secrets found"

# 4. Verify conventional commit format
git log --oneline -5

# 5. Check for merge conflicts
git fetch origin main
git merge-base --is-ancestor origin/main HEAD && echo "✅ No conflicts" || echo "⚠️ Rebase needed"
```

---

## 🔥 Emergency Hotfix Workflow

**For critical production fixes:**

```bash
# 1. Create hotfix from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-issue-name

# 2. Make minimal fix
# ... edit files ...
git add <files>
git commit -m "fix: resolve critical production issue"

# 3. Push and create urgent PR
git push -u origin hotfix/critical-issue-name
gh pr create \
  --base main \
  --head hotfix/critical-issue-name \
  --title "🔥 HOTFIX: Critical Issue Name" \
  --body "## Critical Issue

**Severity:** HIGH
**Impact:** Production down / Data loss / Security

## Root Cause
...

## Fix
...

## Testing
- [ ] Tested locally
- [ ] Verified in staging

## Deployment
Requires immediate merge and deploy.
" \
  --label "hotfix,priority:high" \
  --assignee @me

# 4. Request immediate review
# 5. Merge and monitor deployment
gh pr merge --squash --delete-branch
```

---

## 📋 Common PR Scenarios

### **Scenario A: RAG Feature Integration**

```bash
git checkout -b feature/rag-compliance-endpoint
# ... make changes ...
git add backend/clausebot_api/routes/chat_compliance.py
git add backend/clausebot_api/services/rag_service.py
git add backend/sql/supabase_pgvector_rag.sql
git commit -m "feat: add RAG compliance chat endpoint (feature-flagged)"
git push -u origin feature/rag-compliance-endpoint
gh pr create --base main --title "feat: RAG compliance endpoint" --label "enhancement,rag"
```

### **Scenario B: Golden Test Addition**

```bash
git checkout -b test/golden-Q042-Q057
# ... create test files ...
git add ops/golden_dataset/golden-Q042.json
git add ops/golden_dataset/golden-Q043.json
# ... (add all)
git commit -m "test: add golden tests Q042-Q057 for D1.1:2025"
git push -u origin test/golden-Q042-Q057
gh pr create --base main --title "test: golden tests Q042-Q057" --label "testing,d1.1-2025"
```

### **Scenario C: Documentation Update**

```bash
git checkout -b docs/update-api-specification
# ... update docs ...
git add docs/API_SPEC.md
git add README.md
git commit -m "docs: update API specification with RAG endpoints"
git push -u origin docs/update-api-specification
gh pr create --base main --title "docs: update API specification" --label "documentation"
```

### **Scenario D: Bug Fix**

```bash
git checkout -b fix/airtable-connection-retry
# ... implement fix ...
git add backend/clausebot_api/services/airtable_service.py
git commit -m "fix: add retry logic for Airtable connection timeout"
git push -u origin fix/airtable-connection-retry
gh pr create --base main --title "fix: Airtable connection retry" --label "bug"
```

---

## 🎯 PR Best Practices

1. **Keep PRs Small:** Aim for <500 lines of code changes
2. **Single Responsibility:** One feature/fix per PR
3. **Descriptive Titles:** Use conventional commit format
4. **Complete Descriptions:** Explain what, why, and how
5. **Test Coverage:** Include tests with code changes
6. **Documentation:** Update docs with feature changes
7. **Clean Commits:** Squash work-in-progress commits
8. **CI Green:** Never merge with failing CI
9. **Review Responses:** Address all review comments
10. **Delete Branches:** Clean up after merge

---

## 🛠️ Troubleshooting

### **Problem: PR shows merge conflicts**

```bash
# Rebase on latest main
git checkout feature/your-branch
git fetch origin main
git rebase origin/main

# Resolve conflicts
# ... edit conflicted files ...
git add <resolved-files>
git rebase --continue

# Force push (safe with --force-with-lease)
git push --force-with-lease
```

### **Problem: CI tests failing**

```bash
# Pull CI logs
gh run view --log

# Run tests locally
curl -fsS https://clausebotai.onrender.com/health | jq

# Check specific endpoint
curl -fsS "https://clausebotai.onrender.com/v1/quiz?count=1" | jq
```

### **Problem: Accidentally committed secrets**

```bash
# Remove from last commit
git reset HEAD~1
# Remove secret from file
git add <file>
git commit -m "fix: remove accidentally committed secret"

# If already pushed, rotate the secret immediately
# Then force push:
git push --force-with-lease

# Alert team about compromised secret
```

### **Problem: Need to split large PR**

```bash
# Create new branch from main
git checkout main
git checkout -b feature/part-1

# Cherry-pick specific commits
git cherry-pick <commit-sha>

# Push and create separate PR
git push -u origin feature/part-1
gh pr create --base main --title "feat: Part 1 of larger feature"
```

---

## 📊 PR Labels Reference

| Label | Usage |
|-------|-------|
| `enhancement` | New features |
| `bug` | Bug fixes |
| `documentation` | Docs only |
| `testing` | Test additions |
| `hotfix` | Critical production fixes |
| `priority:high` | High priority |
| `priority:low` | Low priority |
| `rag` | RAG-related changes |
| `d1.1-2025` | D1.1:2025 updates |
| `wip` | Work in progress |
| `needs-review` | Awaiting review |
| `needs-testing` | Needs QA |

---

## 🔗 Quick Links

- **Repository:** https://github.com/miltmon/clausebotai
- **CI/CD Runs:** https://github.com/miltmon/clausebotai/actions
- **Render Dashboard:** https://dashboard.render.com/web/srv-d37fjc0gjchc73c8gfs0
- **Vercel Dashboard:** https://vercel.com/miltmonllc/clausebot
- **OpenAPI Docs:** https://clausebotai.onrender.com/docs

---

**Last Updated:** November 3, 2025  
**Version:** 1.0  
**Owner:** Miltmon LLC

