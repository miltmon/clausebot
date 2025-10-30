#!/usr/bin/env bash
set -euo pipefail

################################################################################
# Repo Audit Script - Read-only security & health check across GitHub repos
#
# This script performs READ-ONLY checks on multiple repositories:
# - Collaborators & permissions
# - Webhooks configuration
# - GitHub Actions secrets (names only, not values)
# - Latest workflow run status
# - External service reachability (Supabase, Airtable)
#
# Requirements:
#   - curl, jq (preinstalled on GitHub Actions Ubuntu runners)
#   - GITHUB_API_TOKEN or ORG_GITHUB_TOKEN env var (PAT with repo scope)
#
# Optional env vars:
#   - SUPABASE_URL: Supabase instance to check (default: hqhughgdraokwmreronk.supabase.co)
#   - AIRTABLE_API_KEY: Airtable API key for authenticated checks (optional)
################################################################################

# Token selection (prefer ORG_GITHUB_TOKEN for cross-repo access)
GITHUB_API_TOKEN="${GITHUB_API_TOKEN:-${ORG_GITHUB_TOKEN:-}}"
if [[ -z "$GITHUB_API_TOKEN" ]]; then
  echo "❌ ERROR: GITHUB_API_TOKEN or ORG_GITHUB_TOKEN must be set"
  echo "   For cross-repo access, create a PAT with 'repo' and 'admin:repo_hook' scopes"
  exit 2
fi

# External service configuration
SUPABASE_URL="${SUPABASE_URL:-https://hqhughgdraokwmreronk.supabase.co}"
AIRTABLE_API_KEY="${AIRTABLE_API_KEY:-}"

# Repository list - all repos to audit
REPOS=(
  "miltmon/clausebot-api"
  "miltmon/clausebotai"
  "miltmon/clausebot"
  "miltmon/gemini-2-0-flash-image-generation-and-editing"
  "miltmon/wix-classes-subscriptions"
  "miltmon/nextjs-commerce"
  "miltmon/nextjs-ai-chatbot"
  "miltmon/clausebot.ai-answer-engine-generative-ui"
  "miltmon/awsbokphoneapp"
  "miltmon/idletime-herb-vault"
  "miltmon/table-id-helper"
  "miltmon/WeldMap-"
  "miltmon/456-three-dice"
  "miltmon/rgs-family-connect"
)

# Output setup
OUTDIR="repo_audit_output"
mkdir -p "$OUTDIR"

timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
report_file="${OUTDIR}/repo-audit-${timestamp}.json"

echo "🔍 Starting repository audit at ${timestamp}"
echo "   Scanning ${#REPOS[@]} repositories..."

# Initialize JSON report
echo "{" > "$report_file"
echo "  \"generated_at\": \"${timestamp}\"," >> "$report_file"
echo "  \"audit_version\": \"1.0.0\"," >> "$report_file"
echo "  \"external_services\": {" >> "$report_file"

################################################################################
# External Service Checks
################################################################################

echo "📡 Checking external services..."

# Supabase health check
supabase_status=0
supabase_response_time=0
if [[ -n "$SUPABASE_URL" ]]; then
  start_time=$(date +%s%3N)
  if curl -sf --max-time 10 "${SUPABASE_URL}/rest/v1/" -o /dev/null 2>&1; then
    supabase_status=200
    end_time=$(date +%s%3N)
    supabase_response_time=$((end_time - start_time))
    echo "   ✅ Supabase: reachable (${supabase_response_time}ms)"
  else
    supabase_status=0
    echo "   ⚠️  Supabase: unreachable or timeout"
  fi
fi

echo "    \"supabase\": {" >> "$report_file"
echo "      \"url\": \"${SUPABASE_URL}\"," >> "$report_file"
echo "      \"status\": ${supabase_status}," >> "$report_file"
echo "      \"response_time_ms\": ${supabase_response_time}" >> "$report_file"
echo "    }," >> "$report_file"

