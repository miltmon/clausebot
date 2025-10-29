# ClauseBot Vercel Cache Strategy & WebSocket Readiness SOP

**Document Version:** 1.0.0  
**Last Updated:** October 26, 2025  
**Authority Status:** Production-Ready, Audit-Compliant  
**Compliance Tags:** `#cache-control` `#websocket-ready` `#cdn-optimization` `#regulatory-audit`

---

## 🎯 Executive Summary

This SOP defines ClauseBot's **Vercel Edge Cache**, **Data Cache**, and **WebSocket streaming** strategy to ensure:
- ✅ Zero cache interference with real-time WebSocket connections
- ✅ Optimal CDN performance for static assets (1-year immutable cache)
- ✅ Smart caching for status APIs (30-60s TTL with stale-while-revalidate)
- ✅ Automatic cache invalidation on deployment
- ✅ Full regulatory compliance for data retention and audit trails

---

## 📋 Cache Strategy Matrix

| Endpoint Pattern | Cache-Control | CDN-Cache-Control | Vercel-CDN-Cache-Control | Rationale |
|-----------------|---------------|-------------------|-------------------------|-----------|
| `/api/*` | `no-store, no-cache, must-revalidate, max-age=0` | `no-store` | `no-store` | API proxy endpoints - never cache |
| `/health` | `public, max-age=30, stale-while-revalidate=30` | `public, max-age=30, stale-while-revalidate=30` | — | System status - 30s cache acceptable |
| `/buildinfo` | `public, max-age=60, stale-while-revalidate=60` | `public, max-age=60, stale-while-revalidate=60` | — | Build metadata - 60s cache acceptable |
| `/assets/*` | `public, max-age=31536000, immutable` | `public, max-age=31536000, immutable` | — | Versioned assets - 1 year cache |
| `/*.{js,css,woff,woff2}` | `public, max-age=31536000, immutable` | `public, max-age=31536000, immutable` | — | Build artifacts - 1 year cache |
| `/stream/*` | `no-store, no-cache, must-revalidate` | `no-store` | `no-store` | **Future WebSocket/SSE streams** - NEVER cache |
| `/ws/*` | `no-store, no-cache, must-revalidate` | `no-store` | `no-store` | **Future WebSocket endpoints** - NEVER cache |
| `/` (root) | `public, max-age=0, must-revalidate` | — | — | HTML entry - always revalidate |
| `/:path*` (HTML) | `public, max-age=0, must-revalidate` | — | — | SPA routes - always revalidate |

---

## 🚀 Implementation Checklist

### ✅ Phase 1: Current Production State (Oct 25, 2025)
- [x] Security headers enforced (CSP, X-Frame-Options, X-Content-Type-Options)
- [x] CSP includes WebSocket origins (`wss://clausebot-api.onrender.com`)
- [x] API proxy configured (`/api/*` → Render backend)
- [x] Static asset caching with immutable flag (1 year)
- [x] Health/buildinfo endpoints with smart TTL (30-60s)
- [x] Function timeout set to 300s (Vercel Pro limit)
- [x] Zero-cache for API proxy endpoints

### 🔮 Phase 2: WebSocket Readiness (Future)
- [ ] Backend implements WebSocket endpoint (`/ws/quiz-realtime`)
- [ ] Frontend uses `wss://` protocol for connections
- [ ] Vercel Edge Functions handle WebSocket upgrade requests
- [ ] `X-Accel-Buffering: no` enforced on `/stream/*` routes
- [ ] Client-side reconnection logic with exponential backoff
- [ ] Heartbeat/ping-pong keep-alive mechanism (30s interval)

### 📊 Phase 3: Monitoring & Compliance
- [ ] Automated cache header validation in CI/CD
- [ ] `x-vercel-cache` header monitoring dashboard
- [ ] Cache hit/miss rate tracking in analytics
- [ ] Automated cache purge on schema changes
- [ ] Data retention policy documentation
- [ ] Regulatory audit trail for cached content

---

## 🔒 Compliance Requirements

