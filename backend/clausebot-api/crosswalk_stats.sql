-- Supabase Crosswalk Statistics View
-- Provides real-time verification metrics for Grok monitoring

-- View: verified ratio + counts for crosswalk monitoring
create or replace view public.crosswalk_stats as
select
  count(*)::int as total,
  sum((verification_status='verified')::int)::int as verified,
  sum((verification_status='needs_review')::int)::int as needs_review,
  case when count(*)=0 then 0::numeric
       else (sum((verification_status='verified')::int)::numeric / count(*)) end as verified_ratio
from public.clauses_crosswalk;

-- Grant read access to authenticated users
grant select on public.crosswalk_stats to authenticated;

-- RLS remains enabled on base table; view is read-only public
-- This view supports the Grok watchpoint: verified_ratio < 0.50 threshold
