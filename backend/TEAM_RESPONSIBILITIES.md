# ClauseBot RAG - Team Responsibilities & Escalation

**Last Updated:** 2025-11-02  
**Version:** 1.0  
**Purpose:** Define ownership, escalation paths, and contact methods for ClauseBot RAG operations

---

## Component Ownership Matrix

| Component | Primary Owner | Backup | Slack Channel | Response SLA | Notes |
|-----------|---------------|--------|---------------|--------------|-------|
| **RAG Endpoint** (`/v1/chat/compliance`) | `@rag-lead` | `@backend-engineer` | `#rag-team` | 2 hours | Includes embedding, retrieval, generation pipeline |
| **Supabase Database** (`clause_embeddings`, `chat_citations`) | `@platform-lead` | `@sre-oncall` | `#ops-platform` | 1 hour | Database infrastructure, connectivity, performance |
| **OpenAI Integration** (embeddings + LLM) | `@rag-lead` | `@backend-engineer` | `#rag-team` | 2 hours | API keys, rate limits, cost management |
| **Data Ingestion** (`ingest_aws_d11.py`) | `@content-engineer` | `@rag-lead` | `#data-ops` | 1 day | Clause chunking, embedding generation, quality |
| **CI/CD Workflows** (smoke + golden validation) | `@devops-lead` | `@sre-oncall` | `#ops-ci` | 4 hours | GitHub Actions, artifact management |
| **Golden Dataset** (`golden.json`) | `@qa-lead` | `@curriculum-owner` | `#qa-validation` | 1 week | Test curation, expected clause maintenance |
| **Render Deployment** | `@platform-lead` | `@sre-oncall` | `#ops-platform` | 1 hour | Service config, env vars, deployments |
| **Frontend Integration** (Vercel) | `@frontend-lead` | `@fullstack-engineer` | `#frontend-team` | 4 hours | API client, citation UI, error handling |

---

## Escalation Paths

### 🔴 **CRITICAL (P0) - Production Down**

**Severity:** P0 - System Unavailable  
**Examples:**
- All API endpoints returning 5xx
- Supabase completely unreachable
- OpenAI API key compromised/leaked
- Data breach or security incident

**Action:**
1. **Immediately page:** `@oncall-sre` via PagerDuty
2. **Notify:** `#incident-response` channel
3. **Escalate to:** VP Engineering if no response in 15 minutes

**Response SLA:** 30 minutes  
**Resolution SLA:** 4 hours

**Contacts:**
- PagerDuty: [Insert PagerDuty rotation link]
- Emergency: [Insert emergency phone number]
- Security: security@company.com

---

### 🟠 **HIGH (P1) - Feature Degraded**

**Severity:** P1 - Core Feature Impaired  
**Examples:**
- RAG endpoint returning 503 (feature flag issue)
- Golden validation pass rate <50%
- Ingestion pipeline failed completely
- OpenAI rate limit exceeded causing widespread failures

**Action:**
1. **Notify:** `@rag-lead` + `@platform-lead` in `#rag-team`
2. **Create:** GitHub issue with `priority:high` label
3. **Escalate to:** `@oncall-sre` if no response in 1 hour

**Response SLA:** 2 hours  
**Resolution SLA:** Same business day

**Runbooks:**
- Deployment: `clausebot/backend/DEPLOYMENT_RUNBOOK_CURSOR.md`
- Rollback: `clausebot/ops/rollback-playbook.md`

---

### 🟡 **MEDIUM (P2) - Quality Issue**

**Severity:** P2 - Degraded Quality  
**Examples:**
- Golden validation pass rate 50-80%
- RAG response latency >5 seconds
- Citation accuracy concerns from user feedback
- Retrieval returning wrong clauses consistently

**Action:**
1. **Create:** GitHub issue with `priority:medium` label
2. **Notify:** `@rag-team` in `#rag-team` Slack
3. **Schedule:** Review in next daily standup

**Response SLA:** Next business day  
**Resolution SLA:** 1 week

**Diagnostic Playbook:** `.github/workflows/GOLDEN_FAILURE_CHECKLIST.md`

---

### 🟢 **LOW (P3) - Enhancement/Optimization**

**Severity:** P3 - Improvement Opportunity  
**Examples:**
- Golden dataset expansion requests
- Similarity threshold tuning
- Documentation updates
- Performance optimizations

**Action:**
1. **Create:** GitHub issue with `priority:low` label
2. **Tag:** Appropriate owner in issue description
3. **Review:** During sprint planning

**Response SLA:** Sprint planning cycle  
**Resolution SLA:** As capacity permits

---

## On-Call Rotation

### Current On-Call Schedule
- **Platform/SRE:** [Insert PagerDuty schedule link]
- **Backend Engineering:** [Insert rotation schedule]
- **RAG/ML:** Monday-Friday business hours, escalate to platform after hours

### On-Call Responsibilities
- Respond to pages within SLA
- Triage incidents using appropriate runbooks
- Escalate if issue is outside expertise
- Document incident in post-mortem template

---

## Contact Directory

### Primary Contacts

