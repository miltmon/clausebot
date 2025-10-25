# CURSOR Integration Functions for ClauseBot Dual-Database API
# Send diagnostic incidents directly to the unified API endpoint

param(
    [string]$ApiBase = "https://clausebot-api.onrender.com",
    [string]$LocalApiBase = "http://127.0.0.1:8000"
)

function Send-CursorIncidentToDualDB {
    param(
        [Parameter(Mandatory=$true)]
        [string]$IncidentType,
        
        [ValidateSet("low", "medium", "high", "critical")]
        [string]$Severity = "medium",
        
        [ValidateRange(0, 1)]
        [double]$Confidence = 0.8,
        
        [hashtable]$AdditionalContext = @{},
        
        [string]$ApiEndpoint = $script:ApiBase,
        
        [switch]$UseLocal
    )
    
    if ($UseLocal) {
        $ApiEndpoint = $script:LocalApiBase
    }
    
    Write-Host "🚨 Sending CURSOR incident to ClauseBot API..." -ForegroundColor Yellow
    Write-Host "   Type: $IncidentType" -ForegroundColor Gray
    Write-Host "   Severity: $Severity" -ForegroundColor Gray
    Write-Host "   Endpoint: $ApiEndpoint" -ForegroundColor Gray
    
    # Gather enhanced system context
    $systemContext = @{
        timestamp = (Get-Date).ToString("o")
        os = "$([System.Environment]::OSVersion.VersionString)"
        machine_name = $env:COMPUTERNAME
        user = $env:USERNAME
        powershell_version = $PSVersionTable.PSVersion.ToString()
        cursor_session = $true
    }
    
    # Add memory info
    try {
        $memory = Get-CimInstance -ClassName Win32_OperatingSystem
        $systemContext.total_memory_gb = [math]::Round($memory.TotalVisibleMemorySize / 1MB, 2)
        $systemContext.free_memory_gb = [math]::Round($memory.FreePhysicalMemory / 1MB, 2)
        $systemContext.memory_usage_percent = [math]::Round((1 - ($memory.FreePhysicalMemory / $memory.TotalVisibleMemorySize)) * 100, 1)
    } catch {
        $systemContext.memory_error = $_.Exception.Message
    }
    
    # Add GPU info for Chrome-related incidents
    $gpuInfo = @{}
    if ($IncidentType -like "*chrome*" -or $IncidentType -like "*hang*") {
        try {
            $gpu = Get-CimInstance -ClassName Win32_VideoController | Where-Object { $_.Name -notlike "*Basic*" } | Select-Object -First 1
            if ($gpu) {
                $gpuInfo.name = $gpu.Name
                $gpuInfo.driver_version = $gpu.DriverVersion
                $gpuInfo.driver_date = $gpu.DriverDate
                $gpuInfo.adapter_ram = $gpu.AdapterRAM
            }
        } catch {
            $gpuInfo.error = $_.Exception.Message
        }
    }
    
    # Chrome configuration for browser incidents
    $chromeConfig = @{}
    if ($IncidentType -like "*chrome*" -or $IncidentType -like "*browser*") {
        try {
            # Try to get Chrome version from registry
            $chromeVersion = Get-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe" -ErrorAction SilentlyContinue
            if ($chromeVersion) {
                $chromeConfig.install_path = $chromeVersion.'(default)'
            }
            
            # Check for Chrome processes
            $chromeProcesses = Get-Process -Name "chrome" -ErrorAction SilentlyContinue
            if ($chromeProcesses) {
                $chromeConfig.process_count = $chromeProcesses.Count
                $chromeConfig.total_memory_mb = [math]::Round(($chromeProcesses | Measure-Object WorkingSet -Sum).Sum / 1MB, 1)
            }
        } catch {
            $chromeConfig.error = $_.Exception.Message
        }
    }
    
    # Merge additional context
    foreach ($key in $AdditionalContext.Keys) {
        $systemContext[$key] = $AdditionalContext[$key]
    }
    
    # Build the incident payload
    $incident = @{
        incident_type = $IncidentType
        severity = $Severity
        confidence = $Confidence
        system_context = $systemContext
    }
    
    # Add optional sections if they have data
    if ($gpuInfo.Count -gt 0) {
        $incident.gpu_info = $gpuInfo
    }
    
    if ($chromeConfig.Count -gt 0) {
        $incident.chrome_config = $chromeConfig
    }
    
    try {
        $response = Invoke-RestMethod -Method POST -Uri "$ApiEndpoint/api/cursor/incident" -Body ($incident | ConvertTo-Json -Depth 4) -ContentType "application/json" -TimeoutSec 15
        
        Write-Host "   ✅ Incident sent successfully!" -ForegroundColor Green
        Write-Host "   ID: $($response.id)" -ForegroundColor Gray
        Write-Host "   Supabase: $($response.supabase_inserted)" -ForegroundColor Gray
        Write-Host "   Airtable: $($response.airtable_created)" -ForegroundColor Gray
        
        if ($response.airtable_record_id) {
            Write-Host "   Airtable Record: $($response.airtable_record_id)" -ForegroundColor Gray
        }
        
        return $response
    }
    catch {
        Write-Host "   ❌ Failed to send incident!" -ForegroundColor Red
        Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
        
        # Try to save locally as fallback
        try {
            $fallbackPath = "$env:TEMP\cursor_incident_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
            $incident | ConvertTo-Json -Depth 4 | Set-Content -Path $fallbackPath -Encoding UTF8
            Write-Host "   💾 Incident saved locally: $fallbackPath" -ForegroundColor Yellow
        } catch {
            Write-Host "   ❌ Could not save fallback file" -ForegroundColor Red
        }
        
        throw
    }
}

