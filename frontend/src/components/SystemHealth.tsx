import { useEffect, useState } from 'react';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, AlertCircle, Clock } from 'lucide-react';

interface BuildInfo {
  REPO: string;
  SHA: string;
  DATE: string;
}

interface SystemStatus {
  backend: 'operational' | 'degraded' | 'down';
  frontend: 'operational' | 'degraded' | 'down';
  buildInfo: BuildInfo | null;
  lastCheck: number;
}

export const SystemHealth = () => {
  const [status, setStatus] = useState<SystemStatus>({
    backend: 'operational',
    frontend: 'operational',
    buildInfo: null,
    lastCheck: Date.now(),
  });

  useEffect(() => {
    checkSystemHealth();
    const interval = setInterval(checkSystemHealth, 60000); // Check every minute
    return () => clearInterval(interval);
  }, []);

  const checkSystemHealth = async () => {
    try {
      // Check backend health
      const backendRes = await fetch('https://clausebot-api.onrender.com/health', {
        signal: AbortSignal.timeout(5000),
      });
      
      // Get build info
      const buildInfoRes = await fetch('https://clausebot-api.onrender.com/buildinfo', {
        signal: AbortSignal.timeout(5000),
      });

      const buildData = buildInfoRes.ok ? await buildInfoRes.json() : null;

      setStatus({
        backend: backendRes.ok ? 'operational' : 'degraded',
        frontend: 'operational', // If this code runs, frontend is up
        buildInfo: buildData,
        lastCheck: Date.now(),
      });

      // Track health check in GA4
      if (typeof window !== 'undefined' && (window as any).gtag) {
        (window as any).gtag('event', 'system_health_check', {
          backend_status: backendRes.ok ? 'operational' : 'degraded',
          response_time: backendRes.headers.get('x-response-time'),
          build_sha: buildData?.SHA?.substring(0, 7),
        });
      }
    } catch (error) {
      console.error('Health check failed:', error);
      setStatus(prev => ({
        ...prev,
        backend: 'down',
        lastCheck: Date.now(),
      }));
    }
  };

  const getStatusBadge = (service: 'operational' | 'degraded' | 'down') => {
    switch (service) {
      case 'operational':
        return (
          <Badge className="gap-1 bg-green-600 hover:bg-green-700">
            <CheckCircle className="h-3 w-3" /> 
            Operational
          </Badge>
        );
      case 'degraded':
        return (
          <Badge className="gap-1 bg-yellow-600 hover:bg-yellow-700">
            <AlertCircle className="h-3 w-3" /> 
            Degraded
          </Badge>
        );
      case 'down':
        return (
          <Badge className="gap-1 bg-red-600 hover:bg-red-700">
            <AlertCircle className="h-3 w-3" /> 
            Down
          </Badge>
        );
    }
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
      });
    } catch {
      return 'Unknown';
    }
  };

  return (
    <div className="inline-flex items-center gap-3 text-sm">
      <a 
        href="/health" 
        className="flex items-center gap-2 hover:opacity-80 transition-opacity"
        onClick={() => {
          if (typeof window !== 'undefined' && (window as any).gtag) {
            (window as any).gtag('event', 'health_page_viewed', {
              source: 'footer_widget',
              backend_status: status.backend,
            });
          }
        }}
      >
        <span className="text-muted-foreground">System Status:</span>
        {getStatusBadge(status.backend)}
      </a>
      
      {status.buildInfo && status.buildInfo.DATE !== 'unknown' && (
        <span className="text-xs text-muted-foreground flex items-center gap-1">
          <Clock className="h-3 w-3" />
          {formatDate(status.buildInfo.DATE)}
        </span>
      )}
    </div>
  );
};
