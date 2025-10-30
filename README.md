1. astro dev start
2. Install node/npm & update claude desktop (or adjust for LLM client of choice as needed):
```
{
  "mcpServers": {
    "airflow-mcp": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "http://localhost:8000/sse"
      ]
    }
  }
}
``` 
3. Ask your LLM to update the revenue dashboard ;)