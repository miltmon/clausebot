-- Create codes table for reference standards
CREATE TABLE public.codes (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  edition TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create clauses table for parsed code sections
CREATE TABLE public.clauses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code_id TEXT REFERENCES public.codes(id) ON DELETE CASCADE,
  clause_ref TEXT NOT NULL,
  text TEXT,
  meta JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create user_documents junction table
CREATE TABLE public.user_documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  doc_id UUID REFERENCES public.reference_documents(id) ON DELETE CASCADE NOT NULL,
  status TEXT DEFAULT 'uploaded' CHECK (status IN ('uploaded', 'queued', 'parsed', 'failed')),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, doc_id)
);

-- Enable RLS on all tables
ALTER TABLE public.codes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.clauses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_documents ENABLE ROW LEVEL SECURITY;

-- Clauses are public reference material (read-only for all authenticated users)
CREATE POLICY "Anyone can read clauses"
  ON public.clauses FOR SELECT
  USING (true);

CREATE POLICY "Only admins can insert clauses"
  ON public.clauses FOR INSERT
  WITH CHECK (false);

-- Codes are public reference material
CREATE POLICY "Anyone can read codes"
  ON public.codes FOR SELECT
  USING (true);

CREATE POLICY "Only admins can insert codes"
  ON public.codes FOR INSERT
  WITH CHECK (false);

-- User documents: users can only see their own
CREATE POLICY "Users can read their own user_documents"
  ON public.user_documents FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own user_documents"
  ON public.user_documents FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own user_documents"
  ON public.user_documents FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own user_documents"
  ON public.user_documents FOR DELETE
  USING (auth.uid() = user_id);

-- Update reference_documents RLS to be user-scoped properly
DROP POLICY IF EXISTS "Allow authenticated users to view documents" ON public.reference_documents;
DROP POLICY IF EXISTS "Allow authenticated users to insert documents" ON public.reference_documents;
DROP POLICY IF EXISTS "Allow authenticated users to delete documents" ON public.reference_documents;

CREATE POLICY "Users can read their own documents"
  ON public.reference_documents FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own documents"
  ON public.reference_documents FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own documents"
  ON public.reference_documents FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own documents"
  ON public.reference_documents FOR DELETE
  USING (auth.uid() = user_id);

-- Seed initial code standards
INSERT INTO public.codes (id, title, edition) VALUES
  ('aws_d1_1', 'AWS D1.1 Structural Welding Code - Steel', '2025'),
  ('asme_ix', 'ASME Section IX Welding and Brazing Qualifications', '2023'),
  ('api_1104', 'API 1104 Welding of Pipelines and Related Facilities', '2021'),
  ('nbb_i', 'NBBI National Board Inspection Code', '2023')
ON CONFLICT (id) DO NOTHING;