#!/bin/bash
# ClauseBot Emergency Rollback Script
# Quickly revert to previous deployment in case of critical issues

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
RENDER_API_KEY="${RENDER_API_KEY}"
SERVICE_ID="${CLAUSEBOT_SERVICE_ID}"

# Check requirements
if [ -z "$RENDER_API_KEY" ]; then
    echo -e "${RED}❌ ERROR: RENDER_API_KEY not set${NC}"
    echo "Set it with: export RENDER_API_KEY=your_key"
    exit 1
fi

if [ -z "$SERVICE_ID" ]; then
    echo -e "${RED}❌ ERROR: CLAUSEBOT_SERVICE_ID not set${NC}"
    echo "Set it with: export CLAUSEBOT_SERVICE_ID=srv-xxxxx"
    exit 1
fi

# Check for required tools
command -v curl >/dev/null 2>&1 || { echo "❌ curl is required but not installed."; exit 1; }
command -v jq >/dev/null 2>&1 || { echo "❌ jq is required but not installed."; exit 1; }

echo -e "${RED}🚨 ClauseBot Emergency Rollback${NC}"
echo "================================"
echo ""

# Get current and previous deploys
echo "📋 Fetching deploy history..."
DEPLOYS=$(curl -s -H "Authorization: Bearer $RENDER_API_KEY" \
    "https://api.render.com/v1/services/$SERVICE_ID/deploys" | \
    jq -r '.[] | "\(.id)|\(.status)|\(.createdAt)"' | head -n 5)

echo ""
echo "Recent deploys:"
echo "$DEPLOYS" | nl

# Get previous successful deploy
CURRENT_DEPLOY=$(echo "$DEPLOYS" | head -n 1 | cut -d'|' -f1)
PREVIOUS_DEPLOY=$(echo "$DEPLOYS" | grep "live" | tail -n 1 | cut -d'|' -f1)

if [ -z "$PREVIOUS_DEPLOY" ]; then
    PREVIOUS_DEPLOY=$(echo "$DEPLOYS" | sed -n '2p' | cut -d'|' -f1)
fi

echo ""
echo -e "${YELLOW}Current deploy:${NC} $CURRENT_DEPLOY"
echo -e "${GREEN}Rollback target:${NC} $PREVIOUS_DEPLOY"
echo ""

# Confirm rollback
read -p "$(echo -e ${YELLOW}⚠️  Are you sure you want to rollback? [y/N]:${NC} )" -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Rollback cancelled"
    exit 0
fi

echo ""
echo "🔄 Triggering rollback..."

# Trigger rollback via Render API
RESPONSE=$(curl -s -X POST \
    -H "Authorization: Bearer $RENDER_API_KEY" \
    "https://api.render.com/v1/services/$SERVICE_ID/deploys/$PREVIOUS_DEPLOY/restart")

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Rollback initiated${NC}"
else
    echo -e "${RED}❌ Rollback failed${NC}"
    echo "Response: $RESPONSE"
    exit 1
fi

echo ""
echo "⏳ Waiting for deploy to complete..."
sleep 30  # Initial wait

# Poll deploy status
for i in {1..20}; do
    STATUS=$(curl -s -H "Authorization: Bearer $RENDER_API_KEY" \
        "https://api.render.com/v1/services/$SERVICE_ID/deploys/$PREVIOUS_DEPLOY" | \
        jq -r '.status')
    
    echo "   Status: $STATUS (check $i/20)"
    
    if [ "$STATUS" = "live" ]; then
        echo -e "${GREEN}✅ Rollback complete!${NC}"
        break
    elif [ "$STATUS" = "build_failed" ] || [ "$STATUS" = "deactivated" ]; then
        echo -e "${RED}❌ Rollback failed with status: $STATUS${NC}"
        exit 1
    fi
    
    sleep 10
done

echo ""
echo "🔍 Verifying health..."
sleep 10  # Wait for service to stabilize

# Health check
HEALTH_URL="https://clausebot-api.onrender.com/health"
HEALTH_RESPONSE=$(curl -s -w "\n%{http_code}" "$HEALTH_URL")
HTTP_CODE=$(echo "$HEALTH_RESPONSE" | tail -n1)
BODY=$(echo "$HEALTH_RESPONSE" | head -n-1)

echo "Health check: $HEALTH_URL"
echo "Status: $HTTP_CODE"
echo "Body: $BODY"

if [ "$HTTP_CODE" = "200" ]; then
    OK=$(echo "$BODY" | jq -r '.ok' 2>/dev/null || echo "false")
    if [ "$OK" = "true" ]; then
        echo -e "${GREEN}✅ Health check passed${NC}"
    else
        echo -e "${YELLOW}⚠️  Health check returned ok=false${NC}"
    fi
else
    echo -e "${RED}❌ Health check failed with status $HTTP_CODE${NC}"
    echo -e "${YELLOW}⚠️  Service may need additional time to start${NC}"
fi

echo ""
echo "================================"
echo -e "${GREEN}🎉 Rollback procedure complete${NC}"
echo ""
echo "Next steps:"
echo "1. Monitor service logs in Render Dashboard"
echo "2. Run smoke tests: ./scripts/smoke-test.sh"
echo "3. Investigate root cause of original issue"
echo "4. Fix and redeploy when ready"
echo ""
echo "Dashboard: https://dashboard.render.com/web/$SERVICE_ID"