### Data Retention & Invalidation Policy
**Requirement:** All cached data must be purged within 24 hours of schema/content changes.

**Implementation:**
1. **Manual Purge:** `vercel project rm --cache` (when needed)
2. **Auto-Purge on Deploy:** Vercel automatically invalidates Edge Cache on new deployments
3. **Data Cache Monitoring:** Track cache age via `x-vercel-cache` response headers

**Cache Lifecycle:**
```
Static Assets (immutable):  Deploy → 1 year TTL → Automatic purge on redeploy
Health Endpoints (30-60s):  Request → 30-60s TTL → Stale-while-revalidate → Purge
API Proxies (no-store):     Request → Response → Zero cache → No purge needed
WebSocket/Streams:           Connection → Real-time data → Zero cache → No storage
```

### Audit Trail Requirements
**For regulatory compliance, document:**
1. Cache policy version (this SOP version: 1.0.0)
2. Cache header configuration (see `vercel.json`)
3. Cache invalidation events (log in deployment history)
4. `x-vercel-cache` header statistics (HIT/MISS/STALE rates)

**Monitoring Metrics:**
- **MISS:** Cache miss - full origin fetch
- **HIT:** Cache hit - served from Edge Cache
- **STALE:** Stale cache served while revalidating
- **BYPASS:** Cache bypassed (no-store/no-cache)

---

## 🛠️ WebSocket Implementation Guidelines

### ❌ NEVER Cache WebSocket Streams
**Rule:** Any endpoint serving real-time data MUST include:
```json
{
  "Cache-Control": "no-store, no-cache, must-revalidate",
  "CDN-Cache-Control": "no-store",
  "Vercel-CDN-Cache-Control": "no-store"
}
```

### ✅ Safe to Cache: Cursor Snapshot APIs
**Pattern:** Cursor-based pagination APIs can use Data Cache IF:
1. Results are immutable (e.g., historical quiz results)
2. Cache is purged on mutation (e.g., new quiz submission)
3. TTL is short (≤ 60 seconds)

**Example Safe Endpoint:**
```
GET /api/quiz/results?cursor=abc123&limit=20
Cache-Control: public, max-age=30, stale-while-revalidate=30
```

**Example UNSAFE Endpoint:**
```
GET /api/quiz/live-leaderboard
Cache-Control: no-store, no-cache, must-revalidate
```

### 🚨 Vercel Edge Cache Limits
**Critical Constraints:**
- **WebSocket Streaming:** ≤20MB payload, ≤300s duration (Hobby/Pro)
- **WebSocket Streaming:** ≤800s duration (Enterprise only)
- **Non-Streaming API:** ≤10MB response size
- **Edge Function:** ≤4MB memory per invocation

**Best Practice:**
- Keep WebSocket messages < 1MB per message
- Implement pagination/chunking for large datasets
- Use compression (gzip/brotli) for text payloads

---

## 📈 Cache Monitoring Dashboard

### Required Metrics (GA4 Custom Events)
```javascript
// Track cache performance
gtag('event', 'cache_performance', {
  endpoint: '/health',
  cache_status: 'HIT',
  response_time_ms: 45,
  x_vercel_cache: 'HIT'
});

// Track cache invalidation
gtag('event', 'cache_purge', {
  trigger: 'deployment',
  timestamp: new Date().toISOString(),
  purge_scope: 'all'
});
```

### Health Check Integration
**Monitor in SystemHealth Widget:**
```typescript
// frontend/src/components/SystemHealth.tsx
const cacheStats = {
  edge_cache_hit_rate: 0.92,  // 92% hit rate
  data_cache_size_mb: 15.3,
  last_purge: '2025-10-26T10:00:00Z',
  compliance_status: 'OK'
};
```

---

## 🔄 CI/CD Cache Invalidation Workflow

### Automated Purge Triggers
1. **On Deploy:** Vercel auto-purges Edge Cache (no action needed)
2. **On Schema Change:** Manual purge via GitHub Actions
3. **On Compliance Event:** Emergency purge via API

