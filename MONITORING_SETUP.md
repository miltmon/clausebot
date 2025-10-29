# 🔍 ClauseBot Monitoring Setup Guide

**Complete guide for bulletproof monitoring and observability**

---

## 📋 Overview

This guide covers setting up production monitoring for:
- ✅ **Uptime monitoring** (UptimeRobot)
- ✅ **Log aggregation** (Render Logs / Datadog)
- ✅ **Performance metrics** (Cache hit rates, response times)
- ✅ **Alerting** (Slack, Email, PagerDuty)
- ✅ **Audit trails** (Supabase audit_log)

---

## 🎯 Monitoring Targets

| Component | Metrics | Alert Threshold | Action |
|-----------|---------|-----------------|--------|
| API Health | `/health` status | 5xx errors > 5% | Page on-call |
| Cache | Hit rate | < 60% | Investigate |
| Response Time | p95 latency | > 100ms | Review logs |
| Sync Job | Success rate | < 95% | Check Airtable |
| Backup Job | Success rate | < 100% | Check S3 |

---

## 1️⃣ Uptime Monitoring (UptimeRobot)

### Setup

1. **Go to UptimeRobot:**  
   https://uptimerobot.com (Free plan: 50 monitors, 5-min checks)

2. **Create monitors for:**

   **Monitor 1: API Health**
   ```
   Name: ClauseBot API Health
   Type: HTTP(S)
   URL: https://clausebot-api.onrender.com/health
   Interval: 5 minutes
   Alert when: Keyword (JSON: "ok":true) not found
   ```

   **Monitor 2: Cache Health**
   ```
   Name: ClauseBot Cache Health
   Type: HTTP(S)
   URL: https://clausebot-api.onrender.com/health/cache
   Interval: 5 minutes
   Alert when: Keyword ("ok":true) not found
   ```

   **Monitor 3: Quiz Endpoint**
   ```
   Name: ClauseBot Quiz API
   Type: HTTP(S)
   URL: https://clausebot-api.onrender.com/quiz?count=1
   Interval: 10 minutes
   Alert when: Status code != 200
   ```

   **Monitor 4: Frontend**
   ```
   Name: ClauseBot Frontend
   Type: HTTP(S)
   URL: https://clausebot.vercel.app/
   Interval: 5 minutes
   Alert when: Status code != 200
   ```

3. **Set up alert contacts:**
   - **Email:** Your email address
   - **Slack:** https://my.slack.com/services/new/incoming-webhook
   - **Webhook:** For custom integrations

### Alert Configuration

```yaml
# Alert Thresholds
Down for: 5 minutes
Notify every: 30 minutes (while down)
Notify when: Monitor goes down OR up
```

### API Integration (Optional)

```bash
# Add monitors via UptimeRobot API
curl -X POST "https://api.uptimerobot.com/v2/newMonitor" \
  -d "api_key=YOUR_KEY" \
  -d "friendly_name=ClauseBot API Health" \
  -d "url=https://clausebot-api.onrender.com/health" \
  -d "type=1" \
  -d "interval=300" \
  -d "keyword_type=2" \
  -d "keyword_value=\"ok\":true"
```

---

## 2️⃣ Structured Logging

### Render Native Logs

**View logs:**
```bash
# Via Render Dashboard
https://dashboard.render.com/web/YOUR_SERVICE_ID/logs

# Via Render CLI (if available)
render logs YOUR_SERVICE_ID --tail
```

**Log format (JSON):**
```json
{
  "timestamp": "2025-10-28T15:30:00.123Z",
  "level": "INFO",
  "service": "clausebot-api",
  "message": "Cache hit",
  "request_id": "abc123",
  "context": {"endpoint": "/quiz", "hit_rate": 0.75}
}
```

### Log Aggregation (Datadog)

**Setup:**

1. **Create Datadog account:** https://www.datadoghq.com/

2. **Get API key:** Integrations → APIs → Create API Key

3. **Configure Render log streaming:**
   ```yaml
   # render.yaml (add to services)
   services:
     - type: web
       name: clausebot-api
       # ... other config
       logStreams:
         - type: datadog
           apiKey: ${DATADOG_API_KEY}
           tags:
             - service:clausebot-api
             - env:production
   ```

4. **Set environment variable:**
   - Render Dashboard → Service → Environment
   - Add: `DATADOG_API_KEY` = your_key

