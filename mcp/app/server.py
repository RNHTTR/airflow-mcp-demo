from mcp.app import mcp

# Import modules so their decorators run and register with the shared MCP instance
from tools import deliverable

if __name__ == "__main__":
    mcp.run()
