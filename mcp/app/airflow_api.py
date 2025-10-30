import json, time, requests
from mcp.app.config import (
    AIRFLOW_BASE_URL,
    AIRFLOW_USERNAME, AIRFLOW_PASSWORD,
    POLL_INTERVAL_SEC, RUN_TIMEOUT_SEC
)

def _session():
    s = requests.Session()
    s.headers.update({"Accept":"application/json","Content-Type":"application/json"})
    s.auth = (AIRFLOW_USERNAME, AIRFLOW_PASSWORD)
    return s

def af_post(path: str, payload: dict) -> dict:
    r = _session().post(f"{AIRFLOW_BASE_URL}/{path}", data=json.dumps(payload), timeout=30)
    r.raise_for_status()
    return r.json()

def af_get(path: str) -> dict:
    r = _session().get(f"{AIRFLOW_BASE_URL}/{path}", timeout=30)
    r.raise_for_status()
    return r.json()

def trigger_dag_run(dag_id: str, run_id_prefix: str = "mcp") -> str:
    dag_run_id = f"{run_id_prefix}_{dag_id}_{int(time.time())}"
    data = af_post(f"/dags/{dag_id}/dagRuns", payload={"dag_run_id": dag_run_id})
    return data.get("dag_run_id", dag_run_id)

def get_run_state(dag_id: str, dag_run_id: str) -> str:
    data = af_get(f"/dags/{dag_id}/dagRuns/{dag_run_id}")
    return (data.get("state") or "").lower()
