import json, time, requests
from typing import Optional
from app.config import (
    AIRFLOW_BASE_URL,
    AIRFLOW_USERNAME, AIRFLOW_PASSWORD,
    POLL_INTERVAL_SEC, RUN_TIMEOUT_SEC
)
from datetime import datetime

# Cache for JWT token
_token_cache: Optional[dict] = None

def _get_jwt_token() -> str:
    """Get JWT token from Airflow, using cache if available."""
    global _token_cache
    
    # Check if we have a valid cached token
    if _token_cache and _token_cache.get("expires_at", 0) > time.time():
        return _token_cache["access_token"]
    
    # Get new token - note: auth endpoint does NOT use /api/v2 prefix
    print(f"Authenticating with Airflow (username: {AIRFLOW_USERNAME})")
    
    # Strip /api/v2 from base URL for auth endpoint
    auth_base_url = AIRFLOW_BASE_URL.replace("/api/v2", "")
    
    response = requests.post(
        f"{auth_base_url}/auth/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={"username": AIRFLOW_USERNAME, "password": AIRFLOW_PASSWORD},
        timeout=30
    )
    response.raise_for_status()
    
    token_data = response.json()
    access_token = token_data["access_token"]
    
    # Cache token (assume 1 hour expiry if not specified)
    _token_cache = {
        "access_token": access_token,
        "expires_at": time.time() + 3600  # 1 hour from now
    }
    
    return access_token

def _session():
    """Create a requests session with JWT authentication."""
    s = requests.Session()
    s.headers.update({
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {_get_jwt_token()}"
    })
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
    data = af_post(f"dags/{dag_id}/dagRuns", payload={"dag_run_id": dag_run_id, "logical_date": None})
    return data.get("dag_run_id", dag_run_id)

def get_run_state(dag_id: str, dag_run_id: str) -> str:
    data = af_get(f"dags/{dag_id}/dagRuns/{dag_run_id}")
    return (data.get("state") or "").lower()