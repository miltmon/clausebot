const REDACT_PATTERNS = [
  { name: 'email', re: /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}/g },
  { name: 'apiKey', re: /\b(?:sk-|ghp_|AKIA)[A-Za-z0-9-_]{16,}\b/g },
  { name: 'ip', re: /\b(?:\d{1,3}\.){3}\d{1,3}\b/g },
  { name: 'cc', re: /\b(?:\d[ -]*?){13,19}\b/g }
];

function redact(text) {
  if (!text) return text;
  let out = String(text);
  for (const p of REDACT_PATTERNS) out = out.replace(p.re, `[REDACTED:${p.name}]`);
  return out;
}

module.exports = (req, res, next) => {
  if (process.env.REDACT_LOGS === 'true') {
    const safeHeaders = {};
    for (const [k, v] of Object.entries(req.headers)) {
      safeHeaders[k] = k.toLowerCase().includes('authorization') ? '[REDACTED:auth]' : redact(v);
    }
    req._safe_log = {
      path: req.path,
      method: req.method,
      headers: safeHeaders,
      body: redact(JSON.stringify(req.body || {})).slice(0, 4000)
    };
  }
  next();
};
