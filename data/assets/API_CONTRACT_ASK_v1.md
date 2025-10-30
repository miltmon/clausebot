# ClauseBot `/ask` API Contract — v1.0 (Pilot)

**Status:** Pilot (Preview). This contract defines the request/response and operational expectations for the `/ask` endpoint.

## 1) Endpoint
- **POST** `/ask`
- **Auth:** (Pilot) Bearer token via `Authorization: Bearer <token>` or IP-allowlist
- **Content-Type:** `application/json`

## 2) Request (JSON)
```jsonc
{
  "query": "What lighting is required for visual weld inspection?",
  "codes": ["AWS_D1_1", "ASME_IX"],         // optional: constrain sources
  "top_k": 3,                               // optional: number of citations to return
  "client": {                               // optional: client metadata for analytics
    "app_version": "tracks-1.2.0",
    "session_id": "uuid-..."
  }
}
```

### Field Notes
- `query` (string, required): The user’s natural-language question.
- `codes` (array<string>, optional): Limit retrieval to standards. Allowed values: `AWS_D1_1`, `ASME_IX`, `API_1104`. (Others are ignored for v1.0.)
- `top_k` (int, optional, default=3, range 1–5): Max citations to return.
- `client` (object, optional): Freeform client metadata; not used for answering.

## 3) Response (JSON 200)
```jsonc
{
  "request_id": "b9e6b2f0-5d24-4f01-8d5c-7e2d0f1be9a1",
  "mode": "demo",                // "demo" or "live"
  "reason": "demo_only",         // reason when demo/no-call path chosen
  "answer": "For visual inspection, ensure adequate lighting... (summary)...",
  "citations": ["AWS D1.1 6.7.1", "ASME IX QW-302.1"],
  "normalized_clause_ids": ["AWS_D1_1:6.7.1", "ASME_IX:QW-302.1"],
  "latency_ms": 134,
  "safety_flags": [],
  "notes": {
    "disclaimer": "Always verify against the official code.",
    "eval": {"ranked": true}
  }
}
```

### Response Semantics
- `mode`: Reflects runtime path. **demo** = no external model called; **live** = model call made.
- `reason`: Describes why demo path was taken (`demo_only`, `quota_reached`, etc.).
- `citations`: Short-form references; **no verbatim code text** is returned.
- `normalized_clause_ids`: Stable identifiers for accuracy scoring.
- `safety_flags`: e.g., `audit_schema_violation`, `rate_limited`, `licensing_block`.

## 4) Error Responses
- **400** Bad Request — malformed input
  ```json
  {"error":{"code":"bad_request","message":"missing field: query"}}
  ```
- **401** Unauthorized — missing/invalid token
  ```json
  {"error":{"code":"unauthorized","message":"invalid or missing token"}}
  ```
- **429** Too Many Requests — app/day caps or rate limits
  ```json
  {"error":{"code":"rate_limited","message":"daily cap reached","retry_after_s":"86400"}}
  ```
- **500** Internal Error
  ```json
  {"error":{"code":"server_error","message":"unexpected error"}}
  ```

## 5) Operational Expectations (Pilot)
- **Accuracy target:** ≥85% top-1 clause reference on a 150–200 question eval set (Beta gate).
- **Latency target:** p95 ≤ 1000 ms on common queries.
- **Uptime target (hosted):** ≥99.5% monthly.
- **Rate limits:** Suggest 10 req/min per token and daily caps via `MAX_REQ_PER_DAY`.

## 6) Safety, Licensing, Compliance
- **No verbatim code text** is returned. Responses are summaries with citations.
- **Disclaimers:** Always include “verify against official code” language.
- **Escalation:** Ambiguity triggers “consult SME” guidance.
- **Audit:** All requests/decisions logged with privacy-preserving hashes (see audit schema).

## 7) Versioning & Headers
- `X-API-Version: 1`
- `X-Request-Id` is returned for end-to-end tracing.
- Breaking changes will bump the version header and `/v{n}` prefix when applicable.

## 8) Examples
### cURL
```bash
curl -s -X POST http://localhost:8080/ask   -H "Content-Type: application/json"   -H "Authorization: Bearer <TOKEN>"   -d '{"query":"What lighting is required for visual weld inspection?", "codes":["AWS_D1_1"], "top_k":3}'
```

### PowerShell
```powershell
Invoke-RestMethod -Uri http://localhost:8080/ask -Method Post -ContentType 'application/json'   -Headers @{ Authorization = 'Bearer <TOKEN>' }   -Body '{"query":"What lighting is required for visual weld inspection?","codes":["AWS_D1_1"],"top_k":3}' | ConvertTo-Json -Depth 6
```

---

## 9) SLAs & Support (Pilot)
- **Priority:** P2 during Pilot; business-hours email support.
- **Incident Process:** If service degrades (latency, uptime, accuracy), Pilot partners receive status updates and an incident postmortem per runbook.

*This contract is intentionally conservative for Pilot. We’ll expand fields (filters, pagination of references, feedback telemetry) post-Beta.*
