import logging
import sys
from mcp.server.fastmcp import FastMCP
from autosar_mcp.core.workspace_manager import WorkspaceManager
# Import new tool modules
from autosar_mcp.tools import project, refactor, query

logger = logging.getLogger("autosar_mcp.server")

# Initialize FastMCP Server
mcp = FastMCP("autosar_mcp-server")

# Global Workspace Manager
workspace_manager = WorkspaceManager()

# Register Tools
logger.info("Registering tools...")
project.register(mcp, workspace_manager)
refactor.register(mcp, workspace_manager)
query.register(mcp, workspace_manager)

# Resources and Prompts can be registered here in the future
