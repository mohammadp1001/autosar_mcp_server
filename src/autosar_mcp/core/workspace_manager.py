"""Workspace management helpers for the AUTOSAR MCP server.

This module provides an in-memory, ID-based API over ``autosar.xml.Workspace``.
The server/tool layer exchanges string IDs instead of passing Python objects.
"""

import os
from typing import Any, Optional

import autosar.xml
import autosar.xml.reader as ar_reader
import autosar.xml.writer as ar_writer

from autosar_mcp.core.registry import ObjectRegistry


class WorkspaceManager:
    """
    MCP-ready Workspace manager using ObjectRegistry.
    All objects are accessed via IDs.
    """

    def __init__(self):
        """Initializes the workspace manager with an empty registry.

        Args:
            None.

        Returns:
            None.
        """
        self.registry = ObjectRegistry()

    # --------------------------------------------------
    # Workspace lifecycle
    # --------------------------------------------------

    def create_workspace(self) -> str:
        """Creates a new AUTOSAR workspace and returns its registry ID.

        Args:
            None.

        Returns:
            Workspace ID (e.g. ``ws_<uuid>``).
        """
        ws = autosar.xml.Workspace()
        return self.registry.put(ws, prefix="ws")

    def delete_workspace(self, workspace_id: str) -> None:
        """Deletes a workspace from the registry.

        Args:
            workspace_id: Workspace ID to delete.

        Returns:
            None.
        """
        self.registry.delete(workspace_id)

    def reset_workspace(self, workspace_id: str) -> None:
        """Resets an existing workspace ID to a new empty workspace.

        Args:
            workspace_id: Workspace ID to reset.

        Returns:
            None.

        Raises:
            KeyError: If the workspace ID does not exist.
            TypeError: If the ID exists but is not a workspace.
        """
        self.registry.get(workspace_id, autosar.xml.Workspace)
        new_ws = autosar.xml.Workspace()
        self.registry._store[workspace_id] = new_ws  # overwrite safely

    # --------------------------------------------------
    # ARXML I/O
    # --------------------------------------------------

    def load_arxml(self, workspace_id: str, file_path: str) -> None:
        """Loads an ARXML file into a workspace.

        Args:
            workspace_id: Workspace ID to load into.
            file_path: Path to an ARXML file.

        Returns:
            None.

        Raises:
            FileNotFoundError: If ``file_path`` does not exist.
            KeyError: If the workspace ID does not exist.
            TypeError: If the ID exists but is not a workspace.
        """
        ws = self.registry.get(workspace_id, autosar.xml.Workspace)

        if not os.path.exists(file_path):
            raise FileNotFoundError(file_path)

        reader = ar_reader.Reader()
        document = reader.read_file(file_path)

        for package in document.packages:
            ws.append(package)

    # TODO: consider supporting older schema versions (e.g. 48-51) as a policy option.
    def save_arxml(self, workspace_id: str, file_path: str, version: int = 51) -> None:
        """Saves a workspace into an ARXML file.

        Args:
            workspace_id: Workspace ID to save.
            file_path: Destination ARXML path to write.
            version: AUTOSAR schema version for writing (default: 51).

        Returns:
            None.

        Raises:
            KeyError: If the workspace ID does not exist.
            TypeError: If the ID exists but is not a workspace.
        """
        ws = self.registry.get(workspace_id, autosar.xml.Workspace)

        document = autosar.xml.Document(
            packages=ws.packages,
            schema_version=version
        )

        writer = ar_writer.Writer(schema_version=version)
        writer.write_file(document, file_path)

    # --------------------------------------------------
    # Package Map
    # --------------------------------------------------

    def create_package_map(self, workspace_id: str, mapping: dict[str, str]) -> None:
        """Creates/overwrites a package map for a workspace.

        Args:
            workspace_id: Workspace ID to update.
            mapping: Mapping from package key to AUTOSAR path.

        Returns:
            None.

        Raises:
            KeyError: If the workspace ID does not exist.
            TypeError: If the ID exists but is not a workspace.
        """
        ws = self.registry.get(workspace_id, autosar.xml.Workspace)
        ws.create_package_map(mapping)

    # --------------------------------------------------
    # Query helpers (LLM-safe)
    # --------------------------------------------------

    def find_element(self, workspace_id: str, path: str) -> dict | None:
        """Finds an element by AUTOSAR path and returns a safe summary dict.

        Args:
            workspace_id: Workspace ID to query.
            path: AUTOSAR absolute path to search for.

        Returns:
            A small dictionary describing the element (type/name/ref), or None if
            not found.
        """
        ws = self.registry.get(workspace_id, autosar.xml.Workspace)
        element = ws.find(path)

        if element is None:
            return None

        return {
            "type": element.__class__.__name__,
            "name": getattr(element, "name", None),
            "ref": str(element.ref()) if hasattr(element, "ref") else None,
        }

    def list_root_packages(self, workspace_id: str) -> list[str]:
        """Lists root package names for a workspace.

        Args:
            workspace_id: Workspace ID to query.

        Returns:
            List of root package names.
        """
        ws = self.registry.get(workspace_id, autosar.xml.Workspace)
        return [pkg.name for pkg in ws.packages]

    def get_workspace(self, workspace_id: str) -> autosar.xml.Workspace:
        """Returns the underlying AUTOSAR workspace object for an ID.

        Args:
            workspace_id: Workspace ID to retrieve.

        Returns:
            The ``autosar.xml.Workspace`` instance.

        Raises:
            KeyError: If the workspace ID does not exist.
            TypeError: If the ID exists but is not a workspace.
        """
        return self.registry.get(workspace_id, autosar.xml.Workspace)

    def get_element(self, workspace_id: str, path: str) -> Optional[Any]:
        """Returns a raw AUTOSAR element by path.

        Args:
            workspace_id: Workspace ID to query.
            path: AUTOSAR absolute path to search for.

        Returns:
            The found element object, or None if not found.
        """
        ws = self.get_workspace(workspace_id)
        return ws.find(path)
