# Lovable Integration Guide

## Step 1: Deploy TypeScript API

### Render Deployment
1. Push your code to GitHub
2. Connect to Render
3. Set environment variables in Render dashboard:
   ```
   NODE_ENV=production
   PORT=8080
   API_KEYS=prod_read:READ_ONLY,prod_admin:ADMIN
   ALLOWED_ORIGINS=https://lovable.dev,https://your-lovable-domain.lovable.app
   ```

### Verify Deployment
```bash
curl https://your-api-domain.onrender.com/v1/healthz
# Should return: {"status":"healthy",...}
```

## Step 2: Add Server-Side Proxy in Lovable

### Option A: Next.js Pages Router
Create `pages/api/clausebot/[...path].ts`:

```typescript
import type { NextApiRequest, NextApiResponse } from 'next';

const API_BASE = process.env.CLAUSEBOT_API_BASE!;
const API_KEY = process.env.CLAUSEBOT_API_KEY!;

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    const path = (req.query.path as string[]).join('/');
    const queryString = req.url?.includes('?') ? '?' + req.url.split('?')[1] : '';
    const url = `${API_BASE}/v1/${path}${queryString}`;

    const response = await fetch(url, {
      method: req.method,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${API_KEY}`,
      },
      body: ['POST', 'PUT', 'PATCH'].includes(req.method || '') 
        ? JSON.stringify(req.body || {}) 
        : undefined,
    });

    const data = await response.text();
    res.status(response.status).send(data);
  } catch (error) {
    console.error('ClauseBot API proxy error:', error);
    res.status(500).json({ error: 'Proxy error', message: error.message });
  }
}
```

### Option B: Next.js App Router
Create `app/api/clausebot/[...path]/route.ts`:

```typescript
import { NextRequest, NextResponse } from 'next/server';

const API_BASE = process.env.CLAUSEBOT_API_BASE!;
const API_KEY = process.env.CLAUSEBOT_API_KEY!;

async function handler(req: NextRequest, { params }: { params: { path: string[] } }) {
  try {
    const path = params.path.join('/');
    const searchParams = req.nextUrl.searchParams.toString();
    const queryString = searchParams ? `?${searchParams}` : '';
    const url = `${API_BASE}/v1/${path}${queryString}`;

    const body = req.method !== 'GET' ? await req.text() : undefined;

    const response = await fetch(url, {
      method: req.method,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${API_KEY}`,
      },
      body,
    });

    const data = await response.text();
    return new NextResponse(data, { 
      status: response.status,
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (error) {
    console.error('ClauseBot API proxy error:', error);
    return NextResponse.json({ error: 'Proxy error' }, { status: 500 });
  }
}

export { handler as GET, handler as POST, handler as PUT, handler as DELETE };
```

### Option C: Supabase Edge Function (if not Next.js)
Create `supabase/functions/clausebot-proxy/index.ts`:

```typescript
import { serve } from 'https://deno.land/std@0.168.0/http/server.ts';

const API_BASE = Deno.env.get('CLAUSEBOT_API_BASE')!;
const API_KEY = Deno.env.get('CLAUSEBOT_API_KEY')!;

serve(async (req) => {
  try {
    const url = new URL(req.url);
    const path = url.pathname.replace('/functions/v1/clausebot-proxy/', '');
    const targetUrl = `${API_BASE}/v1/${path}${url.search}`;

    const body = req.method !== 'GET' ? await req.text() : undefined;

    const response = await fetch(targetUrl, {
      method: req.method,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${API_KEY}`,
      },
      body,
    });

    const data = await response.text();
    return new Response(data, {
      status: response.status,
      headers: { 
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
      },
    });
  } catch (error) {
    return new Response(JSON.stringify({ error: 'Proxy error' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
});
```

## Step 3: Environment Variables in Lovable

Add these **server-only** environment variables:
```
CLAUSEBOT_API_BASE=https://your-api-domain.onrender.com
CLAUSEBOT_API_KEY=prod_read
```

**CRITICAL**: Do NOT expose `CLAUSEBOT_API_KEY` as a public environment variable.

## Step 4: Frontend Service Layer

Create or update your ClauseBot service:

```typescript
// src/services/clausebot.ts
const BASE_URL = '/api/clausebot'; // or '/functions/v1/clausebot-proxy' for Edge Functions

export interface HealthResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  version: string;
  uptime: number;
  requestId: string;
}

export interface SearchResult {
  id: string;
  title: string;
  content: string;
  category: string;
  relevance: number;
  metadata?: Record<string, any>;
}

export interface QuizQuestion {
  id: string;
  question: string;
  options: string[];
  correct_answer: string;
  category: string;
  difficulty: string;
  explanation?: string;
}

// Health check
export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch(`${BASE_URL}/healthz`, { cache: 'no-store' });
  if (!response.ok) throw new Error('Health check failed');
  return response.json();
}

// Service intelligence
export async function getIntel() {
  const response = await fetch(`${BASE_URL}/intel`, { cache: 'no-store' });
  if (!response.ok) throw new Error('Intel fetch failed');
  return response.json();
}

// Content search
export async function search(query: string, limit = 10): Promise<SearchResult[]> {
  const url = new URL(`${BASE_URL}/search`, window.location.origin);
  url.searchParams.set('q', query);
  url.searchParams.set('limit', String(limit));
  
  const response = await fetch(url.toString(), { cache: 'no-store' });
  if (!response.ok) throw new Error('Search failed');
  
  const data = await response.json();
  return data.results;
}

// Quiz generation (ADMIN only - goes through server proxy)
export async function generateQuiz(payload: { 
  topic: string; 
  count: number;
  difficulty?: 'easy' | 'medium' | 'hard';
  category?: string;
}): Promise<QuizQuestion[]> {
  const response = await fetch(`${BASE_URL}/quiz/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  
  if (!response.ok) throw new Error('Quiz generation failed');
  
  const data = await response.json();
  return data.questions;
}
```

## Step 5: Quick Integration Test

Add this to your main component to verify the connection:

```typescript
import { useEffect, useState } from 'react';
import { getHealth } from './services/clausebot';

export function ApiStatusIndicator() {
  const [status, setStatus] = useState<'loading' | 'healthy' | 'error'>('loading');

  useEffect(() => {
    getHealth()
      .then(() => setStatus('healthy'))
      .catch(() => setStatus('error'));
  }, []);

  return (
    <div className="flex items-center gap-2">
      <div className={`w-2 h-2 rounded-full ${
        status === 'healthy' ? 'bg-green-500' : 
        status === 'error' ? 'bg-red-500' : 'bg-yellow-500'
      }`} />
      <span className="text-sm">API {status}</span>
    </div>
  );
}
```

## Step 6: Gradual Migration

1. **Start with health check** - Verify the proxy works
2. **Replace search** - Swap your current search to use `search(query)`
3. **Add quiz generation** - Use `generateQuiz()` for admin features
4. **Enhance intel** - Display real service capabilities

## Next: Real Data Integration

Once the proxy is working, I'll help you replace the stubs with real Supabase queries:
- `/v1/search` → Query your AWS D1.1 content
- `/v1/intel` → Real service capabilities
- `/v1/quiz/generate` → Your Airtable questions

This architecture keeps your API keys secure while giving you the flexibility of both systems! 🚀