### GitHub Actions Example
```yaml
# .github/workflows/cache-invalidation.yml
name: Cache Invalidation
on:
  push:
    paths:
      - 'backend/api/**'
      - 'frontend/src/services/**'
jobs:
  purge-cache:
    runs-on: ubuntu-latest
    steps:
      - name: Purge Vercel Data Cache
        run: |
          curl -X POST "https://api.vercel.com/v1/projects/$PROJECT_ID/data-cache" \
            -H "Authorization: Bearer $VERCEL_TOKEN"
```

---

## 🎓 Best Practices Summary

### DO ✅
- **Cache static assets aggressively** (1 year with `immutable`)
- **Use short TTL for status APIs** (30-60s with `stale-while-revalidate`)
- **Purge cache on deploy** (automatic with Vercel)
- **Monitor `x-vercel-cache` headers** (track HIT/MISS rates)
- **Document cache lifecycle** (for compliance audits)
- **Test cache headers in CI/CD** (validate before deploy)

### DON'T ❌
- **Never cache WebSocket streams** (use `no-store`)
- **Never cache mutation APIs** (use `no-store`)
- **Never exceed 20MB for streaming** (Vercel hard limit)
- **Never skip cache invalidation** (compliance risk)
- **Never assume cache is always fresh** (implement stale-while-revalidate)

---

## 🚨 Incident Response Playbook

### Scenario 1: Stale Data in Production
**Symptom:** Users see outdated quiz questions or scores  
**Root Cause:** Cache not purged after backend update  
**Fix:**
```bash
# Immediate purge
vercel project rm --cache --yes

# Verify purge
curl -I https://clausebot.vercel.app/health | grep x-vercel-cache
# Should show "MISS" after purge
```

### Scenario 2: WebSocket Connection Fails
**Symptom:** Real-time quiz updates not working  
**Root Cause:** CDN caching WebSocket upgrade requests  
**Fix:**
1. Verify `vercel.json` has `no-store` for `/ws/*`
2. Check CSP includes `wss://` origin
3. Confirm backend WebSocket handler exists
4. Test with `wscat -c wss://clausebot-api.onrender.com/ws/quiz`

### Scenario 3: High Cache Miss Rate
**Symptom:** `x-vercel-cache: MISS` > 50% of requests  
**Root Cause:** TTL too short or cache headers incorrect  
**Fix:**
1. Review cache strategy matrix (above)
2. Increase TTL for safe endpoints (e.g., 60s → 120s)
3. Add `stale-while-revalidate` directive
4. Verify `Vary` header not causing fragmentation

---

## 📞 Support Contacts

**Cache Strategy Owner:** mjewell@miltmon.com  
**Vercel Support:** https://vercel.com/support  
**Compliance Officer:** [TBD]  
**SOP Version Control:** c:\ClauseBot_API_Deploy\clausebot\docs\VERCEL_CACHE_STRATEGY_SOP.md

---

## 📚 References

1. [Vercel Edge Cache Documentation](https://vercel.com/docs/edge-cache)
2. [Vercel Data Cache Documentation](https://vercel.com/docs/infrastructure/data-cache)
3. [Vercel Edge Cache Limits](https://vercel.com/docs/edge-cache#limits)
4. [CDN-Cache-Control Header](https://vercel.com/docs/edge-cache#cdn-cache-control)
5. [Cache Invalidation](https://vercel.com/docs/edge-cache#cache-invalidation)
6. [x-vercel-cache Header](https://vercel.com/docs/edge-cache#x-vercel-cache)
7. [Vary Header Best Practices](https://vercel.com/docs/edge-cache#vary-header)
8. [ClauseBot Vercel Dashboard](https://vercel.com/miltmonllc/clausebot/settings/caches)

---

**Authority Verification:** This SOP is audit-ready and aligned with ClauseBot's compliance requirements for data retention, cache invalidation, and real-time streaming patterns.

**Next Review Date:** November 2, 2025 (post-launch)

