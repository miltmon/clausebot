# ClauseBot Uptime Monitoring Guide

**Last Updated:** October 25, 2025  
**Scheduled Setup:** November 2, 2025 at 10:00 AM PT  
**Monitoring Service:** UptimeRobot (Free Tier)

---

## 📊 MONITORING OVERVIEW

### What We Monitor

**Infrastructure Endpoints (Critical):**
- API Health: `https://clausebot-api.onrender.com/health`
- Frontend: `https://clausebot.vercel.app/`

**Content Endpoints (Important):**
- Quiz API: `https://clausebot-api.onrender.com/v1/quiz`
- Quiz Health: `https://clausebot-api.onrender.com/health/quiz/detailed`

### Monitoring Intervals

- **Check Frequency:** Every 5 minutes
- **Alert Threshold:** 2 consecutive failures (10 minutes downtime)
- **Timeout:** 30 seconds per request

---

## 🚨 ALERT TIERS

### Tier 1: Email Alert (10 min downtime)
- **Contact:** [REDACTED - Internal use only]
- **Trigger:** 2 consecutive failures
- **Response Time:** 30 minutes during business hours
- **Actions:** Check dashboard, investigate logs

### Tier 2: SMS Escalation (15 min downtime)
- **Contact:** [REDACTED - Internal use only]
- **Trigger:** 3 consecutive failures
- **Response Time:** Immediate
- **Actions:** Emergency response, rollback if needed

---

## 📋 MONITOR CONFIGURATIONS

### Monitor 1: ClauseBot API Health

**Purpose:** Core backend health check

**Configuration:**
```
Name: ClauseBot API Health
Type: HTTP(s)
URL: https://clausebot-api.onrender.com/health
Method: GET
Expected Status: 200 OK
Expected Response: {"ok": true}
Interval: Every 5 minutes
Timeout: 30 seconds
Alert After: 2 consecutive failures
SSL/TLS: Enabled
```

**Expected Response:**
```json
{
  "ok": true,
  "service": "clausebot-api",
  "version": "0.1.0"
}
```

**Alert Actions:**
1. Check Render logs: https://dashboard.render.com/web/srv-d37fjc0gjchc73c8gfs0/logs
2. Verify `/buildinfo` endpoint for deployment status
3. Check Render service status page
4. Review recent deploys for breaking changes

---

### Monitor 2: ClauseBot Frontend

**Purpose:** Frontend availability and SSL certificate monitoring

**Configuration:**
```
Name: ClauseBot Frontend
Type: HTTP(s)
URL: https://clausebot.vercel.app/
Method: GET
Expected Status: 200 OK
Keyword Check: "ClauseBot" (in page title/content)
Interval: Every 5 minutes
Timeout: 30 seconds
Alert After: 2 consecutive failures
SSL Certificate Monitoring: Enabled (alert 7 days before expiry)
```

**Expected Response:**
- 200 OK status
- Page loads with ClauseBot branding
- No JavaScript errors in console

**Alert Actions:**
1. Check Vercel deployment status: https://vercel.com/miltmonllc/clausebot/deployments
2. Review Vercel logs for build failures
3. Test locally: `npm run dev` in frontend directory
4. Check DNS configuration if SSL issues

---

### Monitor 3: ClauseBot Quiz API

**Purpose:** Quiz content delivery verification

**Configuration:**
```
Name: ClauseBot Quiz API
Type: HTTP(s)
URL: https://clausebot-api.onrender.com/v1/quiz
Method: GET
Expected Status: 200 OK
Keyword Check: "items" (in response body)
Interval: Every 5 minutes
Timeout: 30 seconds
Alert After: 2 consecutive failures
```

**Expected Response:**
```json
{
  "count": 5,
  "category": "default",
  "source": "airtable",
  "items": [...]
}
```

**Alert Actions:**
1. Check Airtable connection: `/health/airtable` endpoint
2. Review Airtable API status
3. Check AIRTABLE_API_KEY environment variable in Render
4. Verify quiz data in Airtable base

---

### Monitor 4: ClauseBot Quiz Health

**Purpose:** Quiz data quality and availability monitoring

**Configuration:**
```
Name: ClauseBot Quiz Health
Type: HTTP(s)
URL: https://clausebot-api.onrender.com/health/quiz/detailed
Method: GET
Expected Status: 200 OK
Keyword Check: "eligible" (in response body)
Interval: Every 5 minutes
Timeout: 30 seconds
Alert After: 2 consecutive failures
```

**Expected Response:**
```json
{
  "records": {
    "total": 121,
    "quiz_eligible": 114,
    "production_ready": 16
  },
  "distribution": {...}
}
```

**Alert Actions:**
1. Check Airtable connection status
2. Review data quality metrics
3. Verify production-ready question count
4. Check filtering logic if eligible count drops

---

## 🔧 INCIDENT RESPONSE PROCEDURES

### Level 1: Single Monitor Down

**Symptoms:**
- One monitor reports down
- Other monitors still green

