#!/bin/bash
set -e

echo "════════════════════════════════════════════════════════════════"
echo "🚀 CLAUSEBOT MONOREPO CONSOLIDATION"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Verify we're in the right directory
if [ ! -f "package.json" ] || [ ! -d "frontend" ]; then
    echo "❌ ERROR: Not in clausebot monorepo root"
    echo "Please run this from: c:/ClauseBot_API_Deploy/clausebot"
    exit 1
fi

echo "✅ Confirmed: In clausebot monorepo"
echo ""

# Check if clausebot-api exists as sibling
if [ ! -d "../clausebot-api" ]; then
    echo "❌ ERROR: ../clausebot-api not found"
    echo "Please ensure clausebot-api repo exists at: c:/ClauseBot_API_Deploy/clausebot-api"
    exit 1
fi

echo "✅ Confirmed: clausebot-api repo found"
echo ""

# Create feature branch
echo "📌 Step 1: Creating feature branch..."
git checkout -b feat/import-clausebot-api 2>/dev/null || git checkout feat/import-clausebot-api
echo "✅ Branch: feat/import-clausebot-api"
echo ""

# Add remote (remove if exists)
echo "🔗 Step 2: Adding remote for clausebot-api..."
git remote remove clausebot-api-remote 2>/dev/null || true
git remote add clausebot-api-remote ../clausebot-api
echo "✅ Remote added"
echo ""

# Fetch
echo "⬇️  Step 3: Fetching clausebot-api history..."
git fetch clausebot-api-remote
echo "✅ Fetch complete"
echo ""

# Import with subtree (preserves history)
echo "🔀 Step 4: Importing via git subtree..."
echo "   This preserves all commit history from clausebot-api"
echo ""
git subtree add --prefix=backend/clausebot-api clausebot-api-remote main
echo ""
echo "✅ Subtree import complete"
echo ""

# Verify
echo "🔍 Step 5: Verifying import..."
if [ -d "backend/clausebot-api" ]; then
    echo "✅ Directory created: backend/clausebot-api"
    
    if [ -f "backend/clausebot-api/clausebot_api/routes/agent_memory.py" ]; then
        echo "✅ BEADS code found: agent_memory.py"
    else
        echo "⚠️  WARNING: agent_memory.py not found"
    fi
    
    if [ -f "backend/clausebot-api/test_beads_integration.ps1" ]; then
        echo "✅ Test suite found: test_beads_integration.ps1"
    else
        echo "⚠️  WARNING: test_beads_integration.ps1 not found"
    fi
else
    echo "❌ ERROR: Import failed - directory not created"
    exit 1
fi
echo ""

# Show file structure
echo "📁 Imported file structure:"
ls -la backend/clausebot-api/ | head -15
echo ""

# Show commit history
echo "📜 Preserved commit history (last 5 commits):"
git log backend/clausebot-api/ --oneline | head -5
echo ""

# Show git status
echo "📊 Current git status:"
git status
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "✅ IMPORT COMPLETE!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📋 NEXT STEPS:"
echo ""
echo "1️⃣  Review imported files:"
echo "   cd backend/clausebot-api && ls -la"
echo ""
echo "2️⃣  Test locally (in new terminal):"
echo "   cd backend/clausebot-api"
echo "   python -m venv .venv"
echo "   source .venv/bin/activate  # or .venv\\Scripts\\activate on Windows"
echo "   pip install -r requirements.txt"
echo "   uvicorn clausebot_api.main:app --reload"
echo ""
echo "3️⃣  Run integration tests (in another terminal):"
echo "   cd backend/clausebot-api"
echo "   pwsh test_beads_integration.ps1 -BaseUrl http://localhost:8000"
echo ""
echo "4️⃣  Push and create PR:"
echo "   git push origin feat/import-clausebot-api"
echo "   gh pr create --title 'chore: import clausebot-api into monorepo' --base main"
echo ""
echo "5️⃣  After merge, update:"
echo "   - .github/workflows/ci.yml (backend tests)"
echo "   - Render deployment config (point to backend/clausebot-api)"
echo "   - Root README.md (document new structure)"
echo ""
echo "🔒 ROLLBACK: If needed, run: git reset --hard origin/main"
echo ""
