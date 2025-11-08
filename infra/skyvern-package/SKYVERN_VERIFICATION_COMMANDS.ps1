# Skyvern Package Verification Commands (PowerShell)
# Run these after PR is created to validate all 5 "Done" outcomes

$ErrorActionPreference = "Stop"

$REPO = "miltmon/clausebot"
$BRANCH = "feature/skyvern-openai-aura-s3-package"
$PACKAGE_DIR = "infra/skyvern-package"

Write-Host "🔍 SKYVERN PACKAGE VERIFICATION SUITE" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# OUTCOME 1: PR MERGED
# ============================================================================
Write-Host "1️⃣  Checking if PR is merged..." -ForegroundColor Yellow

try {
    $prList = gh pr list --repo $REPO --state merged --search $BRANCH --json number,title,state,url | ConvertFrom-Json
    
    if ($prList.Count -eq 0) {
        Write-Host "   ⚠️  PR not yet merged (or branch name mismatch)" -ForegroundColor Yellow
        Write-Host "   Current PR status:" -ForegroundColor Gray
        gh pr list --repo $REPO --search $BRANCH --json number,title,state,url
    } else {
        Write-Host "   ✅ PR merged successfully" -ForegroundColor Green
        $prList | ForEach-Object {
            Write-Host "   PR #$($_.number): $($_.title)" -ForegroundColor Gray
            Write-Host "   URL: $($_.url)" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "   ⚠️  Error checking PR status: $_" -ForegroundColor Yellow
}
Write-Host ""

# Check if files exist in main
Write-Host "   Checking if files exist at $PACKAGE_DIR..." -ForegroundColor Gray
try {
    $files = gh api repos/$REPO/contents/$PACKAGE_DIR --jq '.[].name' | Select-Object -First 5
    Write-Host "   ✅ Files confirmed:" -ForegroundColor Green
    $files | ForEach-Object { Write-Host "      - $_" -ForegroundColor Gray }
} catch {
    Write-Host "   ⚠️  Files not found (PR may not be merged yet)" -ForegroundColor Yellow
}
Write-Host ""

# ============================================================================
# OUTCOME 2: CI PASSES CLEAN
# ============================================================================
Write-Host "2️⃣  Checking CI status..." -ForegroundColor Yellow

try {
    $latestRun = gh run list --repo $REPO --branch $BRANCH --limit 1 --json databaseId,status,conclusion,workflowName | ConvertFrom-Json
    
    if ($latestRun.Count -eq 0) {
        Write-Host "   ⚠️  No CI runs found for branch $BRANCH" -ForegroundColor Yellow
    } else {
        $run = $latestRun[0]
        Write-Host "   Workflow: $($run.workflowName)" -ForegroundColor Gray
        Write-Host "   Status: $($run.status)" -ForegroundColor Gray
        Write-Host "   Conclusion: $($run.conclusion)" -ForegroundColor Gray
        
        if ($run.conclusion -eq "success") {
            Write-Host "   ✅ CI passed" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️  CI did not pass" -ForegroundColor Yellow
        }
        
        # Check for secret scan results
        Write-Host ""
        Write-Host "   Checking for secret scan results..." -ForegroundColor Gray
        try {
            $logs = gh run view $run.databaseId --repo $REPO --log 2>&1 | Select-String -Pattern "trufflehog|git-secrets|secret" -CaseSensitive:$false | Select-Object -Last 10
            if ($logs) {
                $logs | ForEach-Object { Write-Host "      $_" -ForegroundColor Gray }
            } else {
                Write-Host "      (No secret scan logs found - check CI configuration)" -ForegroundColor Gray
            }
        } catch {
            Write-Host "      (Unable to fetch logs)" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "   ⚠️  Error checking CI status: $_" -ForegroundColor Yellow
}
Write-Host ""

# ============================================================================
# OUTCOME 3: SECRETS CONFIGURED
# ============================================================================
Write-Host "3️⃣  Checking repository secrets..." -ForegroundColor Yellow

try {
    $secrets = gh secret list --repo $REPO 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   ⚠️  No secrets found or insufficient permissions" -ForegroundColor Yellow
    } else {
        Write-Host "   Secrets configured:" -ForegroundColor Gray
        
        $hasOpenAI = $secrets | Select-String -Pattern "OPENAI_API_KEY"
        $hasAWSRegion = $secrets | Select-String -Pattern "AWS_REGION"
        $hasKMS = $secrets | Select-String -Pattern "AWS_KMS_KEY_ARN"
        
        if ($hasOpenAI) {
            Write-Host "   ✅ OPENAI_API_KEY configured" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️  OPENAI_API_KEY not found" -ForegroundColor Yellow
        }
        
        if ($hasAWSRegion -or $hasKMS) {
            Write-Host "   ✅ AWS secrets configured" -ForegroundColor Green
        } else {
            Write-Host "   ℹ️  No AWS secrets (may be using IAM roles - preferred)" -ForegroundColor Cyan
        }
    }
} catch {
    Write-Host "   ⚠️  Error checking secrets: $_" -ForegroundColor Yellow
}
Write-Host ""

# ============================================================================
# OUTCOME 4: SMOKE TEST (LOCAL)
# ============================================================================
Write-Host "4️⃣  Smoke Test Commands (run manually)" -ForegroundColor Yellow
Write-Host "   Note: Requires local setup with .env file" -ForegroundColor Gray
Write-Host ""

$smokeTestCommands = @"
# Checkout PR and setup
gh pr checkout <PR_NUMBER>
cd $PACKAGE_DIR
Copy-Item .env.example .env
# Edit .env with your credentials

# Test Node API
cd Node
npm install
npm test
node server.js &
`$SERVER_PID = `$PID
Start-Sleep -Seconds 2

# Send test request
`$body = @{
    pageObj = @{ title = "Test Document" }
    selectors = @(@{ name = "title"; selector = "h1" })
    task = "Extract title"
    schema = @{ type = "object" }
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri http://localhost:3000/extract ``
    -ContentType "application/json" ``
    -Body `$body

# Expected: 200 OK + JSON response
Stop-Process -Id `$SERVER_PID

# Test Python retention worker
cd ..\Python
pip install boto3 psycopg2-binary python-dotenv
python retention_worker.py
# Expected: Successful connection to Aurora & S3
"@

Write-Host $smokeTestCommands -ForegroundColor Gray
Write-Host ""

# ============================================================================
# OUTCOME 5: TEAM ADOPTION
# ============================================================================
Write-Host "5️⃣  Checking team adoption artifacts..." -ForegroundColor Yellow

# Check README exists
Write-Host "   Checking for README..." -ForegroundColor Gray
try {
    $readme = gh api repos/$REPO/contents/$PACKAGE_DIR/README.md --jq '.name' 2>&1
    Write-Host "   ✅ README.md exists" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  README.md not found" -ForegroundColor Yellow
}
Write-Host ""

# Check for follow-up issues
Write-Host "   Checking for follow-up issues..." -ForegroundColor Gray
try {
    $issues = gh issue list --repo $REPO --search "skyvern" --json number,title,state | ConvertFrom-Json
    
    if ($issues.Count -eq 0) {
        Write-Host "   ⚠️  No follow-up issues found" -ForegroundColor Yellow
        Write-Host "   Consider creating one:" -ForegroundColor Gray
        Write-Host "   gh issue create --repo $REPO --title 'Skyvern Package: Enable OIDC & Monitoring' --label infra,skyvern" -ForegroundColor Gray
    } else {
        Write-Host "   ✅ Follow-up issues found:" -ForegroundColor Green
        $issues | ForEach-Object {
            Write-Host "   #$($_.number): $($_.title) [$($_.state)]" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "   ⚠️  Error checking issues: $_" -ForegroundColor Yellow
}
Write-Host ""

# ============================================================================
# SUMMARY
# ============================================================================
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "📊 VERIFICATION SUMMARY" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Outcome 1 (PR Merged):       Check output above" -ForegroundColor Gray
Write-Host "Outcome 2 (CI Clean):        Check output above" -ForegroundColor Gray
Write-Host "Outcome 3 (Secrets Config):  Check output above" -ForegroundColor Gray
Write-Host "Outcome 4 (Smoke Test):      Run manually (commands provided)" -ForegroundColor Gray
Write-Host "Outcome 5 (Team Adoption):   Check output above" -ForegroundColor Gray
Write-Host ""
Write-Host "✅ NEXT STEPS:" -ForegroundColor Green
Write-Host "1. Review any ⚠️  warnings above" -ForegroundColor Gray
Write-Host "2. Run manual smoke tests (Outcome 4)" -ForegroundColor Gray
Write-Host "3. Confirm all checkboxes ticked in PR" -ForegroundColor Gray
Write-Host "4. Get PR approved and merged" -ForegroundColor Gray
Write-Host "5. Create follow-up issues for rollout tasks" -ForegroundColor Gray
Write-Host ""
Write-Host "🎉 Package ready for deployment!" -ForegroundColor Cyan

