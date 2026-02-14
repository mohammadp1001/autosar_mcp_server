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
    async def create_sender_receiver_interface(workspace_id: str, package_path: str, name: str) -> dict[str, Any]:
        req = models.CreateSenderReceiverInterfaceIn(workspace_id=workspace_id, package_path=package_path, name=name)
        try:
            ws = _get_workspace(req.workspace_id)
            package = _get_element(ws, req.package_path)
            if not isinstance(package, ar_element.Package):
                return models.ToolResult(
                    ok=False,
                    message=f"'{req.package_path}' is not a Package.",
                ).model_dump()

            interface = ar_element.SenderReceiverInterface(req.name)
            package.append(interface)
            return models.ToolResult(
                ok=True,
                message=f"Created SenderReceiverInterface '{req.name}' in '{req.package_path}'.",
            ).model_dump()
        except Exception as exc:
            logger.exception("create_sender_receiver_interface failed")
            return models.ToolResult(ok=False, message=str(exc)).model_dump()

    @mcp.tool()
    async def create_data_element(workspace_id: str, interface_path: str, name: str, type_ref: str) -> dict[str, Any]:
        req = models.CreateDataElementIn(
            workspace_id=workspace_id,
            interface_path=interface_path,
            name=name,
            type_ref=type_ref,
        )
        try:
            ws = _get_workspace(req.workspace_id)
            interface = _get_element(ws, req.interface_path)
            if not isinstance(interface, ar_element.SenderReceiverInterface):
                return models.ToolResult(
                    ok=False,
                    message=f"'{req.interface_path}' is not a SenderReceiverInterface.",
                ).model_dump()

            interface.create_data_element(req.name, req.type_ref)
            return models.ToolResult(
                ok=True,
                message=f"Created data element '{req.name}' in '{req.interface_path}'.",
            ).model_dump()
        except Exception as exc:
            logger.exception("create_data_element failed")
            return models.ToolResult(ok=False, message=str(exc)).model_dump()

    @mcp.tool()
    async def create_client_server_interface(workspace_id: str, package_path: str, name: str) -> dict[str, Any]:
        req = models.CreateClientServerInterfaceIn(workspace_id=workspace_id, package_path=package_path, name=name)
        try:
            ws = _get_workspace(req.workspace_id)
            package = _get_element(ws, req.package_path)
            if not isinstance(package, ar_element.Package):
                return models.ToolResult(ok=False, message=f"'{req.package_path}' is not a Package.").model_dump()

            interface = ar_element.ClientServerInterface(req.name)
            package.append(interface)
            return models.ToolResult(
                ok=True,
                message=f"Created ClientServerInterface '{req.name}' in '{req.package_path}'.",
            ).model_dump()
        except Exception as exc:
            logger.exception("create_client_server_interface failed")
            return models.ToolResult(ok=False, message=str(exc)).model_dump()

    @mcp.tool()
    async def create_operation(workspace_id: str, interface_path: str, name: str) -> dict[str, Any]:
        req = models.CreateOperationIn(workspace_id=workspace_id, interface_path=interface_path, name=name)
        try:
            ws = _get_workspace(req.workspace_id)
            interface = _get_element(ws, req.interface_path)
            if not isinstance(interface, ar_element.ClientServerInterface):
                return models.ToolResult(
                    ok=False,
                    message=f"'{req.interface_path}' is not a ClientServerInterface.",
                ).model_dump()

            interface.create_operation(req.name)
            return models.ToolResult(
                ok=True,
                message=f"Created operation '{req.name}' in '{req.interface_path}'.",
            ).model_dump()
        except Exception as exc:
            logger.exception("create_operation failed")
            return models.ToolResult(ok=False, message=str(exc)).model_dump()

    @mcp.tool()
    async def create_component_type(workspace_id: str, package_path: str, name: str, component_type: str) -> dict[str, Any]:
        req = models.CreateComponentTypeIn(
            workspace_id=workspace_id,
            package_path=package_path,
            name=name,
            component_type=component_type,
        )
        try:
            ws = _get_workspace(req.workspace_id)
            package = _get_element(ws, req.package_path)
            if not isinstance(package, ar_element.Package):
                return models.ToolResult(ok=False, message=f"'{req.package_path}' is not a Package.").model_dump()

            t = req.component_type
            component = None
            if t == "Application":
                component = ar_element.ApplicationSoftwareComponentType(req.name)
            elif t == "SensorActuator":
                logger.warning("Warning: Component type %s is not supported by this autosar library version.", component_type)
                component = ar_element.ApplicationSoftwareComponentType(req.name)
            elif t == "Service":
                logger.warning("Warning: Component type %s is not supported by this autosar library version.", component_type)
                component = ar_element.ApplicationSoftwareComponentType(req.name)
            elif t == "ComplexDeviceDriver":
                logger.warning("Warning: Component type %s is not supported by this autosar library version.", component_type)
                component = ar_element.ApplicationSoftwareComponentType(req.name)
            elif t == "Composition":
                component = ar_element.CompositionSwComponentType(req.name)
            else:
                return models.ToolResult(ok=False, message=f"Unknown component_type '{t}'.").model_dump()

            package.append(component)
            return models.ToolResult(
                ok=True,
                message=f"Created {t} component '{req.name}' in '{req.package_path}'.",
            ).model_dump()
        except Exception as exc:
            logger.exception("create_component_type failed")
            return models.ToolResult(ok=False, message=str(exc)).model_dump()

    @mcp.tool()
    async def create_port(
        workspace_id: str,
        component_path: str,
        port_name: str,
        interface_path: str,
        port_type: str,
    ) -> dict[str, Any]:
        req = models.CreatePortIn(
            workspace_id=workspace_id,
            component_path=component_path,
            port_name=port_name,
            interface_path=interface_path,
            port_type=port_type,
        )
        try:
            ws = _get_workspace(req.workspace_id)

            component = _get_element(ws, req.component_path)
            if not isinstance(component, ar_element.SwComponentType):
                return models.ToolResult(
                    ok=False,
                    message=f"'{req.component_path}' is not a SwComponentType (got {type(component)}).",
                ).model_dump()

            interface = _get_element(ws, req.interface_path)
            if interface is None:
                return models.ToolResult(ok=False, message=f"Interface '{req.interface_path}' not found.").model_dump()

            if req.port_type == "P":
                component.create_p_port(req.port_name, interface)
            elif req.port_type == "R":
                component.create_r_port(req.port_name, interface)
            elif req.port_type == "PR":
                component.create_pr_port(req.port_name, interface)
            else:
                return models.ToolResult(
                    ok=False,
                    message=f"Invalid port_type '{req.port_type}'. Use P, R, or PR.",
                ).model_dump()

            return models.ToolResult(
                ok=True,
                message=f"Created {req.port_type}-Port '{req.port_name}' in '{req.component_path}'.",
            ).model_dump()
        except Exception as exc:
            logger.exception("create_port failed")
            return models.ToolResult(ok=False, message=str(exc)).model_dump()

    @mcp.tool()
    async def create_implementation_data_type(
        workspace_id: str,
        package_path: str,
        name: str,
        category: str = "VALUE",
        base_type_ref: Optional[str] = None,
    ) -> dict[str, Any]:
        req = models.CreateImplementationDataTypeIn(
            workspace_id=workspace_id,
            package_path=package_path,
            name=name,
            category=category,
            base_type_ref=base_type_ref,
        )
        try:
            ws = _get_workspace(req.workspace_id)
            package = _get_element(ws, req.package_path)
            if not isinstance(package, ar_element.Package):
                return models.ToolResult(ok=False, message=f"'{req.package_path}' is not a Package.").model_dump()

            data_type = ar_element.ImplementationDataType(req.name, category=req.category)

            # NOTE: base_type_ref wiring typically requires SwDataDefProps; keep it out for now.
            package.append(data_type)

            details = {"category": req.category, "base_type_ref": req.base_type_ref}
            return models.ToolResult(
                ok=True,
                message=f"Created ImplementationDataType '{req.name}' in '{req.package_path}'.",
                details=details,
            ).model_dump()
        except Exception as exc:
            logger.exception("create_implementation_data_type failed")
            return models.ToolResult(ok=False, message=str(exc)).model_dump()

    @mcp.tool()
    async def create_sw_base_type_in_package(
        workspace_id: str,
        package_path: str,
        name: str,
        size: Optional[int] = None,
        max_size: Optional[int] = None,
        encoding: Optional[str] = None,
        alignment: Optional[int] = None,
        byte_order: Optional[str] = None,
        native_declaration: Optional[str] = None,
    ) -> dict:
        """
        Create SW-BASE-TYPE directly under a package path.
        """
        try:
            ws = _get_workspace(workspace_id)
            pkg = _ensure_package(ws, package_path)
            elem = ar_element.SwBaseType(
                name=name,
                size=size,
                max_size=max_size,
                encoding=encoding,
                alignment=alignment,
                byte_order=_parse_byte_order(byte_order),
                native_declaration=native_declaration,
            )
            pkg.append(elem)
            return models.ToolResult(
                ok=True,
                message=f"Created SwBaseType '{name}' in '{package_path}'.",
                details={"ref": str(elem.ref()) if elem.ref() else None},
            ).model_dump()
        except Exception as e:
            return models.ToolResult(ok=False, message=str(e)).model_dump()

    @mcp.tool()
    async def create_unit_in_package(
        workspace_id: str,
        package_path: str,
        name: str,
        display_name: Optional[str] = None,
        factor: Optional[float] = None,
        offset: Optional[float] = None,
        physical_dimension_ref: Optional[str] = None,
    ) -> dict:
        """
        Create UNIT directly under a package path.
        """
        try:
            ws = _get_workspace(workspace_id)
            pkg = _ensure_package(ws, package_path)
            unit = ar_element.Unit(
                name=name,
                display_name=display_name,
                factor=factor,
                offset=offset,
                physical_dimension_ref=physical_dimension_ref,
            )
            pkg.append(unit)
            return models.ToolResult(
                ok=True,
                message=f"Created Unit '{name}' in '{package_path}'.",
                details={"ref": str(unit.ref()) if unit.ref() else None},
            ).model_dump()
        except Exception as e:
            return models.ToolResult(ok=False, message=str(e)).model_dump()

    @mcp.tool()
    async def create_constant_in_package(
        workspace_id: str,
        package_path: str,
        name: str,
        value: Any,
    ) -> dict:
        """
        Create CONSTANT-SPECIFICATION under a package path.
        Uses ConstantSpecification.make_constant for convenience.
        """
        try:
            ws = _get_workspace(workspace_id)
            pkg = _ensure_package(ws, package_path)
            const = ar_element.ConstantSpecification.make_constant(name=name, value=value)
            pkg.append(const)
            return models.ToolResult(
                ok=True,
                message=f"Created ConstantSpecification '{name}' in '{package_path}'.",
                details={"ref": str(const.ref()) if const.ref() else None},
            ).model_dump()
        except Exception as e:
            return models.ToolResult(ok=False, message=str(e)).model_dump()

    @mcp.tool()
    async def add_sw_base_type_by_package_key(
        workspace_id: str,
        package_key: str,
        name: str,
        size: Optional[int] = None,
        max_size: Optional[int] = None,
        encoding: Optional[str] = None,
        alignment: Optional[int] = None,
        byte_order: Optional[str] = None,
        native_declaration: Optional[str] = None,
    ) -> dict:
        """
        Adds SW-BASE-TYPE using Workspace package_map key (requires create_package_map done earlier).
        Mirrors ar_xml.Workspace.add_element(package_key, element).
        """
        req = models.AddElementByKeySwBaseTypeIn(
            workspace_id=workspace_id,
            package_key=package_key,
            name=name,
            size=size,
            max_size=max_size,
            encoding=encoding,
            alignment=alignment,
            byte_order=byte_order,  # validated by model literal set
            native_declaration=native_declaration,
        )
        try:
            ws = _get_workspace(req.workspace_id)
            elem = ar_element.SwBaseType(
                name=req.name,
                size=req.size,
                max_size=req.max_size,
                encoding=req.encoding,
                alignment=req.alignment,
                byte_order=_parse_byte_order(req.byte_order),
                native_declaration=req.native_declaration,
            )
            ws.add_element(req.package_key, elem)
            return models.ToolResult(
                ok=True,
                message=f"Added SwBaseType '{req.name}' to package_key '{req.package_key}'.",
                details={"ref": str(elem.ref()) if elem.ref() else None},
            ).model_dump()
        except Exception as e:
            return models.ToolResult(ok=False, message=str(e)).model_dump()

    @mcp.tool()
    async def add_constant_by_package_key(workspace_id: str, package_key: str, name: str, value: Any) -> dict:
        """
        Adds CONSTANT-SPECIFICATION using Workspace package_map key (requires create_package_map done earlier).
        """
        req = models.AddElementByKeyConstantIn(
            workspace_id=workspace_id,
            package_key=package_key,
            name=name,
            value=value,
        )
        try:
            ws = _get_workspace(req.workspace_id)
            const = ar_element.ConstantSpecification.make_constant(name=req.name, value=req.value)
            ws.add_element(req.package_key, const)
            return models.ToolResult(
                ok=True,
                message=f"Added ConstantSpecification '{req.name}' to package_key '{req.package_key}'.",
                details={"ref": str(const.ref()) if const.ref() else None},
            ).model_dump()
        except Exception as e:
            return models.ToolResult(ok=False, message=str(e)).model_dump()

    @mcp.tool()
    async def add_unit_by_package_key(
        workspace_id: str,
        package_key: str,
        name: str,
        display_name: Optional[str] = None,
        factor: Optional[float] = None,
        offset: Optional[float] = None,
        physical_dimension_ref: Optional[str] = None,
    ) -> dict:
        """
        Adds UNIT using Workspace package_map key (requires create_package_map done earlier).
        """
        req = models.AddElementByKeyUnitIn(
            workspace_id=workspace_id,
            package_key=package_key,
            name=name,
            display_name=display_name,
            factor=factor,
            offset=offset,
            physical_dimension_ref=physical_dimension_ref,
        )
        try:
            ws = _get_workspace(req.workspace_id)
            unit = ar_element.Unit(
                name=req.name,
                display_name=req.display_name,
                factor=req.factor,
                offset=req.offset,
                physical_dimension_ref=req.physical_dimension_ref,
            )
            ws.add_element(req.package_key, unit)
            return models.ToolResult(
                ok=True,
                message=f"Added Unit '{req.name}' to package_key '{req.package_key}'.",
                details={"ref": str(unit.ref()) if unit.ref() else None},
            ).model_dump()
        except Exception as e:
            return models.ToolResult(ok=False, message=str(e)).model_dump()