function Test-ClauseBotDualDatabaseAPI {
    param(
        [string]$ApiEndpoint = $script:ApiBase,
        [switch]$UseLocal,
        [switch]$Detailed
    )
    
    if ($UseLocal) {
        $ApiEndpoint = $script:LocalApiBase
    }
    
    Write-Host "🧪 Testing ClauseBot Dual-Database API" -ForegroundColor Blue
    Write-Host "=====================================" -ForegroundColor Blue
    Write-Host "Endpoint: $ApiEndpoint" -ForegroundColor Gray
    Write-Host ""
    
    $results = @{
        endpoint = $ApiEndpoint
        timestamp = (Get-Date).ToString("o")
        tests = @()
    }
    
    # Test 1: Health Check
    Write-Host "1️⃣  Health Check..." -ForegroundColor Cyan
    try {
        $health = Invoke-RestMethod -Uri "$ApiEndpoint/health" -TimeoutSec 10
        Write-Host "   ✅ API is responding" -ForegroundColor Green
        Write-Host "   Supabase: $($health.supabase)" -ForegroundColor Gray
        Write-Host "   Airtable: $($health.airtable)" -ForegroundColor Gray
        Write-Host "   Overall: $($health.ok)" -ForegroundColor Gray
        
        $results.tests += @{
            name = "Health Check"
            status = "PASS"
            details = $health
        }
    }
    catch {
        Write-Host "   ❌ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
        $results.tests += @{
            name = "Health Check"
            status = "FAIL"
            error = $_.Exception.Message
        }
    }
    
    # Test 2: Detailed Health (if available)
    if ($Detailed) {
        Write-Host ""
        Write-Host "2️⃣  Detailed Health..." -ForegroundColor Cyan
        try {
            $detailedHealth = Invoke-RestMethod -Uri "$ApiEndpoint/health/detailed" -TimeoutSec 10
            Write-Host "   ✅ Detailed health available" -ForegroundColor Green
            
            $results.tests += @{
                name = "Detailed Health"
                status = "PASS"
                details = $detailedHealth
            }
        }
        catch {
            Write-Host "   ⚠️  Detailed health not available (optional)" -ForegroundColor Yellow
            $results.tests += @{
                name = "Detailed Health"
                status = "SKIP"
                error = $_.Exception.Message
            }
        }
    }
    
    # Test 3: Read Operations
    Write-Host ""
    Write-Host "3️⃣  Read Operations..." -ForegroundColor Cyan
    try {
        $incidents = Invoke-RestMethod -Uri "$ApiEndpoint/api/incidents?limit=5" -TimeoutSec 10
        Write-Host "   ✅ Can read incidents from Supabase ($($incidents.Count) records)" -ForegroundColor Green
        
        $results.tests += @{
            name = "Read Incidents"
            status = "PASS"
            details = @{ count = $incidents.Count }
        }
    }
    catch {
        Write-Host "   ❌ Cannot read incidents: $($_.Exception.Message)" -ForegroundColor Red
        $results.tests += @{
            name = "Read Incidents"
            status = "FAIL"
            error = $_.Exception.Message
        }
    }
    
    # Test 4: CURSOR Incident Integration
    Write-Host ""
    Write-Host "4️⃣  CURSOR Incident Integration..." -ForegroundColor Cyan
    try {
        $testIncident = Send-CursorIncidentToDualDB -IncidentType "api_validation_test" -Severity "low" -Confidence 0.99 -ApiEndpoint $ApiEndpoint -AdditionalContext @{ validation_test = $true }
        
        Write-Host "   ✅ CURSOR integration working" -ForegroundColor Green
        
        $results.tests += @{
            name = "CURSOR Integration"
            status = "PASS"
            details = $testIncident
        }
    }
    catch {
        Write-Host "   ❌ CURSOR integration failed: $($_.Exception.Message)" -ForegroundColor Red
        $results.tests += @{
            name = "CURSOR Integration"
            status = "FAIL"
            error = $_.Exception.Message
        }
    }
    
    # Summary
    Write-Host ""
    Write-Host "📊 SUMMARY" -ForegroundColor Magenta
    Write-Host "==========" -ForegroundColor Magenta
    
    $passedTests = ($results.tests | Where-Object { $_.status -eq "PASS" }).Count
    $failedTests = ($results.tests | Where-Object { $_.status -eq "FAIL" }).Count
    $totalTests = $results.tests.Count
    
    Write-Host "Passed: $passedTests" -ForegroundColor Green
    Write-Host "Failed: $failedTests" -ForegroundColor Red
    Write-Host "Total: $totalTests" -ForegroundColor White
    
    if ($failedTests -eq 0) {
        Write-Host ""
        Write-Host "🎉 All tests passed! API is ready for production." -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "⚠️  Some tests failed. Check configuration and try again." -ForegroundColor Yellow
    }
    
    # Save results to Google Drive if path exists
    $driveRoot = "G:\ClauseBot_OPPS_Workspace"
    if (Test-Path $driveRoot) {
        try {
            $reportPath = "$driveRoot\Shared\api_validation_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
            $results | ConvertTo-Json -Depth 5 | Set-Content -Path $reportPath -Encoding UTF8
            Write-Host ""
            Write-Host "📄 Results saved to Google Drive: $reportPath" -ForegroundColor Gray
        } catch {
            Write-Host ""
            Write-Host "⚠️  Could not save to Google Drive: $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }
    
    return $results
}

# Quick helper functions
function Send-ChromeHangIncident {
    param([switch]$UseLocal)
    Send-CursorIncidentToDualDB -IncidentType "chrome_result_code_hung" -Severity "high" -Confidence 0.85 -UseLocal:$UseLocal
}

function Send-GPUDriverIncident {
    param([switch]$UseLocal)
    Send-CursorIncidentToDualDB -IncidentType "gpu_driver_issue" -Severity "medium" -Confidence 0.75 -UseLocal:$UseLocal
}

function Send-MemoryPressureIncident {
    param([switch]$UseLocal)
    Send-CursorIncidentToDualDB -IncidentType "memory_pressure_detected" -Severity "medium" -Confidence 0.70 -UseLocal:$UseLocal
}

# Export functions for module use
Export-ModuleMember -Function Send-CursorIncidentToDualDB, Test-ClauseBotDualDatabaseAPI, Send-ChromeHangIncident, Send-GPUDriverIncident, Send-MemoryPressureIncident
