from __future__ import annotations
import os
import pendulum
from airflow.sdk import DAG, Asset, task
from airflow.providers.postgres.hooks.postgres import PostgresHook

CONN_ID = os.getenv("PG_ANALYTICS_CONN_ID", "PG_ANALYTICS")

with DAG(
    dag_id="enrich",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule=[Asset("enrich")],
    catchup=False,
    tags=["exec_dashboard"],
    doc_md="Creates/updates analytics.fct_pipeline_enriched from raw_salesforce_oppty.",
) as dag:

    @task
    def ensure_table():
        ddl = """
        CREATE TABLE IF NOT EXISTS analytics.fct_pipeline_enriched (
          id TEXT PRIMARY KEY,
          is_new_acv BOOLEAN,
          acv NUMERIC,
          opened_month DATE
        );
        """
        PostgresHook(CONN_ID).run(ddl)

    @task(outlets=[Asset("refresh_dashboard")])
    def transform():
        sql = """
        INSERT INTO analytics.fct_pipeline_enriched (id, is_new_acv, acv, opened_month)
        SELECT r.id,
               (r.stage = 'Closed Won') AS is_new_acv,
               CASE WHEN r.stage = 'Closed Won' THEN r.amount ELSE 0 END AS acv,
               DATE_TRUNC('month', r.created_at)::date AS opened_month
        FROM analytics.raw_salesforce_oppty r
        ON CONFLICT (id) DO UPDATE SET
          is_new_acv   = EXCLUDED.is_new_acv,
          acv          = EXCLUDED.acv,
          opened_month = EXCLUDED.opened_month;
        """
        PostgresHook(CONN_ID).run(sql)

    ensure_table() >> transform()
