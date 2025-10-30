import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import dotenv from 'dotenv';

import { requestIdMiddleware } from './middleware/requestId';
import { AuthMiddleware } from './middleware/auth';
import healthRouter from './routes/health';
import intelRouter from './routes/intel';
import searchRouter from './routes/search';
import quizRouter from './routes/quiz';
import exaRouter from './routes/exa-search';
import websetsRouter from './routes/websets';

// Load environment variables
dotenv.config();

const app = express();
const port = process.env.PORT || 8080;

// Initialize auth middleware
const authMiddleware = new AuthMiddleware(process.env.API_KEYS || '');

// Security middleware
app.use(helmet());

// CORS configuration
const allowedOrigins = process.env.ALLOWED_ORIGINS?.split(',') || [
  'http://localhost:3000',
  'https://lovable.dev'
];

app.use(cors({
  origin: allowedOrigins,
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Request-ID']
}));

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: {
    error: 'Too Many Requests',
    message: 'Rate limit exceeded. Please try again later.',
    code: 'RATE_LIMIT_EXCEEDED'
  },
  standardHeaders: true,
  legacyHeaders: false
});

app.use(limiter);

// Body parsing middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Request ID middleware (must be before routes)
app.use(requestIdMiddleware);

// Routes
app.use('/v1', healthRouter);
app.use('/v1', authMiddleware.authenticate('READ_ONLY'), intelRouter);
app.use('/v1', authMiddleware.authenticate('READ_ONLY'), searchRouter);
app.use('/v1', authMiddleware.authenticate('READ_ONLY'), exaRouter);
app.use('/v1', authMiddleware.authenticate('READ_ONLY'), websetsRouter);
app.use('/v1', authMiddleware.authenticate('ADMIN'), quizRouter);

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    service: 'ClauseBot API Starter',
    version: '1.0.0',
    status: 'running',
    endpoints: {
      health: '/v1/healthz',
      intel: '/v1/intel (requires READ_ONLY)',
      search: '/v1/search (requires READ_ONLY)',
      exa_search: '/v1/exa/search (requires READ_ONLY)',
      exa_trending: '/v1/exa/trending (requires READ_ONLY)',
      websets_search: '/v1/websets/search (requires READ_ONLY)',
      websets_multi_search: '/v1/websets/multi-search (requires READ_ONLY)',
      websets_list: '/v1/websets (requires READ_ONLY)',
      quiz: '/v1/quiz/generate (requires ADMIN)'
    },
    documentation: '/docs'
  });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({
    error: 'Not Found',
    message: `Route ${req.originalUrl} not found`,
    code: 'ROUTE_NOT_FOUND',
    timestamp: new Date().toISOString()
  });
});

// Error handler
app.use((err: any, req: any, res: any, next: any) => {
  console.error('Error:', err);
  
  res.status(err.status || 500).json({
    error: 'Internal Server Error',
    message: err.message || 'Something went wrong',
    code: 'INTERNAL_ERROR',
    requestId: req.requestId,
    timestamp: new Date().toISOString()
  });
});

// Start server
app.listen(port, () => {
  console.log(`🚀 ClauseBot API starter running on port ${port}`);
  console.log(`📚 Available endpoints:`);
  console.log(`   GET  /v1/healthz`);
  console.log(`   GET  /v1/intel (auth required)`);
  console.log(`   GET  /v1/search (auth required)`);
  console.log(`   POST /v1/quiz/generate (admin required)`);
  console.log(`🔐 Configure API_KEYS environment variable for authentication`);
});

export default app;
