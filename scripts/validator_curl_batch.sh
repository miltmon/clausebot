#!/usr/bin/env bash
# Golden Test Validator - Batch Mode
# Validates Q026-Q041 against ClauseBot golden validator endpoint

set -euo pipefail

# ========================================
# CONFIGURATION
# ========================================

VALIDATOR_URL="${VALIDATOR_URL:-https://clausebot-api.onrender.com/v1/golden/validate}"
VALIDATOR_TOKEN="${VALIDATOR_TOKEN:-}"  # Set via environment or leave empty if no auth required

# Test IDs to validate
TEST_IDS=(
  "Q026" "Q027" "Q028" "Q029" "Q030" 
  "Q031" "Q032" "Q033" "Q034" "Q035" 
  "Q036" "Q037" "Q038" "Q039" "Q040" "Q041"
)

# ========================================
# DEPENDENCY CHECK
# ========================================

if ! command -v curl >/dev/null 2>&1; then
  echo "ERROR: curl is required but not installed."
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "ERROR: jq is required but not installed."
  exit 1
fi

# ========================================
# BUILD REQUEST PAYLOAD
# ========================================

echo "Building validator request payload..."

# Convert bash array to JSON array
IDS_JSON=$(printf '%s\n' "${TEST_IDS[@]}" | jq -R . | jq -s .)

REQUEST_PAYLOAD=$(jq -n \
  --argjson ids "$IDS_JSON" \
  '{test_ids: $ids}')

echo "Request payload:"
echo "$REQUEST_PAYLOAD" | jq .

# ========================================
# SEND VALIDATION REQUEST
# ========================================

echo ""
echo "Sending batch validation request to: $VALIDATOR_URL"
echo ""

# Build curl command with optional auth
CURL_OPTS=(-X POST "$VALIDATOR_URL" \
  -H "Content-Type: application/json" \
  -d "$REQUEST_PAYLOAD" \
  -w "\nHTTP_CODE:%{http_code}\n" \
  -s)

if [ -n "$VALIDATOR_TOKEN" ]; then
  CURL_OPTS+=(-H "Authorization: Bearer $VALIDATOR_TOKEN")
fi

RESPONSE=$(curl "${CURL_OPTS[@]}")

# Extract HTTP code and body
HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_CODE:/d')

echo "HTTP Status: $HTTP_CODE"
echo ""

# ========================================
# PARSE AND DISPLAY RESULTS
# ========================================

if [ "$HTTP_CODE" != "200" ]; then
  echo "ERROR: Validator returned non-200 status code: $HTTP_CODE"
  echo "Response body:"
  echo "$BODY" | jq . || echo "$BODY"
  exit 2
fi

echo "Validation Results:"
echo "==================="
echo ""

# Parse results
TOTAL_TESTS=$(echo "$BODY" | jq -r '.total_tests // 0')
PASSED=$(echo "$BODY" | jq -r '.passed // 0')
FAILED=$(echo "$BODY" | jq -r '.failed // 0')
PASS_RATE=$(echo "$BODY" | jq -r '.pass_rate // 0')

echo "Total Tests:  $TOTAL_TESTS"
echo "Passed:       $PASSED"
echo "Failed:       $FAILED"
echo "Pass Rate:    $PASS_RATE"
echo ""

# Display individual results if available
if echo "$BODY" | jq -e '.results' >/dev/null 2>&1; then
  echo "Individual Test Results:"
  echo "------------------------"
  echo "$BODY" | jq -r '.results[] | "\(.id): \(.status) - \(.message // "OK")"'
  echo ""
fi

# Display failures in detail
FAILURE_COUNT=$(echo "$BODY" | jq '[.results[] | select(.status != "PASS")] | length')
if [ "$FAILURE_COUNT" -gt 0 ]; then
  echo "❌ FAILURES DETECTED ($FAILURE_COUNT):"
  echo "======================================"
  echo "$BODY" | jq -r '.results[] | select(.status != "PASS") | "ID: \(.id)\nStatus: \(.status)\nIssue: \(.message)\nDetails: \(.details // "N/A")\n"'
  exit 3
fi

# ========================================
# SUCCESS SUMMARY
# ========================================

echo "✅ ALL TESTS PASSED ($PASSED/$TOTAL_TESTS)"
echo ""
echo "Next steps:"
echo "  1. Review SME initials (all currently 'TBD')"
echo "  2. Assign SME for content review"
echo "  3. After SME approval, run staging ingest:"
echo "     psql \$SUPABASE_STAGING_URL -f ops/ingest_golden_Q026_Q041.sql"
echo ""

exit 0

