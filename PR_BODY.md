# chore: add org-wide repo audit script + workflow

## Summary
Adds a read-only repository audit system to the `miltmon/clausebot` monorepo. The system:
- Scans a curated list of org repos for collaborators, webhooks, actions secrets (names), and latest workflow run.
- Probes external services (Supabase, Airtable) for reachability.
- Produces a timestamped JSON artifact (repo_audit_output/repo-audit-<timestamp>.json).
- Runs daily at 06:00 UTC and can be triggered manually.

## Files added
- `scripts/repo_audit.sh` — read-only audit script (curl + jq)
- `.github/workflows/repo-audit.yml` — scheduled/manual GitHub Action (uploads artifacts)

## Required secrets (recommended)
- `ORG_GITHUB_TOKEN` — PAT with `repo` and `admin:repo_hook` scopes (recommended for cross-repo visibility)
- `AIRTABLE_API_KEY` — optional (for authenticated Airtable checks)
- `SUPABASE_URL` — optional override for Supabase health probe

> Note: Without `ORG_GITHUB_TOKEN` the workflow will fall back to `GITHUB_TOKEN` with limited scope.

## How to verify (quick)
1. Trigger manual run from Actions UI or CLI:
   `gh workflow run "Repo Audit (Org-Wide)" --repo miltmon/clausebot` 
2. Inspect run logs:
   `gh run view <RUN_ID> --repo miltmon/clausebot --log` 
3. Download artifact:
   `gh run download <RUN_ID> --repo miltmon/clausebot -n repo-audit-<RUN_ID>` 
4. Open JSON:
   `jq . repo-audit-*.json` 

## Security & operational notes
- This script is read-only and does not modify any repo settings.
- The action retains artifacts for 90 days (adjust via `retention-days` in workflow).
- If you use an org-scoped secret, prefer GitHub Organization Secrets for governance.
- Rotate the PAT after initial verification if you used a temporary token.

## Next steps (post-merge)
- Add `ORG_GITHUB_TOKEN` to repo/org secrets.
- Run the audit, download the artifact, and paste it here (or upload) — I will parse it and generate the prioritized remediation backlog and PR templates automatically.
