# ClauseBot Exa.ai Integration - Production Checklist

## 🎯 Go-Live Mini-Runbook (30-45 min)

### 1️⃣ Preflight (5 min)

**Endpoints Up:**
```powershell
# Webhook health check
curl -sS http://localhost:8088/health | jq
# Expected: {"ok": true, "inbox": "G:\\ClauseBot_OPPS_Workspace\\Shared\\compliance_updates\\inbox", "time": "2025-10-01T..."}
```

**Paths Exist (Drive-first):**
- ✅ `G:\ClauseBot_OPPS_Workspace\Shared\compliance_updates\inbox\`
- ✅ `G:\ClauseBot_OPPS_Workspace\Windsurf\receipts\`
- ✅ `G:\ClauseBot_OPPS_Workspace\Windsurf\audit_trails\`

**Secrets:**
- ✅ Webhook token (if added) not in logs
- ✅ Stored in local .env or Windows Credential Manager

**Scheduler:**
- ✅ "ClauseBot_ExaCompliance_Hourly" → Next run < 60 min
- ✅ Runs as user with Drive access

### 2️⃣ Smoke Test: Push + Pull (10-15 min)

**A. Webhook (Push Path):**
```powershell
$body = @'
{
  "source":"exa.ai",
  "webset_id":"aws_cwi_resources",
  "items":[
    {
      "title":"AWS D1.1 2025 Rev 1 – Clause 6 updates",
      "url":"https://example.org/aws-d1-1-2025-r1",
      "description":"Preheat minimum raised to 75°C for Group II steels (summary).",
      "detected_at":"2025-10-01T18:17:32Z",
      "sections":["6.1.4","6.2.1"],
      "impact_tags":["procedure","preheat"]
    }
  ]
}'@
Invoke-RestMethod -Method POST -Uri "http://localhost:8088/exa/webset/ingest" -Body $body -ContentType "application/json"
```
**Expected:** New `exa_*.json` in `G:\ClauseBot_OPPS_Workspace\Shared\compliance_updates\inbox\`

**B. Puller (Batch Path):**
```powershell
.\~\Diagnostics\exa_pull.ps1 -ExportPath "C:\Exports\cwi_webset.csv" -WebsetId "aws_cwi_resources"
```
**Expected:** Only new items ingested (URL-hash dedupe). No full-text anywhere.

### 3️⃣ CURSOR → Windsurf Handoff (10 min)

Feed 1 inbox file through StandardsUpdate path:
```powershell
.\~\Diagnostics\windsurf_compliance_cascade.ps1 -ComplianceUpdatePath "path\to\inbox\file.json" -DryRun
```

**Confirm:**
- ✅ Receipt in `Windsurf\receipts\compliance_*.json`
- ✅ Audit in `Windsurf\audit_trails\compliance_audit_*.json`
- ✅ HITL prompt fires for medium/high (test approve/deny)

### 4️⃣ Scorecard + Dashboard (5-10 min)

```powershell
& "$HOME\build_team_scorecard.ps1" -DriveRoot "G:\ClauseBot_OPPS_Workspace"
```

**Open Google Sheet - Verify:**
- ✅ Compliance tiles populated (Score, Updates 24h, Freshness, Versions)
- ✅ Dashboard header GREEN
- ✅ Schema/parity checks show details

### 5️⃣ Guardrails & Rollback (5 min)

**Kill Switch (Document and Verify):**
```powershell
# Disable hourly task
Disable-ScheduledTask -TaskName "ClauseBot_ExaCompliance_Hourly"

# Stop webhook
# Stop uvicorn process/service
```

**Write Safety:**
- ✅ Windsurf writes only after HITL approval
- ✅ Staging KB by default

**Logs:**
- ✅ Audit parity check passes (Drive vs S3)
- ✅ Validator RED = no auto-apply

---

## 📋 Production Checklist (One Page)

### 🔧 Reliability

**Idempotency:**
- ✅ Puller maintains `seen_urls.json`
- ✅ Webhook dedup via `provenance.change_id`

**Backoff:**
- ✅ Exponential backoff on Exa export read failures (puller)

**Rate Limits:**
- ✅ Cap webhook POST size & item count per request

### 🛡️ Security

**Webhook Security:**
- ✅ Webhook secret (HMAC or bearer) required
- ✅ Reject requests without valid authentication

**Data Protection:**
- ✅ Drop PII; store metadata only (title, URL, tags, timestamps, hashes)
- ✅ No full-text content storage

**Access Control:**
- ✅ Least-privilege service account for scheduled tasks

### 📊 Observability

**Counters:**
- ✅ `updates_detected_24h`
- ✅ `high_impact_updates`
- ✅ `update_latency_avg_s`

**Alerts:**
- ✅ Validator RED → Slack ping
- ✅ Freshness == "stale" → pause auto-apply

**Tracing:**
- ✅ Include `provenance.change_id` in receipts & dashboard rows

### 🏛️ Governance

**HITL Policy:**
- ✅ Auto-apply only low impact
- ✅ Medium/high require approval

**Audit:**
- ✅ Quarterly audit: sample receipts to verify no full-text content stored

**Versioning:**
- ✅ Include `knowledge_base_versions` in scorecard each update

---

## 🎯 7-Day Pilot Targets

Add to your scorecard:

| Metric | Target | Current |
|--------|--------|---------|
| **Standards Currency** | ≥ 95% | - |
| **Update Latency** | ≤ 30s (push) / ≤ 1h (pull) | - |
| **HITL Bypasses** | Zero | - |
| **Audit Parity** | 100% (Drive ↔ S3) | - |
| **Full-text Retained** | Zero (validator strict mode) | - |

---

## 🔧 Hardening Enhancements

### Webhook Security Enhancement
```python
import hmac
import hashlib

