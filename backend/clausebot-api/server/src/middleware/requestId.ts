import { Request, Response, NextFunction } from 'express';
import { v4 as uuidv4 } from 'uuid';
import { RequestWithAuth } from '../types';

export function requestIdMiddleware(req: RequestWithAuth, res: Response, next: NextFunction): void {
  req.requestId = uuidv4();
  res.setHeader('X-Request-ID', req.requestId);
  next();
}
