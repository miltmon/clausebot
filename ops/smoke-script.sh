#!/usr/bin/env bash
# smoke-script.sh
# Quick, idempotent smoke tests for ClauseBot post-deployment
# Safe to run in CI or manually

set -euo pipefail

API_BASE="${API_BASE:-https://clausebot-api.onrender.com}"
SUPABASE_URL="${SUPABASE_URL:-}"
SUPABASE_SERVICE_ROLE_KEY="${SUPABASE_SERVICE_ROLE_KEY:-}"

EXIT_CODE=0

echo "=========================================="
echo "ClauseBot Smoke Tests"
echo "=========================================="
echo "API Base: $API_BASE"
echo "Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo ""

# Function to check endpoint
check_endpoint() {
    local name="$1"
    local url="$2"
    local expected_status="${3:-200}"
    
    echo -n "Checking $name... "
    
    response=$(curl -s -w "\n%{http_code}" "$url" || echo "000")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "$expected_status" ]; then
        echo "✅ PASS (HTTP $http_code)"
        return 0
    else
        echo "❌ FAIL (HTTP $http_code, expected $expected_status)"
        echo "Response: $body"
        EXIT_CODE=1
        return 1
    fi
}

# Function to check JSON response
check_json_field() {
    local name="$1"
    local url="$2"
    local field="$3"
    local expected_value="$4"
    
    echo -n "Checking $name... "
    
    response=$(curl -s "$url")
    actual_value=$(echo "$response" | jq -r ".$field" 2>/dev/null || echo "")
    
    if [ "$actual_value" = "$expected_value" ]; then
        echo "✅ PASS ($field=$actual_value)"
        return 0
    else
        echo "❌ FAIL ($field='$actual_value', expected '$expected_value')"
        echo "Response: $response"
        EXIT_CODE=1
        return 1
    fi
}

# 1. Core health check
echo "=== Core Health ==="
check_endpoint "API Health" "$API_BASE/health" 200

# 2. Quiz endpoints (existing functionality)
echo ""
echo "=== Quiz Endpoints ==="
check_endpoint "Quiz Baseline Random" "$API_BASE/api/quiz/baseline/random" 200

# 3. RAG health check (may be disabled)
echo ""
echo "=== RAG Health ==="
rag_health_response=$(curl -s "$API_BASE/v1/chat/compliance/health" || echo '{"status":"error"}')
rag_status=$(echo "$rag_health_response" | jq -r '.status' 2>/dev/null || echo "error")

echo -n "RAG Health Status... "
if [ "$rag_status" = "operational" ] || [ "$rag_status" = "no_data" ] || [ "$rag_status" = "degraded" ]; then
    echo "✅ PASS (status=$rag_status)"
    
    # If RAG is enabled and operational, test a sample query
    rag_enabled=$(echo "$rag_health_response" | jq -r '.rag_enabled' 2>/dev/null || echo "false")
    if [ "$rag_enabled" = "true" ] && [ "$rag_status" = "operational" ]; then
        echo ""
        echo "=== RAG Query Test ==="
        echo -n "Sample RAG Query... "
        
        query_payload='{"query":"What is preheat?","top_k":3}'
        query_response=$(curl -s -X POST \
            -H "Content-Type: application/json" \
            -d "$query_payload" \
            "$API_BASE/v1/chat/compliance" || echo '{"error":"failed"}')
        
        answer=$(echo "$query_response" | jq -r '.answer' 2>/dev/null || echo "")
        
        if [ -n "$answer" ] && [ "$answer" != "null" ]; then
            echo "✅ PASS (got answer: ${#answer} chars)"
        else
            echo "❌ FAIL (no answer received)"
            echo "Response: $query_response"
            EXIT_CODE=1
        fi
    else
        echo "RAG disabled or no data - skipping query test"
    fi
else
    echo "⚠️  WARN (status=$rag_status) - RAG may be disabled or not configured"
fi

# 4. Optional: Supabase clause count check
if [ -n "$SUPABASE_URL" ] && [ -n "$SUPABASE_SERVICE_ROLE_KEY" ]; then
    echo ""
    echo "=== Supabase Clause Count ==="
    echo -n "Checking clause_embeddings count... "
    
    # Use Supabase REST API to count rows
    count_response=$(curl -s \
        -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
        -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
        -H "Range: 0-0" \
        "$SUPABASE_URL/rest/v1/clause_embeddings?select=clause_id" || echo "")
    
    count=$(echo "$count_response" | jq 'length' 2>/dev/null || echo "0")
    
    if [ "$count" -gt 0 ]; then
        echo "✅ PASS (found $count+ clauses)"
    else
        echo "⚠️  WARN (count=$count) - database may be empty"
    fi
fi

# Summary
echo ""
echo "=========================================="
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ ALL SMOKE TESTS PASSED"
else
    echo "❌ SOME TESTS FAILED"
fi
echo "=========================================="

exit $EXIT_CODE

