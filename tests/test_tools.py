import sys
import types
import unittest
from pathlib import Path
from unittest.mock import Mock


def _install_fake_autosar_modules() -> None:
    """
    Provide minimal autosar.* modules so src/autosar_mcp/tools.py can be imported
    in environments where the external autosar dependency is not installed.
    """
    if "autosar" in sys.modules:
        return

    autosar = types.ModuleType("autosar")
    autosar.__path__ = []  # mark as package for nested imports

    autosar_xml = types.ModuleType("autosar.xml")
    autosar_xml.__path__ = []  # mark as package for nested imports
    autosar_xml_element = types.ModuleType("autosar.xml.element")
    autosar_xml_enum = types.ModuleType("autosar.xml.enumeration")
    autosar_xml_reader = types.ModuleType("autosar.xml.reader")
    autosar_xml_writer = types.ModuleType("autosar.xml.writer")

    class Workspace:  # pragma: no cover - only for import-time typing
        pass

    class Document:  # pragma: no cover - only for import-time typing
        def __init__(self, *args, **kwargs):
            self.packages = kwargs.get("packages", [])

    class Package:  # pragma: no cover - only for import-time typing
        pass

    class _ByteOrder:  # pragma: no cover - only for helper mapping
        BIG_ENDIAN = object()
        LITTLE_ENDIAN = object()
        OPAQUE = object()

    autosar_xml.Workspace = Workspace
    autosar_xml.Document = Document
    autosar_xml_element.Package = Package
    autosar_xml_enum.ByteOrder = _ByteOrder

    class Reader:  # pragma: no cover
        def read_file(self, _path: str):
            return Document(packages=[])

    class Writer:  # pragma: no cover
        def __init__(self, *args, **kwargs):
            pass

        def write_file(self, _document, _path: str):
            return None

    autosar_xml_reader.Reader = Reader
    autosar_xml_writer.Writer = Writer

    autosar.xml = autosar_xml

    sys.modules["autosar"] = autosar
    sys.modules["autosar.xml"] = autosar_xml
    sys.modules["autosar.xml.element"] = autosar_xml_element
    sys.modules["autosar.xml.enumeration"] = autosar_xml_enum
    sys.modules["autosar.xml.reader"] = autosar_xml_reader
    sys.modules["autosar.xml.writer"] = autosar_xml_writer


class _FakeMCP:
    def __init__(self) -> None:
        self.tools: dict[str, object] = {}

    def tool(self):
        def decorator(fn):
            self.tools[fn.__name__] = fn
            return fn

        return decorator


