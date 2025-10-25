# ClauseBot API Documentation

This document provides comprehensive documentation for the ClauseBot API integration, including endpoints, authentication, request/response formats, and best practices.

## 🌐 Base URL

```
https://clausebot-api.onrender.com
```

All API endpoints are accessed via HTTPS only.

## 📋 API Overview

The ClauseBot API provides AI-powered welding code compliance verification, question answering, and citation lookup services. The API is built to handle AWS D1.1, ASME IX, and API 1104 standards.

### Key Features
- ✅ Clause-cited answer verification
- ✅ Question search and lookup
- ✅ Multi-standard support (AWS D1.1, ASME IX, API 1104)
- ✅ Confidence scoring
- ✅ Citation tracking
- ✅ Audit-ready responses

## 🔑 Authentication

Currently, the API does not require authentication for public endpoints. Future versions will implement API key authentication.

### Future Authentication (Planned)
```http
Authorization: Bearer YOUR_API_KEY
```

## 📡 API Endpoints

### Health Check

#### GET `/ready`
Check API health and availability.

**Response**
```json
{
  "status": "ok"
}
```

**Status Codes**
- `200 OK` - API is healthy
- `503 Service Unavailable` - API is down

---

### Get API Edition

#### GET `/v1/edition`
Get current API version and edition information.

**Response**
```json
{
  "version": "1.0.0",
  "edition": "professional"
}
```

**Status Codes**
- `200 OK` - Success

---

### Search Questions

#### GET `/v1/questions/search`
Search for questions in the knowledge base.

**Query Parameters**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `q` | string | Yes | Search query |

**Request Example**
```http
GET /v1/questions/search?q=undercut%20limit
```

**Response**
```json
[
  {
    "id": "q-12345",
    "question": "What is the undercut limit in AWS D1.1:2025?",
    "category": "visual_inspection",
    "difficulty": "basic",
    "tags": ["aws-d1.1", "undercut", "acceptance-criteria"]
  },
  {
    "id": "q-12346",
    "question": "How is undercut measured according to AWS D1.1?",
    "category": "visual_inspection",
    "difficulty": "intermediate",
    "tags": ["aws-d1.1", "undercut", "measurement"]
  }
]
```

**Status Codes**
- `200 OK` - Success
- `400 Bad Request` - Invalid query parameter
- `500 Internal Server Error` - Server error

---

### Verify Answer

#### POST `/v1/answers/verify`
Verify an answer to a welding code question with citations.

**Request Headers**
```http
Content-Type: application/json
Accept: application/json
```

**Request Body**
```json
{
  "question": "What is the undercut limit in AWS D1.1:2025 Clause 8?",
  "intent": "clause_lookup",
  "mode": "audit"
}
```

**Request Parameters**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `question` | string | Yes | The question to verify |
| `intent` | enum | Yes | Type of query: `audit`, `clause_lookup`, `study_help`, `visual`, `fallback` |
| `mode` | enum | Yes | Verification mode: `audit` (strict), `standard` (flexible) |

**Response**
```json
{
  "id": "ans-67890",
  "answer": "According to AWS D1.1:2025 Clause 8.15.1, undercut shall not exceed 1/32 inch (1 mm) for material less than 1 inch thick, or 1/16 inch (2 mm) for material 1 inch or greater in thickness.",
  "confidence": 0.95,
  "citations": [
    "AWS D1.1:2025 — Clause 8.15.1",
    "AWS D1.1:2025 — Table 8.1"
  ],
  "verdict": "VERIFIED",
  "timestamp": "2025-01-18T12:34:56.789Z"
}
```

**Response Fields**
| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique answer identifier |
| `answer` | string | The verified answer text |
| `confidence` | number | Confidence score (0-1) |
| `citations` | array | List of code citations |
| `verdict` | enum | Verification status: `VERIFIED`, `INSUFFICIENT_EVIDENCE`, `ERROR` |
| `timestamp` | string | ISO 8601 timestamp |

**Verdict Values**
- `VERIFIED` - Answer has been verified with citations
- `INSUFFICIENT_EVIDENCE` - Not enough data to verify
- `ERROR` - Error occurred during verification

**Status Codes**
- `200 OK` - Success
- `400 Bad Request` - Invalid request body
- `422 Unprocessable Entity` - Invalid intent or mode
- `500 Internal Server Error` - Server error

---

### Get Question by ID

#### GET `/v1/questions/{id}`
Retrieve a specific question by its ID.

**Path Parameters**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Question ID |

**Request Example**
```http
GET /v1/questions/q-12345
```

**Response**
```json
{
  "id": "q-12345",
  "question": "What is the undercut limit in AWS D1.1:2025?",
  "category": "visual_inspection",
  "difficulty": "basic",
  "tags": ["aws-d1.1", "undercut", "acceptance-criteria"]
}
```

**Status Codes**
- `200 OK` - Success
- `404 Not Found` - Question not found
- `500 Internal Server Error` - Server error

---

### Get Answer by ID

#### GET `/v1/answers/{id}`
Retrieve a specific answer by its ID.

**Path Parameters**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | string | Yes | Answer ID |

**Request Example**
```http
GET /v1/answers/ans-67890
```

