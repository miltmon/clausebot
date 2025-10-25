#!/bin/bash
# CI Gate: Prevent premature 2025 claims without verification
# Part of Grok operational contract - blocks unverified 2025 content

set -euo pipefail

# Configuration
API="${API:-http://127.0.0.1:8000}"
SRV_KEY="${SUPABASE_SERVICE_ROLE_KEY:-}"

if [[ -z "$SRV_KEY" ]]; then
    echo "❌ SUPABASE_SERVICE_ROLE_KEY not set"
    exit 1
fi

echo "🔍 Checking for unverified 2025 content..."

# Fetch crosswalk data for 2025 target edition
RESP=$(curl -sS -H "Authorization: Bearer $SRV_KEY" \
    "$API/v1/crosswalk?edition_target=2025" || {
    echo "❌ Failed to fetch crosswalk data"
    exit 1
})

# Check for unverified content without TBD badge
BAD=$(echo "$RESP" | jq '[.items[] | select(.verification_status != "verified" and (.summary_target|tostring|test("TBD"; "i")|not))] | length')

if [[ "$BAD" -eq 0 ]]; then
    echo "✅ All unverified 2025 content properly marked with TBD"
    exit 0
else
    echo "❌ Found $BAD unverified 2025 content items without TBD badge"
    echo "   This violates the conservative content policy"
    echo "   Either verify the content or add TBD markers"
    exit 1
fi
