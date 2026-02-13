import logging
import autosar.xml.element as ar_element
import autosar
from mcp.server.fastmcp import FastMCP
from autosar_mcp.core.workspace_manager import WorkspaceManager

logger = logging.getLogger("autosar_mcp.tools.query")

def register(mcp: FastMCP, manager: WorkspaceManager):
    @mcp.tool()
    async def run_python_script(script_content: str) -> str:
        """
        Executes a Python script to manipulate the workspace directly.
        
        The script has access to:
        - `workspace`: The autosar.xml.Workspace object.
        - `ar_element`: The autosar.xml.element module.
        - `manager`: The WorkspaceManager instance.
        """
        try:
            local_scope = {
                "workspace": manager.workspace,
                "ar_element": ar_element,
                "manager": manager,
                "autosar": autosar
            }
            exec(script_content, {}, local_scope)
            return "Script executed successfully."
        except Exception as e:
            return f"Error executing script: {str(e)}"
