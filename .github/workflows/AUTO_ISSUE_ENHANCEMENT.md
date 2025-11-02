# Auto-Issue Enhancement for Golden Validation

**Purpose:** Automatically create GitHub issues when golden validation fails  
**Status:** Optional - Add after 2-4 weeks of stable operations (pass rate >90%)  
**Why Wait:** Prevents alert fatigue during initial tuning period

---

## When to Enable This

✅ **Enable when:**
- Golden validation pass rate >90% consistently for 2 weeks
- Failure patterns are well understood
- Team comfortable triaging from existing checklist
- False positive rate <10%

❌ **Don't enable if:**
- Still tuning similarity thresholds
- Pass rate fluctuating week-to-week
- Team needs manual review first

---

## Installation

Add this step to `.github/workflows/golden-validation.yml` **after** the artifact upload step:

```yaml
      - name: Create GitHub Issue on validation failure
        if: failure() && steps.run_smoke.outputs.smoke_status == 'failed'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            
            // Find latest report
            const reportFiles = fs.readdirSync('clausebot/ops/reports')
              .filter(f => f.startsWith('golden-report-') && f.endsWith('.json'))
              .sort()
              .reverse();
            
            if (reportFiles.length === 0) {
              console.log('No report found, skipping issue creation');
              return;
            }
            
            const reportPath = `clausebot/ops/reports/${reportFiles[0]}`;
            const report = JSON.parse(fs.readFileSync(reportPath, 'utf8'));
            const summary = report.summary || {};
            
            // Extract failure details
            const failedTests = (report.results || [])
              .filter(r => !r.passed)
              .slice(0, 5); // Show top 5 failures
            
            // Build issue body
            let body = `## 🔴 Golden Dataset Validation Failed\n\n`;
            body += `**Pass Rate:** ${(summary.pass_rate * 100).toFixed(1)}% (threshold: 90%)\n`;
            body += `**Total Tests:** ${summary.total_tests}\n`;
            body += `**Passed:** ${summary.passed}\n`;
            body += `**Failed:** ${summary.failed}\n`;
            body += `**Average Latency:** ${summary.avg_latency_ms?.toFixed(0)}ms\n\n`;
            
            body += `### Top Failures\n\n`;
            failedTests.forEach((test, idx) => {
              body += `#### ${idx + 1}. ${test.id} - ${test.query}\n`;
              body += `- **Expected:** ${JSON.stringify(test.expected_clauses)}\n`;
              body += `- **Got (top-5):** ${JSON.stringify(test.actual_topk)}\n`;
              body += `- **Reason:** ${test.reason}\n`;
              body += `- **Similarity:** ${test.best_similarity?.toFixed(2) || 'N/A'}\n\n`;
            });
            
            body += `### Triage Steps\n\n`;
            body += `1. Download artifact: [golden-validation-reports](${context.payload.repository.html_url}/actions/runs/${context.runId})\n`;
            body += `2. Review full CSV for patterns\n`;
            body += `3. Follow [Failure Checklist](.github/workflows/GOLDEN_FAILURE_CHECKLIST.md)\n`;
            body += `4. Check if ingestion ran recently\n`;
            body += `5. Verify similarity thresholds in golden.json\n\n`;
            
            body += `### Quick Diagnostics\n\n`;
            body += `\`\`\`bash\n`;
            body += `# Check Supabase ingestion\n`;
            body += `SELECT count(*) FROM clause_embeddings;\n\n`;
            body += `# Re-run failed test locally\n`;
            body += `python ops/golden-validate.py --golden ops/golden_dataset/golden.json --verbose\n`;
            body += `\`\`\`\n\n`;
            
            body += `**Workflow Run:** ${context.payload.repository.html_url}/actions/runs/${context.runId}\n`;
            body += `**Commit:** ${context.sha.substring(0, 7)}\n`;
            body += `**Timestamp:** ${new Date().toISOString()}\n`;
            
            // Create the issue
            const issue = await github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: `[Golden Validation] Pass rate ${(summary.pass_rate * 100).toFixed(1)}% below threshold`,
              body: body,
              labels: ['rag-validation', 'automated', 'needs-triage'],
              assignees: [] // Add default assignees if desired: ['@rag-lead']
            });
            
            console.log(`Created issue #${issue.data.number}`);
```

---

## Configuration

### Required GitHub Permissions

Add to workflow file (top level):
```yaml
permissions:
  contents: read
  issues: write  # Required for issue creation
```

---

**Ready to enable after RAG stabilizes!** 🚀

