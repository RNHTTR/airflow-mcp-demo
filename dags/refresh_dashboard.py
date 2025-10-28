from __future__ import annotations
import os
import pendulum
import requests
from airflow import DAG
from airflow.decorators import task
from airflow.providers.postgres.hooks.postgres import PostgresHook

CONN_ID = os.getenv("PG_ANALYTICS_CONN_ID", "PG_ANALYTICS")

# optional Metabase env (put in .env)
MB_URL = os.getenv("METABASE_URL", "http://metabase:3000")
MB_USER = os.getenv("METABASE_USERNAME") or None
MB_PASS = os.getenv("METABASE_PASSWORD") or None
MB_CARD_ID = os.getenv("METABASE_CARD_ID")  # e.g., "1"

with DAG(
    dag_id="refresh_dashboard",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule=None,
    catchup=False,
    tags=["exec_dashboard"],
    doc_md="Refreshes mv_exec_kpis and optionally warms a Metabase card.",
) as dag:

    @task
    def ensure_objects():
        sql = """
        CREATE MATERIALIZED VIEW IF NOT EXISTS analytics.mv_exec_kpis AS
        SELECT
          DATE_TRUNC('month', opened_month) AS month,
          SUM(CASE WHEN is_new_acv THEN acv ELSE 0 END) AS new_acv,
          SUM(acv) AS total_pipeline
        FROM analytics.fct_pipeline_enriched
        GROUP BY 1;

        CREATE OR REPLACE FUNCTION analytics.refresh_exec_kpis() RETURNS void
        LANGUAGE plpgsql AS $$
        BEGIN
          REFRESH MATERIALIZED VIEW CONCURRENTLY analytics.mv_exec_kpis;
        END $$;
        """
        PostgresHook(CONN_ID).run(sql)

    @task
    def refresh_mv():
        PostgresHook(CONN_ID).run("SELECT analytics.refresh_exec_kpis();")

    @task
    def warm_metabase():
        # only attempt if creds and card id provided
        if not (MB_USER and MB_PASS and MB_CARD_ID):
            return "metabase: skipped (not configured)"
        try:
            s = requests.Session()
            r = s.post(f"{MB_URL}/api/session", json={"username": MB_USER, "password": MB_PASS}, timeout=15)
            r.raise_for_status()
            q = s.post(f"{MB_URL}/api/card/{int(MB_CARD_ID)}/query", json={}, timeout=30)
            q.raise_for_status()
            return f"metabase: warmed card {MB_CARD_ID}"
        except Exception as e:
            # non-fatal in local demo; log the error string
            return f"metabase: warm failed: {e}"

    ensure_objects() >> refresh_mv() >> warm_metabase()
