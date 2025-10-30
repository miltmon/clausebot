# ClauseBot Environment Variables Map

## Required for Production Deployment

### Vercel Frontend Environment Variables (Production Scope)
**Note: This is a Vite/React app, not Next.js - use VITE_ prefix**
```bash
VITE_API_BASE=https://clausebot-api.onrender.com
VITE_SUPABASE_URL=https://hqhughgdraokwmreronk.supabase.co  
VITE_SUPABASE_ANON_KEY=<your-anon-key-here>
VITE_GIT_COMMIT_SHA=<auto-populated-by-vercel>
```

### Render Backend Environment Variables
```bash
# FastAPI Configuration
ENV=production
ALLOWED_ORIGINS=https://clausebot.miltmonndt.com,https://*.vercel.app

# Cross-Platform Storage
CLAUSEBOT_SHARED_DIR=/var/opt/clausebot

# Database Configuration  
SUPABASE_URL=https://hqhughgdraokwmreronk.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<service-role-key-from-supabase.txt>
AIRTABLE_API_KEY=pat0MY5k9x8iMNuvS
AIRTABLE_BASE_ID=<real-base-id-from-airtable>
AIRTABLE_TABLE_DEFAULT=incidents

# AI Provider (Optional)
MODEL_PROVIDER=openai
MODEL_NAME=gpt-4
OPENAI_API_KEY=<your-openai-key>

# Compliance Evaluation (PowerShell Integration)
CLAUSEBOT_API_BASE=https://clausebot-api.onrender.com
GITHUB_PAT=<github-models-token>
AZURE_MODELS_ENDPOINT=<azure-ai-endpoint>
AZURE_MODELS_KEY=<azure-ai-key>
```

## Security Notes

### ⚠️ NEVER put service role keys in frontend
- Frontend gets `SUPABASE_ANON_KEY` (public)
- Backend gets `SUPABASE_SERVICE_ROLE_KEY` (private)

### ✅ CORS Configuration
- API allows: `https://clausebot.miltmonndt.com` and `https://*.vercel.app`
- Prevents unauthorized domain access

## Health Check URLs

### Frontend Status Page
- Production: `https://clausebot.miltmonndt.com/status`
- Preview: `https://<deployment-id>.vercel.app/status`

### API Health Endpoints  
- Simple: `https://clausebot-api.onrender.com/healthz`
- Detailed: `https://clausebot-api.onrender.com/health`

## Deployment Checklist

### Before Promoting to Production:
1. ✅ Check preview deployment `/status` page
2. ✅ Verify API `/healthz` returns `{"ok": true}`
3. ✅ Confirm no console errors in browser
4. ✅ Test one critical user flow

### If Deployment Fails:
1. Check Vercel build logs for missing env vars
2. Verify API CORS allows frontend domain
3. Use Instant Rollback to previous stable build
4. Fix issues and redeploy

## Last Updated
- Date: October 2, 2025
- API Version: 1.0.0
- Frontend Framework: Next.js
