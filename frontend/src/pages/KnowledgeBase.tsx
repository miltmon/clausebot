import { DocumentUpload } from '@/components/KnowledgeBase/DocumentUpload';
import { DocumentList } from '@/components/KnowledgeBase/DocumentList';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { AlertCircle } from 'lucide-react';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import { Helmet } from 'react-helmet';

const KnowledgeBase = () => {
  const isBackendConfigured = !!import.meta.env.VITE_SUPABASE_URL;

  return (
    <>
      <Helmet>
        <title>Knowledge Base - ClauseBot</title>
        <meta name="robots" content="noindex,nofollow" />
      </Helmet>
      <Navbar />
      <div className="container mx-auto py-8 px-4 max-w-6xl">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold mb-2">Knowledge Base</h1>
          <p className="text-muted-foreground">
            Upload and manage documents for AI-powered reference and context
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
                To use the Knowledge Base feature, you need to enable Lovable Cloud for database and storage functionality.
              </CardDescription>
            </CardHeader>
          </Card>
        )}
        
        <div className="grid gap-6 lg:grid-cols-2">
          <DocumentUpload />
          <div className="lg:col-span-2">
            <DocumentList />
          </div>
        </div>
      </div>
    </div>
    <Footer />
    </>
  );
};

export default KnowledgeBase;
