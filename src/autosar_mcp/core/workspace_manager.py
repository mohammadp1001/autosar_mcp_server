"""Workspace management helpers for the AUTOSAR MCP server.

This module provides an in-memory, ID-based API over ``autosar.xml.Workspace``.
The server/tool layer exchanges string IDs instead of passing Python objects.
"""

import os
from typing import Any, Optional

import autosar.xml
import autosar.xml.reader as ar_reader
import autosar.xml.writer as ar_writer
import autosar.xml.element as ar_element

from autosar_mcp.core.registry import ObjectRegistry

# pylint: disable=line-too-long


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

    def create_swc_internal_behavior(self, workspace_id: str, component_path: str) -> None:
        """Creates an internal behavior object for a software component.

        Args:
            workspace_id: Workspace ID containing the component.
            component_path: AUTOSAR path to the component type.

        Returns:
            None.
        """
        ws = self.get_workspace(workspace_id)
        component = ws.find(component_path)
        component.create_internal_behavior()

    def create_runnable(self, workspace_id: str, component_path: str, runnable_name: str, symbol: str) -> None:
        """Creates a runnable in a component's internal behavior.

        Args:
            workspace_id: Workspace ID containing the component.
            component_path: AUTOSAR path to the component type.
            runnable_name: Runnable short name.
            symbol: Runnable symbol name.

        Returns:
            None.
        """
        ws = self.get_workspace(workspace_id)
        component = ws.find(component_path)
        ib = component.internal_behavior
        ib.create_runnable(runnable_name, symbol=symbol)


    def create_timing_event(self, workspace_id: str, component_path: str, runnable_name: str, period: float) -> None:
        """Creates a timing event that triggers a runnable.

        Args:
            workspace_id: Workspace ID containing the component.
            component_path: AUTOSAR path to the component type.
            runnable_name: Runnable name to trigger.
            period: Timing period in seconds.

        Returns:
            None.
        """
        ws = self.get_workspace(workspace_id)
        component = ws.find(component_path)
        ib = component.internal_behavior
        ib.create_timing_event(runnable_name, period)


    def create_data_received_event(self, workspace_id: str, component_path: str, runnable_name: str, port_path: str, data_element_name: str) -> None:
        """Creates a data-received event that triggers a runnable.

        Args:
            workspace_id: Workspace ID containing the component.
            component_path: AUTOSAR path to the component type.
            runnable_name: Runnable name to trigger.
            port_path: AUTOSAR path to the port.
            data_element_name: Data element name on the interface.

        Returns:
            None.
        """
        ws = self.get_workspace(workspace_id)
        component = ws.find(component_path)
        ib = component.internal_behavior
        ib.create_data_received_event(runnable_name, port_path, data_element_name)


    def create_operation_invoked_event(self, workspace_id: str, component_path: str, runnable_name: str, operation_name: str) -> None:
        """Creates an operation-invoked event that triggers a runnable.

        Args:
            workspace_id: Workspace ID containing the component.
            component_path: AUTOSAR path to the component type.
            runnable_name: Runnable name to trigger.
            operation_name: Operation name on the client-server interface.

        Returns:
            None.
        """
        ws = self.get_workspace(workspace_id)
        component = ws.find(component_path)
        ib = component.internal_behavior
        ib.create_operation_invoked_event(runnable_name, operation_name)


    def create_mode_switch_event(self, workspace_id: str, component_path: str, runnable_name: str, mode_group_ref: str) -> None:
        """Creates a mode-switch event that triggers a runnable.

        Args:
            workspace_id: Workspace ID containing the component.
            component_path: AUTOSAR path to the component type.
            runnable_name: Runnable name to trigger.
            mode_group_ref: Reference to the mode declaration group.

        Returns:
            None.
        """
        ws = self.get_workspace(workspace_id)
        component = ws.find(component_path)
        ib = component.internal_behavior
        ib.create_mode_switch_event(runnable_name, mode_group_ref)


    def set_nonqueued_receiver_com_spec(self, workspace_id: str, component_path: str, port_name: str, data_element_name: str, alive_timeout: int | None) -> None:
        """Sets non-queued receiver communication spec on a port.

        Args:
            workspace_id: Workspace ID containing the component.
            component_path: AUTOSAR path to the component type.
            port_name: Port short name to update.
            data_element_name: Data element short name to configure.
            alive_timeout: Optional alive timeout value.

        Returns:
            None.
        """
        ws = self.get_workspace(workspace_id)
        component = ws.find(component_path)
        port = component.find(port_name)
        port.set_nonqueued_receiver_com_spec(data_element_name, alive_timeout)


    def set_queued_sender_com_spec(self, workspace_id: str, component_path: str, port_name: str, data_element_name: str, queue_length: int) -> None:
        """Sets queued sender communication spec on a port.

        Args:
            workspace_id: Workspace ID containing the component.
            component_path: AUTOSAR path to the component type.
            port_name: Port short name to update.
            data_element_name: Data element short name to configure.
            queue_length: Queue length for queued sending.

        Returns:
            None.
        """
        ws = self.get_workspace(workspace_id)
        component = ws.find(component_path)
        port = component.find(port_name)
        port.set_queued_sender_com_spec(data_element_name, queue_length)


    def create_mode_declaration_group(self, workspace_id: str, package_path: str, name: str, modes: list[str]) -> None:
        """Creates a ModeDeclarationGroup with given modes in a package.

        Args:
            workspace_id: Workspace ID containing the package.
            package_path: AUTOSAR path to the package.
            name: ModeDeclarationGroup short name.
            modes: List of mode names to create.

        Returns:
            None.
        """
        ws = self.get_workspace(workspace_id)
        package = ws.find(package_path)
        mdg = ar_element.ModeDeclarationGroup(name)
        for mode in modes:
            mdg.create_mode_declaration(mode)
        package.append(mdg)


    def create_mode_switch_interface(self, workspace_id: str, package_path: str, name: str, mode_group_ref: str) -> None:
        """Creates a ModeSwitchInterface in a package.

        Args:
            workspace_id: Workspace ID containing the package.
            package_path: AUTOSAR path to the package.
            name: ModeSwitchInterface short name.
            mode_group_ref: Reference to a mode declaration group.

        Returns:
            None.
        """
        ws = self.get_workspace(workspace_id)
        package = ws.find(package_path)
        interface = ar_element.ModeSwitchInterface(name, mode_group_ref=mode_group_ref)
        package.append(interface)


    def create_assembly_connector(self, workspace_id: str, composition_path: str, provider_component: str, provider_port: str, requester_component: str, requester_port: str) -> None:
        """Creates an assembly connector within a composition.

        Args:
            workspace_id: Workspace ID containing the composition.
            composition_path: AUTOSAR path to the composition component.
            provider_component: Provider inner component name.
            provider_port: Provider port name.
            requester_component: Requester inner component name.
            requester_port: Requester port name.

        Returns:
            None.
        """
        ws = self.get_workspace(workspace_id)
        composition = ws.find(composition_path)
        composition.create_assembly_connector(
            provider_component, provider_port,
            requester_component, requester_port
        )


    def create_delegation_connector(self, workspace_id: str, composition_path: str, inner_component: str, inner_port: str, outer_port: str) -> None:
        """Creates a delegation connector within a composition.

        Args:
            workspace_id: Workspace ID containing the composition.
            composition_path: AUTOSAR path to the composition component.
            inner_component: Inner component short name.
            inner_port: Inner port short name.
            outer_port: Outer port short name.

        Returns:
            None.
        """
        ws = self.get_workspace(workspace_id)
        composition = ws.find(composition_path)
        composition.create_delegation_connector(
            inner_component, inner_port, outer_port
        )


    def set_port_api_option(self, workspace_id: str, component_path: str, port_name: str, enable_take_address: bool, indirect_api: bool) -> None:
        """Sets PortAPIOption settings on a port.

        Args:
            workspace_id: Workspace ID containing the component.
            component_path: AUTOSAR path to the component type.
            port_name: Port short name to update.
            enable_take_address: Whether take-address is enabled.
            indirect_api: Whether indirect API is enabled.

        Returns:
            None.
        """
        ws = self.get_workspace(workspace_id)
        component = ws.find(component_path)
        port = component.find(port_name)
        port.set_port_api_option(enable_take_address=enable_take_address, indirect_api=indirect_api)

    def create_sender_receiver_interface(self, workspace_id: str, package_path: str, name: str) -> None:
        """Creates a SenderReceiverInterface in a package.

        Args:
            workspace_id: Workspace ID containing the package.
            package_path: AUTOSAR path to the package.
            name: Interface short name.

        Returns:
            None.
        """
        ws = self.get_workspace(workspace_id)
        package = ws.find(package_path)
        if not isinstance(package, ar_element.Package):
            raise TypeError(f"'{package_path}' is not a Package.")
        interface = ar_element.SenderReceiverInterface(name)
        package.append(interface)


    def create_data_element(self, workspace_id: str, interface_path: str, name: str, type_ref: str) -> None:
        """Creates a data element under a SenderReceiverInterface.

        Args:
            workspace_id: Workspace ID containing the interface.
            interface_path: AUTOSAR path to the sender-receiver interface.
            name: Data element short name.
            type_ref: Type reference (AUTOSAR ref string).

        Returns:
            None.
        """
        ws = self.get_workspace(workspace_id)
        interface = ws.find(interface_path)
        if not isinstance(interface, ar_element.SenderReceiverInterface):
            raise TypeError(f"'{interface_path}' is not a SenderReceiverInterface.")
        interface.create_data_element(name, type_ref)


    def create_client_server_interface(self, workspace_id: str, package_path: str, name: str) -> None:
        """Creates a ClientServerInterface in a package.

        Args:
            workspace_id: Workspace ID containing the package.
            package_path: AUTOSAR path to the package.
            name: Interface short name.

        Returns:
            None.
        """
        ws = self.get_workspace(workspace_id)
        package = ws.find(package_path)
        if not isinstance(package, ar_element.Package):
            raise TypeError(f"'{package_path}' is not a Package.")
        interface = ar_element.ClientServerInterface(name)
        package.append(interface)


    def create_operation(self, workspace_id: str, interface_path: str, name: str) -> None:
        """Creates an operation under a ClientServerInterface.

        Args:
            workspace_id: Workspace ID containing the interface.
            interface_path: AUTOSAR path to the client-server interface.
            name: Operation short name.

        Returns:
            None.
        """
        ws = self.get_workspace(workspace_id)
        interface = ws.find(interface_path)
        if not isinstance(interface, ar_element.ClientServerInterface):
            raise TypeError(f"'{interface_path}' is not a ClientServerInterface.")
        interface.create_operation(name)


    def create_component_type(self, workspace_id: str, package_path: str, name: str, component_type: str) -> None:
        """Creates a software component type in a package.

        Args:
            workspace_id: Workspace ID containing the package.
            package_path: AUTOSAR path to the package.
            name: Component short name.
            component_type: Component kind (e.g. "Application", "Composition").

        Returns:
            None.
        """
        ws = self.get_workspace(workspace_id)
        package = ws.find(package_path)
        if not isinstance(package, ar_element.Package):
            raise TypeError(f"'{package_path}' is not a Package.")

        if component_type == "Application":
            component = ar_element.ApplicationSoftwareComponentType(name)
        elif component_type == "Composition":
            component = ar_element.CompositionSwComponentType(name)
        else:
            # Fallback to Application since other types don't exist
            component = ar_element.ApplicationSoftwareComponentType(name)

        package.append(component)


    def create_port(self, workspace_id: str, component_path: str, port_name: str, interface_path: str, port_type: str) -> None:
        """Creates a port on a software component type.

        Args:
            workspace_id: Workspace ID containing the component.
            component_path: AUTOSAR path to the component type.
            port_name: Port short name to create.
            interface_path: AUTOSAR path to the port interface.
            port_type: Port kind ("P", "R", or "PR").

        Returns:
            None.
        """
        ws = self.get_workspace(workspace_id)
        component = ws.find(component_path)
        if not isinstance(component, ar_element.SwComponentType):
            raise TypeError(f"'{component_path}' is not a SwComponentType.")

        interface = ws.find(interface_path)
        if interface is None:
            raise ValueError(f"Interface '{interface_path}' not found.")

        if port_type == "P":
            component.create_p_port(port_name, interface)
        elif port_type == "R":
            component.create_r_port(port_name, interface)
        elif port_type == "PR":
            component.create_pr_port(port_name, interface)
        else:
            raise ValueError(f"Invalid port_type '{port_type}'.")


    def create_implementation_data_type(
        self,
        workspace_id: str,
        package_path: str,
        name: str,
        category: str = "VALUE",
    ) -> None:
        """Creates an ImplementationDataType in a package.

        Args:
            workspace_id: Workspace ID containing the package.
            package_path: AUTOSAR path to the package.
            name: Data type short name.
            category: Implementation data type category.
        Returns:
            None.
        """
        ws = self.get_workspace(workspace_id)
        package = ws.find(package_path)
        if not isinstance(package, ar_element.Package):
            raise TypeError(f"'{package_path}' is not a Package.")

        data_type = ar_element.ImplementationDataType(name, category=category)
        package.append(data_type)


    def create_sw_base_type_in_package(
        self,
        workspace_id: str,
        package_path: str,
        name: str,
        size: int | None = None,
        max_size: int | None = None,
        encoding: str | None = None,
        alignment: int | None = None,
        byte_order: str | None = None,
        native_declaration: str | None = None,
    ) -> None:
        """Creates a SwBaseType in a package (creating packages if needed).

        Args:
            workspace_id: Workspace ID containing the package.
            package_path: AUTOSAR path to the package.
            name: SwBaseType short name.
            size: Optional size in bits.
            max_size: Optional max size in bits.
            encoding: Optional encoding name.
            alignment: Optional alignment in bits/bytes depending on schema usage.
            byte_order: Optional byte order string (currently not wired).
            native_declaration: Optional native declaration string.

        Returns:
            None.
        """
        ws = self.get_workspace(workspace_id)
        pkg = ws.make_packages(package_path.lstrip("/"))
        elem = ar_element.SwBaseType(
            name=name,
            size=size,
            max_size=max_size,
            encoding=encoding,
            alignment=alignment,
            byte_order=byte_order,
            native_declaration=native_declaration,
        )
        pkg.append(elem)


    def create_unit_in_package(
        self,
        workspace_id: str,
        package_path: str,
        name: str,
        display_name: str | None = None,
        factor: float | None = None,
        offset: float | None = None,
        physical_dimension_ref: str | None = None,
    ) -> None:
        """Creates a Unit in a package (creating packages if needed).

        Args:
            workspace_id: Workspace ID containing the package.
            package_path: AUTOSAR path to the package.
            name: Unit short name.
            display_name: Optional display name.
            factor: Optional scaling factor.
            offset: Optional offset.
            physical_dimension_ref: Optional physical dimension reference.

        Returns:
            None.
        """
        ws = self.get_workspace(workspace_id)
        pkg = ws.make_packages(package_path.lstrip("/"))
        unit = ar_element.Unit(
            name=name,
            display_name=display_name,
            factor=factor,
            offset=offset,
            physical_dimension_ref=physical_dimension_ref,
        )
        pkg.append(unit)


    def create_constant_in_package(self, workspace_id: str, package_path: str, name: str, value) -> None:
        """Creates a ConstantSpecification in a package (creating packages if needed).

        Args:
            workspace_id: Workspace ID containing the package.
            package_path: AUTOSAR path to the package.
            name: Constant short name.
            value: Value accepted by ``ConstantSpecification.make_constant``.

        Returns:
            None.
        """
        ws = self.get_workspace(workspace_id)
        pkg = ws.make_packages(package_path.lstrip("/"))
        const = ar_element.ConstantSpecification.make_constant(name=name, value=value)
        pkg.append(const)


    def add_sw_base_type_by_package_key(self, workspace_id: str, package_key: str, **kwargs) -> None:
        """Adds a SwBaseType element to a package selected by package map key.

        Args:
            workspace_id: Workspace ID containing the package map.
            package_key: Package map key.
            **kwargs: SwBaseType constructor keyword arguments.

        Returns:
            None.
        """
        ws = self.get_workspace(workspace_id)
        elem = ar_element.SwBaseType(**kwargs)
        ws.add_element(package_key, elem)


    def add_constant_by_package_key(self, workspace_id: str, package_key: str, name: str, value) -> None:
        """Adds a ConstantSpecification to a package selected by package map key.

        Args:
            workspace_id: Workspace ID containing the package map.
            package_key: Package map key.
            name: Constant short name.
            value: Value accepted by ``ConstantSpecification.make_constant``.

        Returns:
            None.
        """
        ws = self.get_workspace(workspace_id)
        const = ar_element.ConstantSpecification.make_constant(name=name, value=value)
        ws.add_element(package_key, const)


    def add_unit_by_package_key(self, workspace_id: str, package_key: str, **kwargs) -> None:
        """Adds a Unit element to a package selected by package map key.

        Args:
            workspace_id: Workspace ID containing the package map.
            package_key: Package map key.
            **kwargs: Unit constructor keyword arguments.

        Returns:
            None.
        """
        ws = self.get_workspace(workspace_id)
        unit = ar_element.Unit(**kwargs)
        ws.add_element(package_key, unit)
