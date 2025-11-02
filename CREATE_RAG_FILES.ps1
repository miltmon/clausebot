# CREATE_RAG_FILES.ps1
# Auto-generates all ClauseBot RAG files from the bundle
# Run from: clausebot/ directory
# Usage: .\CREATE_RAG_FILES.ps1

$ErrorActionPreference = "Stop"

Write-Host "🚀 Creating ClauseBot RAG file structure..." -ForegroundColor Cyan

# Create directories
$dirs = @(
    "backend\sql",
    "backend\clausebot_api\services",
    "backend\clausebot_api\routes",
    "backend\scripts",
    "ops",
    "ops\golden_dataset",
    ".github\workflows"
)

foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "✅ Created directory: $dir" -ForegroundColor Green
    }
}

Write-Host "`n📝 Note: File contents are too large to embed in this script." -ForegroundColor Yellow
Write-Host "Please copy the content from the conversation for each file listed below:" -ForegroundColor Yellow
Write-Host ""

$files = @(
    @{Path="backend\sql\supabase_pgvector_rag.sql"; Size="~150 lines"},
    @{Path="backend\clausebot_api\services\rag_service.py"; Size="~250 lines"},
    @{Path="backend\clausebot_api\routes\chat_compliance.py"; Size="~100 lines"},
    @{Path="backend\scripts\ingest_aws_d11.py"; Size="~150 lines"},
    @{Path="ops\smoke-script.sh"; Size="~130 lines"},
    @{Path="ops\rollback-playbook.md"; Size="~250 lines"},
    @{Path="ops\golden-validate.py"; Size="~500 lines"},
    @{Path="ops\golden_dataset\golden.json"; Size="~400 lines"},
    @{Path="ops\README.md"; Size="~200 lines"},
    @{Path=".github\workflows\post-deploy-smoke.yml"; Size="~150 lines"},
    @{Path=".github\workflows\golden-validation.yml"; Size="~150 lines"},
    @{Path=".github\workflows\GOLDEN_FAILURE_CHECKLIST.md"; Size="~300 lines"},
    @{Path=".github\workflows\README.md"; Size="~150 lines"}
)

Write-Host "Files to create (copy content from conversation):" -ForegroundColor Cyan
foreach ($file in $files) {
    Write-Host "  📄 $($file.Path) ($($file.Size))" -ForegroundColor White
}

Write-Host "`n✅ Directory structure created!" -ForegroundColor Green
Write-Host "Next: Paste file contents from the conversation into each file above." -ForegroundColor Yellow
Write-Host "Then run: git add . && git commit -m 'feat: Add ClauseBot RAG implementation suite'" -ForegroundColor Yellow

