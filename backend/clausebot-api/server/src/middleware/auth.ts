import { Request, Response, NextFunction } from 'express';
import { ApiKey, RequestWithAuth } from '../types';

export class AuthMiddleware {
  private apiKeys: Map<string, ApiKey['scope']> = new Map();

  constructor(apiKeysConfig: string) {
    this.parseApiKeys(apiKeysConfig);
  }

  private parseApiKeys(config: string): void {
    if (!config) return;
    
    const pairs = config.split(',');
    for (const pair of pairs) {
      const [key, scope] = pair.trim().split(':');
      if (key && scope && (scope === 'READ_ONLY' || scope === 'ADMIN')) {
        this.apiKeys.set(key, scope as ApiKey['scope']);
      }
    }
  }

  public authenticate(requiredScope?: ApiKey['scope']) {
    return (req: RequestWithAuth, res: Response, next: NextFunction) => {
      const authHeader = req.headers.authorization;
      
      if (!authHeader || !authHeader.startsWith('Bearer ')) {
        return res.status(401).json({
          error: 'Unauthorized',
          message: 'Missing or invalid Authorization header',
          code: 'AUTH_MISSING',
          requestId: req.requestId,
          timestamp: new Date().toISOString()
        });
      }

      const token = authHeader.substring(7); // Remove 'Bearer ' prefix
      const scope = this.apiKeys.get(token);

      if (!scope) {
        return res.status(401).json({
          error: 'Unauthorized',
          message: 'Invalid API key',
          code: 'AUTH_INVALID',
          requestId: req.requestId,
          timestamp: new Date().toISOString()
        });
      }

      // Check scope permissions
      if (requiredScope && requiredScope === 'ADMIN' && scope !== 'ADMIN') {
        return res.status(403).json({
          error: 'Forbidden',
          message: 'Insufficient permissions',
          code: 'AUTH_INSUFFICIENT_SCOPE',
          requestId: req.requestId,
          timestamp: new Date().toISOString()
        });
      }

      req.apiKey = { key: token, scope };
      next();
    };
  }

  public optionalAuth() {
    return (req: RequestWithAuth, res: Response, next: NextFunction) => {
      const authHeader = req.headers.authorization;
      
      if (authHeader && authHeader.startsWith('Bearer ')) {
        const token = authHeader.substring(7);
        const scope = this.apiKeys.get(token);
        
        if (scope) {
          req.apiKey = { key: token, scope };
        }
      }
      
      next();
    };
  }
}
