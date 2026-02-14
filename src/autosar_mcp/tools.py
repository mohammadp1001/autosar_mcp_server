"""Tool registrations for the AUTOSAR MCP server."""

# pylint: disable=missing-function-docstring,broad-exception-caught, line-too-long

from __future__ import annotations

from typing import Any, Optional
import logging

import autosar.xml.element as ar_element
import autosar.xml.enumeration as ar_enum
import autosar.xml as ar_xml

from autosar_mcp import models
from autosar_mcp.core.workspace_manager import WorkspaceManager

logger = logging.getLogger("autosar_mcp.tools.tools")

def register_tools(mcp: Any, manager: WorkspaceManager) -> None:
    """
    Register MCP tools on a FastMCP instance.
    """

    def _get_workspace(workspace_id: str) -> ar_xml.Workspace:
        return manager.get_workspace(workspace_id)

    def _get_element(workspace: ar_xml.Workspace, path: str):
        return workspace.find(path)

    def _ensure_package(workspace: ar_xml.Workspace, package_path: str) -> ar_element.Package:
        # Workspace.make_packages expects a ref WITHOUT leading '/'
        ref = package_path[1:] if package_path.startswith("/") else package_path
        if not ref:
            raise ValueError("package_path cannot be '/'")
        return workspace.make_packages(ref)

    def _parse_byte_order(value: Optional[str]) -> Optional[ar_enum.ByteOrder]:
        if value is None:
            return None
        # Map strings to enums if possible; keep strict & explicit.
        mapping = {
            "BIG_ENDIAN": ar_enum.ByteOrder.BIG_ENDIAN,
            "LITTLE_ENDIAN": ar_enum.ByteOrder.LITTLE_ENDIAN,
            "OPAQUE": ar_enum.ByteOrder.OPAQUE,
        }
        if value not in mapping:
            raise ValueError(f"Invalid byte_order '{value}'. Allowed: {', '.join(mapping.keys())}")
        return mapping[value]

    @mcp.tool()
    async def create_workspace() -> dict[str, Any]:
        ws_id = manager.create_workspace()
        return models.CreateWorkspaceOut(workspace_id=ws_id).model_dump()

    @mcp.tool()
    async def reset_workspace(workspace_id: str) -> dict[str, Any]:
        req = models.WorkspaceIdIn(workspace_id=workspace_id)
        manager.reset_workspace(req.workspace_id)
        return {"ok": True}

    @mcp.tool()
    async def delete_workspace(workspace_id: str) -> dict[str, Any]:
        req = models.WorkspaceIdIn(workspace_id=workspace_id)
        manager.delete_workspace(req.workspace_id)
        return {"ok": True}

    @mcp.tool()
    async def load_arxml(workspace_id: str, file_path: str) -> dict[str, Any]:
        req = models.LoadArxmlIn(workspace_id=workspace_id, file_path=file_path)
        manager.load_arxml(req.workspace_id, req.file_path)
        return {"ok": True}

    @mcp.tool()
    async def save_arxml(workspace_id: str, file_path: str, version: int = 51) -> dict[str, Any]:
        req = models.SaveArxmlIn(workspace_id=workspace_id, file_path=file_path, version=version)
        manager.save_arxml(req.workspace_id, req.file_path, req.version)
        return {"ok": True}

    @mcp.tool()
    async def create_package_map(workspace_id: str, mapping: dict[str, str]) -> dict[str, Any]:
        req = models.CreatePackageMapIn(workspace_id=workspace_id, mapping=mapping)
        manager.create_package_map(req.workspace_id, req.mapping)
        return {"ok": True}

    @mcp.tool()
    async def find_element(workspace_id: str, path: str) -> dict[str, Any]:
        req = models.FindElementIn(workspace_id=workspace_id, path=path)
        elem = manager.find_element(req.workspace_id, req.path)
        out = models.FindElementOut(found=elem is not None, element=elem)
        return out.model_dump()

    @mcp.tool()
    async def list_root_packages(workspace_id: str) -> dict[str, Any]:
        req = models.WorkspaceIdIn(workspace_id=workspace_id)
        pkgs = manager.list_root_packages(req.workspace_id)
        return models.ListRootPackagesOut(packages=pkgs).model_dump()

    @mcp.tool()
    async def create_swc_internal_behavior(workspace_id: str, component_path: str) -> dict:
        manager.create_swc_internal_behavior(workspace_id, component_path)
        return {"ok": True}


    @mcp.tool()
    async def create_runnable(workspace_id: str, component_path: str, runnable_name: str, symbol: str) -> dict:
        manager.create_runnable(workspace_id, component_path, runnable_name, symbol)
        return {"ok": True}


    @mcp.tool()
    async def create_timing_event(workspace_id: str, component_path: str, runnable_name: str, period: float) -> dict:
        manager.create_timing_event(workspace_id, component_path, runnable_name, period)
        return {"ok": True}


    @mcp.tool()
    async def create_data_received_event(workspace_id: str, component_path: str, runnable_name: str, port_path: str, data_element_name: str) -> dict:
        manager.create_data_received_event(workspace_id, component_path, runnable_name, port_path, data_element_name)
        return {"ok": True}


    @mcp.tool()
    async def create_operation_invoked_event(workspace_id: str, component_path: str, runnable_name: str, operation_name: str) -> dict:
        manager.create_operation_invoked_event(workspace_id, component_path, runnable_name, operation_name)
        return {"ok": True}


    @mcp.tool()
    async def create_mode_switch_event(workspace_id: str, component_path: str, runnable_name: str, mode_group_ref: str) -> dict:
        manager.create_mode_switch_event(workspace_id, component_path, runnable_name, mode_group_ref)
        return {"ok": True}


    @mcp.tool()
    async def set_nonqueued_receiver_com_spec(workspace_id: str, component_path: str, port_name: str, data_element_name: str, alive_timeout: int | None = None) -> dict:
        manager.set_nonqueued_receiver_com_spec(workspace_id, component_path, port_name, data_element_name, alive_timeout)
        return {"ok": True}


    @mcp.tool()
    async def set_queued_sender_com_spec(workspace_id: str, component_path: str, port_name: str, data_element_name: str, queue_length: int) -> dict:
        manager.set_queued_sender_com_spec(workspace_id, component_path, port_name, data_element_name, queue_length)
        return {"ok": True}


    @mcp.tool()
    async def create_mode_declaration_group(workspace_id: str, package_path: str, name: str, modes: list[str]) -> dict:
        manager.create_mode_declaration_group(workspace_id, package_path, name, modes)
        return {"ok": True}


    @mcp.tool()
    async def create_mode_switch_interface(workspace_id: str, package_path: str, name: str, mode_group_ref: str) -> dict:
        manager.create_mode_switch_interface(workspace_id, package_path, name, mode_group_ref)
        return {"ok": True}


    @mcp.tool()
    async def create_assembly_connector(workspace_id: str, composition_path: str, provider_component: str, provider_port: str, requester_component: str, requester_port: str) -> dict:
        manager.create_assembly_connector(workspace_id, composition_path, provider_component, provider_port, requester_component, requester_port)
        return {"ok": True}


    @mcp.tool()
    async def create_delegation_connector(workspace_id: str, composition_path: str, inner_component: str, inner_port: str, outer_port: str) -> dict:
        manager.create_delegation_connector(workspace_id, composition_path, inner_component, inner_port, outer_port)
        return {"ok": True}


    @mcp.tool()
    async def set_port_api_option(workspace_id: str, component_path: str, port_name: str, enable_take_address: bool, indirect_api: bool) -> dict:
        manager.set_port_api_option(workspace_id, component_path, port_name, enable_take_address, indirect_api)
        return {"ok": True}


    @mcp.tool()
    async def create_sender_receiver_interface(workspace_id: str, package_path: str, name: str) -> dict:
        manager.create_sender_receiver_interface(workspace_id, package_path, name)
        return {"ok": True}


    @mcp.tool()
    async def create_data_element(workspace_id: str, interface_path: str, name: str, type_ref: str) -> dict:
        manager.create_data_element(workspace_id, interface_path, name, type_ref)
        return {"ok": True}


    @mcp.tool()
    async def create_client_server_interface(workspace_id: str, package_path: str, name: str) -> dict:
        manager.create_client_server_interface(workspace_id, package_path, name)
        return {"ok": True}


    @mcp.tool()
    async def create_operation(workspace_id: str, interface_path: str, name: str) -> dict:
        manager.create_operation(workspace_id, interface_path, name)
        return {"ok": True}


    @mcp.tool()
    async def create_component_type(workspace_id: str, package_path: str, name: str, component_type: str) -> dict:
        manager.create_component_type(workspace_id, package_path, name, component_type)
        return {"ok": True}


    @mcp.tool()
    async def create_port(
        workspace_id: str,
        component_path: str,
        port_name: str,
        interface_path: str,
        port_type: str,
    ) -> dict:
        manager.create_port(workspace_id, component_path, port_name, interface_path, port_type)
        return {"ok": True}


    @mcp.tool()
    async def create_implementation_data_type(
        workspace_id: str,
        package_path: str,
        name: str,
        category: str = "VALUE",
        base_type_ref: str | None = None,
    ) -> dict:
        manager.create_implementation_data_type(
            workspace_id,
            package_path,
            name,
            category,
            base_type_ref,
        )
        return {"ok": True}


    @mcp.tool()
    async def create_sw_base_type_in_package(
        workspace_id: str,
        package_path: str,
        name: str,
        size: int | None = None,
        max_size: int | None = None,
        encoding: str | None = None,
        alignment: int | None = None,
        byte_order: str | None = None,
        native_declaration: str | None = None,
    ) -> dict:
        manager.create_sw_base_type_in_package(
            workspace_id,
            package_path,
            name,
            size,
            max_size,
            encoding,
            alignment,
            byte_order,
            native_declaration,
        )
        return {"ok": True}


    @mcp.tool()
    async def create_unit_in_package(
        workspace_id: str,
        package_path: str,
        name: str,
        display_name: str | None = None,
        factor: float | None = None,
        offset: float | None = None,
        physical_dimension_ref: str | None = None,
    ) -> dict:
        manager.create_unit_in_package(
            workspace_id,
            package_path,
            name,
            display_name,
            factor,
            offset,
            physical_dimension_ref,
        )
        return {"ok": True}


    @mcp.tool()
    async def create_constant_in_package(
        workspace_id: str,
        package_path: str,
        name: str,
        value,
    ) -> dict:
        manager.create_constant_in_package(workspace_id, package_path, name, value)
        return {"ok": True}


    @mcp.tool()
    async def add_sw_base_type_by_package_key(workspace_id: str, package_key: str, **kwargs) -> dict:
        manager.add_sw_base_type_by_package_key(workspace_id, package_key, **kwargs)
        return {"ok": True}


    @mcp.tool()
    async def add_constant_by_package_key(workspace_id: str, package_key: str, name: str, value) -> dict:
        manager.add_constant_by_package_key(workspace_id, package_key, name, value)
        return {"ok": True}


    @mcp.tool()
    async def add_unit_by_package_key(workspace_id: str, package_key: str, **kwargs) -> dict:
        manager.add_unit_by_package_key(workspace_id, package_key, **kwargs)
        return {"ok": True}
