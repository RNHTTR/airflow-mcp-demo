\connect analytics

create schema if not exists analytics;

create table if not exists analytics.raw_salesforce_oppty (
  id text primary key,
  created_at timestamp not null,
  stage text,
  amount numeric,
  close_date date
);

create table if not exists analytics.fct_pipeline_enriched (
  id text primary key,
  is_new_acv boolean,
  acv numeric,
  opened_month date
);

create materialized view if not exists analytics.mv_exec_kpis as
select
  date_trunc('month', opened_month) as month,
  sum(case when is_new_acv then acv else 0 end) as new_acv,
  sum(acv) as total_pipeline
from analytics.fct_pipeline_enriched
group by 1;

create or replace function analytics.refresh_exec_kpis() returns void language plpgsql as $$
begin
  refresh materialized view concurrently analytics.mv_exec_kpis;
end $$;
