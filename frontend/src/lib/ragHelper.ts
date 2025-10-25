import { SupabaseClient } from '@supabase/supabase-js';

interface ReferenceDocument {
  title: string;
  content_extracted: string;
  page_count: number | null;
  estimated_tokens: number | null;
}

interface RAGContext {
  context: string;
  tokenCount: number;
  docsLoaded: number;
}

/**
 * Load reference documents from the knowledge base for RAG context
 * Handles large documents with intelligent chunking and token management
 * 
 * @param supabase - Supabase client instance
 * @param functionName - Name of the AI function (for KB toggle setting)
 * @param entityName - Optional entity name for entity-specific documents
 * @returns Object containing formatted context, token count, and document count
 */
export async function loadReferenceDocuments(
  supabase: SupabaseClient,
  functionName: string,
  entityName?: string,
  maxTokenOverride?: number
): Promise<RAGContext> {
  
  try {
    // Check admin setting to enable/disable KB per function
    const { data: setting } = await supabase
      .from('admin_settings')
      .select('value')
      .eq('key', `${functionName}_use_kb`)
      .maybeSingle();
    
    if (setting?.value === 'false') {
      console.log(`KB disabled for function: ${functionName}`);
      return { context: '', tokenCount: 0, docsLoaded: 0 };
    }
    
    // Get token limit for this function (default 200000 for large docs)
    const { data: tokenSetting } = await supabase
      .from('admin_settings')
      .select('value')
      .eq('key', `${functionName}_tokens`)
      .maybeSingle();

    const maxTokens = maxTokenOverride || (tokenSetting ? parseInt(tokenSetting.value) : 200000);
    
    // Load system scope documents (highest priority)
    const { data: systemDocs } = await supabase
      .from('reference_documents')
      .select('title, content_extracted, page_count, estimated_tokens')
      .eq('scope', 'system')
      .order('priority', { ascending: false });
    
    // Load global scope documents
    const { data: globalDocs } = await supabase
      .from('reference_documents')
      .select('title, content_extracted, page_count, estimated_tokens')
      .eq('scope', 'global')
      .order('priority', { ascending: false });
    
    // Load entity-specific documents if entity name provided
    let entityDocs: ReferenceDocument[] = [];
    if (entityName) {
      const { data: artistDocs } = await supabase
        .from('reference_documents')
        .select('title, content_extracted, page_count, estimated_tokens')
        .eq('scope', 'artist')
        .ilike('artist_name', entityName)
        .order('priority', { ascending: false });
      
      const { data: entitySpecificDocs } = await supabase
        .from('reference_documents')
        .select('title, content_extracted, page_count, estimated_tokens')
        .eq('scope', 'entity')
        .ilike('entity_name', entityName)
        .order('priority', { ascending: false });
      
      entityDocs = [...(artistDocs || []), ...(entitySpecificDocs || [])];
    }
    
    // Combine all documents in priority order: system -> global -> entity-specific
    const allDocs = [
      ...(systemDocs || []),
      ...(globalDocs || []),
      ...entityDocs
    ].filter(doc => doc.content_extracted && doc.content_extracted.trim().length > 0);
    
    if (allDocs.length === 0) {
      console.log('No reference documents found');
      return { context: '', tokenCount: 0, docsLoaded: 0 };
    }
    
    // Implement token budget with intelligent chunking for large documents
    let totalTokens = 0;
    const selectedDocs: ReferenceDocument[] = [];
    const chunkWarnings: string[] = [];

    for (const doc of allDocs) {
      const docTokens = doc.estimated_tokens || Math.ceil(doc.content_extracted.length / 3.5);
      
      // If single document is larger than max tokens, take a chunk
      if (docTokens > maxTokens && selectedDocs.length === 0) {
        const chunkRatio = maxTokens / docTokens;
        const chunkSize = Math.floor(doc.content_extracted.length * chunkRatio);
        const chunkedDoc = {
          ...doc,
          content_extracted: doc.content_extracted.substring(0, chunkSize) + 
            `\n\n[Note: Document truncated. Showing ${Math.floor(chunkRatio * 100)}% of ${doc.page_count || 'N/A'} pages due to token limits. Full document: ${doc.title}]`,
          estimated_tokens: maxTokens,
        };
        selectedDocs.push(chunkedDoc);
        totalTokens = maxTokens;
        chunkWarnings.push(`${doc.title} (truncated to fit limit)`);
        break;
      }
      
      // Add document if within token limit
      if (totalTokens + docTokens <= maxTokens) {
        selectedDocs.push(doc);
        totalTokens += docTokens;
      } else {
        // Try to fit a partial document if space remains
        const remainingTokens = maxTokens - totalTokens;
        if (remainingTokens > 1000) { // Only chunk if >1000 tokens remain
          const chunkRatio = remainingTokens / docTokens;
          const chunkSize = Math.floor(doc.content_extracted.length * chunkRatio);
          const chunkedDoc = {
            ...doc,
            content_extracted: doc.content_extracted.substring(0, chunkSize) + 
              `\n\n[Note: Document truncated. Showing ${Math.floor(chunkRatio * 100)}% due to token limits.]`,
            estimated_tokens: remainingTokens,
          };
          selectedDocs.push(chunkedDoc);
          totalTokens += remainingTokens;
          chunkWarnings.push(`${doc.title} (partial)`);
        }
        console.log(`Token limit reached. Skipped: ${doc.title}`);
        break;
      }
    }
    
    // Format context with metadata
    let context = '';
    
    if (chunkWarnings.length > 0) {
      context += `[Document Loading Info: Some documents are shown partially due to size: ${chunkWarnings.join(', ')}]\n\n`;
    }
    
    context += selectedDocs.map(doc => {
      const pageInfo = doc.page_count ? ` (~${doc.page_count.toLocaleString()} pages, ${(doc.estimated_tokens || 0).toLocaleString()} tokens)` : '';
      return `
=== ${doc.title}${pageInfo} ===
${doc.content_extracted}
`;
    }).join('\n\n');
    
    console.log(`[RAG] Loaded ${selectedDocs.length}/${allDocs.length} documents, ~${totalTokens.toLocaleString()} tokens for ${functionName} (limit: ${maxTokens.toLocaleString()})`);
    
    return {
      context,
      tokenCount: totalTokens,
      docsLoaded: selectedDocs.length
    };
    
  } catch (error) {
    console.error('Error loading reference documents:', error);
    return { context: '', tokenCount: 0, docsLoaded: 0 };
  }
}

/**
 * Format prompt with RAG context for AI completions
 * 
 * @param userInput - User's input/question
 * @param referenceContext - Context from loadReferenceDocuments
 * @param systemPrompt - Optional system prompt to prepend
 * @returns Formatted prompt with context
 */
export function formatPromptWithContext(
  userInput: string,
  referenceContext: string,
  systemPrompt?: string
): string {
  const parts = [];
  
  if (systemPrompt) {
    parts.push(`=== SYSTEM INSTRUCTIONS ===\n${systemPrompt}\n`);
  }
  
  if (referenceContext) {
    parts.push(`=== REFERENCE MATERIALS ===\n${referenceContext}\n`);
  }
  
  parts.push(`=== USER INPUT ===\n${userInput}`);
  
  return parts.join('\n');
}
