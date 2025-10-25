import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, AlertCircle, Clock, Database, Server, Globe, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';

interface HealthData {
  health?: any;
  quizHealth?: any;
  buildInfo?: any;
}

const Health = () => {
  const [healthData, setHealthData] = useState<HealthData | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  useEffect(() => {
    fetchHealthData();
    const interval = setInterval(fetchHealthData, 30000); // Auto-refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const fetchHealthData = async () => {
    try {
      setLoading(true);
      const [health, quizHealth, buildInfo] = await Promise.allSettled([
        fetch('https://clausebot-api.onrender.com/health').then(r => r.json()),
        fetch('https://clausebot-api.onrender.com/health/quiz/detailed').then(r => r.json()),
        fetch('https://clausebot-api.onrender.com/buildinfo').then(r => r.json()),
      ]);

      setHealthData({
        health: health.status === 'fulfilled' ? health.value : null,
        quizHealth: quizHealth.status === 'fulfilled' ? quizHealth.value : null,
        buildInfo: buildInfo.status === 'fulfilled' ? buildInfo.value : null,
      });
      
      setLastUpdated(new Date());
      
      // Track health dashboard view
      if (typeof window !== 'undefined' && (window as any).gtag) {
        (window as any).gtag('event', 'health_dashboard_viewed', {
          backend_status: health.status === 'fulfilled' ? 'operational' : 'down',
          quiz_status: quizHealth.status === 'fulfilled' ? 'operational' : 'down',
        });
      }
    } catch (error) {
      console.error('Health check failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const getServiceStatus = (data: any) => {
    if (!data) return 'down';
    if (data.status === 'connected' || data.service === 'healthy') return 'operational';
    return 'degraded';
  };

  const StatusBadge = ({ status }: { status: 'operational' | 'degraded' | 'down' }) => {
    switch (status) {
      case 'operational':
        return (
          <Badge className="bg-green-600 hover:bg-green-700">
            <CheckCircle className="h-3 w-3 mr-1" />
            Operational
          </Badge>
        );
      case 'degraded':
        return (
          <Badge className="bg-yellow-600 hover:bg-yellow-700">
            <AlertCircle className="h-3 w-3 mr-1" />
            Degraded
          </Badge>
        );
      case 'down':
        return (
          <Badge className="bg-red-600 hover:bg-red-700">
            <AlertCircle className="h-3 w-3 mr-1" />
            Down
          </Badge>
        );
    }
  };

  return (
    <>
      <Navbar />
      <div className="min-h-screen bg-gradient-to-br from-background to-muted py-24">
        <div className="container mx-auto px-4 max-w-4xl">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold mb-4">System Health Dashboard</h1>
            <p className="text-muted-foreground mb-4">Real-time status of ClauseBot services</p>
            <div className="flex items-center justify-center gap-4 text-sm text-muted-foreground">
              <span>Last updated: {lastUpdated.toLocaleTimeString()}</span>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={fetchHealthData}
                disabled={loading}
                className="gap-2"
              >
                <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
            </div>
          </div>

          {loading && !healthData ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary mb-4"></div>
              <p className="text-muted-foreground">Checking system health...</p>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Backend API Status */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Server className="h-5 w-5" />
                    Backend API
                  </CardTitle>
                  <CardDescription>FastAPI service on Render</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span>Status</span>
                    <StatusBadge status={getServiceStatus(healthData?.health)} />
                  </div>
                  {healthData?.buildInfo && (
                    <>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground">Repository</span>
                        <code className="bg-muted px-2 py-1 rounded text-xs">
                          {healthData.buildInfo.REPO || 'miltmon/clausebot'}
                        </code>
                      </div>
                      {healthData.buildInfo.SHA !== 'unknown' && (
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-muted-foreground">Commit SHA</span>
                          <code className="bg-muted px-2 py-1 rounded text-xs">
                            {healthData.buildInfo.SHA?.substring(0, 7)}
                          </code>
                        </div>
                      )}
                      {healthData.buildInfo.DATE !== 'unknown' && (
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-muted-foreground">Last Deploy</span>
                          <span>{new Date(healthData.buildInfo.DATE).toLocaleString()}</span>
                        </div>
                      )}
                    </>
                  )}
                </CardContent>
              </Card>

              {/* Quiz Service Status */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Database className="h-5 w-5" />
                    Quiz Service
                  </CardTitle>
                  <CardDescription>Airtable-powered quiz questions</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span>Connection</span>
                    <StatusBadge status={getServiceStatus(healthData?.quizHealth)} />
                  </div>
                  {healthData?.quizHealth && (
                    <>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground">Total Questions</span>
                        <span className="font-medium">{healthData.quizHealth.total || 'Unknown'}</span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground">Eligible Questions</span>
                        <span className="font-medium">{healthData.quizHealth.eligible || 'Unknown'}</span>
                      </div>
                      {healthData.quizHealth.sample_question && (
                        <div className="text-xs text-muted-foreground p-3 bg-muted rounded">
                          <div className="font-medium mb-1">Sample Question:</div>
                          <div>"{healthData.quizHealth.sample_question.substring(0, 100)}..."</div>
                        </div>
                      )}
                    </>
                  )}
                </CardContent>
              </Card>

              {/* Frontend Status */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Globe className="h-5 w-5" />
                    Frontend
                  </CardTitle>
                  <CardDescription>React app on Vercel</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span>Status</span>
                    <StatusBadge status="operational" />
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Deployment</span>
                    <span>clausebot.vercel.app</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Last Checked</span>
                    <span>{lastUpdated.toLocaleTimeString()}</span>
                  </div>
                </CardContent>
              </Card>

              {/* Monitoring Info */}
              <Card className="bg-blue-50 border-blue-200">
                <CardContent className="pt-6">
                  <div className="flex items-start gap-3">
                    <Clock className="h-5 w-5 text-blue-600 mt-0.5" />
                    <div>
                      <div className="font-medium text-blue-900 mb-1">
                        Advanced Monitoring
                      </div>
                      <div className="text-sm text-blue-800">
                        UptimeRobot monitoring will be activated on <strong>November 2, 2025</strong> with 
                        email and SMS alerts for any service disruptions.
                      </div>
                      <div className="text-xs text-blue-700 mt-2">
                        Contact: mjewell@miltmon.com | SMS: +1-310-755-1124
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </div>
      </div>
      <Footer />
    </>
  );
};

export default Health;
