import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.39.3";

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

interface ReferenceDocument {
  title: string;
  content_extracted: string;
  page_count: number | null;
  estimated_tokens: number | null;
}

async function loadReferenceDocuments(
  supabase: any,
  functionName: string,
  entityName?: string
): Promise<{ context: string; tokenCount: number; docsLoaded: number }> {
  
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
    
    // Load documents in priority order: system -> global -> entity-specific
    const { data: systemDocs } = await supabase
      .from('reference_documents')
      .select('title, content_extracted, page_count, estimated_tokens')
      .eq('scope', 'system')
      .order('priority', { ascending: false });
    
    const { data: globalDocs } = await supabase
      .from('reference_documents')
      .select('title, content_extracted, page_count, estimated_tokens')
      .eq('scope', 'global')
      .order('priority', { ascending: false });
    
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
    
    // Combine and format context
    const allDocs = [...(systemDocs || []), ...(globalDocs || []), ...entityDocs]
      .filter(doc => doc.content_extracted && doc.content_extracted.trim().length > 0);
    
    const context = allDocs.map(doc => {
      const pageInfo = doc.page_count ? ` (${doc.page_count} pages)` : '';
      return `
=== ${doc.title}${pageInfo} ===
${doc.content_extracted}
`;
    }).join('\n\n');
    
    const totalTokens = allDocs.reduce((sum, doc) => 
      sum + (doc.estimated_tokens || Math.ceil(doc.content_extracted.length / 4)), 
      0
    );
    
    console.log(`Loaded ${allDocs.length} documents (${totalTokens} tokens)`);
    
    return { context, tokenCount: totalTokens, docsLoaded: allDocs.length };
    
  } catch (error) {
    console.error('Error loading reference documents:', error);
    return { context: '', tokenCount: 0, docsLoaded: 0 };
  }
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const { question, entityName } = await req.json();
    
    if (!question) {
      throw new Error('Question is required');
    }

    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_ANON_KEY') ?? ''
    );

    const LOVABLE_API_KEY = Deno.env.get('LOVABLE_API_KEY');
    if (!LOVABLE_API_KEY) {
      throw new Error('LOVABLE_API_KEY not configured');
    }

    // Load knowledge base documents
    const { context: referenceContext, tokenCount, docsLoaded } = 
      await loadReferenceDocuments(supabaseClient, 'ai-rag-example', entityName);

    console.log(`KB Context: ${docsLoaded} docs, ${tokenCount} tokens`);

    // Check token limit setting
    const { data: tokenSetting } = await supabaseClient
      .from('admin_settings')
      .select('value')
      .eq('key', 'ai_rag_example_tokens')
      .maybeSingle();

    const maxTokens = tokenSetting?.value ? parseInt(tokenSetting.value) : 4096;

    // Construct prompt with reference materials
    const prompt = referenceContext 
      ? `=== REFERENCE MATERIALS ===\n${referenceContext}\n\n=== USER QUESTION ===\n${question}`
      : question;

    // Call Lovable AI
    const response = await fetch('https://ai.gateway.lovable.dev/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${LOVABLE_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'google/gemini-2.5-flash',
        messages: [
          {
            role: 'system',
            content: 'You are a helpful assistant. Answer based on the reference materials provided when available.'
          },
          {
            role: 'user',
            content: prompt
          }
        ],
        max_tokens: maxTokens
      })
    });

    if (!response.ok) {
      if (response.status === 429) {
        throw new Error('Rate limits exceeded, please try again later.');
      }
      if (response.status === 402) {
        throw new Error('Payment required, please add funds to your Lovable AI workspace.');
      }
      const errorText = await response.text();
      console.error('AI gateway error:', response.status, errorText);
      throw new Error('AI gateway error');
    }

    const data = await response.json();
    const answer = data.choices?.[0]?.message?.content;

    if (!answer) {
      throw new Error('No answer generated');
    }

    return new Response(
      JSON.stringify({
        answer,
        metadata: {
          docsLoaded,
          tokensUsed: tokenCount,
          model: 'google/gemini-2.5-flash'
        }
      }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );

  } catch (error) {
    console.error('Error in ai-rag-example:', error);
    return new Response(
      JSON.stringify({
        error: error instanceof Error ? error.message : 'Unknown error'
      }),
      { 
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    );
  }
});