def verify_webhook_signature(body: bytes, signature: str, secret: str) -> bool:
    """Verify HMAC signature from Exa.ai webhook"""
    expected = hmac.new(
        secret.encode('utf-8'),
        body,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)

@app.post("/exa/webset/ingest")
async def ingest(payload: IngestPayload, request: Request):
    # Verify signature
    signature = request.headers.get("X-Exa-Signature")
    if not signature:
        raise HTTPException(status_code=401, detail="Missing signature")
    
    body = await request.body()
    if not verify_webhook_signature(body, signature, WEBHOOK_SECRET):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Continue with existing logic...
```

### Puller Enhancements
```powershell
# Add to exa_pull.ps1
param(
    [datetime]$Since = (Get-Date).AddHours(-25),  # Only process recent items
    [switch]$WarnOnClockSkew = $true
)

# Clock skew detection
if ($WarnOnClockSkew) {
    $serverTime = (Get-Date).ToUniversalTime()
    $maxSkew = [TimeSpan]::FromMinutes(5)
    # Add skew detection logic
}

# Compact ops log
$opsLogEntry = @{
    timestamp = (Get-Date).ToString("o")
    operation = "exa_pull"
    items_processed = $written
    items_skipped = $skipped
    export_source = $ExportPath
    webset_id = $WebsetId
}
$opsLogPath = Join-Path $StateDir "ops.log"
($opsLogEntry | ConvertTo-Json -Compress) | Add-Content -Path $opsLogPath
```

### Validator Strict Mode
```powershell
# Add to validator
param([switch]$Strict = $false)

if ($Strict) {
    # Freshness must be "current" or flip RED
    if ($healthMetrics.knowledge_base_freshness -ne "current") {
        $validatorStatus = "RED"
        $issues += "Knowledge base not current in strict mode"
    }
}
```

### Slack Notifier
```powershell
function Send-SlackAlert {
    param(
        [string]$Message,
        [string]$Channel = "#clausebot-alerts",
        [string]$WebhookUrl = $env:SLACK_WEBHOOK_URL
    )
    
    $payload = @{
        channel = $Channel
        text = "🚨 ClauseBot Alert: $Message"
        username = "ClauseBot-Monitor"
    } | ConvertTo-Json
    
    try {
        Invoke-RestMethod -Uri $WebhookUrl -Method POST -Body $payload -ContentType "application/json"
    } catch {
        Write-Warning "Failed to send Slack alert: $($_.Exception.Message)"
    }
}

# Usage in validator
if ($validatorStatus -eq "RED") {
    Send-SlackAlert "Validator flipped RED - immediate attention required"
}
```

---

## 🚀 Production Deployment Commands

### Start Services
```powershell
# Start webhook server
cd C:\ClauseBot_API_Deploy\clausebot-api
python exa_webhook_app.py

# Enable scheduled task
Enable-ScheduledTask -TaskName "ClauseBot_ExaCompliance_Hourly"

# Run validation
.\production_validation.ps1 -DriveRoot "G:\ClauseBot_OPPS_Workspace"
```

### Monitor Dashboard
- **Google Sheets**: Check compliance metrics every 4 hours
- **Drive Inbox**: Monitor `G:\ClauseBot_OPPS_Workspace\Shared\compliance_updates\inbox\`
- **Audit Trails**: Review `Windsurf\audit_trails\` daily

### Emergency Procedures
```powershell
# Kill switch activation
Disable-ScheduledTask -TaskName "ClauseBot_ExaCompliance_Hourly"
Stop-Process -Name "python" -Force  # Stop webhook server
"EMERGENCY_STOP_$(Get-Date)" | Out-File "G:\ClauseBot_OPPS_Workspace\Shared\.kill_switch"
```

---

## ✅ Final Go/No-Go Criteria

**🟢 GO - Deploy to Production:**
- All preflight checks pass
- Smoke tests successful
- CURSOR → Windsurf handoff working
- Dashboard updating with compliance metrics
- Kill switch tested and documented
- Zero critical security issues

**🔴 NO-GO - Fix Before Deploy:**
- Any preflight check fails
- PII detected in compliance files
- HITL gates not functioning
- Dashboard not updating
- Kill switch not working
- Critical security vulnerabilities

**Production deployment authorized when all GO criteria met and zero NO-GO conditions present.**
