"""
Global configuration for the Airflow MCP server.
Uses environment variables for runtime overrides.

Import it anywhere with:
    from mcp.app.config import AIRFLOW_BASE_URL, AIRFLOW_USERNAME, ...
"""

import os

# --- Airflow REST API connection ---
AIRFLOW_BASE_URL: str = os.getenv("AIRFLOW_BASE_URL")

# Authentication
AIRFLOW_USERNAME: str | None = os.getenv("AIRFLOW_USERNAME", "admin")
AIRFLOW_PASSWORD: str | None = os.getenv("AIRFLOW_PASSWORD", "admin")

# --- Manifest configuration ---
MANIFEST_PATH: str | None = os.getenv("MANIFEST_PATH")

# --- Runtime settings ---
POLL_INTERVAL_SEC: int = int(os.getenv("POLL_INTERVAL_SEC", "3"))
RUN_TIMEOUT_SEC: int = int(os.getenv("RUN_TIMEOUT_SEC", str(20 * 60)))  # default 20 minutes

# --- Defaults / constants ---
DEFAULT_MANIFEST = [
    {
        "workflow": "Revenue Dashboard",
        "entrypoint": "extract_from_salesforce",
    }
]
