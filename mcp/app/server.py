from app import mcp

# Import modules so their decorators run and register with the shared MCP instance
from tools import deliverable

if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8000)
