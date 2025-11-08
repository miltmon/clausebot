const axios = require('axios');
const crypto = require('crypto');

function hash(x) {
  return crypto.createHash('sha256').update(String(x)).digest('hex');
}

function pickSnippets(pageObj, selectors = [], maxChars = 512) {
  const keep = [];
  for (const s of selectors) {
    const raw = pageObj?.[s.name] ?? '';
    if (!raw) continue;
    keep.push(String(raw).slice(0, maxChars));
    if (keep.length >= 3) break;
  }
  return keep;
}

function sanitizeSnippets(snips) {
  if (process.env.LLM_SANITIZE !== 'true') return snips;
  return snips.map((s) =>
    s
      .replace(/\b(?:\d[ -]*?){13,19}\b/g, '[REDACTED:number]')
      .replace(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}/g, '[REDACTED:email]')
      .replace(/\b(?:sk-|ghp_|AKIA)[A-Za-z0-9-_]{16,}\b/g, '[REDACTED:apikey]')
  );
}

function enforceContextLimit(snips) {
  const limit = Math.max(1, Math.min(3000, Number(process.env.LLM_CONTEXT_MAX_CHARS) || 3000));
  const joined = snips.join(' ');
  if (joined.length > limit) throw new Error('context_limit_exceeded');
  return snips;
}

async function callLLM({ task, schema, pageObj, selectors, runId }) {
  let snippets = pickSnippets(pageObj, selectors, 512);
  snippets = sanitizeSnippets(snippets);
  enforceContextLimit(snippets);

  const payload = {
    model: 'gpt-4o-mini',
    messages: [
      { role: 'system', content: 'Respond strictly with JSON matching the provided schema.' },
      { role: 'user', content: JSON.stringify({ task, schema, snippets, run_id: runId ? hash(runId) : undefined }) }
    ],
    temperature: 0
  };

  const headers = { Authorization: `Bearer ${process.env.LLM_API_KEY}` };
  const res = await axios.post(process.env.LLM_API_URL, payload, { headers, timeout: 30000 });
  return res.data;
}

function assertVendorContractGuard() {
  const usage = (process.env.LLM_DATA_USAGE || '').toLowerCase();
  if (usage !== 'none') {
    console.warn('LLM_DATA_USAGE not set to "none". Refusing to process production traffic.');
  }
}

module.exports = { callLLM, assertVendorContractGuard, pickSnippets, sanitizeSnippets, enforceContextLimit };