**Actions:**
1. **Verify the issue** (manual curl test)
2. **Check specific service** (Render/Vercel dashboard)
3. **Review recent deploys** (last 24 hours)
4. **Check service logs** for errors
5. **Document incident** in `docs/incidents/YYYY-MM-DD-description.md`

**Response Time:** 30 minutes

---

### Level 2: Multiple Monitors Down

**Symptoms:**
- 2+ monitors report down simultaneously
- Both Tier 1 and Tier 2 alerts triggered

**Actions:**
1. **Immediate triage** - which services affected?
2. **Check platform status:**
   - Render: https://status.render.com/
   - Vercel: https://www.vercel-status.com/
3. **Review last deploy** - rollback if recent change
4. **Emergency rollback procedure:**
   ```powershell
   # Render - via dashboard (fastest)
   # Vercel - promote last known-good deployment
   ```
5. **Notify stakeholders** if extended outage (>30 min)

**Response Time:** Immediate

---

### Level 3: Complete System Down

**Symptoms:**
- All 4 monitors down
- SMS alerts triggered
- User reports of total unavailability

**Actions:**
1. **Emergency response mode**
2. **Check DNS resolution:**
   ```powershell
   nslookup clausebot.vercel.app
   nslookup clausebot-api.onrender.com
   ```
3. **Check Cloudflare/CDN** if used
4. **Contact platform support:**
   - Render: support@render.com
   - Vercel: support@vercel.com
5. **Execute disaster recovery plan** (see below)

**Response Time:** Immediate

---

## 🆘 DISASTER RECOVERY PLAN

### Scenario 1: Render Backend Outage

**If Render platform is down:**
1. Check Render status page: https://status.render.com/
2. Monitor for incident resolution
3. Consider temporary maintenance mode on frontend
4. Communicate ETA to users if outage >1 hour

**If backend code issue:**
1. Identify problematic commit via `/buildinfo`
2. Rollback to last known-good deployment
3. Test health endpoints after rollback
4. Document root cause

---

### Scenario 2: Vercel Frontend Outage

**If Vercel platform is down:**
1. Check Vercel status: https://www.vercel-status.com/
2. Backend API remains accessible
3. Consider API-only mode for critical integrations

**If frontend build failure:**
1. Review Vercel deployment logs
2. Promote last successful deployment
3. Fix issue in feature branch
4. Test before re-deploying to production

---

### Scenario 3: DNS/Network Issues

**Symptoms:**
- Timeouts on all endpoints
- DNS resolution failures

**Actions:**
1. Check DNS propagation: https://dnschecker.org/
2. Verify domain registrar settings
3. Check Cloudflare configuration (if used)
4. Contact DNS provider support

---

## 📊 MONITORING DASHBOARD ACCESS

### UptimeRobot Dashboard

**URL:** https://uptimerobot.com/dashboard  
**Login:** [Use SSO or saved credentials]

**What to Check:**
- Monitor status (up/down)
- Response times (historical)
- Uptime percentage (SLA tracking)
- Alert history (recent incidents)

**Key Metrics:**
- **30-day uptime:** Target >99.9%
- **Average response time:** <500ms for health endpoints
- **MTTR (Mean Time To Repair):** <30 minutes

---

### Alternative Verification (Manual)

**PowerShell Script:**
```powershell
# Quick manual verification of all endpoints
Write-Host "=== ClauseBot Manual Health Check ===" -ForegroundColor Cyan

$endpoints = @(
    @{Name="API Health"; URL="https://clausebot-api.onrender.com/health"},
    @{Name="Frontend"; URL="https://clausebot.vercel.app/"},
    @{Name="Quiz API"; URL="https://clausebot-api.onrender.com/v1/quiz/fundamentals"},
    @{Name="Crosswalk API"; URL="https://clausebot-api.onrender.com/v1/crosswalk/stats"}
)

foreach ($endpoint in $endpoints) {
    try {
        $response = Invoke-WebRequest $endpoint.URL -UseBasicParsing -TimeoutSec 10
        Write-Host "✅ $($endpoint.Name): $($response.StatusCode)" -ForegroundColor Green
    } catch {
        Write-Host "❌ $($endpoint.Name): FAILED" -ForegroundColor Red
    }
}
```

---

## 📈 REPORTING & ANALYTICS

### Weekly Uptime Report

**Generate every Monday:**
1. Log into UptimeRobot dashboard
2. Navigate to "Reports" section
3. Generate 7-day uptime report
4. Document any incidents in `docs/incidents/`

**Metrics to Track:**
- Overall uptime percentage
- Number of incidents
- Average response time
- MTTR (if any incidents)

---

### Monthly SLA Review

**Generate first of each month:**
1. 30-day uptime percentage
2. Comparison to previous month
3. Trend analysis (improving/degrading)
4. Action items for next month

**SLA Targets:**
- **API Health:** 99.9% uptime (43 minutes downtime/month)
- **Frontend:** 99.9% uptime
- **Content APIs:** 99.5% uptime (3.6 hours downtime/month)

---

