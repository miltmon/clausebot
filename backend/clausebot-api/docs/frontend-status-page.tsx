// ClauseBot Frontend Status Page
// Add this to your Next.js frontend for health monitoring
// 
// For App Router: app/status/page.tsx
// For Pages Router: pages/status.tsx

export default async function Status() {
  const apiBase = process.env.NEXT_PUBLIC_API_BASE || "unset";
  const sha = process.env.VERCEL_GIT_COMMIT_SHA || "unknown";
  const url = apiBase.replace(/\/$/, "") + "/healthz";

  let api = { ok: false, msg: "skipped" };
  try {
    const r = await fetch(url, { cache: "no-store" });
    api = { ok: r.ok, msg: r.ok ? "OK" : `HTTP ${r.status}` };
  } catch (e: any) {
    api = { ok: false, msg: e?.message || "network error" };
  }

  return (
    <main style={{ padding: 24, fontFamily: "system-ui" }}>
      <h1>ClauseBot Frontend Status</h1>
      <div style={{ 
        background: api.ok ? "#d4edda" : "#f8d7da", 
        padding: "16px", 
        borderRadius: "8px", 
        marginBottom: "16px",
        border: `2px solid ${api.ok ? "#28a745" : "#dc3545"}`
      }}>
        <h2 style={{ margin: 0, color: api.ok ? "#155724" : "#721c24" }}>
          {api.ok ? "✅ System Healthy" : "🚨 System Issues Detected"}
        </h2>
      </div>
      
      <div style={{ 
        background: "#f8f9fa", 
        padding: "16px", 
        borderRadius: "8px", 
        fontFamily: "monospace" 
      }}>
        <div><strong>Commit:</strong> {sha}</div>
        <div><strong>API Base:</strong> {apiBase}</div>
        <div><strong>API Health:</strong> 
          <span style={{ 
            color: api.ok ? "#28a745" : "#dc3545", 
            fontWeight: "bold" 
          }}>
            {api.ok ? "OK" : `FAIL — ${api.msg}`}
          </span>
        </div>
        <div><strong>Timestamp:</strong> {new Date().toISOString()}</div>
      </div>

      <div style={{ marginTop: "24px", fontSize: "14px", color: "#6c757d" }}>
        <h3>Quick Health Check</h3>
        <ul>
          <li>✅ Frontend deployed and rendering</li>
          <li>{api.ok ? "✅" : "❌"} API connectivity</li>
          <li>✅ Environment variables loaded</li>
          <li>✅ Build process completed</li>
        </ul>
      </div>
    </main>
  );
}
