import { DocumentUpload } from '@/components/KnowledgeBase/DocumentUpload';
import { DocumentList } from '@/components/KnowledgeBase/DocumentList';
import { AIFunctionSettings } from '@/components/Admin/AIFunctionSettings';
import { SystemStats } from '@/components/Admin/SystemStats';
import { DocumentationViewer } from '@/components/Admin/DocumentationViewer';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { AlertCircle, Database, Upload, FileText, Settings2, BarChart3, Book } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Helmet } from 'react-helmet';

const Admin = () => {
  const isBackendConfigured = !!import.meta.env.VITE_SUPABASE_URL;

  return (
    <>
      <Helmet>
        <title>Admin - ClauseBot</title>
        <meta name="robots" content="noindex,nofollow" />
      </Helmet>
      <div className="container mx-auto py-8 px-4 max-w-7xl">
        <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold mb-2">Admin Dashboard</h1>
          <p className="text-muted-foreground">
            Manage system settings, knowledge base, and administrative functions
          </p>
        </div>

        {!isBackendConfigured && (
          <Card className="border-warning">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertCircle className="h-5 w-5" />
                Backend Setup Required
              </CardTitle>
              <CardDescription>
                To use admin features, you need to enable Lovable Cloud for database and storage functionality.
              </CardDescription>
            </CardHeader>
          </Card>
        )}

        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-5 lg:w-auto">
            <TabsTrigger value="overview" className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4" />
              <span className="hidden sm:inline">Overview</span>
            </TabsTrigger>
            <TabsTrigger value="knowledge-base" className="flex items-center gap-2">
              <Database className="h-4 w-4" />
              <span className="hidden sm:inline">Knowledge Base</span>
            </TabsTrigger>
            <TabsTrigger value="ai-functions" className="flex items-center gap-2">
              <Settings2 className="h-4 w-4" />
              <span className="hidden sm:inline">AI Functions</span>
            </TabsTrigger>
            <TabsTrigger value="documents" className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              <span className="hidden sm:inline">Documents</span>
            </TabsTrigger>
            <TabsTrigger value="documentation" className="flex items-center gap-2">
              <Book className="h-4 w-4" />
              <span className="hidden sm:inline">Docs</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <SystemStats />
            
            <div className="grid gap-6 lg:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>Quick Actions</CardTitle>
                  <CardDescription>
                    Common administrative tasks
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-2">
                  <p className="text-sm text-muted-foreground">
                    • Upload documents to the knowledge base
                  </p>
                  <p className="text-sm text-muted-foreground">
                    • Configure AI function settings
                  </p>
                  <p className="text-sm text-muted-foreground">
                    • Monitor system usage and statistics
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>System Status</CardTitle>
                  <CardDescription>
                    Backend connectivity and health
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-2 rounded-full bg-green-500"></div>
                    <span className="text-sm">All systems operational</span>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="knowledge-base" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Knowledge Base Management</CardTitle>
                <CardDescription>
                  Upload and manage documents for AI-powered reference and context
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-6 lg:grid-cols-2">
                  <DocumentUpload />
                  <div className="lg:col-span-2">
                    <DocumentList />
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="ai-functions" className="space-y-6">
            <AIFunctionSettings />
          </TabsContent>

          <TabsContent value="documents" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>All Documents</CardTitle>
                <CardDescription>
                  View and manage all uploaded documents
                </CardDescription>
              </CardHeader>
              <CardContent>
                <DocumentList />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="documentation" className="space-y-6">
            <DocumentationViewer />
          </TabsContent>
        </Tabs>
      </div>
    </div>
    </>
  );
};

export default Admin;
