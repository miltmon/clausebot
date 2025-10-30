# ClauseBot API Starter

A production-ready TypeScript/Express API starter kit for ClauseBot with OpenAPI 3.1 specification, Bearer authentication, and comprehensive middleware.

## Features

- ✅ **TypeScript + Express** - Modern, type-safe API development
- ✅ **OpenAPI 3.1** - Complete API specification with Swagger UI
- ✅ **Bearer Authentication** - Scoped API keys (READ_ONLY, ADMIN)
- ✅ **Security Middleware** - CORS, Helmet, Rate limiting
- ✅ **Request Tracking** - UUID request IDs for observability
- ✅ **Stub Endpoints** - Ready for real implementation
- ✅ **Production Ready** - Error handling, logging, health checks

## Quick Start (5 minutes)

```bash
# 1. Navigate to server directory
cd server

# 2. Install dependencies
npm install

# 3. Create environment file
echo "PORT=8080
API_KEYS=dev_read:READ_ONLY,dev_admin:ADMIN
ALLOWED_ORIGINS=http://localhost:3000,https://lovable.dev" > .env

# 4. Start development server
npm run dev
```

The API will be running at `http://localhost:8080`

## API Endpoints

### Health Check (No Auth Required)
```bash
curl -s http://localhost:8080/v1/healthz | jq
```

### Service Intelligence (READ_ONLY Auth)
```bash
curl -s http://localhost:8080/v1/intel \
  -H "Authorization: Bearer dev_read" | jq
```

### Search Content (READ_ONLY Auth)
```bash
curl -s "http://localhost:8080/v1/search?q=clause+4" \
  -H "Authorization: Bearer dev_read" | jq
```

### Generate Quiz (ADMIN Auth)
```bash
curl -s -X POST http://localhost:8080/v1/quiz/generate \
  -H "Authorization: Bearer dev_admin" \
  -H "Content-Type: application/json" \
  -d '{"topic":"D1.1 Clause 4","count":3}' | jq
```

## Environment Configuration

Create a `.env` file in the server directory:

```env
# Server Configuration
PORT=8080
NODE_ENV=development

# Authentication - Format: key1:scope1,key2:scope2
API_KEYS=dev_read:READ_ONLY,dev_admin:ADMIN,prod_key:ADMIN

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001,https://lovable.dev

# Optional: Custom rate limiting (default: 100 requests per 15 minutes)
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX=100
```

## Authentication Scopes

| Scope | Access Level | Endpoints |
|-------|-------------|-----------|
| `READ_ONLY` | Read operations | `/v1/intel`, `/v1/search` |
| `ADMIN` | Full access | All endpoints including `/v1/quiz/generate` |

## API Documentation

Once running, visit:
- **Swagger UI**: `http://localhost:8080/docs` (if implemented)
- **OpenAPI Spec**: See `openapi.yaml` file

## Project Structure

```
server/
├── src/
│   ├── middleware/
│   │   ├── auth.ts          # Bearer token authentication
│   │   └── requestId.ts     # Request ID generation
│   ├── routes/
│   │   ├── health.ts        # Health check endpoint
│   │   ├── intel.ts         # Service intelligence
│   │   ├── search.ts        # Content search (stub)
│   │   └── quiz.ts          # Quiz generation (stub)
│   ├── types/
│   │   └── index.ts         # TypeScript interfaces
│   └── index.ts             # Main application
├── openapi.yaml             # OpenAPI 3.1 specification
├── package.json
├── tsconfig.json
└── README.md
```

## Development Commands

```bash
# Install dependencies
npm install

# Start development server (with hot reload)
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run tests
npm test

# Lint code
npm run lint

# Fix linting issues
npm run lint:fix
```

## Stub Implementation Notes

The current endpoints return mock data. To integrate with real services:

### 1. Search Endpoint (`/v1/search`)
Replace the mock results in `src/routes/search.ts` with:
- Supabase queries for AWS D1.1 content
- Elasticsearch integration
- Airtable data source connection

### 2. Quiz Generation (`/v1/quiz/generate`)
Replace the mock questions in `src/routes/quiz.ts` with:
- AI-powered question generation
- Database-driven content selection
- Difficulty assessment algorithms

### 3. Intel Endpoint (`/v1/intel`)
Update `src/routes/intel.ts` to reflect:
- Real feature availability
- Dynamic capability detection
- Environment-specific configurations

## Production Deployment

### Environment Variables
```env
NODE_ENV=production
PORT=8080
API_KEYS=prod_read:READ_ONLY,prod_admin:ADMIN
ALLOWED_ORIGINS=https://clausebot.com,https://app.clausebot.com
```

### Docker Deployment
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY dist ./dist
EXPOSE 8080
CMD ["npm", "start"]
```

### Health Check Integration
The `/v1/healthz` endpoint is designed for:
- Load balancer health checks
- Container orchestration (Kubernetes, Docker Swarm)
- Monitoring systems (UptimeRobot, Datadog)

## Security Features

- **Rate Limiting**: 100 requests per 15 minutes per IP
- **CORS Protection**: Configurable allowed origins
- **Helmet Security**: Standard security headers
- **Bearer Authentication**: Scoped API key validation
- **Request Tracking**: UUID-based request correlation

## Error Handling

All endpoints return consistent error responses:

```json
{
  "error": "Bad Request",
  "message": "Missing required parameter 'q'",
  "code": "MISSING_PARAMETER",
  "requestId": "123e4567-e89b-12d3-a456-426614174000",
  "timestamp": "2025-10-27T15:30:00Z"
}
```

## Next Steps

1. **Integrate Real Data Sources**
   - Connect to Supabase for AWS D1.1 content
   - Implement Airtable integration for editorial workflow
   - Add caching layer (Redis/Memcached)

2. **Add More Endpoints**
   - `/v1/recommend` - Content recommendations
   - `/v1/quiz/grade` - Quiz scoring and analytics
   - `/v1/analytics` - Usage metrics and insights

3. **Enhance Security**
   - JWT token support
   - Role-based access control (RBAC)
   - API key rotation and management

4. **Monitoring & Observability**
   - Structured logging (Winston/Pino)
   - Metrics collection (Prometheus)
   - Distributed tracing (Jaeger/Zipkin)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details.

---

**Built for ClauseBot** - Professional welding education technology
