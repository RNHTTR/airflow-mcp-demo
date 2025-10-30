from __future__ import annotations

from mcp.app import mcp
from mcp.app.manifest import load_manifest, match_deliverable_fuzzy
from mcp.app.airflow_api import trigger_dag_run, get_run_state

@mcp.tool()
def update_deliverable(workflow: str) -> dict:
    """
    Kick off the entrypoint DAG for a workflow.
    Downstream DAGs assumed to be triggered automatically via asset-aware scheduling.
    """
    record = match_deliverable_fuzzy(workflow, load_manifest())
    dag_id = record["entrypoint"]
    run_id = trigger_dag_run(dag_id)
    # state = get_run_state(dag_id, run_id)
    return {
        "workflow": record["workflow"],
        "dag_id": dag_id,
        "dag_run_id": run_id,
        # "state": state,
        # "status_resource_uri": f"airflow-run://{dag_id}/{run_id}"
    }
