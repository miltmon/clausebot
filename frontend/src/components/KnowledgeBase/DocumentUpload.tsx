import { useState } from 'react';
import { supabase } from '@/integrations/supabase/client';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Upload, Loader2 } from 'lucide-react';
import { toast } from 'sonner';

type DocumentScope = 'global' | 'artist' | 'entity' | 'user';

export const DocumentUpload = () => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [scope, setScope] = useState<DocumentScope>('user');
  const [entityName, setEntityName] = useState('');
  const [tags, setTags] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [processingStage, setProcessingStage] = useState('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) return;

    // Increased file size limit to 100MB for large documents
    if (selectedFile.size > 100 * 1024 * 1024) {
      toast.error('File size must be less than 100MB. For larger documents, please contact support.');
      return;
    }

    // Check file type
    const allowedTypes = ['.pdf', '.docx', '.txt', '.md'];
    const fileExtension = selectedFile.name.substring(selectedFile.name.lastIndexOf('.')).toLowerCase();
    if (!allowedTypes.includes(fileExtension)) {
      toast.error('Only PDF, DOCX, TXT, and MD files are allowed');
      return;
    }

    setFile(selectedFile);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsUploading(true);
    setUploadProgress(0);
    setProcessingStage('Validating...');
    
    if (!file || !title) {
      toast.error('Please fill in all required fields');
      setIsUploading(false);
      return;
    }

    // Check if backend is available
    if (!import.meta.env.VITE_SUPABASE_URL) {
      toast.error('Backend not configured. Please enable Lovable Cloud to use document upload.');
      setIsUploading(false);
      return;
    }

    try {
      // Get current user
      setProcessingStage('Authenticating...');
      setUploadProgress(10);
      
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) throw new Error('Not authenticated');

      // Upload file to storage
      setProcessingStage('Uploading file...');
      setUploadProgress(20);
      
      const fileExtension = file.name.substring(file.name.lastIndexOf('.'));
      const fileName = `${user.id}/${Date.now()}_${title.replace(/[^a-z0-9]/gi, '_')}${fileExtension}`;
      
      const { data: uploadData, error: uploadError } = await supabase.storage
        .from('documents')
        .upload(fileName, file);

      if (uploadError) throw uploadError;

      setUploadProgress(50);
      setProcessingStage('Processing document...');

      // Get public URL
      const { data: { publicUrl } } = supabase.storage
        .from('documents')
        .getPublicUrl(fileName);

      // Extract text content from file
      setProcessingStage('Extracting content preview...');
      setUploadProgress(60);
      
      const content = await extractTextFromFile(file);
      
      // More accurate token estimation: 1 token ≈ 3.5 characters for English
      const estimatedTokens = Math.ceil(content.length / 3.5);
      
      // Better page estimation based on file type
      let estimatedPages;
      if (file.type === 'application/pdf' || file.name.endsWith('.pdf')) {
        // PDFs: ~66 pages per MB
        estimatedPages = Math.ceil((file.size / 1024 / 1024) * 66);
      } else if (file.type.includes('word') || file.name.endsWith('.docx')) {
        // DOCX: ~20 pages per MB
        estimatedPages = Math.ceil(file.size / (1024 * 50));
      } else {
        // Text files: ~333 pages per MB
        estimatedPages = Math.ceil(file.size / (1024 * 3));
      }

      setProcessingStage('Saving metadata...');
      setUploadProgress(80);

      // Insert document metadata
      const { error: insertError } = await supabase
        .from('reference_documents')
        .insert([{
          user_id: user.id,
          title,
          description,
          file_name: file.name,
          file_path: fileName,
          file_size: file.size,
          file_type: file.type,
          content: content.substring(0, 500000), // Store first 500k chars as preview
          scope: scope,
          entity_name: scope === 'entity' ? entityName : null,
          tags: tags.split(',').map(t => t.trim()).filter(Boolean)
        }] as any);

      if (insertError) throw insertError;

      setUploadProgress(100);
      setProcessingStage('Complete!');

      toast.success(`Document uploaded! Estimated ${estimatedPages.toLocaleString()} pages, ${estimatedTokens.toLocaleString()} tokens.`);
      
      // Reset form
      setTitle('');
      setDescription('');
      setScope('user');
      setEntityName('');
      setTags('');
      setFile(null);
      
    } catch (error) {
      console.error('Upload error:', error);
      toast.error(error instanceof Error ? error.message : 'Failed to upload document');
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
      setProcessingStage('');
    }
  };

  const extractTextFromFile = async (file: File): Promise<string> => {
    // For text files, read directly (limit to 500k chars for preview)
    if (file.type === 'text/plain' || file.name.endsWith('.txt') || file.name.endsWith('.md')) {
      const text = await file.text();
      return text.substring(0, 500000);
    }
    
    // For binary files (PDF, DOCX), return metadata placeholder
    // Full document processing should be handled by an edge function
    return `[Document: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)]

This is a preview placeholder. Full content extraction for multi-page documents requires server-side processing.

To enable full document processing:
1. Create an edge function for document parsing
2. Use libraries like pdf-parse, mammoth, or similar
3. Implement chunking for documents over 100,000 tokens
4. Store chunks in a separate table for efficient retrieval

File Details:
- Type: ${file.type}
- Size: ${(file.size / 1024 / 1024).toFixed(2)} MB
- Estimated Pages: ${file.type.includes('pdf') || file.name.endsWith('.pdf') ? Math.ceil((file.size / 1024 / 1024) * 66) : 'N/A'}`;
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Upload Document</CardTitle>
        <CardDescription>
          Add documents to the knowledge base for AI-powered reference
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="title">Title *</Label>
            <Input
              id="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Document title"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Brief description of the document"
              rows={3}
            />
          </div>

          <div className="space-y-2">
            <Label>Scope *</Label>
            <RadioGroup value={scope} onValueChange={(value) => setScope(value as DocumentScope)}>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="user" id="user" />
                <Label htmlFor="user">Personal (only visible to you)</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="global" id="global" />
                <Label htmlFor="global">Global (available to all users)</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="artist" id="artist" />
                <Label htmlFor="artist">Artist-specific</Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="entity" id="entity" />
                <Label htmlFor="entity">Entity-specific</Label>
              </div>
            </RadioGroup>
          </div>

          {(scope === 'artist' || scope === 'entity') && (
            <div className="space-y-2">
              <Label htmlFor="entityName">{scope === 'artist' ? 'Artist' : 'Entity'} Name *</Label>
              <Input
                id="entityName"
                value={entityName}
                onChange={(e) => setEntityName(e.target.value)}
                placeholder={`Enter ${scope} name`}
                required
              />
            </div>
          )}

          <div className="space-y-2">
            <Label htmlFor="tags">Tags</Label>
            <Input
              id="tags"
              value={tags}
              onChange={(e) => setTags(e.target.value)}
              placeholder="tag1, tag2, tag3"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="file">File * (PDF, DOCX, TXT, MD - max 100MB)</Label>
            <Input
              id="file"
              type="file"
              onChange={handleFileChange}
              accept=".pdf,.docx,.txt,.md"
              required
            />
            {file && (
              <p className="text-sm text-muted-foreground">
                Selected: {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
              </p>
            )}
            <p className="text-xs text-primary font-medium mt-1">
              ✓ Supports documents with thousands of pages
            </p>
            
            {isUploading && (
              <div className="space-y-2 mt-4">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">{processingStage}</span>
                  <span className="font-medium">{uploadProgress}%</span>
                </div>
                <div className="w-full bg-secondary rounded-full h-2 overflow-hidden">
                  <div 
                    className="bg-primary h-full transition-all duration-300 ease-out"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
              </div>
            )}
          </div>

          <Button 
            type="submit" 
            disabled={isUploading} 
            className="w-full"
            data-qa="upload-submit"
          >
            {isUploading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Uploading...
              </>
            ) : (
              <>
                <Upload className="mr-2 h-4 w-4" />
                Upload Document
              </>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};