| Role | Name | Slack Handle | Email | PagerDuty | Notes |
|------|------|--------------|-------|-----------|-------|
| **SRE Lead** | [Name] | `@sre-lead` | sre-lead@company.com | Yes | Platform infrastructure owner |
| **Backend Lead** | [Name] | `@backend-lead` | backend-lead@company.com | No | RAG service architecture |
| **RAG/ML Lead** | [Name] | `@rag-lead` | ml-lead@company.com | No | Embedding, retrieval, prompts |
| **QA Lead** | [Name] | `@qa-lead` | qa-lead@company.com | No | Golden dataset, test validation |
| **DevOps Lead** | [Name] | `@devops-lead` | devops-lead@company.com | Yes | CI/CD pipelines |
| **Content Engineer** | [Name] | `@content-eng` | content@company.com | No | AWS D1.1 ingestion, chunking |
| **Security Lead** | [Name] | `@security-lead` | security@company.com | Yes | Key rotation, incident response |

### Team Slack Channels

- **#incident-response** - P0/P1 incidents only
- **#rag-team** - RAG feature development and ops
- **#ops-platform** - Infrastructure and deployment
- **#ops-ci** - CI/CD and automation
- **#qa-validation** - Testing and quality assurance
- **#frontend-team** - Frontend integration

### External Contacts

- **Render Support:** support@render.com (for infrastructure issues)
- **Supabase Support:** [Dashboard support link]
- **OpenAI Support:** https://help.openai.com (for API issues)

---

## Runbook & Documentation Index

### Deployment & Operations
- **Main Deployment Guide:** `clausebot/backend/DEPLOYMENT_RUNBOOK_CURSOR.md`
- **Rollback Playbook:** `clausebot/ops/rollback-playbook.md`
- **Ops Toolkit Guide:** `clausebot/ops/README.md`

### Incident Response
- **Golden Validation Failures:** `.github/workflows/GOLDEN_FAILURE_CHECKLIST.md`
- **CI/CD Workflow Guide:** `.github/workflows/README.md`

### Code & Architecture
- **RAG Service:** `clausebot/backend/clausebot_api/services/rag_service.py`
- **Compliance Router:** `clausebot/backend/clausebot_api/routes/chat_compliance.py`
- **SQL Schema:** `clausebot/backend/sql/supabase_pgvector_rag.sql`

---

## Decision-Making Authority

### Who Can Make What Decisions

| Decision Type | Authority | Approval Required | Notes |
|---------------|-----------|-------------------|-------|
| **Feature Flag Toggle** (RAG_ENABLED) | SRE Lead or Backend Lead | None (but notify #rag-team) | Emergency use only |
| **Rollback Deploy** | SRE Lead or DevOps Lead | None in emergency | Document in post-mortem |
| **Golden Dataset Changes** | QA Lead | Review by RAG Lead | Commit requires approval |
| **Similarity Threshold Tuning** | RAG Lead | None | Monitor impact for 48h |
| **Schema Changes** (SQL) | Backend Lead + Platform Lead | Must test in staging | Requires migration plan |
| **OpenAI Model Change** | RAG Lead | Backend Lead approval | Cost impact assessment required |
| **Rate Limit Changes** | Platform Lead | None | Monitor for 24h |

---

## Post-Incident Process

### After Every P0/P1 Incident

1. **Create Post-Mortem** (within 48 hours)
   - Use template: `docs/incident-postmortem-template.md`
   - Include: timeline, root cause, impact, remediation, action items

2. **Review in Team Retro** (next weekly meeting)
   - Discuss prevention measures
   - Update runbooks if needed
   - Assign action items

3. **Update Documentation**
   - Add to "Known Issues" if recurring
   - Update troubleshooting sections
   - Improve monitoring/alerting

### Post-Mortem Template Location
`docs/incident-postmortem-template.md` (to be created)

---

## Maintenance & Review Schedule

### Weekly
- [ ] Review golden validation pass rates (QA Lead)
- [ ] Check OpenAI usage and costs (RAG Lead)
- [ ] Review failed CI runs (DevOps Lead)

### Monthly
- [ ] Rotate access keys if policy requires (Platform Lead)
- [ ] Review and update golden dataset (QA Lead)
- [ ] Performance analysis and optimization (Backend Lead)

### Quarterly
- [ ] Review and update this TEAM_RESPONSIBILITIES.md
- [ ] Audit access permissions
- [ ] Update contact information
- [ ] Review SLA commitments

---

## Training & Onboarding

### New Team Member Checklist

- [ ] Read `DEPLOYMENT_RUNBOOK_CURSOR.md`
- [ ] Shadow on-call rotation (if applicable)
- [ ] Run golden validation locally
- [ ] Practice rollback procedure in staging
- [ ] Review incident post-mortems from last quarter

### Training Resources
- **RAG Architecture Overview:** [Link to internal wiki]
- **AWS D1.1 Compliance Basics:** [Link to training]
- **Supabase Admin Guide:** [Link to docs]

---

## Amendment History

| Date | Version | Changed By | Description |
|------|---------|------------|-------------|
| 2025-11-02 | 1.0 | Initial | Created initial team responsibilities matrix |

---

**Instructions for Customization:**

1. Replace `[Name]`, `[Insert...]` placeholders with actual team member information
2. Update Slack handles (format: @username)
3. Add actual PagerDuty rotation links
4. Update email addresses to match your organization
5. Adjust SLAs based on your team's capacity and business requirements
6. Add company-specific incident response procedures
7. Link to your actual internal wiki/documentation

**To Update This Document:**
- Create PR with changes
- Get approval from Platform Lead + one affected team lead
- Announce changes in #rag-team and #ops-platform
- Update version number and amendment history

