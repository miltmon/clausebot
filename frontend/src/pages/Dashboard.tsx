import { Link } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  BookOpen, 
  Database, 
  Settings2, 
  FileText, 
  GraduationCap, 
  DollarSign, 
  Briefcase,
  LayoutDashboard,
  Upload,
  Search,
  BarChart3,
  Bot,
  Users,
  Shield,
  Zap
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Helmet } from 'react-helmet';

const Dashboard = () => {
  const isBackendConfigured = !!import.meta.env.VITE_SUPABASE_URL;

  const quickActions = [
    {
      title: 'Upload Document',
      description: 'Add documents to knowledge base',
      icon: Upload,
      href: '/admin',
      color: 'bg-blue-500',
      action: 'Knowledge Base Tab',
    },
    {
      title: 'AI Functions',
      description: 'Configure AI settings',
      icon: Bot,
      href: '/admin',
      color: 'bg-purple-500',
      action: 'AI Functions Tab',
    },
    {
      title: 'System Stats',
      description: 'View analytics',
      icon: BarChart3,
      href: '/admin',
      color: 'bg-green-500',
      action: 'Overview Tab',
    },
    {
      title: 'Documentation',
      description: 'Browse system docs',
      icon: BookOpen,
      href: '/admin',
      color: 'bg-indigo-500',
      action: 'Documentation Tab',
    },
  ];

  const mainFeatures = [
    {
      title: 'Academy',
      description: 'Training and educational resources',
      icon: GraduationCap,
      href: '/academy',
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      title: 'Professional',
      description: 'Professional services and tools',
      icon: Briefcase,
      href: '/professional',
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
    },
    {
      title: 'Demo',
      description: 'Try out ClauseBot features',
      icon: Zap,
      href: '/demo',
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-50',
    },
    {
      title: 'Pricing',
      description: 'View plans and pricing',
      icon: DollarSign,
      href: '/pricing',
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
  ];

  const adminTools = [
    {
      title: 'Knowledge Base',
      description: 'Manage reference documents and RAG system',
      icon: Database,
      features: ['Document upload (100MB)', 'Multi-scope support', 'Smart chunking', 'Token management'],
      href: '/admin',
      tab: 'knowledge-base',
    },
    {
      title: 'AI Configuration',
      description: 'Configure AI functions and token limits',
      icon: Settings2,
      features: ['Per-function KB toggle', 'Token limits (10K-500K)', 'Live sync', 'Function management'],
      href: '/admin',
      tab: 'ai-functions',
    },
    {
      title: 'System Overview',
      description: 'Monitor system statistics and health',
      icon: BarChart3,
      features: ['Document count', 'Storage usage', 'Active settings', 'System status'],
      href: '/admin',
      tab: 'overview',
    },
    {
      title: 'Document Management',
      description: 'View and manage all uploaded documents',
      icon: FileText,
      features: ['Search & filter', 'Scope badges', 'Delete documents', 'View metadata'],
      href: '/admin',
      tab: 'documents',
    },
    {
      title: 'Documentation',
      description: 'Browse all system documentation',
      icon: BookOpen,
      features: ['11 doc files', 'Core features', 'Development', 'Reports'],
      href: '/admin',
      tab: 'documentation',
    },
  ];

  const systemStatus = {
    backend: isBackendConfigured ? 'Connected' : 'Not Configured',
    status: isBackendConfigured ? 'Operational' : 'Needs Setup',
    color: isBackendConfigured ? 'text-green-600' : 'text-yellow-600',
    bgColor: isBackendConfigured ? 'bg-green-50' : 'bg-yellow-50',
  };

  return (
    <>
      <Helmet>
        <title>Dashboard - ClauseBot</title>
        <meta name="robots" content="noindex,nofollow" />
      </Helmet>
      <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
        {/* Header */}
      <div className="bg-white border-b">
        <div className="container mx-auto px-4 py-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold mb-2">Dashboard</h1>
              <p className="text-muted-foreground">Central hub for all ClauseBot.Ai tools and features</p>
            </div>
            <Link to="/">
              <Button variant="outline">
                ← Back to Home
              </Button>
            </Link>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8 space-y-8">
        {/* System Status Banner */}
        <Card className={`border-2 ${systemStatus.bgColor}`}>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className={`h-12 w-12 rounded-full ${systemStatus.bgColor} flex items-center justify-center`}>
                  <Shield className={`h-6 w-6 ${systemStatus.color}`} />
                </div>
                <div>
                  <h3 className="font-semibold text-lg">System Status</h3>
                  <p className="text-sm text-muted-foreground">
                    Backend: <span className={`font-medium ${systemStatus.color}`}>{systemStatus.backend}</span>
                    {' • '}
                    Status: <span className={`font-medium ${systemStatus.color}`}>{systemStatus.status}</span>
                  </p>
                </div>
              </div>
              {!isBackendConfigured && (
                <Button variant="default">
                  Enable Backend
                </Button>
              )}
            </div>
          </CardContent>
        </Card>

        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="tools">Admin Tools</TabsTrigger>
            <TabsTrigger value="features">Features</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Zap className="h-5 w-5" />
                  Quick Actions
                </CardTitle>
                <CardDescription>Common tasks and shortcuts</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                  {quickActions.map((action) => (
                    <Link key={action.title} to={action.href}>
                      <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full">
                        <CardContent className="pt-6">
                          <div className="flex flex-col items-center text-center space-y-3">
                            <div className={`h-12 w-12 rounded-full ${action.color} bg-opacity-10 flex items-center justify-center`}>
                              <action.icon className={`h-6 w-6 ${action.color.replace('bg-', 'text-')}`} />
                            </div>
                            <div>
                              <h3 className="font-semibold">{action.title}</h3>
                              <p className="text-xs text-muted-foreground mt-1">{action.description}</p>
                              <p className="text-xs text-primary mt-2">{action.action}</p>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    </Link>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Getting Started */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BookOpen className="h-5 w-5" />
                  Getting Started
                </CardTitle>
                <CardDescription>New to ClauseBot? Start here</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4 md:grid-cols-3">
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-semibold">
                        1
                      </div>
                      <h4 className="font-semibold">Upload Documents</h4>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      Add your reference documents to the knowledge base
                    </p>
                    <Link to="/admin">
                      <Button variant="link" className="p-0 h-auto">
                        Go to Knowledge Base →
                      </Button>
                    </Link>
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <div className="h-8 w-8 rounded-full bg-purple-100 flex items-center justify-center text-purple-600 font-semibold">
                        2
                      </div>
                      <h4 className="font-semibold">Configure AI</h4>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      Set up AI functions and token limits
                    </p>
                    <Link to="/admin">
                      <Button variant="link" className="p-0 h-auto">
                        Configure Settings →
                      </Button>
                    </Link>
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <div className="h-8 w-8 rounded-full bg-green-100 flex items-center justify-center text-green-600 font-semibold">
                        3
                      </div>
                      <h4 className="font-semibold">Explore Features</h4>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      Try the demo and explore capabilities
                    </p>
                    <Link to="/demo">
                      <Button variant="link" className="p-0 h-auto">
                        Try Demo →
                      </Button>
                    </Link>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Admin Tools Tab */}
          <TabsContent value="tools" className="space-y-6">
            <div className="grid gap-6 md:grid-cols-2">
              {adminTools.map((tool) => (
                <Card key={tool.title} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                          <tool.icon className="h-5 w-5 text-primary" />
                        </div>
                        <div>
                          <CardTitle className="text-lg">{tool.title}</CardTitle>
                          <CardDescription className="mt-1">{tool.description}</CardDescription>
                        </div>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-2">
                      <h4 className="text-sm font-semibold">Features:</h4>
                      <ul className="text-sm text-muted-foreground space-y-1">
                        {tool.features.map((feature) => (
                          <li key={feature} className="flex items-center gap-2">
                            <div className="h-1.5 w-1.5 rounded-full bg-primary" />
                            {feature}
                          </li>
                        ))}
                      </ul>
                    </div>
                    <Link to={tool.href}>
                      <Button variant="outline" className="w-full">
                        Open {tool.title}
                      </Button>
                    </Link>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Features Tab */}
          <TabsContent value="features" className="space-y-6">
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
              {mainFeatures.map((feature) => (
                <Link key={feature.title} to={feature.href}>
                  <Card className={`hover:shadow-lg transition-all hover:-translate-y-1 h-full ${feature.bgColor} border-2`}>
                    <CardContent className="pt-6">
                      <div className="flex flex-col items-center text-center space-y-4">
                        <div className={`h-16 w-16 rounded-2xl ${feature.bgColor} flex items-center justify-center border-2`}>
                          <feature.icon className={`h-8 w-8 ${feature.color}`} />
                        </div>
                        <div>
                          <h3 className="font-bold text-lg">{feature.title}</h3>
                          <p className="text-sm text-muted-foreground mt-2">{feature.description}</p>
                        </div>
                        <Button variant="default" size="sm" className="w-full">
                          Explore →
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                </Link>
              ))}
            </div>

            {/* Additional Resources */}
            <Card>
              <CardHeader>
                <CardTitle>Resources & Documentation</CardTitle>
                <CardDescription>Learn more about ClauseBot.Ai</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-3">
                  <div className="space-y-2">
                    <h4 className="font-semibold flex items-center gap-2">
                      <BookOpen className="h-4 w-4" />
                      Documentation
                    </h4>
                    <p className="text-sm text-muted-foreground">
                      Complete guides for all features
                    </p>
                    <Link to="/admin">
                      <Button variant="link" className="p-0 h-auto text-primary">
                        View All Docs →
                      </Button>
                    </Link>
                  </div>

                  <div className="space-y-2">
                    <h4 className="font-semibold flex items-center gap-2">
                      <Users className="h-4 w-4" />
                      Support
                    </h4>
                    <p className="text-sm text-muted-foreground">
                      Get help from our team
                    </p>
                    <Button variant="link" className="p-0 h-auto text-primary">
                      Contact Support →
                    </Button>
                  </div>

                  <div className="space-y-2">
                    <h4 className="font-semibold flex items-center gap-2">
                      <Search className="h-4 w-4" />
                      Knowledge Base
                    </h4>
                    <p className="text-sm text-muted-foreground">
                      Browse system documentation
                    </p>
                    <Link to="/admin">
                      <Button variant="link" className="p-0 h-auto text-primary">
                        Browse Docs →
                      </Button>
                    </Link>
                  </div>
                </div>

                {/* Quick Doc Links */}
                <div className="mt-6 pt-6 border-t">
                  <h4 className="font-semibold mb-3">Popular Documentation</h4>
                  <div className="grid gap-2 md:grid-cols-2">
                    <Link to="/admin">
                      <Button variant="outline" size="sm" className="w-full justify-start">
                        <FileText className="h-4 w-4 mr-2" />
                        Knowledge Base Guide
                      </Button>
                    </Link>
                    <Link to="/admin">
                      <Button variant="outline" size="sm" className="w-full justify-start">
                        <FileText className="h-4 w-4 mr-2" />
                        Large Document Handling
                      </Button>
                    </Link>
                    <Link to="/admin">
                      <Button variant="outline" size="sm" className="w-full justify-start">
                        <FileText className="h-4 w-4 mr-2" />
                        API Reference
                      </Button>
                    </Link>
                    <Link to="/admin">
                      <Button variant="outline" size="sm" className="w-full justify-start">
                        <FileText className="h-4 w-4 mr-2" />
                        Architecture Guide
                      </Button>
                    </Link>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
    </>
  );
};

export default Dashboard;