## 🔔 NOTIFICATION PREFERENCES

### Email Notifications (Tier 1)

**When to Send:**
- Monitor goes down (after 2 consecutive failures)
- Monitor comes back up
- SSL certificate expires in 7 days

**Email Format:**
```
Subject: [ClauseBot] Monitor Down - API Health

Monitor: ClauseBot API Health
Status: DOWN
Duration: 10 minutes
URL: https://clausebot-api.onrender.com/health
Error: 503 Service Unavailable
Time: 2025-11-02 10:15:00 PT

View Incident: [UptimeRobot Link]
```

---

### SMS Notifications (Tier 2)

**When to Send:**
- Monitor down for 15+ minutes (3 consecutive failures)
- Critical system down
- Escalation from Tier 1 if no response

**SMS Format:**
```
ClauseBot ALERT: API Health DOWN 15min
Check: https://uptimerobot.com/dashboard
```

---

## 🛠️ MAINTENANCE WINDOWS

### Scheduled Maintenance

**When maintenance is planned:**
1. Pause monitors in UptimeRobot (prevent false alerts)
2. Duration: Typically 30-60 minutes
3. Re-enable monitors after maintenance completes
4. Verify all monitors green before closing

**How to Pause:**
1. UptimeRobot Dashboard → Monitors
2. Select monitor(s)
3. Click "Pause" → Set duration
4. Add note: "Scheduled maintenance - [description]"

---

### Emergency Maintenance

**For urgent fixes:**
1. SMS notification to acknowledge alert
2. Pause monitors if needed
3. Execute fix/rollback
4. Verify manually before resuming monitors
5. Document in incident log

---

## 📝 INCIDENT DOCUMENTATION

### Incident Template

**File:** `docs/incidents/YYYY-MM-DD-incident-name.md`

```markdown
# Incident: [Short Description]

**Date:** YYYY-MM-DD  
**Duration:** XX minutes  
**Severity:** Critical/High/Medium/Low

## Summary
[Brief description of what happened]

## Timeline
- HH:MM - Initial alert received
- HH:MM - Investigation started
- HH:MM - Root cause identified
- HH:MM - Fix applied
- HH:MM - Service restored

## Root Cause
[Technical explanation]

## Impact
- Affected Services: [List]
- Users Impacted: [Estimated number or "All"]
- Data Loss: [Yes/No - details]

## Resolution
[What fixed it]

## Prevention
[What we'll do to prevent recurrence]

## Action Items
- [ ] Update monitoring alerts
- [ ] Add CI check
- [ ] Documentation update
- [ ] Postmortem review
```

---

## 🔄 FUTURE ENHANCEMENTS

### Q1 2026: Better Stack Migration

**Why Better Stack:**
- Real User Monitoring (RUM)
- Public status page
- Response time percentiles (p50, p95, p99)
- Team collaboration features
- Advanced analytics

**Migration Plan:**
1. Export 90 days of historical data from UptimeRobot
2. Set up Better Stack account (paid tier)
3. Configure identical monitors
4. Run both systems in parallel for 7 days
5. Cut over to Better Stack
6. Keep UptimeRobot as backup for 30 days

---

### Advanced Monitoring (Future)

**Synthetic Monitoring:**
- User journey testing (login → quiz → results)
- Multi-step transaction monitoring
- Geographic performance testing

**APM Integration:**
- Backend performance tracing
- Database query monitoring
- API endpoint latency tracking

**Error Tracking:**
- Sentry for frontend errors
- Backend exception tracking
- User impact correlation

---

## 🎯 SUCCESS METRICS

### Current State (Post-Setup)

- ✅ 4 monitors configured and green
- ✅ Tiered alerting (email + SMS)
- ✅ 5-minute check intervals
- ✅ SSL certificate monitoring

### Target State (30 Days)

- ✅ 99.9% uptime achieved
- ✅ <30 min MTTR for incidents
- ✅ Zero false positive alerts
- ✅ Complete incident documentation

---

## 📞 ESCALATION CONTACTS

### Technical Support

**Platform Issues:**
- Render Support: support@render.com
- Vercel Support: support@vercel.com
- Airtable Support: support@airtable.com

**Internal Escalation:**
- Primary: [REDACTED]
- Secondary: [REDACTED]

---

## 📚 RELATED DOCUMENTATION

**Deployment & Operations:**
- `docs/DEPLOY_VERIFY_ROLLBACK.md` - Deployment runbook
- `RENDER_TROUBLESHOOTING.md` - Render-specific issues
- `VERCEL_DEPLOYMENT_GUIDE.md` - Vercel configuration

**Architecture:**
- `MIGRATION_SUCCESS_REPORT.md` - System architecture
- `FINAL_LOCKDOWN_COMPLETE.md` - Security & compliance

**Incidents:**
- `docs/incidents/` - Historical incident reports

---

**Last Updated:** October 25, 2025  
**Next Review:** January 1, 2026  
**Owner:** MiltmonNDT DevOps  
**Status:** ✅ Ready for November 2, 2025 setup

