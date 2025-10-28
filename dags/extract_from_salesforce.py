# requirements: faker, psycopg2-binary
from __future__ import annotations
import os
from typing import List, Tuple
import random
from datetime import datetime

import pendulum
from airflow import DAG
from airflow.decorators import task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from faker import Faker
from psycopg2.extras import execute_values

CONN_ID = os.getenv("PG_ANALYTICS_CONN_ID", "PG_ANALYTICS")

default_args = {
    "owner": "data",
    "retries": 0,
}

with DAG(
    dag_id="extract_from_salesforce",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule=None,
    catchup=False,
    default_args=default_args,
    tags=["exec_dashboard"],
    doc_md="""
    Generates *incremental* fake opps and upserts them into
    analytics.raw_salesforce_oppty for local demos.
    """,
) as dag:

    @task
    def ensure_tables():
        sql = """
        CREATE SCHEMA IF NOT EXISTS analytics;

        CREATE TABLE IF NOT EXISTS analytics.raw_salesforce_oppty (
          id TEXT PRIMARY KEY,
          created_at TIMESTAMP NOT NULL,
          stage TEXT,
          amount NUMERIC,
          close_date DATE
        );
        """
        hook = PostgresHook(postgres_conn_id=CONN_ID)
        hook.run(sql)

    @task
    def generate_and_load(n_rows: int = 50) -> int:
        fake = Faker()
        stages = ["Prospecting", "Proposal", "Closed Won", "Closed Lost"]
        rows: List[Tuple[str, datetime, str, float, str]] = []

        for _ in range(n_rows):
            oid = fake.uuid4()
            created_at = datetime.utcnow()
            stage = random.choice(stages)
            amount = round(random.uniform(1_000, 50_000), 2)
            close_date = fake.date_between(start_date="-60d", end_date="+30d")
            rows.append((oid, created_at, stage, amount, close_date))

        upsert_sql = """
        INSERT INTO analytics.raw_salesforce_oppty
          (id, created_at, stage, amount, close_date)
        VALUES %s
        ON CONFLICT (id) DO UPDATE SET
          created_at = EXCLUDED.created_at,
          stage      = EXCLUDED.stage,
          amount     = EXCLUDED.amount,
          close_date = EXCLUDED.close_date;
        """

        hook = PostgresHook(postgres_conn_id=CONN_ID)
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                execute_values(cur, upsert_sql, rows, page_size=200)
            conn.commit()

        return len(rows)

    ensure_tables() >> generate_and_load()
