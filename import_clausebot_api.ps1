# PowerShell Import Script for ClauseBot Monorepo Consolidation
param(
    [switch]$Force = $false
)

Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "🚀 CLAUSEBOT MONOREPO CONSOLIDATION" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Verify we're in the right directory
if (!(Test-Path "package.json") -or !(Test-Path "frontend" -PathType Container)) {
    Write-Host "❌ ERROR: Not in clausebot monorepo root" -ForegroundColor Red
    Write-Host "Please run this from: C:\ClauseBot_API_Deploy\clausebot" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Confirmed: In clausebot monorepo" -ForegroundColor Green
Write-Host ""

# Check if clausebot-api exists as sibling
if (!(Test-Path "../clausebot-api" -PathType Container)) {
    Write-Host "❌ ERROR: ../clausebot-api not found" -ForegroundColor Red
    Write-Host "Please ensure clausebot-api repo exists at: C:\ClauseBot_API_Deploy\clausebot-api" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Confirmed: clausebot-api repo found" -ForegroundColor Green
Write-Host ""

# Create feature branch
Write-Host "📌 Step 1: Creating feature branch..." -ForegroundColor Cyan
try {
    git checkout -b feat/import-clausebot-api 2>$null
} catch {
    git checkout feat/import-clausebot-api
}
Write-Host "✅ Branch: feat/import-clausebot-api" -ForegroundColor Green
Write-Host ""

# Add remote (remove if exists)
Write-Host "🔗 Step 2: Adding remote for clausebot-api..." -ForegroundColor Cyan
try {
    git remote remove clausebot-api-remote 2>$null
} catch {
    # Remote doesn't exist, continue
}
git remote add clausebot-api-remote ../clausebot-api
Write-Host "✅ Remote added" -ForegroundColor Green
Write-Host ""

# Fetch
Write-Host "⬇️  Step 3: Fetching clausebot-api history..." -ForegroundColor Cyan
git fetch clausebot-api-remote
Write-Host "✅ Fetch complete" -ForegroundColor Green
Write-Host ""

# Import with subtree (preserves history)
Write-Host "🔀 Step 4: Importing via git subtree..." -ForegroundColor Cyan
Write-Host "   This preserves all commit history from clausebot-api" -ForegroundColor Gray
Write-Host ""
git subtree add --prefix=backend/clausebot-api clausebot-api-remote main
Write-Host ""
Write-Host "✅ Subtree import complete" -ForegroundColor Green
Write-Host ""

# Verify
Write-Host "🔍 Step 5: Verifying import..." -ForegroundColor Cyan
if (Test-Path "backend/clausebot-api" -PathType Container) {
    Write-Host "✅ Directory created: backend/clausebot-api" -ForegroundColor Green
    
    if (Test-Path "backend/clausebot-api/clausebot_api/routes/agent_memory.py") {
        Write-Host "✅ BEADS code found: agent_memory.py" -ForegroundColor Green
    } else {
        Write-Host "⚠️  WARNING: agent_memory.py not found" -ForegroundColor Yellow
    }
    
    if (Test-Path "backend/clausebot-api/test_beads_integration.ps1") {
        Write-Host "✅ Test suite found: test_beads_integration.ps1" -ForegroundColor Green
    } else {
        Write-Host "⚠️  WARNING: test_beads_integration.ps1 not found" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ ERROR: Import failed - directory not created" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Show file structure
Write-Host "📁 Imported file structure:" -ForegroundColor Cyan
Get-ChildItem "backend/clausebot-api" | Select-Object -First 15 | Format-Table Name, Length, LastWriteTime
Write-Host ""

# Show commit history
Write-Host "📜 Preserved commit history (last 5 commits):" -ForegroundColor Cyan
git log backend/clausebot-api/ --oneline | Select-Object -First 5
Write-Host ""

# Show git status
Write-Host "📊 Current git status:" -ForegroundColor Cyan
git status
Write-Host ""

Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "✅ IMPORT COMPLETE!" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 NEXT STEPS:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1️⃣  Review imported files:" -ForegroundColor Yellow
Write-Host "   cd backend/clausebot-api; Get-ChildItem" -ForegroundColor Gray
Write-Host ""
Write-Host "2️⃣  Test locally (in new terminal):" -ForegroundColor Yellow
Write-Host "   cd backend/clausebot-api" -ForegroundColor Gray
Write-Host "   python -m venv .venv" -ForegroundColor Gray
Write-Host "   .\.venv\Scripts\activate" -ForegroundColor Gray
Write-Host "   pip install -r requirements.txt" -ForegroundColor Gray
Write-Host "   uvicorn clausebot_api.main:app --reload" -ForegroundColor Gray
Write-Host ""
Write-Host "3️⃣  Run integration tests (in another terminal):" -ForegroundColor Yellow
Write-Host "   cd backend/clausebot-api" -ForegroundColor Gray
Write-Host "   .\test_beads_integration.ps1 -BaseUrl http://localhost:8000" -ForegroundColor Gray
Write-Host ""
Write-Host "4️⃣  Push and create PR:" -ForegroundColor Yellow
Write-Host "   git push origin feat/import-clausebot-api" -ForegroundColor Gray
Write-Host "   gh pr create --title 'chore: import clausebot-api into monorepo' --base main" -ForegroundColor Gray
Write-Host ""
Write-Host "5️⃣  After merge, update:" -ForegroundColor Yellow
Write-Host "   - .github/workflows/ci.yml (backend tests)" -ForegroundColor Gray
Write-Host "   - Render deployment config (point to backend/clausebot-api)" -ForegroundColor Gray
Write-Host "   - Root README.md (document new structure)" -ForegroundColor Gray
Write-Host ""
Write-Host "🔒 ROLLBACK: If needed, run: git reset --hard origin/main" -ForegroundColor Red
Write-Host ""
