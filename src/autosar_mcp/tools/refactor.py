import logging
import autosar.xml.element as ar_element
from mcp.server.fastmcp import FastMCP
from ..core.workspace_manager import WorkspaceManager

logger = logging.getLogger("autosar_mcp.tools.refactor")

def register(mcp: FastMCP, manager: WorkspaceManager):
    
    @mcp.tool()
    async def create_package(name: str, parent_path: str = "/") -> str:
        """
        Creates a new ARXML package.
        
        Args:
            name: Name of the new package.
            parent_path: Path to the parent package (default: root).
        """
        try:
            parent = manager.get_element(parent_path)
            if parent is None:
                return f"Error: Parent path '{parent_path}' not found."
            
            if not isinstance(parent, (ar_element.Package, ar_element.PackageCollection)):
                return f"Error: Parent '{parent_path}' is not a package."
            
            # create_package automatically appends to parent
            package = parent.create_package(name)
            return f"Created package '{package.name}' at '{parent_path}'."
        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    async def create_sender_receiver_interface(package_path: str, name: str) -> str:
        """
        Creates a Sender-Receiver Interface.
        
        Args:
            package_path: Path to the package where the interface should be created.
            name: Name of the interface.
        """
        try:
            package = manager.get_element(package_path)
            if not isinstance(package, ar_element.Package):
                return f"Error: '{package_path}' is not a package."
            
            interface = ar_element.SenderReceiverInterface(name)
            package.append(interface)
            return f"Created SenderReceiverInterface '{name}' in '{package_path}'."
        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    async def create_data_element(interface_path: str, name: str, type_ref: str) -> str:
        """
        Adds a data element to a Sender-Receiver Interface.
        
        Args:
            interface_path: Path to the SenderReceiverInterface.
            name: Name of the data element.
            type_ref: Reference to the data type (e.g., 'ImplementationDataType').
        """
        try:
            interface = manager.get_element(interface_path)
            if not isinstance(interface, ar_element.SenderReceiverInterface):
                return f"Error: '{interface_path}' is not a SenderReceiverInterface."
            
            # create_data_element(name, type_ref)
            interface.create_data_element(name, type_ref)
            return f"Created data element '{name}' in '{interface_path}'."
        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    async def create_client_server_interface(package_path: str, name: str) -> str:
        """
        Creates a Client-Server Interface.
        """
        try:
            package = manager.get_element(package_path)
            if not isinstance(package, ar_element.Package):
                return f"Error: '{package_path}' is not a package."
            
            interface = ar_element.ClientServerInterface(name)
            package.append(interface)
            return f"Created ClientServerInterface '{name}' in '{package_path}'."
        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    async def create_operation(interface_path: str, name: str) -> str:
        """
        Adds an operation to a Client-Server Interface.
        """
        try:
            interface = manager.get_element(interface_path)
            if not isinstance(interface, ar_element.ClientServerInterface):
                return f"Error: '{interface_path}' is not a ClientServerInterface."
            
            interface.create_operation(name)
            return f"Created operation '{name}' in '{interface_path}'."
        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    async def create_component_type(package_path: str, name: str, type: str) -> str:
        """
        Creates a Software Component.
        
        Args:
            package_path: Path to the package.
            name: Name of the component.
            type: One of 'Application', 'SensorActuator', 'Service', 'ComplexDeviceDriver', 'Composition'.
        """
        try:
            package = manager.get_element(package_path)
            if not isinstance(package, ar_element.Package):
                return f"Error: '{package_path}' is not a package."
            
            component = None
            if type == 'Application':
                component = ar_element.ApplicationSoftwareComponentType(name)
            elif type == 'SensorActuator':
                component = ar_element.SensorActuatorSwComponentType(name)
            elif type == 'Service':
                component = ar_element.ServiceSwComponentType(name)
            elif type == 'ComplexDeviceDriver':
                component = ar_element.ComplexDeviceDriverSwComponentType(name)
            elif type == 'Composition':
                component = ar_element.CompositionSwComponentType(name)
            else:
                return f"Error: Unknown component type '{type}'."
            
            package.append(component)
            return f"Created {type} component '{name}' in '{package_path}'."
        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    async def create_port(component_path: str, port_name: str, interface_path: str, port_type: str) -> str:
        """
        Adds a Port to a component.
        
        Args:
            component_path: Path to the component.
            port_name: Name of the port.
            interface_path: Path/Reference to the Port Interface.
            port_type: 'P' (Provide), 'R' (Require), or 'PR' (Provide-Require).
        """
        try:
            component = manager.get_element(component_path)
            if not isinstance(component, ar_element.SwComponentType):
                 return f"Error: '{component_path}' is not a SwComponentType (got {type(component)})."

            # Resolve Interface Path to Object
            interface = manager.get_element(interface_path)
            if interface is None:
                 return f"Error: Interface path '{interface_path}' not found."

            if port_type == 'P':
                component.create_p_port(port_name, interface)
            elif port_type == 'R':
                component.create_r_port(port_name, interface)
            elif port_type == 'PR':
                 component.create_pr_port(port_name, interface)
            else:
                return f"Error: Invalid port type '{port_type}'."
                
            return f"Created {port_type}-Port '{port_name}' in '{component_path}'."
        except Exception as e:
            return f"Error: {str(e)}"

    @mcp.tool()
    async def create_implementation_data_type(package_path: str, name: str, category: str = "VALUE", base_type_ref: str = None) -> str:
        """
        Creates an Implementation Data Type.
        """
        try:
            package = manager.get_element(package_path)
            if not isinstance(package, ar_element.Package):
                 return f"Error: '{package_path}' is not a package."
            
            data_type = ar_element.ImplementationDataType(name, category=category)
            # TODO: handle base_type_ref
            
            package.append(data_type)
            return f"Created ImplementationDataType '{name}' in '{package_path}'."
        except Exception as e:
            return f"Error: {str(e)}"
