# Large Document Handling Guide

## Overview
This system is designed to handle documents with thousands of pages efficiently through intelligent chunking, token management, and progressive loading strategies.

## File Size Limits

### Upload Limits
- **Maximum file size**: 100MB per document
- **Supported formats**: PDF, DOCX, TXT, MD
- **Typical document sizes**:
  - 1,000 pages PDF: ~15-30MB
  - 5,000 pages PDF: ~75-150MB
  - 10,000 pages text: ~30-50MB

### Storage Considerations
- Supabase Storage default: 100GB total
- For larger storage needs, upgrade Supabase plan
- Consider S3 or external storage for archives >100MB

## Token Management

### Token Estimation
The system uses intelligent token estimation:
```typescript
// More accurate estimation: 1 token ≈ 3.5 characters for English
const estimatedTokens = Math.ceil(textContent.length / 3.5);
```

### Default Token Limits by Function
- **Default**: 200,000 tokens (~150,000 words)
- **Configurable**: 1,000 - 100,000 tokens via admin settings
- **Per-document chunking**: Automatic for documents exceeding limits

### Token Budgeting
The RAG system automatically manages token budgets:

1. **Priority Loading**:
   - System documents (highest priority)
   - Global documents
   - Entity-specific documents

2. **Smart Chunking**:
   - If document exceeds limit, takes largest possible chunk
   - Adds truncation notice with percentage shown
   - Minimum chunk: 1,000 tokens

3. **Multi-document Loading**:
   - Loads documents until token limit reached
   - Partial documents included if space remains
   - Logs skipped documents for monitoring

## Page Estimation

### Improved Accuracy
Different file types have different page densities:

```typescript
if (file.type === 'application/pdf') {
  // PDFs: ~66 pages per MB
  estimatedPages = Math.ceil((file.size / 1024 / 1024) * 66);
} else if (file.type.includes('word')) {
  // DOCX: ~20 pages per MB
  estimatedPages = Math.ceil(file.size / (1024 * 50));
} else {
  // Text: ~333 pages per MB
  estimatedPages = Math.ceil(file.size / (1024 * 3));
}
```

## Upload Process for Large Documents

### Progress Tracking
```
1. Validating...        (10%)
2. Authenticating...    (20%)
3. Uploading file...    (50%)
4. Processing document...(60%)
5. Extracting preview...  (80%)
6. Saving metadata...   (100%)
```

### Content Extraction Strategy

#### For Text Files (TXT, MD)
- Extract first 500,000 characters as preview
- Full text available in storage

#### For Binary Files (PDF, DOCX)
- Store metadata placeholder
- Recommend server-side processing via edge function
- Preview shows file stats and setup instructions

## Implementing Full Document Processing

### Step 1: Create Document Parser Edge Function

```typescript
// supabase/functions/parse-document/index.ts
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

serve(async (req) => {
  const supabase = createClient(
    Deno.env.get('SUPABASE_URL') ?? '',
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
  );

  const { documentId } = await req.json();
  
  // 1. Fetch document from storage
  // 2. Use pdf-parse or mammoth for extraction
  // 3. Chunk content if > 100k tokens
  // 4. Update reference_documents with extracted content
  
  return new Response(JSON.stringify({ success: true }));
});
```

### Step 2: Add Document Chunking Table (Optional)

For extremely large documents (>1M tokens), create a chunks table:

```sql
create table document_chunks (
  id uuid primary key default gen_random_uuid(),
  document_id uuid references reference_documents(id) on delete cascade,
  chunk_index integer not null,
  chunk_text text not null,
  token_count integer,
  created_at timestamp with time zone default now(),
  
  unique(document_id, chunk_index)
);

create index idx_chunks_document on document_chunks(document_id);
```

### Step 3: Implement Semantic Chunking

For best RAG performance with large documents:

```typescript
// Chunk by semantic boundaries (paragraphs, sections)
function semanticChunk(text: string, maxTokens: number = 10000): string[] {
  const chunks: string[] = [];
  const paragraphs = text.split(/\n\n+/);
  
  let currentChunk = '';
  let currentTokens = 0;
  
  for (const para of paragraphs) {
    const paraTokens = Math.ceil(para.length / 3.5);
    
    if (currentTokens + paraTokens > maxTokens && currentChunk) {
      chunks.push(currentChunk);
      currentChunk = para;
      currentTokens = paraTokens;
    } else {
      currentChunk += (currentChunk ? '\n\n' : '') + para;
      currentTokens += paraTokens;
    }
  }
  
  if (currentChunk) chunks.push(currentChunk);
  return chunks;
}
```

## RAG Retrieval for Large Documents

### Chunk-based Retrieval (Advanced)

```typescript
// Load relevant chunks instead of full documents
async function loadRelevantChunks(
  supabase: SupabaseClient,
  query: string,
  maxTokens: number = 50000
): Promise<string> {
  // 1. Use embedding similarity to find relevant chunks
  // 2. Load chunks in order of relevance
  // 3. Stop when token limit reached
  
  // Requires: pgvector extension + embedding generation
}
```

## Performance Optimization

### 1. Lazy Loading
- Don't extract full content on upload for large files
- Process in background via edge function
- Update document status when complete

### 2. Caching
- Cache frequently accessed documents
- Use Supabase realtime for updates
- Implement CDN for static documents

### 3. Progressive Enhancement
- Show preview immediately
- Load full content on-demand
- Stream large responses

## Monitoring & Logging

### Key Metrics to Track
```typescript
console.log(`[RAG] Loaded ${selectedDocs.length}/${allDocs.length} documents`);
console.log(`[RAG] Total tokens: ${totalTokens.toLocaleString()}/${maxTokens.toLocaleString()}`);
console.log(`[RAG] Chunks used: ${chunkWarnings.join(', ')}`);
```

### Admin Dashboard Stats
- Total documents uploaded
- Average document size
- Token usage per function
- Documents requiring chunking

## Best Practices

### 1. Document Preparation
- ✅ Split extremely large documents before upload (>50MB)
- ✅ Use PDF/A format for better text extraction
- ✅ Include table of contents for better chunking
- ✅ Remove unnecessary images/formatting

### 2. Token Budget Allocation
- ✅ Reserve 20% of model context for conversation
- ✅ Prioritize recent/relevant documents
- ✅ Use metadata to filter before loading full content

### 3. User Experience
- ✅ Show upload progress for files >10MB
- ✅ Display estimated processing time
- ✅ Provide feedback on token usage
- ✅ Allow cancellation of long uploads

## Troubleshooting

### Issue: Upload Fails for Large Files
**Solution**: Check Supabase storage quota and increase if needed

### Issue: RAG Performance Slow
**Solution**: Implement document chunking and embedding-based retrieval

### Issue: Token Limit Exceeded
**Solution**: Increase function token limit in admin settings or implement better filtering

### Issue: Out of Memory
**Solution**: Process documents in chunks, use streaming responses

## Future Enhancements

1. **Vector Embeddings**: Use pgvector for semantic search
2. **Document Summarization**: Generate summaries for quick scanning
3. **Incremental Updates**: Update only changed sections
4. **Multi-language Support**: Handle RTL and CJK languages
5. **OCR Integration**: Extract text from scanned documents
6. **Parallel Processing**: Process multiple documents simultaneously

---

**Last Updated**: 2025-10-18  
**Version**: 2.0 (Large Document Support)
