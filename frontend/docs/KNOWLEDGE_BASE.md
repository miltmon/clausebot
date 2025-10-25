# Knowledge Base RAG System Documentation

## Overview

The ClauseBot.Ai Knowledge Base implements a Retrieval-Augmented Generation (RAG) system that allows AI functions to leverage uploaded documents for enhanced context and accuracy.

## Architecture

### Database Schema

**Table: `reference_documents`**
- Stores document metadata and extracted content
- Supports multiple scope levels (system, global, user, artist, entity)
- Includes priority-based retrieval and token estimation

**Table: `admin_settings`**
- Controls KB usage per AI function
- Configures token limits for AI completions

### Storage

**Bucket: `documents`**
- Private bucket for secure document storage
- Supports PDF, DOCX, TXT, and MD files
- **100MB file size limit** per document (supports thousands of pages)
- User-specific folder structure
- Intelligent chunking for documents exceeding token limits

## Document Scopes

### 1. System Scope
- **Access**: Admin-only
- **Priority**: Highest
- **Use Case**: Official documentation, compliance materials
- **Created Via**: `load-reference-documents` edge function

### 2. Global Scope
- **Access**: All users
- **Priority**: High
- **Use Case**: Shared knowledge, general reference materials
- **Created Via**: UI with "Global" scope selection

### 3. Entity Scope (Artist/Entity)
- **Access**: Context-specific
- **Priority**: Medium
- **Use Case**: Artist-specific knowledge, entity documentation
- **Created Via**: UI with entity name

### 4. User Scope
- **Access**: Owner only
- **Priority**: Low
- **Use Case**: Personal documents, user-specific references
- **Created Via**: UI with "Personal" scope selection

## Usage

### Frontend Integration

```typescript
import { DocumentUpload } from '@/components/KnowledgeBase/DocumentUpload';
import { DocumentList } from '@/components/KnowledgeBase/DocumentList';

// In your page component
<DocumentUpload />
<DocumentList />
```

### Backend Integration (Edge Functions)

```typescript
import { createClient } from "@supabase/supabase-js";

// Helper function (copy to each edge function that needs KB)
async function loadReferenceDocuments(
  supabase: any,
  functionName: string,
  entityName?: string
) {
  // Check if KB is enabled for this function
  const { data: setting } = await supabase
    .from('admin_settings')
    .select('value')
    .eq('key', `${functionName}_use_kb`)
    .maybeSingle();
  
  if (setting?.value === 'false') {
    return { context: '', tokenCount: 0, docsLoaded: 0 };
  }
  
  // Load documents in priority order
  // ... (see full implementation in ai-rag-example function)
}

// In your serve handler
serve(async (req) => {
  const { question, entityName } = await req.json();
  
  // Load KB context
  const { context, tokenCount, docsLoaded } = 
    await loadReferenceDocuments(supabase, 'your-function-name', entityName);
  
  // Build prompt with context
  const prompt = context 
    ? `=== REFERENCE MATERIALS ===\n${context}\n\n=== QUESTION ===\n${question}`
    : question;
  
  // Call AI with enhanced context
  // ...
});
```

## Admin Configuration

### Enable/Disable KB Per Function

```sql
-- Enable KB for a function
INSERT INTO admin_settings (key, value, description)
VALUES ('my_function_use_kb', 'true', 'Enable knowledge base for my_function');

-- Disable KB for a function
UPDATE admin_settings 
SET value = 'false' 
WHERE key = 'my_function_use_kb';
```

### Configure Token Limits

```sql
-- Set max tokens for a function
INSERT INTO admin_settings (key, value, description)
VALUES ('my_function_tokens', '8192', 'Max tokens for my_function AI completions');
```

## Document Upload Flow

1. **User uploads file** via DocumentUpload component
2. **File validation**: Size (<10MB), type (PDF/DOCX/TXT/MD)
3. **Storage upload**: File saved to `documents/{user_id}/{timestamp}_{title}.ext`
4. **Text extraction**: Content parsed from file
5. **Database insert**: Metadata and content saved to `reference_documents`
6. **Token estimation**: Rough calculation (content length / 4)

