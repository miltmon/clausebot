# ClauseBot Slack Notifier - Production Alert System
# Sends alerts when validator flips RED or critical issues detected

param(
    [string]$WebhookUrl = $env:SLACK_WEBHOOK_URL,
    [string]$Channel = "#clausebot-alerts",
    [string]$Message,
    [string]$AlertType = "INFO",
    [string]$DriveRoot = "G:\ClauseBot_OPPS_Workspace"
)

function Send-SlackAlert {
    param(
        [string]$Message,
        [string]$AlertType = "INFO",
        [string]$Channel = "#clausebot-alerts",
        [string]$WebhookUrl = $env:SLACK_WEBHOOK_URL
    )
    
    if (-not $WebhookUrl) {
        Write-Warning "SLACK_WEBHOOK_URL not configured - alert not sent: $Message"
        return $false
    }
    
    # Alert type formatting
    $emoji = switch ($AlertType) {
        "CRITICAL" { "🚨" }
        "ERROR" { "❌" }
        "WARNING" { "⚠️" }
        "SUCCESS" { "✅" }
        default { "ℹ️" }
    }
    
    $color = switch ($AlertType) {
        "CRITICAL" { "danger" }
        "ERROR" { "danger" }
        "WARNING" { "warning" }
        "SUCCESS" { "good" }
        default { "#36a64f" }
    }
    
    $payload = @{
        channel = $Channel
        username = "ClauseBot-Monitor"
        icon_emoji = ":robot_face:"
        attachments = @(
            @{
                color = $color
                title = "$emoji ClauseBot Alert - $AlertType"
                text = $Message
                footer = "ClauseBot Production Monitor"
                ts = [int][double]::Parse((Get-Date -UFormat %s))
                fields = @(
                    @{
                        title = "Environment"
                        value = "Production"
                        short = $true
                    }
                    @{
                        title = "Timestamp"
                        value = (Get-Date -Format "yyyy-MM-dd HH:mm:ss UTC")
                        short = $true
                    }
                )
            }
        )
    } | ConvertTo-Json -Depth 5
    
    try {
        Invoke-RestMethod -Uri $WebhookUrl -Method POST -Body $payload -ContentType "application/json" -TimeoutSec 10 | Out-Null
        Write-Host "✅ Slack alert sent successfully" -ForegroundColor Green
        return $true
    } catch {
        Write-Warning "Failed to send Slack alert: $($_.Exception.Message)"
        
        # Log failed alert to file for retry
        $failedAlert = @{
            timestamp = (Get-Date).ToString("o")
            message = $Message
            alert_type = $AlertType
            error = $_.Exception.Message
        }
        
        $logPath = "$DriveRoot\Shared\.failed_alerts.log"
        ($failedAlert | ConvertTo-Json -Compress) | Add-Content -Path $logPath -Encoding UTF8
        
        return $false
    }
}

function Send-ValidatorRedAlert {
    param([string]$Reason, [string]$Details = "")
    
    $message = @"
🚨 VALIDATOR STATUS: RED

**Immediate Action Required**

**Reason:** $Reason

**Details:** $Details

**Actions Taken:**
- Auto-apply disabled
- Manual review required
- Kill switch ready

**Next Steps:**
1. Check Drive workspace health
2. Review audit trails
3. Validate compliance metrics
4. Manual intervention required

**Dashboard:** Check Google Sheets for detailed status
"@
    
    Send-SlackAlert -Message $message -AlertType "CRITICAL" -Channel "#clausebot-alerts"
}

function Send-ComplianceAlert {
    param(
        [string]$UpdateType,
        [string]$Impact,
        [string]$Title,
        [string]$WebsetId
    )
    
    $message = @"
📋 Compliance Update Detected

**Type:** $UpdateType
**Impact:** $Impact
**Title:** $Title
**Webset:** $WebsetId

**Status:** Processing with HITL approval
**Dashboard:** Check team scorecard for updates
"@
    
    $alertType = if ($Impact -eq "high") { "WARNING" } else { "INFO" }
    Send-SlackAlert -Message $message -AlertType $alertType -Channel "#clausebot-compliance"
}

function Send-SystemHealthAlert {
    param(
        [string]$Component,
        [string]$Status,
        [string]$Details
    )
    
    $message = @"
🔧 System Health Alert

**Component:** $Component
**Status:** $Status
**Details:** $Details

**Timestamp:** $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss UTC')
**Environment:** Production
"@
    
    $alertType = if ($Status -eq "DOWN" -or $Status -eq "ERROR") { "ERROR" } else { "WARNING" }
    Send-SlackAlert -Message $message -AlertType $alertType
}

function Send-PilotAMetricsAlert {
    param(
        [hashtable]$Metrics,
        [string]$Status
    )
    
    $message = @"
📊 Pilot A Metrics Update

**Status:** $Status

**Current Metrics:**
- Precision: $($Metrics.precision * 100)%
- Recall: $($Metrics.recall * 100)%
- MTTR Improvement: $($Metrics.mttr_delta_pct * 100)%
- Incidents Today: $($Metrics.incidents_24h)

**Compliance:**
- Standards Currency: $($Metrics.standards_currency * 100)%
- Update Latency: $($Metrics.update_latency_avg_s)s
- HITL Compliance: $($Metrics.hitl_compliance_rate * 100)%

**Dashboard:** Check Google Sheets for detailed analysis
"@
    
    $alertType = if ($Status -eq "DEGRADED") { "WARNING" } elseif ($Status -eq "HEALTHY") { "SUCCESS" } else { "INFO" }
    Send-SlackAlert -Message $message -AlertType $alertType
}

# Main execution if called directly
if ($Message) {
    Send-SlackAlert -Message $Message -AlertType $AlertType -Channel $Channel -WebhookUrl $WebhookUrl
} else {
    Write-Host "ClauseBot Slack Notifier - Available Functions:" -ForegroundColor Cyan
    Write-Host "  Send-SlackAlert - General purpose alert" -ForegroundColor White
    Write-Host "  Send-ValidatorRedAlert - Critical validator failure" -ForegroundColor White
    Write-Host "  Send-ComplianceAlert - Compliance update notification" -ForegroundColor White
    Write-Host "  Send-SystemHealthAlert - System component health" -ForegroundColor White
    Write-Host "  Send-PilotAMetricsAlert - Pilot A performance metrics" -ForegroundColor White
    Write-Host ""
    Write-Host "Usage Examples:" -ForegroundColor Yellow
    Write-Host '  .\slack_notifier.ps1 -Message "Test alert" -AlertType "INFO"' -ForegroundColor Gray
    Write-Host '  Send-ValidatorRedAlert -Reason "Knowledge base stale" -Details "Last update 48h ago"' -ForegroundColor Gray
    Write-Host '  Send-ComplianceAlert -UpdateType "AWS D1.1" -Impact "high" -Title "Clause 6 Updates"' -ForegroundColor Gray
}