**Datadog Dashboards:**
- API Performance: p50/p95/p99 latencies
- Error Rates: 4xx/5xx by endpoint
- Cache Metrics: Hit rate, misses, TTL
- Custom Metrics: Quiz completions, sync success

---

## 3️⃣ Performance Monitoring

### Cache Metrics Endpoint

**Check cache performance:**
```bash
curl https://clausebot-api.onrender.com/health/cache

# Response:
{
  "ok": true,
  "enabled": true,
  "ttl_seconds": 300,
  "keyspace_hits": 12450,
  "keyspace_misses": 3120,
  "hit_rate": 79.98
}
```

**Alert rules:**
```bash
# Slack webhook alert when hit rate < 70%
if [ $(curl -s https://clausebot-api.onrender.com/health/cache | jq '.hit_rate') -lt 70 ]; then
  curl -X POST YOUR_SLACK_WEBHOOK \
    -d '{"text":"⚠️  Cache hit rate below 70%!"}'
fi
```

### Response Time Monitoring

**Track p95 latencies:**
```python
# In clausebot_api/middleware.py
from clausebot_api.logging_config import api_logger

@app.middleware("http")
async def track_response_time(request, call_next):
    start = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start) * 1000
    
    api_logger.info(
        "Request completed",
        path=request.url.path,
        method=request.method,
        status=response.status_code,
        duration_ms=round(duration_ms, 2)
    )
    
    return response
```

---

## 4️⃣ Alerting Configuration

### Slack Alerts

**Setup Slack webhook:**

1. Go to: https://YOUR_WORKSPACE.slack.com/apps/A0F7XDUAZ-incoming-webhooks
2. Click "Add to Slack"
3. Choose channel: `#clausebot-alerts`
4. Copy Webhook URL
5. Save as `SLACK_WEBHOOK_URL` env var in Render

**Alert script:**
```python
# clausebot_api/alerts.py
import requests
import os

def send_slack_alert(message: str, severity: str = "warning"):
    """Send alert to Slack channel."""
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        print(f"⚠️  Alert (no Slack): {message}")
        return
    
    emoji = {"info": ":information_source:", "warning": ":warning:", "critical": ":rotating_light:"}
    
    payload = {
        "text": f"{emoji.get(severity, ':bell:')} *ClauseBot Alert*",
        "blocks": [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": message}
            }
        ]
    }
    
    requests.post(webhook_url, json=payload)
```

**Usage in code:**
```python
from clausebot_api.alerts import send_slack_alert

# Alert on cache issues
if hit_rate < 70:
    send_slack_alert(
        f"Cache hit rate dropped to {hit_rate:.1f}% (target: >70%)",
        severity="warning"
    )

# Alert on sync failures
if sync_failed:
    send_slack_alert(
        f"Airtable sync failed: {error_message}",
        severity="critical"
    )
```

### Email Alerts

**Configure via UptimeRobot (see Section 1)**

Or use SendGrid/AWS SES:
```python
# clausebot_api/alerts.py
import sendgrid
from sendgrid.helpers.mail import Mail

def send_email_alert(subject: str, body: str):
    sg = sendgrid.SendGridAPIClient(api_key=os.getenv("SENDGRID_API_KEY"))
    message = Mail(
        from_email='alerts@clausebot.com',
        to_emails='admin@example.com',
        subject=subject,
        html_content=body
    )
    sg.send(message)
```

---

## 5️⃣ Audit Trail Monitoring

### Query Recent Failures

```python
# Check for failures in last 24 hours
from clausebot_api.audit import query_audit_log
from datetime import datetime, timedelta

failures = query_audit_log(
    start_date=datetime.utcnow() - timedelta(hours=24),
    limit=100
)

for entry in failures:
    if entry['status'] in ['failure', 'partial']:
        print(f"⚠️  {entry['action']} failed: {entry['details']}")
```

### Compliance Reports

```sql
-- Monthly compliance report (run in Supabase)
SELECT 
    DATE_TRUNC('month', timestamp) AS month,
    action,
    status,
    COUNT(*) AS total,
    COUNT(DISTINCT user_id) AS unique_users,
    SUM(CASE WHEN status = 'failure' THEN 1 ELSE 0 END) AS failures,
    ROUND(
        (SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END)::NUMERIC / COUNT(*)) * 100,
        2
    ) AS success_rate
FROM audit_log
WHERE timestamp >= DATE_TRUNC('month', NOW() - INTERVAL '3 months')
GROUP BY DATE_TRUNC('month', timestamp), action, status
ORDER BY month DESC, total DESC;
```

