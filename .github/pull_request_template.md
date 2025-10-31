# 🧠 Agent Memory Feature PR

## ✅ Pre-merge Checklist
- [ ] Migrations applied on staging
- [ ] `CI_DATABASE_URL` and service role secrets configured
- [ ] `AGENT_MEMORY_ENABLED` feature flag present (default: `false`)
- [ ] CI tests passing (beads-integration job)
- [ ] Monitoring alerts configured for `/agent/memory/*`
- [ ] Staging smoke test completed: `.\test_beads_integration.ps1 -BaseUrl <staging-url>`

## Summary
Brief description of changes and impact.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass (test_beads_integration.ps1)
- [ ] Manual testing completed on staging

## Deployment Notes
- [ ] Feature flag controlled: `AGENT_MEMORY_ENABLED=false` by default
- [ ] Database migrations included (if applicable)
- [ ] Environment variables documented
- [ ] Rollback plan documented

## Monitoring & Alerts
- [ ] Error rate alerts configured for new endpoints
- [ ] Performance monitoring in place
- [ ] Audit trail validation completed

## Rollback Plan
If issues arise:
1. Set `AGENT_MEMORY_ENABLED=false` in production config
2. If code rollback needed: `git revert <merge-commit>`
3. Monitor audit logs for investigation

## Reviewers
- [ ] @backend-lead
- [ ] @devops  
- [ ] @qa

## Additional Notes
Any additional context, dependencies, or special considerations.
