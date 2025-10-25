# Monitoring Quick Reference (ClauseBot)

**Setup Date:** Nov 2, 2025  
**Full Guide:** See MONITORING_GUIDE.md

## 🎯 Monitors (UptimeRobot)
- API Health: https://clausebot-api.onrender.com/health  (keyword: "ok")
- Frontend:   https://clausebot.vercel.app/               (keyword: "ClauseBot")
- Quiz Data:  https://clausebot-api.onrender.com/v1/quiz   (keyword: "items")
- Quiz Metric: https://clausebot-api.onrender.com/health/quiz/baseline (keyword: "eligible_in_sample")

## 🚨 Alerts
- Tier 1 (10m): Email → [REDACTED]
- Tier 2 (15m): SMS   → [REDACTED]

## 🔧 Quick Fix
1) API down → Render → Events → redeploy last green
2) Frontend down → Vercel → promote previous deploy
3) Content issue → check Airtable/Supabase; orchestrator logs
4) Log incident → docs/incidents/YYYY-MM-DD.md

## 📅 Roadmap
- Dec 2025: Canary endpoints + synthetics
- Jan 15, 2026: Better Stack (latency/SLO + status page)
