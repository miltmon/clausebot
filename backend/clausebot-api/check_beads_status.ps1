#!/usr/bin/env pwsh
# Beads Agent Memory Status Check
# Usage: .\check_beads_status.ps1 [-BaseUrl "https://clausebot-api.onrender.com"]

param(
    [string]$BaseUrl = "https://clausebot-api.onrender.com"
)

Write-Host "🔍 BEADS AGENT MEMORY STATUS CHECK" -ForegroundColor Cyan
Write-Host "Base URL: $BaseUrl" -ForegroundColor Gray
Write-Host ""

# Quick health check
try {
    $healthResponse = Invoke-RestMethod -Uri "$BaseUrl/health" -Method GET -TimeoutSec 10
    Write-Host "✅ API Health: OK" -ForegroundColor Green
} catch {
    Write-Host "❌ API Health: FAILED - $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Agent memory feature status
try {
    $statsResponse = Invoke-RestMethod -Uri "$BaseUrl/v1/agent/memory/stats" -Method GET -TimeoutSec 10
    if ($statsResponse.success) {
        Write-Host "✅ Agent Memory: ENABLED" -ForegroundColor Green
        Write-Host "   Total Tasks: $($statsResponse.data.total_tasks)" -ForegroundColor Gray
        Write-Host "   Ready Tasks: $($statsResponse.data.ready_tasks)" -ForegroundColor Gray
        Write-Host "   Blocked Tasks: $($statsResponse.data.blocked_tasks)" -ForegroundColor Gray
        Write-Host "   Dependencies: $($statsResponse.data.dependencies)" -ForegroundColor Gray
    } else {
        Write-Host "⚠️  Agent Memory: DISABLED or ERROR" -ForegroundColor Yellow
    }
} catch {
    if ($_.Exception.Response.StatusCode -eq 404) {
        Write-Host "⚠️  Agent Memory: FEATURE NOT DEPLOYED" -ForegroundColor Yellow
    } else {
        Write-Host "❌ Agent Memory: ERROR - $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Ready work check
try {
    $readyResponse = Invoke-RestMethod -Uri "$BaseUrl/v1/agent/memory/ready?limit=3" -Method GET -TimeoutSec 10
    if ($readyResponse.success) {
        $readyCount = $readyResponse.data.Count
        Write-Host "✅ Ready Work: $readyCount items available" -ForegroundColor Green
        if ($readyCount -gt 0) {
            Write-Host "   Top Priority: $($readyResponse.data[0].task.title)" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "⚠️  Ready Work: Not accessible" -ForegroundColor Yellow
}

# Performance check (batch endpoint)
try {
    $startTime = Get-Date
    $batchData = @{
        tasks = @(
            @{
                title = "Status check test task"
                task_type = "task"
                priority = 2
                source = "status_check"
            }
        )
        source = "status_check"
    } | ConvertTo-Json -Depth 3
    
    $batchResponse = Invoke-RestMethod -Uri "$BaseUrl/v1/agent/memory/tasks/batch" -Method POST -Body $batchData -ContentType "application/json" -TimeoutSec 10
    $duration = (Get-Date) - $startTime
    
    if ($batchResponse.success) {
        Write-Host "✅ Batch Performance: $($duration.TotalMilliseconds)ms" -ForegroundColor Green
        if ($duration.TotalMilliseconds -gt 2000) {
            Write-Host "⚠️  Performance Warning: >2s latency" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "⚠️  Batch Operations: Not accessible" -ForegroundColor Yellow
}

# Quiz integration check
try {
    $quizReadyResponse = Invoke-RestMethod -Uri "$BaseUrl/v1/quiz/ready?format=json&limit=1" -Method GET -TimeoutSec 10
    Write-Host "✅ Quiz Integration: Working" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Quiz Integration: Not accessible" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎯 STATUS SUMMARY:" -ForegroundColor Cyan

# Overall status
$allGood = $true
try {
    $statsCheck = Invoke-RestMethod -Uri "$BaseUrl/v1/agent/memory/stats" -Method GET -TimeoutSec 5
    if ($statsCheck.success) {
        Write-Host "✅ BEADS AGENT MEMORY: OPERATIONAL" -ForegroundColor Green
        Write-Host "   Ready for production workloads" -ForegroundColor Gray
    } else {
        Write-Host "⚠️  BEADS AGENT MEMORY: DISABLED" -ForegroundColor Yellow
        Write-Host "   Set AGENT_MEMORY_ENABLED=true to enable" -ForegroundColor Gray
        $allGood = $false
    }
} catch {
    Write-Host "❌ BEADS AGENT MEMORY: NOT AVAILABLE" -ForegroundColor Red
    Write-Host "   Check deployment and feature flag" -ForegroundColor Gray
    $allGood = $false
}

Write-Host ""
if ($allGood) {
    Write-Host "🚀 All systems operational - ready for agent workflows!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Some features not available - check configuration" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "💡 Quick Actions:" -ForegroundColor Cyan
Write-Host "   Enable:  Set AGENT_MEMORY_ENABLED=true in production config" -ForegroundColor Gray
Write-Host "   Disable: Set AGENT_MEMORY_ENABLED=false in production config" -ForegroundColor Gray
Write-Host "   Test:    .\test_beads_integration.ps1 -BaseUrl `"$BaseUrl`"" -ForegroundColor Gray
