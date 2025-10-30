# ClauseBot Platform Independence Policy

## 🔒 Hard Rule: System Independence

ClauseBot and miltmonndt.com operate as **fully independent platforms**:

- Separate repos, build pipelines, deploy targets, environments, secrets, and data sources
- No implicit fallbacks or hidden cross-calls
- If an integration is ever needed, it must be explicit, versioned, and fully logged

## 📋 Scope

### APIs
- **ClauseBot API base:** `https://clausebot-api.onrender.com`
- **miltmonndt.com API base:** (its own service or none)

### Secrets
- Distinct PATs/keys; never shared across projects

### Data
- Distinct Airtable bases/tables/views; no cross-base reads

### CORS
- Each service only allows its own frontends

### Observability
- Each service logs to its own sink with distinct request IDs

### Rollbacks
- Independent rollback plans; one service never blocks the other

## ❌ No-Go Examples

- ❌ miltmonndt.com calling ClauseBot for content without an approved, logged integration
- ❌ Shared `.env` files or Render/Vercel env pages reused between services
- ❌ "If ClauseBot fails, use miltmonndt.com data" (or vice versa)

## ✅ Independence Verification Checklist

### 1) Repos & CI
- [ ] Different GitHub repos or at minimum separate folders and workflows
- [ ] GitHub Actions: distinct pipelines (namespaces, badges, secrets)
- [ ] Branch protection: each repo protects main independently

### 2) Deploy Targets
- [ ] Render: ClauseBot service exists with unique start command & env
- [ ] Vercel: miltmonndt.com project is separate; no shared envs or build hooks
- [ ] Webhooks: Render and Vercel each watch their repo only

### 3) Secrets & Config
- [ ] ClauseBot PAT (`AIRTABLE_API_KEY`) exists only in ClauseBot service
- [ ] miltmonndt.com secrets live only in its service (or none if static)
- [ ] No secret appears in code, commit history, or other project's env page

### 4) Data Sources
- [ ] Airtable base IDs differ (or at minimum, different tables/views)
- [ ] ClauseBot can be disabled (flip env) without affecting miltmonndt.com
- [ ] Inventory checks pass independently (ClauseBot `/health/airtable` → connected)

### 5) Networking & CORS
- [ ] ClauseBot CORS allows only its frontends
- [ ] miltmonndt.com does not call ClauseBot unless explicit integration documented
- [ ] No wildcard origins in prod (avoid `*`)

### 6) Logging & Monitoring
- [ ] Each service emits unique x-request-id and logs own category, status, and errors
- [ ] 422/503 alerting configured independently (if alerting)
- [ ] Log sampling and PII policies documented per service

### 7) Rollback & DR
- [ ] Independent rollback commands (previous deploy/version) verified
- [ ] A failure in one service does not degrade the other's SLA
- [ ] "Maintenance mode" banners are separate and don't reference the other service

## 🧪 Daily Smoke Tests

### ClauseBot
```bash
GET https://clausebot-api.onrender.com/health → {"ok":true,...}
GET https://clausebot-api.onrender.com/health/airtable → "status":"connected"
GET /v1/quiz?count=5&category=Fundamentals → items or 422 with clear message
```

### miltmonndt.com
- Load site, run its own features
- No network calls to ClauseBot unless documented

## 🛠️ Utility Verification Scripts

### Spot Accidental CORS Wildcards
```powershell
$uri = 'https://clausebot-api.onrender.com/health'
$r = Invoke-WebRequest $uri -ErrorAction Stop
"OK from ClauseBot health: $($r.StatusCode)"
# Verify env on Render manually; ensure CORS_ALLOW_ORIGINS does not contain '*'
```

### Prove Airtable Base Uniqueness
```powershell
$base = $env:AIRTABLE_BASE_ID
$table = $env:AIRTABLE_TABLE
$pat = $env:AIRTABLE_API_KEY
$u = "https://api.airtable.com/v0/$base/$([uri]::EscapeDataString($table))?maxRecords=1"
Invoke-WebRequest -Uri $u -Headers @{Authorization="Bearer $pat"} | Out-Null
"ClauseBot Airtable reachable ✅"
```

## 🧭 Governance

### Design Reviews
- Must include "Independence Check" as a required question

### PR Template
- Includes checkbox: "Does this add any cross-service coupling?" (default: No)

### Quarterly Audit
- Run the full checklist
- Save receipts (screenshots, links, commit hashes)

---

## 🎯 Benefits of Independence

- **Fault isolation:** One service failure doesn't cascade
- **Security boundaries:** Secrets and data remain compartmentalized
- **Deployment flexibility:** Independent release cycles and rollback strategies
- **Clear ownership:** No ambiguity about service responsibilities
- **Scalability:** Each service can scale independently based on demand

---

*This policy ensures ClauseBot operates as enterprise-grade software with clear boundaries and observable operations.*
