# 🎯 VERCEL DEPLOYMENT FIX - IMMEDIATE ACTION REQUIRED

## Problem
Vercel project `clausebot.vercel.app` is serving Morphic AI frontend instead of ClauseBot frontend from `miltmon/clausebot/frontend`.

## Solution: Reconnect to Correct Repository

### **Step 1: Disconnect Current Repo**
1. Log into [Vercel Dashboard](https://vercel.com/dashboard)
2. Open project: `clausebot` (or `clausebot.miltmonndt.com`)
3. Go to **Settings** → **Git**
4. Click **Disconnect** next to current repo (`morphic-ai-answer-engine-generative-ui`)

### **Step 2: Import Correct Repository**
1. Click **Import Project** (or **Add New Project**)
2. Select **GitHub** → `miltmon/clausebot`
3. Configure project settings:

```json
{
  "name": "clausebot",
  "framework": "vite",
  "rootDirectory": "frontend",
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "installCommand": "npm ci"
}
```

### **Step 3: Environment Variables**
Add these in **Settings** → **Environment Variables**:

```json
{
  "VITE_API_URL": "https://clausebot-api.onrender.com",
  "VITE_CLAUSEBOT_WS": "wss://clausebot-api.onrender.com/ws",
  "NEXT_PUBLIC_SUPABASE_URL": "https://hqhughgdraokwmreronk.supabase.co",
  "NEXT_PUBLIC_SUPABASE_ANON_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhxaHVnaGdkcmFva3dtcmVyb25rIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjkzNzI4NzcsImV4cCI6MjA0NDk0ODg3N30.VtGK8-TFkl7bLYlJRqRzUdQzZlJWbEVCJEKnxRv0Tho"
}
```

### **Step 4: Deploy and Verify**
1. Click **Deploy**
2. Wait for build completion
3. Test deployment:

```bash
# Quick verification commands
curl -I https://clausebot.vercel.app/ | head -5
curl -s https://clausebot.vercel.app/ | grep -i "clausebot\|welding" | head -3
```

### **Step 5: Domain Configuration**
If using custom domain:
1. **Settings** → **Domains**
2. Ensure `clausebot.vercel.app` points to this project
3. Add custom domains if needed

## Expected Results
- ✅ Homepage shows ClauseBot/Welding interface (not Morphic AI)
- ✅ API calls go to `clausebot-api.onrender.com`
- ✅ No 404s or missing assets
- ✅ WebSocket connections work

## Rollback Plan
If deployment fails:
1. Keep old project active
2. Use new project URL for testing
3. Switch domains only after full verification

## Success Criteria
```bash
# These should return ClauseBot content:
curl -s https://clausebot.vercel.app/ | grep -i "title"
# Should show: ClauseBot - Welding Code Assistant

# API connectivity test:
curl -s https://clausebot-api.onrender.com/v1/health
# Should return: {"status": "healthy"}
```

---
**Execute this checklist now. Estimated time: 5-10 minutes**
