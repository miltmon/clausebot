# ClauseBot Rollout Readiness Checklist
_Last updated: 2025-08-25 (PDT)_

## Infrastructure
- [ ] Hosted endpoint live (no local install)
- [ ] Authentication, rate-limiting, and request logging enabled
- [ ] API routes: `/ask`, `/health`, `/feedback` functional
- [ ] Monitoring/alerts configured

## Accuracy
- [ ] Evaluation set (150–200 prompts) assembled
- [ ] SME reviewer assigned
- [ ] Weekly scorecard cadence established
- [ ] ≥ **85%** top-1 clause reference accuracy on eval set

## Performance
- [ ] **p95 latency ≤ 1.0s** (common queries)
- [ ] **≥99.5%** monthly uptime

## Compliance & Safety
- [ ] Returns **citations + summaries** only (no verbatim code text)
- [ ] Full audit trail (inputs, outputs, citations, timestamps)
- [ ] Disclaimers visible (“Check with your code / governing standard”)
- [ ] Escalation path to SME documented

## Operational Readiness
- [ ] Admin console with basic analytics
- [ ] Security review completed
- [ ] Red-team prompt suite passed
- [ ] Incident runbooks + support SOPs finalized
- [ ] Pilot customer sign-off captured

## Marketing & Communications
- [ ] “Preview/Prototype” labels applied across Tracks + Programs
- [ ] GA4 tracking configured
- [ ] Public messaging flip checklist prepared

### Go/No-Go
- [ ] All gates above checked ✅ (Required before public announcement)
