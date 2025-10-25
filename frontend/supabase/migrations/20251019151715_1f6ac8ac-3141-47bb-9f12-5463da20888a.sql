-- Create document scope enum
CREATE TYPE document_scope AS ENUM ('system', 'global', 'entity');

-- Create reference_documents table
CREATE TABLE public.reference_documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  file_name TEXT NOT NULL,
  file_path TEXT NOT NULL,
  file_size BIGINT,
  file_type TEXT,
  content TEXT,
  scope document_scope NOT NULL DEFAULT 'global',
  entity_name TEXT,
  tags TEXT[],
  metadata JSONB,
  uploaded_at TIMESTAMPTZ DEFAULT now(),
  processed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Create admin_settings table
CREATE TABLE public.admin_settings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  key TEXT UNIQUE NOT NULL,
  value JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Enable RLS
ALTER TABLE public.reference_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.admin_settings ENABLE ROW LEVEL SECURITY;

-- RLS policies for reference_documents (allow all authenticated users to read/write for now)
CREATE POLICY "Allow authenticated users to view documents"
  ON public.reference_documents FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Allow authenticated users to insert documents"
  ON public.reference_documents FOR INSERT
  TO authenticated
  WITH CHECK (true);

CREATE POLICY "Allow authenticated users to delete documents"
  ON public.reference_documents FOR DELETE
  TO authenticated
  USING (true);

-- RLS policies for admin_settings (allow all authenticated users)
CREATE POLICY "Allow authenticated users to view settings"
  ON public.admin_settings FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Allow authenticated users to insert settings"
  ON public.admin_settings FOR INSERT
  TO authenticated
  WITH CHECK (true);

CREATE POLICY "Allow authenticated users to update settings"
  ON public.admin_settings FOR UPDATE
  TO authenticated
  USING (true);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add triggers for updated_at
CREATE TRIGGER update_reference_documents_updated_at
  BEFORE UPDATE ON public.reference_documents
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_admin_settings_updated_at
  BEFORE UPDATE ON public.admin_settings
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Create indexes
CREATE INDEX idx_reference_documents_user_id ON public.reference_documents(user_id);
CREATE INDEX idx_reference_documents_scope ON public.reference_documents(scope);
CREATE INDEX idx_reference_documents_entity_name ON public.reference_documents(entity_name);
CREATE INDEX idx_admin_settings_key ON public.admin_settings(key);

-- Create storage bucket for documents
INSERT INTO storage.buckets (id, name, public)
VALUES ('documents', 'documents', false);

-- Storage policies for documents bucket
CREATE POLICY "Authenticated users can upload documents"
  ON storage.objects FOR INSERT
  TO authenticated
  WITH CHECK (bucket_id = 'documents');

CREATE POLICY "Authenticated users can view documents"
  ON storage.objects FOR SELECT
  TO authenticated
  USING (bucket_id = 'documents');

CREATE POLICY "Authenticated users can delete documents"
  ON storage.objects FOR DELETE
  TO authenticated
  USING (bucket_id = 'documents');