## RAG Retrieval Flow

1. **Function receives request** with optional entity name
2. **Check admin settings**: Is KB enabled for this function?
3. **Load documents by priority**:
   - System scope (highest priority)
   - Global scope
   - Entity-specific scope (if entity name provided)
4. **Filter non-empty content**: Only include docs with extracted text
5. **Format context**: Structured markdown with titles and page counts
6. **Calculate tokens**: Sum of estimated tokens from all loaded docs
7. **Return context**: Formatted string ready for AI prompt

## Security

### Row-Level Security (RLS)

**reference_documents table:**
- Users can view system/global scope documents
- Users can view their own user-scope documents
- Users can only create/update/delete their own documents
- Admins can manage all documents

**Storage bucket policies:**
- Users can upload to their own folder
- Users can view documents they have access to
- Users can delete their own documents
- Admins can manage all documents

## Best Practices

### 1. Document Preparation
- **Clear titles**: Use descriptive, searchable titles
- **Concise descriptions**: Summarize content for quick reference
- **Relevant tags**: Add multiple tags for better organization
- **Appropriate scope**: Choose the most restrictive scope needed

### 2. Token Management
- **Monitor token usage**: Track `estimated_tokens` field
- **Set reasonable limits**: Configure per-function token limits
- **Prioritize documents**: Use priority field for important docs

### 3. Content Quality
- **Extract clean text**: Ensure extracted content is readable
- **Remove formatting**: Strip unnecessary formatting from text
- **Verify accuracy**: Review extracted content before saving

### 4. Performance
- **Limit document size**: Keep individual docs under 10MB
- **Use pagination**: Don't load all docs at once in UI
- **Cache contexts**: Consider caching loaded contexts per session

## API Reference

### Edge Functions

#### `load-reference-documents`
**Purpose**: Bulk load system-scope documents (admin only)

**Request**:
```json
{
  "documents": [
    {
      "title": "Document Title",
      "description": "Optional description",
      "file_name": "filename.txt",
      "file_url": "https://...",
      "content_extracted": "Full text content...",
      "tags": ["tag1", "tag2"],
      "priority": 100
    }
  ]
}
```

**Response**:
```json
{
  "success": true,
  "total": 5,
  "successful": 5,
  "failed": 0,
  "results": [
    {
      "title": "Document Title",
      "success": true,
      "id": "uuid",
      "tokens": 1250
    }
  ]
}
```

#### `ai-rag-example`
**Purpose**: Example AI function with KB integration

**Request**:
```json
{
  "question": "What is the undercut limit?",
  "entityName": "AWS D1.1"
}
```

**Response**:
```json
{
  "answer": "According to the reference materials...",
  "metadata": {
    "docsLoaded": 3,
    "tokensUsed": 5420,
    "model": "google/gemini-2.5-flash"
  }
}
```

## Troubleshooting

### Documents Not Loading
1. Check admin settings: Is `{function_name}_use_kb` enabled?
2. Verify RLS policies: Can the user access the documents?
3. Check content extraction: Does `content_extracted` contain text?
4. Review logs: Check edge function logs for errors

### Token Limit Exceeded
1. Reduce number of documents
2. Increase priority on important docs
3. Configure higher token limit in admin settings
4. Consider implementing document chunking

### Upload Failures
1. Check file size (<10MB)
2. Verify file type (PDF, DOCX, TXT, MD)
3. Ensure user is authenticated
4. Check storage bucket permissions

## Future Enhancements

- **Vector embeddings**: Semantic search for relevant documents
- **Document chunking**: Break large docs into smaller chunks
- **Advanced extraction**: Better parsing for complex documents
- **Version control**: Track document changes over time
- **Usage analytics**: Monitor KB effectiveness per function
- **Collaborative editing**: Allow multiple users to curate documents
