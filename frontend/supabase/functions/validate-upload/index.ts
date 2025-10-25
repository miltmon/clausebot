import { createClient } from 'jsr:@supabase/supabase-js@2';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

const ALLOWED_MIME_TYPES = new Set([
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'text/plain',
  'text/markdown',
]);

const MAX_SIZE = 100 * 1024 * 1024; // 100MB

interface UploadRequest {
  fileName: string;
  fileSize: number;
  mimeType: string;
}

Deno.serve(async (req) => {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const supabase = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_ANON_KEY') ?? '',
      {
        auth: {
          persistSession: false,
        },
      }
    );

    // Verify authentication
    const authHeader = req.headers.get('Authorization');
    if (!authHeader) {
      return new Response(
        JSON.stringify({ error: 'Missing authorization header' }),
        { status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    const { data: { user }, error: authError } = await supabase.auth.getUser(
      authHeader.replace('Bearer ', '')
    );

    if (authError || !user) {
      return new Response(
        JSON.stringify({ error: 'Unauthorized' }),
        { status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    const { fileName, fileSize, mimeType }: UploadRequest = await req.json();

    // Validate file size
    if (fileSize > MAX_SIZE) {
      return new Response(
        JSON.stringify({ 
          error: 'File too large',
          details: `Maximum file size is ${MAX_SIZE / 1024 / 1024}MB` 
        }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // Validate MIME type
    if (!ALLOWED_MIME_TYPES.has(mimeType)) {
      return new Response(
        JSON.stringify({ 
          error: 'Invalid file type',
          details: `Allowed types: PDF, DOCX, TXT, MD. Received: ${mimeType}`,
          allowedTypes: Array.from(ALLOWED_MIME_TYPES)
        }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // Generate secure storage path
    const fileExtension = fileName.substring(fileName.lastIndexOf('.'));
    const sanitizedName = fileName
      .substring(0, fileName.lastIndexOf('.'))
      .replace(/[^a-z0-9_-]/gi, '_')
      .substring(0, 100); // Limit filename length
    
    const timestamp = Date.now();
    const storagePath = `user/${user.id}/${timestamp}-${sanitizedName}${fileExtension}`;

    // Log validation event
    await supabase.from('audit_events').insert({
      user_id: user.id,
      action: 'upload_validated',
      target: fileName,
      meta: { 
        size: fileSize, 
        mime: mimeType,
        storagePath 
      }
    });

    return new Response(
      JSON.stringify({ 
        success: true,
        storagePath,
        validatedMimeType: mimeType
      }),
      { 
        status: 200,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      }
    );

  } catch (error) {
    console.error('Validation error:', error);
    return new Response(
      JSON.stringify({ 
        error: 'Validation failed',
        details: error instanceof Error ? error.message : 'Unknown error'
      }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }
});