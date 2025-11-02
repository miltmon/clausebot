# Repo Audit Remediation Templates

## 1) Add Sentry + structured request timing middleware (High Priority)

**Title:** Add Sentry and response-time middleware to detect runtime errors & P95 latency

**Body:**
Why: We lack runtime observability (exceptions, traces, performance). Add Sentry to capture exceptions and implement middleware to record P50/P95/P99 request latencies.

**Tasks:**
- [ ] Add Sentry SDK and initializer (server only). Use DSN from env `SENTRY_DSN`.
- [ ] Add middleware to capture request start/end & log P50/P95 counters to our metrics backend (stdout + Prometheus-friendly labels).
- [ ] Add a small health endpoint `/internal/metrics` or wire to existing metrics exporter.
- [ ] Add test verifying Sentry init load on startup.
- [ ] Add README snippet for how to configure SENTRY_DSN and how to verify an event via Sentry UI.

**Suggested snippet (Python / FastAPI):**
```python
import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
sentry_sdk.init(dsn=os.getenv("SENTRY_DSN"), traces_sample_rate=0.2)
app.add_middleware(SentryAsgiMiddleware)
```

**Acceptance:**
- Sentry receives test exception event when SENTRY_DSN set.
- P95 calculation visible in logs or metrics exporter within staging.

---

## 2) Replace print logging with structured logging (Medium Priority)

**Title:** Migrate to `structlog` (or Python logging structured config) for better observability

**Body:**
Why: Current print logs are hard to aggregate and do not include structured fields (request id, trace id, env).

**Tasks:**
- [ ] Add structlog to requirements.
- [ ] Create log_config.py module and initialize in app startup.
- [ ] Replace top-level print statements in key modules (auth, payments, webhooks) with logger.info(..., extra={...}).
- [ ] Add correlation id middleware for request tracing.
- [ ] Update docs: how to read logs in production and filter by request id.

**Acceptance:**
- Logs in staging have JSON entries with level, timestamp, request_id, and path.

---

## 3) Resolve duplicate Airtable libraries + dependency hygiene (Low Priority)

**Title:** Cleanup `requirements.txt` — remove duplicate Airtable wrappers and pin versions

**Body:**
Why: Duplicate or overlapping dependency packages cause bloat and subtle behavioral differences. We should pick one Airtable lib and pin stable versions.

**Tasks:**
- [ ] Identify references to airtable-python-wrapper and pyairtable in codebase.
- [ ] Pick preferred library (recommendation: pyairtable) and update code accordingly.
- [ ] Pin versions in requirements.txt and run pip-compile or update lockfile.
- [ ] Run CI tests and fix any import changes.

**Acceptance:**
- CI passes and only pyairtable==x.y.z (or chosen lib) is present in final requirements.
