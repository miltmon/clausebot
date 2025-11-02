# Repo Audit Quick Commands

## Trigger Workflow
```bash
gh workflow run "Repo Audit (Org-Wide)" --repo miltmon/clausebot
```

## Check Recent Runs
```bash
gh run list --repo miltmon/clausebot --workflow="Repo Audit (Org-Wide)" --limit 5
```

## Download Latest Artifact
```bash
# Get the run ID from above, then:
gh run download <RUN_ID> --repo miltmon/clausebot -n repo-audit-<RUN_ID>
unzip repo-audit-<RUN_ID>.zip -d ./audit_results
jq . ./audit_results/repo-audit-*.json
```

## Add Secrets
```bash
# Add PAT (interactive prompt)
echo "<YOUR_PAT>" | gh secret set ORG_GITHUB_TOKEN --repo miltmon/clausebot

# Add optional secrets
gh secret set SUPABASE_URL --repo miltmon/clausebot --body "https://hqhughgdraokwmreronk.supabase.co"
echo "<AIRTABLE_KEY>" | gh secret set AIRTABLE_API_KEY --repo miltmon/clausebot
```

## Quick Analysis
```bash
# External services status
jq '.external_services' ./audit_results/repo-audit-*.json

# Count repos scanned
jq '.repos | length' ./audit_results/repo-audit-*.json

# Find failing workflows
jq -r '.repos | to_entries[] | select(.value.latest_workflow_run.workflow_runs[0].conclusion == "failure") | .key' ./audit_results/repo-audit-*.json
```
