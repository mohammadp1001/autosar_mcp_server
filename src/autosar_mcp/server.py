"""Create and configure the AUTOSAR MCP server."""
from __future__ import annotations

from mcp.server.fastmcp.server import FastMCP

from autosar_mcp.core.workspace_manager import WorkspaceManager
from autosar_mcp import tools


def create_app() -> FastMCP:
    app = FastMCP("autosar-mcp")

    manager = WorkspaceManager()
    tools.register_tools(app, manager)

    return app
