import logging
import sys
from mcp.server.fastmcp import FastMCP
from .core.workspace_manager import WorkspaceManager
# Import new tool modules
from .tools import project, refactor, query

# Configure logging (redundant if using logging_conf, but safe)
# logging_conf is called in main.py, but server might be imported separately
logger = logging.getLogger("autosar_mcp.server")

# Initialize FastMCP Server
mcp = FastMCP("autosar-mcp-server")

# Global Workspace Manager
workspace_manager = WorkspaceManager()

# Register Tools
logger.info("Registering tools...")
project.register(mcp, workspace_manager)
refactor.register(mcp, workspace_manager)
query.register(mcp, workspace_manager)

# Resources and Prompts can be registered here in the future
