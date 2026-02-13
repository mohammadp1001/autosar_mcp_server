from __future__ import annotations

import logging
import sys
from typing import Optional

from autosar_mcp.config import Settings


class _ColorFormatter(logging.Formatter):
    """
    Minimal color formatter for local dev.
    In CI or when stdout isn't a TTY, it behaves like normal.
    """
    COLORS = {
        "DEBUG": "\x1b[36m",   # cyan
        "INFO": "\x1b[32m",    # green
        "WARNING": "\x1b[33m", # yellow
        "ERROR": "\x1b[31m",   # red
        "CRITICAL": "\x1b[35m" # magenta
    }
    RESET = "\x1b[0m"

    def __init__(self, fmt: str, use_color: bool) -> None:
        super().__init__(fmt=fmt, datefmt="%Y-%m-%d %H:%M:%S")
        self.use_color = use_color

    def format(self, record: logging.LogRecord) -> str:
        msg = super().format(record)
        if not self.use_color:
            return msg
        color = self.COLORS.get(record.levelname, "")
        if not color:
            return msg
        return f"{color}{msg}{self.RESET}"


def get_logger(name: str) -> logging.Logger:
    """
    Convenience getter. Use this everywhere instead of logging.getLogger directly.
    """
    return logging.getLogger(name)


def _to_level(level: str) -> int:
    try:
        return logging._nameToLevel[level.upper()]  # pylint: disable=protected-access
    except KeyError:
        return logging.INFO


def setup_logging(settings: Settings, *, force: bool = False) -> None:
    """
    Configure root logging once.

    - Logs go to stderr (good for CLI + piping).
    - Adds a simple formatter with optional color.
    - Avoids duplicate handlers if called multiple times.
    """
    root = logging.getLogger()
    if root.handlers and not force:
        # Already configured
        return

    # Reset handlers if force=True
    if force:
        for h in list(root.handlers):
            root.removeHandler(h)

    level = _to_level(settings.log_level)
    root.setLevel(level)

    handler = logging.StreamHandler(stream=sys.stderr)

    # Keep logs readable: time, level, logger name, message
    fmt = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

    use_color = sys.stderr.isatty() and settings.debug
    handler.setFormatter(_ColorFormatter(fmt, use_color=use_color))
    handler.setLevel(level)

    root.addHandler(handler)

    # Quiet down noisy loggers (tweak as needed)
    for noisy in ("asyncio", "urllib3"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    # Optional: when debug is on, show where logs came from
    if settings.debug:
        _enable_debug_details()


def _enable_debug_details() -> None:
    """
    Adds source details in debug mode without changing every formatter.
    """
    # You can extend this later. For now, just ensure we see DEBUG everywhere.
    logging.getLogger().setLevel(logging.DEBUG)
