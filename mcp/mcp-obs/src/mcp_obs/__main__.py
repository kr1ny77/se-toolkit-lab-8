"""Entry point for running the observability MCP server via python -m mcp_obs."""

from mcp_obs.server import mcp

if __name__ == "__main__":
    mcp.run()
