import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.39.3";

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

interface DocumentInput {
  title: string;
  description?: string;
  file_name: string;
  file_url: string;
  content_extracted: string;
  artist_name?: string;
  entity_name?: string;
  tags?: string[];
  priority?: number;
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    );

    // Verify admin authentication
    const authHeader = req.headers.get('Authorization');
    if (!authHeader) {
      throw new Error('Missing authorization header');
    }

    const token = authHeader.replace('Bearer ', '');
    const { data: { user }, error: authError } = await supabaseClient.auth.getUser(token);
    
    if (authError || !user) {
      throw new Error('Unauthorized');
    }

    // Check if user is admin
    const { data: userRole, error: roleError } = await supabaseClient
      .from('user_roles')
      .select('role')
      .eq('user_id', user.id)
      .eq('role', 'admin')
      .maybeSingle();

    if (roleError || !userRole) {
      throw new Error('Admin access required');
    }

    // Parse request body
    const { documents } = await req.json() as { documents: DocumentInput[] };
    
    if (!Array.isArray(documents) || documents.length === 0) {
      throw new Error('Documents array is required');
    }

    const results = [];

    for (const doc of documents) {
      try {
        // Estimate tokens (rough: 1 token ≈ 4 characters)
        const estimatedTokens = Math.ceil(doc.content_extracted.length / 4);

        // Insert document with system scope
        const { data, error } = await supabaseClient
          .from('reference_documents')
          .insert({
            user_id: user.id,
            title: doc.title,
            description: doc.description || null,
            file_name: doc.file_name,
            file_url: doc.file_url,
            file_size: 0, // Will be updated if needed
            file_type: 'text/plain',
            content_extracted: doc.content_extracted,
            scope: 'system',
            artist_name: doc.artist_name || null,
            entity_name: doc.entity_name || null,
            tags: doc.tags || [],
            priority: doc.priority || 0,
            estimated_tokens: estimatedTokens,
            page_count: null
          })
          .select()
          .single();

        if (error) throw error;

        results.push({
          title: doc.title,
          success: true,
          id: data.id,
          tokens: estimatedTokens
        });

        console.log(`Document "${doc.title}" loaded successfully (${estimatedTokens} tokens)`);
      } catch (docError) {
        console.error(`Error loading document "${doc.title}":`, docError);
        results.push({
          title: doc.title,
          success: false,
          error: docError instanceof Error ? docError.message : 'Unknown error'
        });
      }
    }

    const successCount = results.filter(r => r.success).length;
    console.log(`Loaded ${successCount}/${documents.length} documents successfully`);

    return new Response(
      JSON.stringify({
        success: true,
        total: documents.length,
        successful: successCount,
        failed: documents.length - successCount,
        results
      }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );

  } catch (error) {
    console.error('Error in load-reference-documents:', error);
    return new Response(
      JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }),
      { 
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    );
  }
});
