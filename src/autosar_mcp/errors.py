from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class AutosarMcpError(Exception):
    """
    Base class for all server-defined errors.

    Raise subclasses of this for anything you want to report to the caller
    in a controlled way.
    """


# ---------- Input / Tool contract errors ----------

class ToolInputError(AutosarMcpError):
    """
    Invalid user/tool input (missing fields, wrong types, invalid values).
    """


class NotFoundError(AutosarMcpError):
    """
    Requested element/resource not found (e.g., element ref doesn't exist).
    """


# ---------- Filesystem / security ----------

class PathAccessError(AutosarMcpError):
    """
    Attempted to access a path outside allowed roots or otherwise forbidden.
    """


class FileOperationError(AutosarMcpError):
    """
    General file read/write failure (permissions, missing file, etc.).
    """


# ---------- AUTOSAR / ARXML processing ----------

class ArxmlParseError(AutosarMcpError):
    """
    Wraps autosar.xml.exception.ParseError or similar parsing issues.
    """


class ArxmlWriteError(AutosarMcpError):
    """
    Errors during serialization/writing.
    """


class ValidationError(AutosarMcpError):
    """
    Model is inconsistent (broken refs, duplicates, rule violations).
    """


class RefactorError(AutosarMcpError):
    """
    Safe refactoring could not be applied (would break model, conflicts, etc.).
    """


class ExternalToolError(AutosarMcpError):
    """
    Failure while invoking external tools (e.g. gh cli, graphviz).
    """


# ---------- Optional: a structured payload you can return in resources ----------

@dataclass(frozen=True)
class ErrorReport:
    """
    A safe-to-serialize error payload for resources/tools to return.
    Avoids leaking stack traces by default.
    """
    type: str
    message: str
    context: dict[str, Any] | None = None


def to_error_report(exc: Exception, *, context: dict[str, Any] | None = None) -> ErrorReport:
    """
    Convert any exception into a structured report.

    Use this when you want tools to return errors as JSON-like payloads
    instead of raising (depending on how you design your MCP error policy).
    """
    return ErrorReport(
        type=exc.__class__.__name__,
        message=str(exc),
        context=context,
    )