class ToolsTests(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        src_dir = repo_root / "src"
        if str(src_dir) not in sys.path:
            sys.path.insert(0, str(src_dir))

        _install_fake_autosar_modules()

        # Import after stubbing autosar modules.
        import autosar_mcp.tools as tools_mod  # pylint: disable=import-error

        cls.tools_mod = tools_mod

    def setUp(self) -> None:
        self.mcp = _FakeMCP()
        self.manager = types.SimpleNamespace()

        # Core registry-backed methods
        self.manager.create_workspace = Mock(return_value="ws_12345")
        self.manager.reset_workspace = Mock()
        self.manager.delete_workspace = Mock()
        self.manager.load_arxml = Mock()
        self.manager.save_arxml = Mock()
        self.manager.create_package_map = Mock()
        self.manager.find_element = Mock(return_value=None)
        self.manager.list_root_packages = Mock(return_value=["PkgA", "PkgB"])

        # Extended creation helpers (delegated)
        self.manager.create_swc_internal_behavior = Mock()
        self.manager.create_runnable = Mock()
        self.manager.create_timing_event = Mock()
        self.manager.create_data_received_event = Mock()
        self.manager.create_operation_invoked_event = Mock()
        self.manager.create_mode_switch_event = Mock()
        self.manager.set_nonqueued_receiver_com_spec = Mock()
        self.manager.set_queued_sender_com_spec = Mock()
        self.manager.create_mode_declaration_group = Mock()
        self.manager.create_mode_switch_interface = Mock()
        self.manager.create_assembly_connector = Mock()
        self.manager.create_delegation_connector = Mock()
        self.manager.set_port_api_option = Mock()
        self.manager.create_sender_receiver_interface = Mock()
        self.manager.create_data_element = Mock()
        self.manager.create_client_server_interface = Mock()
        self.manager.create_operation = Mock()
        self.manager.create_component_type = Mock()
        self.manager.create_port = Mock()
        self.manager.create_implementation_data_type = Mock()
        self.manager.create_sw_base_type_in_package = Mock()
        self.manager.create_unit_in_package = Mock()
        self.manager.create_constant_in_package = Mock()
        self.manager.add_sw_base_type_by_package_key = Mock()
        self.manager.add_constant_by_package_key = Mock()
        self.manager.add_unit_by_package_key = Mock()

        self.tools_mod.register_tools(self.mcp, self.manager)  # type: ignore[arg-type]

    async def test_registers_expected_tools(self):
        expected = {
            "create_workspace",
            "reset_workspace",
            "delete_workspace",
            "load_arxml",
            "save_arxml",
            "create_package_map",
            "find_element",
            "list_root_packages",
            "create_swc_internal_behavior",
            "create_runnable",
            "create_timing_event",
            "create_data_received_event",
            "create_operation_invoked_event",
            "create_mode_switch_event",
            "set_nonqueued_receiver_com_spec",
            "set_queued_sender_com_spec",
            "create_mode_declaration_group",
            "create_mode_switch_interface",
            "create_assembly_connector",
            "create_delegation_connector",
            "set_port_api_option",
            "create_sender_receiver_interface",
            "create_data_element",
            "create_client_server_interface",
            "create_operation",
            "create_component_type",
            "create_port",
            "create_implementation_data_type",
            "create_sw_base_type_in_package",
            "create_unit_in_package",
            "create_constant_in_package",
            "add_sw_base_type_by_package_key",
            "add_constant_by_package_key",
            "add_unit_by_package_key",
        }

        self.assertTrue(expected.issubset(set(self.mcp.tools.keys())))

    async def test_create_workspace_returns_model(self):
        out = await self.mcp.tools["create_workspace"]()
        self.manager.create_workspace.assert_called_once_with()
        self.assertEqual(out["workspace_id"], "ws_12345")

    async def test_reset_delete_load_save_package_map(self):
        out = await self.mcp.tools["reset_workspace"]("ws_12345")
        self.assertEqual(out, {"ok": True})
        self.manager.reset_workspace.assert_called_once_with("ws_12345")

        out = await self.mcp.tools["delete_workspace"]("ws_12345")
        self.assertEqual(out, {"ok": True})
        self.manager.delete_workspace.assert_called_once_with("ws_12345")

        out = await self.mcp.tools["load_arxml"]("ws_12345", "C:\\tmp\\x.arxml")
        self.assertEqual(out, {"ok": True})
        self.manager.load_arxml.assert_called_once_with("ws_12345", "C:\\tmp\\x.arxml")

        out = await self.mcp.tools["save_arxml"]("ws_12345", "C:\\tmp\\y.arxml", 51)
        self.assertEqual(out, {"ok": True})
        self.manager.save_arxml.assert_called_once_with("ws_12345", "C:\\tmp\\y.arxml", 51)

        mapping = {"A": "/PkgA", "B": "/PkgB"}
        out = await self.mcp.tools["create_package_map"]("ws_12345", mapping)
        self.assertEqual(out, {"ok": True})
        self.manager.create_package_map.assert_called_once_with("ws_12345", mapping)

    async def test_find_element_and_list_root_packages(self):
        self.manager.find_element.return_value = {"type": "Dummy", "name": "X", "ref": "/X"}
        out = await self.mcp.tools["find_element"]("ws_12345", "/X")
        self.manager.find_element.assert_called_once_with("ws_12345", "/X")
        self.assertEqual(out, {"found": True, "element": {"type": "Dummy", "name": "X", "ref": "/X"}})

        out = await self.mcp.tools["list_root_packages"]("ws_12345")
        self.manager.list_root_packages.assert_called_once_with("ws_12345")
        self.assertEqual(out, {"packages": ["PkgA", "PkgB"]})

    async def test_delegated_tools_forward_arguments(self):
        cases = [
            ("create_swc_internal_behavior", ("ws", "/Comp"), {}, "create_swc_internal_behavior", ()),
            ("create_runnable", ("ws", "/Comp", "Run", "Sym"), {}, "create_runnable", ()),
            ("create_timing_event", ("ws", "/Comp", "Run", 0.01), {}, "create_timing_event", ()),
            ("create_data_received_event", ("ws", "/Comp", "Run", "/Port", "Elem"), {}, "create_data_received_event", ()),
            ("create_operation_invoked_event", ("ws", "/Comp", "Run", "Op"), {}, "create_operation_invoked_event", ()),
            ("create_mode_switch_event", ("ws", "/Comp", "Run", "/ModeGroup"), {}, "create_mode_switch_event", ()),
            ("set_nonqueued_receiver_com_spec", ("ws", "/Comp", "P", "Elem", None), {}, "set_nonqueued_receiver_com_spec", ()),
            ("set_queued_sender_com_spec", ("ws", "/Comp", "P", "Elem", 10), {}, "set_queued_sender_com_spec", ()),
            ("create_mode_declaration_group", ("ws", "/Pkg", "MDG", ["A", "B"]), {}, "create_mode_declaration_group", ()),
            ("create_mode_switch_interface", ("ws", "/Pkg", "MSI", "/ModeGroup"), {}, "create_mode_switch_interface", ()),
            ("create_assembly_connector", ("ws", "/Comp", "ProvC", "ProvP", "ReqC", "ReqP"), {}, "create_assembly_connector", ()),
            ("create_delegation_connector", ("ws", "/Comp", "InnerC", "InnerP", "OuterP"), {}, "create_delegation_connector", ()),
            ("set_port_api_option", ("ws", "/Comp", "P", True, False), {}, "set_port_api_option", ()),
            ("create_sender_receiver_interface", ("ws", "/Pkg", "If"), {}, "create_sender_receiver_interface", ()),
            ("create_data_element", ("ws", "/If", "E", "/T"), {}, "create_data_element", ()),
            ("create_client_server_interface", ("ws", "/Pkg", "If"), {}, "create_client_server_interface", ()),
            ("create_operation", ("ws", "/If", "Op"), {}, "create_operation", ()),
            ("create_component_type", ("ws", "/Pkg", "C", "Application"), {}, "create_component_type", ()),
            ("create_port", ("ws", "/C", "P", "/If", "P"), {}, "create_port", ()),
            ("create_implementation_data_type", ("ws", "/Pkg", "T", "VALUE", None), {}, "create_implementation_data_type", ()),
            ("create_sw_base_type_in_package", ("ws", "/Pkg", "BT", None, None, None, None, None, None), {}, "create_sw_base_type_in_package", ()),
            ("create_unit_in_package", ("ws", "/Pkg", "U", None, None, None, None), {}, "create_unit_in_package", ()),
            ("create_constant_in_package", ("ws", "/Pkg", "K", 123), {}, "create_constant_in_package", ()),
            ("add_sw_base_type_by_package_key", ("ws", "Key"), {"name": "BT"}, "add_sw_base_type_by_package_key", ()),
            ("add_constant_by_package_key", ("ws", "Key", "K", 1), {}, "add_constant_by_package_key", ()),
            ("add_unit_by_package_key", ("ws", "Key"), {"name": "U"}, "add_unit_by_package_key", ()),
        ]

        for tool_name, args, kwargs, method_name, _ in cases:
            with self.subTest(tool=tool_name):
                method = getattr(self.manager, method_name)
                method.reset_mock()
                out = await self.mcp.tools[tool_name](*args, **kwargs)
                self.assertEqual(out, {"ok": True})
                method.assert_called_once_with(*args, **kwargs)


if __name__ == "__main__":
    unittest.main()
