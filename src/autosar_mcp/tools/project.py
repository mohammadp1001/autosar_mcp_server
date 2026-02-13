import logging
from mcp.server.fastmcp import FastMCP
from autosar_mcp.core.workspace_manager import WorkspaceManager

logger = logging.getLogger("autosar_mcp.tools.project")

def register(mcp: FastMCP, workspace_manager: WorkspaceManager):
    @mcp.tool()
    async def load_workspace(files: list[str], clear_previous: bool = False) -> str:
        """
        Loads one or more ARXML files into the active workspace.
        
        Args:
            files: List of absolute file paths to ARXML files.
            clear_previous: If True, clears the existing workspace before loading.
        """
        try:
            if clear_previous:
                workspace_manager.clear()
            
            workspace_manager.load_files(files)
            return f"Successfully loaded {len(files)} files."
        except Exception as e:
            logger.error(f"Error loading workspace: {e}")
            return f"Error: {str(e)}"

    @mcp.tool()
    async def save_workspace(target_directory: str, version: int = 51) -> str:
        """
        Writes the current in-memory workspace to ARXML files.
        
        Args:
            target_directory: Directory to save the files.
            version: Schema version (e.g., 51 for R22-11).
        """
        try:
            workspace_manager.save(target_directory, version)
            return f"Workspace saved to {target_directory} (v{version})"
        except Exception as e:
            logger.error(f"Error saving workspace: {e}")
            return f"Error: {str(e)}"

    @mcp.tool()
    async def list_packages(path: str = "/") -> str:
        """
        Lists sub-packages and elements within a given package path.
        """
        try:
            return workspace_manager.list_content(path)
        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    async def read_element(path: str) -> str:
        """
        Returns the string representation of a specific element.
        """
        try:
            return workspace_manager.get_element_str(path)
        except Exception as e:
            return f"Error: {str(e)}"