**Response**
```json
{
  "id": "ans-67890",
  "answer": "According to AWS D1.1:2025 Clause 8.15.1...",
  "confidence": 0.95,
  "citations": [
    "AWS D1.1:2025 — Clause 8.15.1"
  ],
  "verdict": "VERIFIED",
  "timestamp": "2025-01-18T12:34:56.789Z"
}
```

**Status Codes**
- `200 OK` - Success
- `404 Not Found` - Answer not found
- `500 Internal Server Error` - Server error

---

## 🔄 Client Integration

### TypeScript Client

The ClauseBot.Ai frontend includes a TypeScript API client (`src/services/clausebotApi.ts`):

```typescript
import { clausebotApi } from '@/services/clausebotApi';

// Health check
const health = await clausebotApi.checkHealth();

// Search questions
const questions = await clausebotApi.searchQuestions('undercut limit');

// Verify answer
const answer = await clausebotApi.verifyAnswer({
  question: 'What is the undercut limit?',
  intent: 'clause_lookup',
  mode: 'audit'
});
```

### React Hook

Use the `useClausebotApi` hook for easier integration:

```typescript
import { useClausebotApi } from '@/hooks/useClauesbotApi';

function MyComponent() {
  const { isLoading, error, verifyAnswer } = useClausebotApi();
  
  const handleVerify = async () => {
    const result = await verifyAnswer({
      question: 'What is the undercut limit?',
      intent: 'clause_lookup',
      mode: 'audit'
    });
    
    if (result) {
      console.log('Answer:', result.answer);
      console.log('Citations:', result.citations);
    }
  };
  
  return (
    <button onClick={handleVerify} disabled={isLoading}>
      {isLoading ? 'Verifying...' : 'Verify Answer'}
    </button>
  );
}
```

## 🎯 Intent Types

The `intent` parameter helps the API understand the context of the question:

| Intent | Description | Use Case |
|--------|-------------|----------|
| `audit` | Audit/compliance verification | Pre-weld reviews, inspection reports |
| `clause_lookup` | Direct code clause lookup | Finding specific requirements |
| `study_help` | CWI exam preparation | Learning and studying |
| `visual` | Visual inspection guidance | Defect evaluation |
| `fallback` | General question | Unclassified queries |

## 🎚️ Mode Types

The `mode` parameter controls verification strictness:

| Mode | Description | Behavior |
|------|-------------|----------|
| `audit` | Strict verification | Returns `INSUFFICIENT_EVIDENCE` if uncertain |
| `standard` | Flexible verification | Returns best available answer |

**Recommendation**: Use `audit` mode for compliance-critical applications, `standard` mode for educational purposes.

## ⚡ Rate Limiting

Current rate limits (subject to change):
- **Requests per minute**: 60
- **Requests per hour**: 1000
- **Requests per day**: 10000

Rate limit headers are included in responses:
```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1642521600
```

## 🔍 Error Handling

### Error Response Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid intent value",
    "details": {
      "field": "intent",
      "value": "invalid_intent"
    }
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid request parameters |
| `NOT_FOUND` | 404 | Resource not found |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |
| `SERVICE_UNAVAILABLE` | 503 | API temporarily unavailable |

### Retry Strategy

Recommended retry strategy with exponential backoff:

```typescript
async function retryWithBackoff(fn, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      
      const delay = Math.pow(2, i) * 1000; // 1s, 2s, 4s
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
}
```

## 📊 Response Times

Expected response times:
- **Health Check**: < 100ms
- **Question Search**: < 500ms
- **Answer Verification**: < 1200ms

## 🔒 Security Best Practices

1. **HTTPS Only**: Always use HTTPS for API requests
2. **Input Validation**: Validate and sanitize all inputs
3. **Error Handling**: Don't expose sensitive error details to users
4. **Rate Limiting**: Respect rate limits to avoid throttling
5. **Caching**: Cache responses appropriately (7-day max)

## 📈 Analytics Integration

Track API usage with analytics:

```typescript
// Track answer verification
gtag('event', 'answer_verify', {
  verdict: response.verdict,
  has_citations: response.citations.length > 0,
  confidence: response.confidence,
  intent: request.intent,
  mode: request.mode
});
```

## 🚀 Performance Optimization

### Caching Strategy

1. **Browser Cache**: Cache GET requests for 5 minutes
2. **Service Worker**: Cache responses for offline use
3. **localStorage**: Store recent Q&A pairs (max 50)

### Request Optimization

1. **Debounce Search**: Debounce search input (300ms)
2. **Cancel Requests**: Cancel pending requests on new input
3. **Batch Requests**: Group related queries when possible

## 🧪 Testing

### Test Endpoints

Use these test questions for integration testing:

```json
{
  "question": "What is the maximum porosity allowed in AWS D1.1?",
  "intent": "clause_lookup",
  "mode": "audit"
}
```

Expected response: Clause 8.15.2 citation with VERIFIED verdict

## 📝 Changelog

### v1.0.0 (2025-01-18)
- Initial API release
- Question search endpoint
- Answer verification endpoint
- Health check endpoint
- Edition information endpoint

---

**API Status**: Production  
**Last Updated**: 2025-01-18  
**Support**: api-support@clausebot.ai
