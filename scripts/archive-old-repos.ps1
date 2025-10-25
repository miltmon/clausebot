# Archive Old ClauseBot Repositories
# This script archives the legacy repositories now that migration is complete

Write-Host "`n=== ClauseBot Legacy Repository Archival ===" -ForegroundColor Cyan
Write-Host "Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n" -ForegroundColor Gray

# Check if GitHub CLI is installed
$ghInstalled = Get-Command gh -ErrorAction SilentlyContinue

if (-not $ghInstalled) {
    Write-Host "❌ GitHub CLI (gh) not found!" -ForegroundColor Red
    Write-Host "`nPlease install it or use the GitHub web UI:" -ForegroundColor Yellow
    Write-Host "  https://github.com/miltmon/clausebot-api/settings" -ForegroundColor Cyan
    Write-Host "  https://github.com/miltmon/clausebotai/settings" -ForegroundColor Cyan
    Write-Host "`nScroll to 'Danger Zone' → 'Archive this repository'" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ GitHub CLI detected`n" -ForegroundColor Green

# Archive clausebot-api
Write-Host "[1/2] Archiving clausebot-api..." -ForegroundColor Yellow
try {
    gh repo edit miltmon/clausebot-api --archived
    Write-Host "  ✅ clausebot-api archived successfully" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Failed to archive clausebot-api: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "  Manual URL: https://github.com/miltmon/clausebot-api/settings" -ForegroundColor Cyan
}

# Archive clausebotai
Write-Host "`n[2/2] Archiving clausebotai..." -ForegroundColor Yellow
try {
    gh repo edit miltmon/clausebotai --archived
    Write-Host "  ✅ clausebotai archived successfully" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Failed to archive clausebotai: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "  Manual URL: https://github.com/miltmon/clausebotai/settings" -ForegroundColor Cyan
}

# Verify archival
Write-Host "`n=== Verification ===" -ForegroundColor Cyan

Write-Host "`nChecking clausebot-api..." -ForegroundColor Yellow
gh repo view miltmon/clausebot-api --json isArchived --jq '.isArchived' | ForEach-Object {
    if ($_ -eq "true") {
        Write-Host "  ✅ Confirmed archived" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️ Not archived - check manually" -ForegroundColor Yellow
    }
}

Write-Host "`nChecking clausebotai..." -ForegroundColor Yellow
gh repo view miltmon/clausebotai --json isArchived --jq '.isArchived' | ForEach-Object {
    if ($_ -eq "true") {
        Write-Host "  ✅ Confirmed archived" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️ Not archived - check manually" -ForegroundColor Yellow
    }
}

Write-Host "`n=== Archival Complete ===" -ForegroundColor Cyan
Write-Host "`nLegacy repositories are now read-only." -ForegroundColor Gray
Write-Host "All code and history remain accessible." -ForegroundColor Gray
Write-Host "`nActive monorepo: https://github.com/miltmon/clausebot" -ForegroundColor Green
Write-Host "`n🎉 Weekend debugging loop: OFFICIALLY CLOSED! 🎉`n" -ForegroundColor Green

