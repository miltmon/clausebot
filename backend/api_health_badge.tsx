'use client'
import { useEffect, useState } from 'react';

export function ApiHealthBadge() {
  const [ok, setOk] = useState<boolean | null>(null);

  useEffect(() => {
    let cancelled = false;
    const hit = async () => {
      try {
        const r = await fetch(`${process.env.NEXT_PUBLIC_API_BASE}/health`, { signal: AbortSignal.timeout(10000) });
        const j = r.ok ? await r.json() : { ok: false };
        if (!cancelled) setOk(!!j.ok);
      } catch { if (!cancelled) setOk(false); }
    };
    hit();
    const id = setInterval(hit, 30000);
    return () => { cancelled = true; clearInterval(id); };
  }, []);

  if (ok === null) return <span className="text-sm text-gray-500">API: checking…</span>;
  return (
    <span className={`text-sm ${ok ? 'text-green-600' : 'text-red-600'}`}>
      API: {ok ? 'Online' : 'Offline'}
    </span>
  );
}
