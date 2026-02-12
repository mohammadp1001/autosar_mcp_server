from __future__ import annotations

from pathlib import Path
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, field_validator


# ----------------------------
# Generic / shared primitives
# ----------------------------

RefStr = str  # AUTOSAR ref path like "/DataTypes/Speed_T"
FilePathStr = str


class ToolResult(BaseModel):
    """
    Standard result envelope for tools.

    Keep it consistent so clients can handle responses uniformly.
    """
    ok: bool = True
    message: str | None = None
    warnings: list[str] = Field(default_factory=list)
    data: dict[str, Any] = Field(default_factory=dict)


class WarningItem(BaseModel):
    code: str
    message: str
    context: dict[str, Any] = Field(default_factory=dict)


class IssueItem(BaseModel):
    severity: Literal["info", "warning", "error"]
    code: str
    message: str
    location: dict[str, Any] = Field(default_factory=dict)  # file, line, ref, etc.


# ----------------------------
# Project loading / context
# ----------------------------

class ProjectSelector(BaseModel):
    """
    Identifies what the caller wants to operate on.
    """
    root_dir: FilePathStr = Field(..., description="Directory containing ARXML files")
    arxml_glob: str = Field("**/*.arxml", description="Glob for discovery under root_dir")
    schema_version: int | None = Field(None, description="Override schema version; default comes from server settings")

    @field_validator("root_dir")
    @classmethod
    def _root_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("root_dir cannot be empty")
        return v


class LoadProjectRequest(ProjectSelector):
    """
    Load and build an in-memory representation (object graph + index).
    """
    stop_on_parse_error: bool = False
    warn_on_unprocessed_element: bool = True
    use_full_path_on_warning: bool = False


class LoadProjectResponse(BaseModel):
    project_id: str
    file_count: int
    package_count: int
    element_count: int
    warnings: list[str] = Field(default_factory=list)


# ----------------------------
# Element identity / metadata
# ----------------------------

class ElementKey(BaseModel):
    """
    Common way to point at an element.
    Provide either 'ref' or ('package_ref' + 'name') depending on use-case.
    """
    ref: RefStr | None = None
    package_ref: RefStr | None = None
    name: str | None = None

    @field_validator("ref")
    @classmethod
    def _ref_format(cls, v: str | None) -> str | None:
        if v is None:
            return None
        if not v.startswith("/"):
            raise ValueError("ref must start with '/' (example: /DataTypes/Speed_T)")
        return v

    @field_validator("name")
    @classmethod
    def _name_non_empty(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("name cannot be empty")
        return v

    def require_ref_or_package_and_name(self) -> None:
        if self.ref:
            return
        if self.package_ref and self.name:
            return
        raise ValueError("Provide either 'ref' OR both 'package_ref' and 'name'.")


class ElementSummary(BaseModel):
    ref: RefStr
    name: str
    type: str
    package_ref: RefStr | None = None
    source_file: FilePathStr | None = None


# ----------------------------
# Query requests/responses
# ----------------------------

class FindElementRequest(BaseModel):
    project_id: str
    key: ElementKey


class FindElementResponse(BaseModel):
    found: bool
    element: ElementSummary | None = None


class SearchRequest(BaseModel):
    project_id: str
    query: str = Field(..., description="Free text / substring search")
    type_filter: list[str] = Field(default_factory=list, description="Optional class names to filter")
    limit: int = 50

    @field_validator("limit")
    @classmethod
    def _limit_range(cls, v: int) -> int:
        if v < 1 or v > 5000:
            raise ValueError("limit must be between 1 and 5000")
        return v


class SearchResponse(BaseModel):
    results: list[ElementSummary] = Field(default_factory=list)


# ----------------------------
# Refactoring
# ----------------------------

class RenameRequest(BaseModel):
    project_id: str
    target_ref: RefStr
    new_name: str
    dry_run: bool = True

    @field_validator("target_ref")
    @classmethod
    def _target_ref_format(cls, v: str) -> str:
        if not v.startswith("/"):
            raise ValueError("target_ref must start with '/'")
        return v

    @field_validator("new_name")
    @classmethod
    def _new_name_ok(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("new_name cannot be empty")
        return v


class RenameResult(BaseModel):
    renamed_ref: RefStr
    old_name: str
    new_name: str
    updated_reference_count: int = 0
    affected_files: list[FilePathStr] = Field(default_factory=list)


# ----------------------------
# Validation
# ----------------------------

class ValidateRequest(BaseModel):
    project_id: str
    checks: list[str] = Field(default_factory=list, description="Optional list of check IDs. Empty = run defaults.")


class ValidateResponse(BaseModel):
    ok: bool
    issues: list[IssueItem] = Field(default_factory=list)


# ----------------------------
# Graph export / visualization
# ----------------------------

class GraphRequest(BaseModel):
    project_id: str
    root_ref: RefStr | None = None
    depth: int = 3
    direction: Literal["depends_on", "depended_by", "both"] = "depends_on"
    format: Literal["dot", "json"] = "dot"
    max_nodes: int = 2500

    @field_validator("depth")
    @classmethod
    def _depth_range(cls, v: int) -> int:
        if v < 1 or v > 50:
            raise ValueError("depth must be between 1 and 50")
        return v


class GraphResponse(BaseModel):
    format: Literal["dot", "json"]
    content: str | dict[str, Any]
    node_count: int
    edge_count: int


# ----------------------------
# Generation (RTE types, doc splitting)
# ----------------------------

class GenerateRteTypesRequest(BaseModel):
    project_id: str
    dest_dir: FilePathStr
    header_name: str = "Rte_Type.h"
    dry_run: bool = False


class GenerateRteTypesResponse(BaseModel):
    ok: bool
    generated_files: list[FilePathStr] = Field(default_factory=list)
    message: str | None = None
