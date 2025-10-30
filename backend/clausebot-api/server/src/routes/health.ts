import { Router, Response } from 'express';
import { RequestWithAuth, HealthResponse } from '../types';

const router = Router();

router.get('/healthz', (req: RequestWithAuth, res: Response<HealthResponse>) => {
  const uptime = process.uptime();
  
  const healthResponse: HealthResponse = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: process.env.npm_package_version || '1.0.0',
    uptime: Math.floor(uptime),
    requestId: req.requestId || 'unknown'
  };

  res.json(healthResponse);
});

export default router;
