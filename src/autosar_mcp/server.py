"""The main entry point of """
from __future__ import annotations

from mcp.server.fastmcp.server import FastMCP

from autosar_mcp.core.workspace_manager import WorkspaceManager
from autosar_mcp import tools

# Create MCP app
app = FastMCP("autosar-mcp")

# Create backend manager (holds ObjectRegistry)
manager = WorkspaceManager()

# Register tools
tools.register_tools(app, manager)


def get_app() -> FastMCP:
    """Optional helper for tests/embedding."""
    return app


if __name__ == "__main__":
    # Depending on your FastMCP version, this might be `app.run()` or `app.serve()`.
    # Keep one; adjust if your runtime expects a different entrypoint.
    app.run()
