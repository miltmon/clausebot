#!/usr/bin/env node
/**
 * CI Compliance Summary Generator
 * 
 * Generates an HTML summary of CI/CD compliance checks, test results,
 * security scans, and performance metrics.
 * 
 * Usage: node scripts/build-ci-summary.js
 * 
 * This script aggregates results from various CI workflows and creates
 * a comprehensive compliance summary that can be uploaded as an artifact.
 */

const fs = require('fs');
const path = require('path');

// Configuration
const config = {
  outputDir: './ci-reports',
  outputFile: 'ci-compliance-summary.html',
  artifacts: {
    semgrep: './semgrep.sarif',
    playwright: './playwright-report',
    lighthouse: './.lighthouseci',
    spectral: './spectral-results.json',
    schemathesis: './schemathesis-report.xml',
    k6: './k6-results.json',
  },
};

// Utility functions
function ensureDirectoryExists(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

function fileExists(filepath) {
  try {
    return fs.existsSync(filepath);
  } catch {
    return false;
  }
}

function readJsonFile(filepath) {
  try {
    const content = fs.readFileSync(filepath, 'utf8');
    return JSON.parse(content);
  } catch (error) {
    console.warn(`Warning: Could not read ${filepath}: ${error.message}`);
    return null;
  }
}

// Summary generators
function generateSemgrepSummary() {
  const semgrepFile = config.artifacts.semgrep;
  if (!fileExists(semgrepFile)) {
    return '<p class="status-warning">⚠️ Semgrep results not found</p>';
  }

  const data = readJsonFile(semgrepFile);
  if (!data || !data.runs) {
    return '<p class="status-warning">⚠️ Semgrep results could not be parsed</p>';
  }

  const results = data.runs[0]?.results || [];
  const errorCount = results.filter(r => r.level === 'error').length;
  const warningCount = results.filter(r => r.level === 'warning').length;

  const status = errorCount === 0 ? 'status-pass' : 'status-fail';
  return `
    <div class="${status}">
      <h3>🔒 Semgrep Security Scan</h3>
      <p>Errors: ${errorCount} | Warnings: ${warningCount}</p>
      <p>Total Issues: ${results.length}</p>
    </div>
  `;
}

function generatePlaywrightSummary() {
  return `
    <div class="status-info">
      <h3>🎭 Playwright E2E Tests</h3>
      <p>Check artifact for detailed test results</p>
    </div>
  `;
}

function generateLighthouseSummary() {
  return `
    <div class="status-info">
      <h3>💡 Lighthouse Performance & Accessibility</h3>
      <p>Check artifact for detailed metrics</p>
    </div>
  `;
}

function generateSpectralSummary() {
  const spectralFile = config.artifacts.spectral;
  if (!fileExists(spectralFile)) {
    return '<p class="status-warning">⚠️ Spectral results not found</p>';
  }

  const data = readJsonFile(spectralFile);
  if (!data) {
    return '<p class="status-warning">⚠️ Spectral results could not be parsed</p>';
  }

  const results = Array.isArray(data) ? data : [];
  const errorCount = results.filter(r => r.severity === 0).length;
  const warningCount = results.filter(r => r.severity === 1).length;

  const status = errorCount === 0 ? 'status-pass' : 'status-fail';
  return `
    <div class="${status}">
      <h3>📋 Spectral API Contract Linting</h3>
      <p>Errors: ${errorCount} | Warnings: ${warningCount}</p>
    </div>
  `;
}

function generateK6Summary() {
  const k6File = config.artifacts.k6;
  if (!fileExists(k6File)) {
    return '<p class="status-warning">⚠️ k6 results not found</p>';
  }

  const data = readJsonFile(k6File);
  if (!data || !data.metrics) {
    return '<p class="status-warning">⚠️ k6 results could not be parsed</p>';
  }

  const metrics = data.metrics;
  const checksPassed = metrics.checks?.values?.passes || 0;
  const checksTotal = metrics.checks?.values?.rate || 1;
  const passRate = ((checksPassed / checksTotal) * 100).toFixed(2);

  const status = passRate >= 90 ? 'status-pass' : 'status-fail';
  return `
    <div class="${status}">
      <h3>⚡ k6 Performance Testing</h3>
      <p>Check Pass Rate: ${passRate}%</p>
      <p>Total Requests: ${metrics.http_reqs?.values?.count || 0}</p>
    </div>
  `;
}

// Main HTML generator
function generateHTML() {
  const timestamp = new Date().toISOString();
  const runId = process.env.GITHUB_RUN_ID || 'local';
  const repo = process.env.GITHUB_REPOSITORY || 'unknown';
  const sha = process.env.GITHUB_SHA?.substring(0, 7) || 'unknown';

  return `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CI Compliance Summary - ${repo}</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
      background: #f5f5f5;
      padding: 20px;
    }
    .container {
      max-width: 1200px;
      margin: 0 auto;
      background: white;
      padding: 30px;
      border-radius: 8px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    h1 { color: #333; margin-bottom: 10px; }
    .meta { color: #666; font-size: 14px; margin-bottom: 30px; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
    .card {
      border: 1px solid #e0e0e0;
      border-radius: 6px;
      padding: 20px;
      background: #fafafa;
    }
    .card h3 { margin-bottom: 10px; color: #444; }
    .status-pass { border-left: 4px solid #4caf50; }
    .status-fail { border-left: 4px solid #f44336; }
    .status-warning { border-left: 4px solid #ff9800; color: #f57c00; }
    .status-info { border-left: 4px solid #2196f3; }
    p { margin: 5px 0; color: #666; }
    footer {
      margin-top: 40px;
      padding-top: 20px;
      border-top: 1px solid #e0e0e0;
      text-align: center;
      color: #999;
      font-size: 12px;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>🛡️ CI/CD Compliance Summary</h1>
    <div class="meta">
      <p>Repository: ${repo} | Commit: ${sha}</p>
      <p>Run ID: ${runId} | Generated: ${timestamp}</p>
    </div>

    <div class="grid">
      ${generateSemgrepSummary()}
      ${generatePlaywrightSummary()}
      ${generateLighthouseSummary()}
      ${generateSpectralSummary()}
      ${generateK6Summary()}
    </div>

    <footer>
      <p>Generated by scripts/build-ci-summary.js</p>
      <p>This report aggregates results from multiple CI workflows</p>
    </footer>
  </div>
</body>
</html>
  `.trim();
}

// Main execution
function main() {
  console.log('Generating CI compliance summary...');

  ensureDirectoryExists(config.outputDir);
  const html = generateHTML();
  const outputPath = path.join(config.outputDir, config.outputFile);

  fs.writeFileSync(outputPath, html, 'utf8');
  console.log(`✅ Summary generated: ${outputPath}`);
  console.log(`\nNext steps:`);
  console.log(`- Review the summary: open ${outputPath}`);
  console.log(`- Upload as artifact in your CI workflow`);
  console.log(`- Customize this script to include additional metrics`);
}

if (require.main === module) {
  main();
}

module.exports = { generateHTML };
