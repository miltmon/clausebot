-- ClauseBot Usage Events Table for Telemetry and Cost Tracking
-- Run this in your Supabase SQL editor

-- Create usage_events table for AI model usage tracking
create table if not exists public.usage_events (
  id bigserial primary key,
  ts timestamptz default now(),
  user_id text,
  provider_model text not null,
  input_tokens int default 0,
  output_tokens int default 0,
  estimated_usd numeric(10,4) default 0,
  actual_usd numeric(10,4),
  latency_ms int,
  prompt_hash text,
  endpoint text,
  success boolean default true,
  error_message text,
  metadata jsonb
);

-- Indexes for performance
create index if not exists idx_usage_events_ts on public.usage_events (ts desc);
create index if not exists idx_usage_events_user_id on public.usage_events (user_id);
create index if not exists idx_usage_events_provider_model on public.usage_events (provider_model);
create index if not exists idx_usage_events_success on public.usage_events (success);

-- RLS policies
alter table public.usage_events enable row level security;

-- Allow service role to insert and read
create policy "usage_events_service_insert" on public.usage_events
  for insert to service_role with check (true);

create policy "usage_events_service_select" on public.usage_events
  for select to service_role using (true);

-- Allow public read access for aggregated metrics (no PII)
create policy "usage_events_public_select" on public.usage_events
  for select using (true);

-- Create view for daily cost aggregation
create or replace view public.v_daily_costs as
select 
  date_trunc('day', ts) as date,
  provider_model,
  count(*) as requests,
  sum(input_tokens) as total_input_tokens,
  sum(output_tokens) as total_output_tokens,
  sum(estimated_usd) as estimated_cost_usd,
  sum(actual_usd) as actual_cost_usd,
  avg(latency_ms) as avg_latency_ms,
  count(*) filter (where success = false) as error_count
from public.usage_events
group by date_trunc('day', ts), provider_model
order by date desc, provider_model;

-- Create view for real-time metrics
create or replace view public.v_usage_metrics_24h as
select 
  provider_model,
  count(*) as requests_24h,
  sum(estimated_usd) as cost_24h_usd,
  avg(latency_ms) as avg_latency_ms,
  count(*) filter (where success = false) as errors_24h,
  max(ts) as last_request
from public.usage_events
where ts >= now() - interval '24 hours'
group by provider_model;

-- Grant permissions on views
grant select on public.v_daily_costs to public;
grant select on public.v_usage_metrics_24h to public;

-- Function to log usage event (called from API)
create or replace function public.log_usage_event(
  p_user_id text default null,
  p_provider_model text default 'openai:gpt-4',
  p_input_tokens int default 0,
  p_output_tokens int default 0,
  p_estimated_usd numeric default 0,
  p_latency_ms int default 0,
  p_prompt_hash text default null,
  p_endpoint text default '/api/assist',
  p_success boolean default true,
  p_error_message text default null,
  p_metadata jsonb default '{}'::jsonb
) returns bigint as $$
declare
  event_id bigint;
begin
  insert into public.usage_events (
    user_id, provider_model, input_tokens, output_tokens, 
    estimated_usd, latency_ms, prompt_hash, endpoint, 
    success, error_message, metadata
  ) values (
    p_user_id, p_provider_model, p_input_tokens, p_output_tokens,
    p_estimated_usd, p_latency_ms, p_prompt_hash, p_endpoint,
    p_success, p_error_message, p_metadata
  ) returning id into event_id;
  
  return event_id;
end;
$$ language plpgsql security definer;

-- Grant execute permission on function
grant execute on function public.log_usage_event to public;

-- Sample data for testing (optional)
insert into public.usage_events (
  user_id, provider_model, input_tokens, output_tokens, 
  estimated_usd, latency_ms, endpoint, success
) values 
  ('test-user', 'openai:gpt-4', 150, 75, 0.0135, 1250, '/api/assist', true),
  ('test-user', 'anthropic:claude-3-sonnet', 200, 100, 0.0045, 980, '/api/assist', true),
  ('cursor-system', 'openai:gpt-4', 300, 150, 0.027, 1800, '/api/cursor/incident', true);

-- Verify setup
select 'Usage events table created successfully' as status;
select * from public.v_usage_metrics_24h;
select * from public.v_daily_costs limit 5;