---

## 6️⃣ Dashboard Setup

### Grafana Dashboard (Optional)

**Metrics to track:**
1. Request Rate (req/sec)
2. Error Rate (% 4xx/5xx)
3. P50/P95/P99 Latency
4. Cache Hit Rate
5. Database Connection Pool
6. Background Job Queue Length

**Example PromQL queries:**
```promql
# Request rate
rate(http_requests_total[5m])

# Error rate
rate(http_requests_total{status=~"5.."}[5m])
/ rate(http_requests_total[5m])

# P95 latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

---

## 7️⃣ Monitoring Checklist

### Daily Checks
- [ ] Review Uptime Robot status (all green)
- [ ] Check cache hit rate (>70%)
- [ ] Review error logs (0 critical errors)
- [ ] Verify backup job ran successfully
- [ ] Verify sync job ran successfully

### Weekly Checks
- [ ] Review performance trends (response times)
- [ ] Check disk usage (backups, logs)
- [ ] Review audit trail for anomalies
- [ ] Test rollback procedure
- [ ] Update runbooks if needed

### Monthly Checks
- [ ] Review SLA metrics (uptime, latency)
- [ ] Generate compliance report
- [ ] Test disaster recovery
- [ ] Rotate secrets
- [ ] Update dependencies

---

## 8️⃣ Alert Runbooks

### Alert: API Health Check Failed

**Severity:** Critical  
**Response Time:** 5 minutes

**Steps:**
1. Check Render Dashboard logs
2. Verify database connectivity
3. Check cache connectivity
4. Review recent deploys
5. If widespread: Execute rollback script
6. If isolated: Restart service

**Command:**
```bash
# Check logs
render logs clausebot-api --tail

# Restart service (if needed)
render restart clausebot-api

# Rollback (if critical)
./scripts/rollback.sh
```

### Alert: Cache Hit Rate < 70%

**Severity:** Warning  
**Response Time:** 30 minutes

**Steps:**
1. Check `/health/cache` endpoint
2. Review cache TTL settings
3. Check for unusual query patterns
4. Consider increasing QUIZ_CACHE_TTL
5. Verify cache storage not full

**Investigation:**
```bash
# Check cache metrics
curl https://clausebot-api.onrender.com/health/cache | jq

# Review logs for cache misses
render logs clausebot-api | grep "Cache miss"
```

### Alert: Sync Job Failed

**Severity:** High  
**Response Time:** 15 minutes

**Steps:**
1. Check cron job logs in Render Dashboard
2. Verify Airtable API token valid
3. Check Supabase connectivity
4. Review error message in logs
5. Manually trigger sync if safe

**Command:**
```bash
# Check cron logs
render logs clausebot-nightly-sync

# Manual trigger (via Render Dashboard)
# Services → clausebot-nightly-sync → Manual Run
```

---

## 9️⃣ Tools & Resources

### Monitoring Tools
- **UptimeRobot:** https://uptimerobot.com (Free tier)
- **Datadog:** https://www.datadoghq.com (APM + Logs)
- **New Relic:** https://newrelic.com (Alternative to Datadog)
- **Sentry:** https://sentry.io (Error tracking)

### Alert Channels
- **Slack:** https://api.slack.com/messaging/webhooks
- **PagerDuty:** https://www.pagerduty.com (On-call rotation)
- **Opsgenie:** https://www.atlassian.com/software/opsgenie

### Dashboard Tools
- **Grafana:** https://grafana.com (Metrics dashboards)
- **Kibana:** https://www.elastic.co/kibana (Log analysis)
- **Render Dashboard:** Native service monitoring

---

## 🎯 Success Metrics

After setup, you should have:
- ✅ **4 monitors** tracking uptime (UptimeRobot)
- ✅ **Slack alerts** configured for critical issues
- ✅ **Structured logging** with JSON output
- ✅ **Cache metrics** tracked in real-time
- ✅ **Audit trail** for compliance
- ✅ **Runbooks** for common alerts
- ✅ **Dashboard** showing key metrics

**SLA Targets:**
- Uptime: 99.9% (< 43 minutes downtime/month)
- P95 Latency: < 100ms (cached), < 1s (uncached)
- Cache Hit Rate: > 70%
- Sync Success Rate: > 99%
- Backup Success Rate: 100%

---

**Last Updated:** October 28, 2025  
**Version:** 1.0.0 (Bulletproof)  
**Status:** Production-Ready

