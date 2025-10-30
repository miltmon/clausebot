import { Router, Response } from 'express';
import { RequestWithAuth, IntelResponse } from '../types';

const router = Router();

router.get('/intel', (req: RequestWithAuth, res: Response<IntelResponse>) => {
  const intelResponse: IntelResponse = {
    service: 'ClauseBot API',
    version: process.env.npm_package_version || '1.0.0',
    environment: process.env.NODE_ENV || 'development',
    features: [
      'search',
      'quiz-generation',
      'health-monitoring',
      'rate-limiting',
      'bearer-auth'
    ],
    capabilities: [
      'D1.1 AWS welding standards',
      'clause-based search',
      'adaptive quiz generation',
      'real-time health checks'
    ],
    requestId: req.requestId || 'unknown'
  };

  res.json(intelResponse);
});

export default router;
