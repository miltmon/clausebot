import { useState, useEffect } from 'react';
import { supabase } from '@/integrations/supabase/client';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Trash2, Globe, User, Loader2, Download } from 'lucide-react';
import { toast } from 'sonner';

interface Document {
  id: string;
  title: string | null;
  description: string | null;
  file_name: string;
  file_size: number | null;
  scope: string;
  entity_name: string | null;
  tags: string[] | null;
  created_at: string;
  file_path: string;
  file_type: string | null;
  content: string | null;
  processed_at: string | null;
  user_id: string;
}

export const DocumentList = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      // Check if backend is available
      if (!import.meta.env.VITE_SUPABASE_URL) {
        setDocuments([]);
        setIsLoading(false);
        return;
      }

      const { data, error } = await supabase
        .from('reference_documents')
        .select('*')
        .order('created_at', { ascending: false });

      if (error) throw error;
      setDocuments(data || []);
    } catch (error) {
      console.error('Error fetching documents:', error);
      toast.error('Failed to load documents');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = async (doc: Document) => {
    try {
      // Generate signed URL with 60s TTL
      const { data, error } = await supabase.storage
        .from('documents')
        .createSignedUrl(doc.file_path, 60);

      if (error) throw error;

      // Open download in new tab
      window.open(data.signedUrl, '_blank');
      
      toast.success('Download started');
    } catch (error) {
      console.error('Download error:', error);
      toast.error('Failed to download document');
    }
  };

  const handleDelete = async (doc: Document) => {
    if (!confirm(`Are you sure you want to delete "${doc.title}"?`)) return;

    setDeletingId(doc.id);
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) throw new Error('Not authenticated');

      // Delete from storage using file_path
      const { error: storageError } = await supabase.storage
        .from('documents')
        .remove([doc.file_path]);

      if (storageError) console.error('Storage deletion error:', storageError);

      // Delete from database
      const { error: dbError } = await supabase
        .from('reference_documents')
        .delete()
        .eq('id', doc.id);

      if (dbError) throw dbError;

      // Log audit event
      await supabase.from('audit_events').insert({
        user_id: user.id,
        action: 'document_deleted',
        target: doc.title || doc.file_name,
        meta: { doc_id: doc.id, file_path: doc.file_path }
      });

      toast.success('Document deleted successfully');
      fetchDocuments();
    } catch (error) {
      console.error('Delete error:', error);
      toast.error('Failed to delete document');
    } finally {
      setDeletingId(null);
    }
  };

  const getScopeIcon = (scope: string) => {
    if (scope === 'global') return <Globe className="h-4 w-4" />;
    return <User className="h-4 w-4" />;
  };

  const getScopeBadge = (doc: Document) => {
    if (doc.scope === 'global') {
      return <Badge variant="secondary"><Globe className="h-3 w-3 mr-1" />Global</Badge>;
    }
    if (doc.scope === 'entity' && doc.entity_name) {
      return <Badge variant="outline">{doc.entity_name}</Badge>;
    }
    if (doc.scope === 'system') {
      return <Badge variant="default">System</Badge>;
    }
    return <Badge variant="secondary"><User className="h-3 w-3 mr-1" />Personal</Badge>;
  };

  if (isLoading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-8">
          <Loader2 className="h-6 w-6 animate-spin" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Knowledge Base Documents</CardTitle>
        <CardDescription>
          {documents.length} document{documents.length !== 1 ? 's' : ''} in your knowledge base
        </CardDescription>
      </CardHeader>
      <CardContent>
        {documents.length === 0 ? (
          <p className="text-center text-muted-foreground py-8">
            No documents uploaded yet. Upload your first document to get started.
          </p>
        ) : (
          <div className="space-y-4">
            {documents.map((doc) => (
              <div
                key={doc.id}
                className="flex items-start justify-between p-4 border rounded-lg hover:bg-accent/50 transition-colors"
              >
                <div className="flex-1 space-y-2">
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold">{doc.title || 'Untitled'}</h3>
                    {getScopeBadge(doc)}
                  </div>
                  
                  {doc.description && (
                    <p className="text-sm text-muted-foreground">{doc.description}</p>
                  )}
                  
                  {doc.tags && doc.tags.length > 0 && (
                    <div className="flex items-center gap-2 flex-wrap">
                      {doc.tags.map((tag) => (
                        <Badge key={tag} variant="outline" className="text-xs">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  )}
                  
                  <div className="flex items-center gap-4 text-xs text-muted-foreground">
                    <span>{doc.file_name}</span>
                    {doc.file_size && <span>{(doc.file_size / 1024 / 1024).toFixed(2)} MB</span>}
                    <span>{new Date(doc.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
                
                <div className="flex items-center gap-2">
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleDownload(doc)}
                    data-qa="download-document"
                  >
                    <Download className="h-4 w-4" />
                  </Button>
                  
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleDelete(doc)}
                    disabled={deletingId === doc.id}
                    data-qa="delete-document"
                  >
                    {deletingId === doc.id ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Trash2 className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};
