from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import os

from autosar.base import DEFAULT_SCHEMA_VERSION


def _env(name: str, default: str | None = None) -> str | None:
    """Read environment variable with optional default."""
    val = os.getenv(name)
    return val if val is not None else default


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be an int, got {raw!r}") from exc


@dataclass(frozen=True)
class Settings:
    """
    Central configuration for the AUTOSAR MCP server.

    Keep this as the single source of truth.
    Everything else should depend on Settings, not on os.environ directly.
    """

    # --- Server/runtime
    server_name: str = "autosar-mcp"
    log_level: str = "INFO"
    debug: bool = False

    # --- Project / filesystem
    workspace_root: Path = field(default_factory=lambda: Path.cwd())
    allowed_roots: tuple[Path, ...] = field(default_factory=tuple)  # sandboxing
    temp_dir: Path = field(default_factory=lambda: Path(".autosar-mcp/tmp"))

    # --- AUTOSAR / ARXML behavior
    schema_version: int = DEFAULT_SCHEMA_VERSION
    warn_on_unprocessed_element: bool = True
    use_full_path_on_warning: bool = False
    stop_on_parse_error: bool = False  # if True, Reader stops at first parse error

    # --- Output formatting
    xml_indent_step: int = 2  # Writer uses 2 today; keep configurable for future
    skip_root_attr_on_write_str: bool = True

    # --- GitHub / gh integration
    enable_gh_cli: bool = True
    gh_binary: str = "gh"

    # --- Graph export (dependency visualization)
    graph_default_format: str = "dot"  # dot | json
    graph_max_nodes: int = 2500

    def validate(self) -> "Settings":
        """
        Validate settings and ensure directories exist when appropriate.
        """
        if self.schema_version <= 0:
            raise ValueError("schema_version must be positive")

        if self.allowed_roots:
            # Ensure allowed_roots are absolute
            for p in self.allowed_roots:
                if not p.is_absolute():
                    raise ValueError(f"allowed_roots must be absolute paths. Got: {p}")

        # Create temp dir if needed
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        return self


def load_settings() -> Settings:
    """
    Load settings from environment variables.

    You can later extend this to:
    - load a TOML/YAML config file
    - merge CLI args (preferred) on top of env
    """
    allowed_roots_raw = _env("AUTOSAR_MCP_ALLOWED_ROOTS", "")
    allowed_roots: tuple[Path, ...] = tuple(
        Path(p).expanduser().resolve()
        for p in allowed_roots_raw.split(os.pathsep)
        if p.strip()
    )

    root_raw = _env("AUTOSAR_MCP_WORKSPACE_ROOT", None)
    workspace_root = Path(root_raw).expanduser().resolve() if root_raw else Path.cwd().resolve()

    s = Settings(
        server_name=_env("AUTOSAR_MCP_SERVER_NAME", "autosar-mcp") or "autosar-mcp",
        log_level=(_env("AUTOSAR_MCP_LOG_LEVEL", "INFO") or "INFO").upper(),
        debug=_env_bool("AUTOSAR_MCP_DEBUG", False),

        workspace_root=workspace_root,
        allowed_roots=allowed_roots,
        temp_dir=Path(_env("AUTOSAR_MCP_TEMP_DIR", str(workspace_root / ".autosar-mcp/tmp"))).expanduser().resolve(),

        schema_version=_env_int("AUTOSAR_MCP_SCHEMA_VERSION", DEFAULT_SCHEMA_VERSION),
        warn_on_unprocessed_element=_env_bool("AUTOSAR_MCP_WARN_UNPROCESSED", True),
        use_full_path_on_warning=_env_bool("AUTOSAR_MCP_WARN_FULL_PATH", False),
        stop_on_parse_error=_env_bool("AUTOSAR_MCP_STOP_ON_PARSE_ERROR", False),

        xml_indent_step=_env_int("AUTOSAR_MCP_XML_INDENT_STEP", 2),
        skip_root_attr_on_write_str=_env_bool("AUTOSAR_MCP_SKIP_ROOT_ATTR_ON_WRITE_STR", True),

        enable_gh_cli=_env_bool("AUTOSAR_MCP_ENABLE_GH", True),
        gh_binary=_env("AUTOSAR_MCP_GH_BIN", "gh") or "gh",

        graph_default_format=_env("AUTOSAR_MCP_GRAPH_FORMAT", "dot") or "dot",
        graph_max_nodes=_env_int("AUTOSAR_MCP_GRAPH_MAX_NODES", 2500),
    )
    return s.validate()