# Airtable API check
airtable_status=0
airtable_response_time=0
start_time=$(date +%s%3N)
if [[ -n "$AIRTABLE_API_KEY" ]]; then
  # Authenticated check to /v0/meta/bases (requires API key)
  if curl -sf --max-time 10 -H "Authorization: Bearer ${AIRTABLE_API_KEY}" "https://api.airtable.com/v0/meta/bases" -o /dev/null 2>&1; then
    airtable_status=200
    end_time=$(date +%s%3N)
    airtable_response_time=$((end_time - start_time))
    echo "   ✅ Airtable: authenticated & reachable (${airtable_response_time}ms)"
  else
    airtable_status=401
    echo "   ⚠️  Airtable: auth failed or unreachable"
  fi
else
  # Unauthenticated ping (just check api.airtable.com is up)
  if curl -sf --max-time 10 "https://api.airtable.com" -o /dev/null 2>&1; then
    airtable_status=200
    end_time=$(date +%s%3N)
    airtable_response_time=$((end_time - start_time))
    echo "   ✅ Airtable: reachable (unauthenticated ping, ${airtable_response_time}ms)"
  else
    airtable_status=0
    echo "   ⚠️  Airtable: unreachable"
  fi
fi

echo "    \"airtable\": {" >> "$report_file"
echo "      \"url\": \"https://api.airtable.com\"," >> "$report_file"
echo "      \"authenticated\": $([ -n "$AIRTABLE_API_KEY" ] && echo "true" || echo "false")," >> "$report_file"
echo "      \"status\": ${airtable_status}," >> "$report_file"
echo "      \"response_time_ms\": ${airtable_response_time}" >> "$report_file"
echo "    }" >> "$report_file"

echo "  }," >> "$report_file"
echo "  \"repos\": {" >> "$report_file"

################################################################################
# Repository Checks
################################################################################

echo ""
echo "📚 Scanning repositories..."

first=true
for repo in "${REPOS[@]}"; do
  echo "   Scanning: $repo"
  
  if $first; then
    first=false
  else
    echo "," >> "$report_file"
  fi
  
  echo -n "    \"$repo\": {" >> "$report_file"

  # 1. Collaborators & permissions
  collab_json="$(curl -sf -H "Authorization: Bearer $GITHUB_API_TOKEN" \
    -H "Accept: application/vnd.github+json" \
    "https://api.github.com/repos/${repo}/collaborators" 2>/dev/null || echo "[]")"
  echo "\"collaborators\": $collab_json," >> "$report_file"

  # 2. Webhooks
  hooks_json="$(curl -sf -H "Authorization: Bearer $GITHUB_API_TOKEN" \
    -H "Accept: application/vnd.github+json" \
    "https://api.github.com/repos/${repo}/hooks" 2>/dev/null || echo "[]")"
  echo "\"webhooks\": $hooks_json," >> "$report_file"

  # 3. Actions secrets (list names only - values are never exposed by API)
  secrets_json="$(curl -sf -H "Authorization: Bearer $GITHUB_API_TOKEN" \
    -H "Accept: application/vnd.github+json" \
    "https://api.github.com/repos/${repo}/actions/secrets" 2>/dev/null || echo "{\"secrets\":[]}")"
  echo "\"actions_secrets\": $secrets_json," >> "$report_file"

  # 4. Latest workflow run
  runs_json="$(curl -sf -H "Authorization: Bearer $GITHUB_API_TOKEN" \
    -H "Accept: application/vnd.github+json" \
    "https://api.github.com/repos/${repo}/actions/runs?per_page=1" 2>/dev/null || echo "{\"workflow_runs\":[]}")"
  echo "\"latest_workflow_run\": $runs_json" >> "$report_file"

  echo -n "}" >> "$report_file"
done

# Close JSON structure
echo "" >> "$report_file"
echo "  }" >> "$report_file"
echo "}" >> "$report_file"

################################################################################
# Report Summary
################################################################################

echo ""
echo "✅ Audit complete!"
echo ""
echo "📄 Report written to: $report_file"
ls -lh "$report_file"
echo ""
echo "💡 Query examples:"
echo "   cat $report_file | jq '.external_services'"
echo "   cat $report_file | jq -r '.repos | keys[]'"
echo "   cat $report_file | jq -r '.repos | to_entries[] | select(.value.latest_workflow_run.workflow_runs[0].conclusion == \"failure\") | .key'"

exit 0
