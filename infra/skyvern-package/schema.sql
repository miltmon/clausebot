create table if not exists runs (
  run_id uuid primary key,
  run_hash char(64) not null,
  job_type text not null,
  start_ts timestamptz not null default now(),
  end_ts timestamptz,
  duration_ms int,
  status text check (status in ('pending','success','fail')) not null,
  output_schema_version text,
  output_ref text,
  error_summary text,
  operator_role text,
  retain_until timestamptz
);

create index if not exists runs_end_ts_idx on runs (end_ts);

create table if not exists outputs (
  id bigserial primary key,
  run_id uuid references runs(run_id) on delete cascade,
  created_at timestamptz not null default now(),
  schema_version text not null,
  payload jsonb not null
);

create index if not exists outputs_run_id_idx on outputs (run_id);

create table if not exists artifacts (
  id bigserial primary key,
  run_id uuid references runs(run_id) on delete cascade,
  created_at timestamptz not null default now(),
  kind text check (kind in ('screenshot','dom_snapshot','log')) not null,
  uri text not null,
  redacted boolean not null default true
);
