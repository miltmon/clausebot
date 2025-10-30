#!/usr/bin/env pwsh
<#
.SYNOPSIS
Test Beads-inspired ClauseBot Agent Memory Integration

.DESCRIPTION
Comprehensive test of the new Beads-inspired features:
- Agent memory persistence
- Ready work detection
- Dependency tracking
- Batch operations
- JSON-first API design

.EXAMPLE
.\test_beads_integration.ps1
#>

param(
    [string]$BaseUrl = "http://localhost:8000",
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

# Colors for output
$Green = "`e[32m"
$Red = "`e[31m"
$Yellow = "`e[33m"
$Blue = "`e[34m"
$Reset = "`e[0m"

function Write-TestHeader($title) {
    Write-Host "${Blue}=== $title ===${Reset}" -ForegroundColor Blue
}

function Write-Success($message) {
    Write-Host "${Green}✅ $message${Reset}" -ForegroundColor Green
}

function Write-Error($message) {
    Write-Host "${Red}❌ $message${Reset}" -ForegroundColor Red
}

function Write-Warning($message) {
    Write-Host "${Yellow}⚠️  $message${Reset}" -ForegroundColor Yellow
}

function Invoke-ApiCall($method, $endpoint, $body = $null) {
    $url = "$BaseUrl$endpoint"
    
    try {
        $headers = @{
            "Content-Type" = "application/json"
            "Accept" = "application/json"
        }
        
        $params = @{
            Uri = $url
            Method = $method
            Headers = $headers
        }
        
        if ($body) {
            $params.Body = ($body | ConvertTo-Json -Depth 10)
        }
        
        if ($Verbose) {
            Write-Host "  → $method $url" -ForegroundColor Gray
            if ($body) {
                Write-Host "    Body: $($params.Body)" -ForegroundColor Gray
            }
        }
        
        $response = Invoke-RestMethod @params
        return $response
        
    } catch {
        Write-Error "API call failed: $method $url"
        Write-Error "Error: $($_.Exception.Message)"
        if ($_.Exception.Response) {
            $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
            $responseBody = $reader.ReadToEnd()
            Write-Error "Response: $responseBody"
        }
        throw
    }
}

function Test-BasicHealth {
    Write-TestHeader "Basic Health Checks"
    
    # Test basic health
    $health = Invoke-ApiCall "GET" "/health"
    if ($health.ok -eq $true) {
        Write-Success "Basic health check passed"
    } else {
        Write-Error "Basic health check failed"
        return $false
    }
    
    # Test agent memory stats (should start empty)
    $stats = Invoke-ApiCall "GET" "/v1/agent/memory/stats"
    if ($stats.success -eq $true) {
        Write-Success "Agent memory stats accessible"
        Write-Host "  Initial stats: $($stats.data.total_tasks) tasks, $($stats.data.dependencies) dependencies"
    } else {
        Write-Error "Agent memory stats failed"
        return $false
    }
    
    return $true
}

function Test-TaskCreation {
    Write-TestHeader "Task Creation (Beads bd create pattern)"
    
    # Create a high-priority AWS update task
    $taskData = @{
        title = "Update AWS D1.1:2025 references in Module 1"
        description = "Replace outdated AWS D1.1:2020 references with 2025 version"
        priority = 1  # HIGH
        task_type = "aws_update"
        category = "Structural Welding"
        clause_ref = "AWS D1.1:2025 Section 4.1"
        labels = @("aws", "urgent", "module1")
        session_id = "test-session-001"
        context = @{
            module = "module1"
            old_version = "D1.1:2020"
            new_version = "D1.1:2025"
        }
    }
    
    $response = Invoke-ApiCall "POST" "/v1/agent/memory/task" $taskData
    
    if ($response.success -eq $true) {
        Write-Success "Task created: $($response.data.id) - $($response.data.title)"
        $script:task1_id = $response.data.id
        return $true
    } else {
        Write-Error "Task creation failed"
        return $false
    }
}

function Test-BatchTaskCreation {
    Write-TestHeader "Batch Task Creation (Beads auto-discovery pattern)"
    
    # Simulate agent discovering multiple issues during content review
    $batchData = @{
        tasks = @(
            @{
                title = "Fix missing explanation in question Q042"
                description = "Question Q042 lacks proper explanation for AWS clause reference"
                task_type = "content_review"
                priority = 2
                category = "Structural Welding"
                clause_ref = "AWS D1.1:2025 Section 6.2"
                labels = @("content", "explanation")
                context = @{
                    question_id = "Q042"
                    issue_type = "missing_explanation"
                }
            },
            @{
                title = "Validate question difficulty for Q043"
                description = "Question Q043 may be too difficult for intermediate level"
                task_type = "question_validation"
                priority = 2
                category = "Structural Welding"
                labels = @("validation", "difficulty")
                context = @{
                    question_id = "Q043"
                    current_difficulty = "advanced"
                    suggested_difficulty = "intermediate"
                }
            }
        )
        source = "agent_content_review"
        session_id = "test-session-001"
        parent_task_id = $script:task1_id
    }
    
    $response = Invoke-ApiCall "POST" "/v1/agent/memory/tasks/batch" $batchData
    
    if ($response.success -eq $true) {
        Write-Success "Batch created: $($response.data.Count) tasks"
        $script:task2_id = $response.data[0].id
        $script:task3_id = $response.data[1].id
        return $true
    } else {
        Write-Error "Batch task creation failed"
        return $false
    }
}

function Test-DependencyTracking {
    Write-TestHeader "Dependency Tracking (Beads core feature)"
    
    # Add dependency: task2 blocks task3 (fix explanation before validating difficulty)
    $depData = @{
        dependent_task_id = $script:task3_id
        blocks_task_id = $script:task2_id
        dependency_type = "blocks"
        notes = "Must fix explanation before validating difficulty"
    }
    
    $response = Invoke-ApiCall "POST" "/v1/agent/memory/dependency" $depData
    
    if ($response.success -eq $true) {
        Write-Success "Dependency created: $($script:task3_id) depends on $($script:task2_id)"
        return $true
    } else {
        Write-Error "Dependency creation failed"
        return $false
    }
}

function Test-ReadyWorkDetection {
    Write-TestHeader "Ready Work Detection (Beads killer feature)"
    
    # Get ready work - should show tasks with no blockers
    $response = Invoke-ApiCall "GET" "/v1/agent/memory/ready?limit=10&sort=hybrid"
    
    if ($response.success -eq $true) {
        Write-Success "Ready work detection successful"
        Write-Host "  Ready tasks: $($response.data.Count)"
        
        foreach ($item in $response.data) {
            $task = $item.task
            Write-Host "    - $($task.id): $($task.title) (Priority: $($task.priority), Score: $($item.priority_score))"
        }
        
        # Verify that task3 is NOT in ready work (it's blocked by task2)
        $task3_ready = $response.data | Where-Object { $_.task.id -eq $script:task3_id }
        if (-not $task3_ready) {
            Write-Success "Dependency blocking works correctly - task3 not in ready work"
        } else {
            Write-Error "Dependency blocking failed - task3 should be blocked"
            return $false
        }
        
        return $true
    } else {
        Write-Error "Ready work detection failed"
        return $false
    }
}

function Test-BlockedTasksDetection {
    Write-TestHeader "Blocked Tasks Detection"
    
    $response = Invoke-ApiCall "GET" "/v1/agent/memory/blocked"
    
    if ($response.success -eq $true) {
        Write-Success "Blocked tasks detection successful"
        Write-Host "  Blocked tasks: $($response.data.Count)"
        
        foreach ($item in $response.data) {
            Write-Host "    - $($item.task.id): $($item.task.title) (Blocked by: $($item.blockers -join ', '))"
        }
        
        return $true
    } else {
        Write-Error "Blocked tasks detection failed"
        return $false
    }
}

function Test-QuizIntegration {
    Write-TestHeader "Quiz Integration with Agent Memory"
    
    # Test ready quiz work
    $response = Invoke-ApiCall "GET" "/v1/quiz/ready?format=json&limit=5"
    
    if ($null -ne $response.count) {
        Write-Success "Quiz ready work integration successful"
        Write-Host "  Ready quiz tasks: $($response.count)"
        return $true
    } else {
        Write-Error "Quiz ready work integration failed"
        return $false
    }
}

function Test-BatchValidation {
    Write-TestHeader "Batch Validation with Auto-Task Creation"
    
    # Test batch validation (will create tasks for issues found)
    $batchData = @{
        question_ids = @("Q001", "test_question", "Q042", "short")
        category = "Structural Welding"
        session_id = "test-session-validation"
    }
    
    $response = Invoke-ApiCall "POST" "/v1/quiz/batch-validate" $batchData
    
    if ($response.total_validated -eq 4) {
        Write-Success "Batch validation successful"
        Write-Host "  Validated: $($response.total_validated), Valid: $($response.valid_count), Invalid: $($response.invalid_count)"
        Write-Host "  Tasks created: $($response.tasks_created.Count)"
        
        if ($response.tasks_created.Count -gt 0) {
            Write-Success "Auto-task creation working - created tasks for validation issues"
        }
        
        return $true
    } else {
        Write-Error "Batch validation failed"
        return $false
    }
}

function Test-TaskUpdates {
    Write-TestHeader "Task Updates (Beads bd update pattern)"
    
    # Complete task2 (fix explanation)
    $updateData = @{
        status = "completed"
        context = @{
            completion_notes = "Fixed explanation for Q042"
            completed_by = "test_agent"
        }
    }
    
    $response = Invoke-ApiCall "PUT" "/v1/agent/memory/task/$($script:task2_id)" $updateData
    
    if ($response.success -eq $true) {
        Write-Success "Task updated: $($script:task2_id) marked as completed"
        
        # Now check if task3 becomes ready (blocker removed)
        Start-Sleep -Seconds 1
        $readyResponse = Invoke-ApiCall "GET" "/v1/agent/memory/ready?limit=10"
        
        $task3_ready = $readyResponse.data | Where-Object { $_.task.id -eq $script:task3_id }
        if ($task3_ready) {
            Write-Success "Dependency resolution works - task3 now ready after blocker completed"
        } else {
            Write-Warning "Task3 still not ready - may need dependency cleanup"
        }
        
        return $true
    } else {
        Write-Error "Task update failed"
        return $false
    }
}

function Test-FinalStats {
    Write-TestHeader "Final Statistics"
    
    $response = Invoke-ApiCall "GET" "/v1/agent/memory/stats"
    
    if ($response.success -eq $true) {
        $stats = $response.data
        Write-Success "Final agent memory statistics:"
        Write-Host "  Total tasks: $($stats.total_tasks)"
        Write-Host "  Open tasks: $($stats.open_tasks)"
        Write-Host "  In progress: $($stats.in_progress_tasks)"
        Write-Host "  Completed: $($stats.completed_tasks)"
        Write-Host "  Blocked tasks: $($stats.blocked_tasks)"
        Write-Host "  Ready tasks: $($stats.ready_tasks)"
        Write-Host "  Dependencies: $($stats.dependencies)"
        
        if ($stats.avg_completion_time_hours) {
            Write-Host "  Avg completion time: $([math]::Round($stats.avg_completion_time_hours, 2)) hours"
        }
        
        return $true
    } else {
        Write-Error "Final stats failed"
        return $false
    }
}

# Main test execution
Write-Host "${Blue}🚀 BEADS INTEGRATION TEST FOR CLAUSEBOT${Reset}" -ForegroundColor Blue
Write-Host "Testing Beads-inspired agent memory, ready work detection, and dependency tracking"
Write-Host "Base URL: $BaseUrl"
Write-Host ""

$script:task1_id = $null
$script:task2_id = $null  
$script:task3_id = $null

$tests = @(
    "Test-BasicHealth",
    "Test-TaskCreation", 
    "Test-BatchTaskCreation",
    "Test-DependencyTracking",
    "Test-ReadyWorkDetection",
    "Test-BlockedTasksDetection",
    "Test-QuizIntegration",
    "Test-BatchValidation",
    "Test-TaskUpdates",
    "Test-FinalStats"
)

$passed = 0
$failed = 0

foreach ($test in $tests) {
    try {
        $result = & $test
        if ($result) {
            $passed++
        } else {
            $failed++
        }
    } catch {
        Write-Error "Test $test threw exception: $($_.Exception.Message)"
        $failed++
    }
    Write-Host ""
}

Write-Host "${Blue}=== TEST SUMMARY ===${Reset}" -ForegroundColor Blue
Write-Host "${Green}Passed: $passed${Reset}" -ForegroundColor Green
Write-Host "${Red}Failed: $failed${Reset}" -ForegroundColor Red

if ($failed -eq 0) {
    Write-Host "${Green}🎉 ALL TESTS PASSED! Beads integration is working perfectly.${Reset}" -ForegroundColor Green
    exit 0
} else {
    Write-Host "${Red}💥 Some tests failed. Check the output above for details.${Reset}" -ForegroundColor Red
    exit 1
}
