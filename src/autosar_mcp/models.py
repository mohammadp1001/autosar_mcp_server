"""Pydantic models for AUTOSAR MCP server tool I/O.

This module defines request/response schemas used by the server/tool layer.
All models forbid extra fields to keep inputs strict and predictable.
"""
from typing import Any, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict

# pylint: disable=line-too-long

# -------------------------
# Pydantic I/O models
# -------------------------

class CreateWorkspaceOut(BaseModel):
    """Response model for workspace creation."""
    model_config = ConfigDict(extra="forbid")
    workspace_id: str


class WorkspaceIdIn(BaseModel):
    """Request model containing a workspace identifier."""
    model_config = ConfigDict(extra="forbid")
    workspace_id: str = Field(..., min_length=5)


class LoadArxmlIn(BaseModel):
    """Request model for loading a single ARXML file into a workspace."""
    model_config = ConfigDict(extra="forbid")
    workspace_id: str = Field(..., min_length=5)
    file_path: str = Field(..., min_length=1)


class SaveArxmlIn(BaseModel):
    """Request model for saving a workspace to an ARXML file."""
    model_config = ConfigDict(extra="forbid")
    workspace_id: str = Field(..., min_length=5)
    file_path: str = Field(..., min_length=1)
    version: int = Field(default=51, ge=1)


class CreatePackageMapIn(BaseModel):
    """Request model for defining a workspace package map."""
    model_config = ConfigDict(extra="forbid")
    workspace_id: str = Field(..., min_length=5)
    mapping: dict[str, str]


class FindElementIn(BaseModel):
    """Request model for finding an element by AUTOSAR path."""
    model_config = ConfigDict(extra="forbid")
    workspace_id: str = Field(..., min_length=5)
    path: str = Field(..., min_length=1)


class FindElementOut(BaseModel):
    """Response model for an element lookup."""
    model_config = ConfigDict(extra="forbid")
    found: bool
    element: Optional[dict[str, Any]] = None


class ListRootPackagesOut(BaseModel):
    """Response model listing root package names in a workspace."""
    model_config = ConfigDict(extra="forbid")
    packages: list[str]


class CreateSenderReceiverInterfaceIn(BaseModel):
    """Request model for creating a Sender-Receiver interface."""
    model_config = ConfigDict(extra="forbid")
    workspace_id: str = Field(..., min_length=5)
    package_path: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)


class CreateDataElementIn(BaseModel):
    """Request model for creating a data element under an SR interface."""
    model_config = ConfigDict(extra="forbid")
    workspace_id: str = Field(..., min_length=5)
    interface_path: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    type_ref: str = Field(..., min_length=1)


class CreateClientServerInterfaceIn(BaseModel):
    """Request model for creating a Client-Server interface."""
    model_config = ConfigDict(extra="forbid")
    workspace_id: str = Field(..., min_length=5)
    package_path: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)


class CreateOperationIn(BaseModel):
    """Request model for creating an operation under a CS interface."""
    model_config = ConfigDict(extra="forbid")
    workspace_id: str = Field(..., min_length=5)
    interface_path: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)


class CreateComponentTypeIn(BaseModel):
    """Request model for creating an AUTOSAR component type."""
    model_config = ConfigDict(extra="forbid")
    workspace_id: str = Field(..., min_length=5)
    package_path: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    component_type: str = Field(..., min_length=1)


class CreatePortIn(BaseModel):
    """Request model for creating a port on a component type."""
    model_config = ConfigDict(extra="forbid")
    workspace_id: str = Field(..., min_length=5)
    component_path: str = Field(..., min_length=1)
    port_name: str = Field(..., min_length=1)
    interface_path: str = Field(..., min_length=1)
    port_type: str = Field(..., min_length=1)  # P, R, PR


class CreateImplementationDataTypeIn(BaseModel):
    """Request model for creating an ImplementationDataType."""
    model_config = ConfigDict(extra="forbid")
    workspace_id: str = Field(..., min_length=5)
    package_path: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    category: str = Field(default="VALUE", min_length=1)
    base_type_ref: Optional[str] = None


class ToolResult(BaseModel):
    """Generic tool execution result."""
    model_config = ConfigDict(extra="forbid")
    ok: bool
    message: str
    details: Optional[dict[str, Any]] = None


class AddElementByKeySwBaseTypeIn(BaseModel):
    """Request model for adding a SwBaseType into a package selected by key."""
    model_config = ConfigDict(extra="forbid")
    workspace_id: str = Field(..., min_length=5)
    package_key: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    size: Optional[int] = Field(default=None, ge=0)
    max_size: Optional[int] = Field(default=None, ge=0)
    encoding: Optional[str] = None
    alignment: Optional[int] = Field(default=None, ge=0)
    byte_order: Optional[Literal["MOST_SIGNIFICANT_BYTE_FIRST", "MOST_SIGNIFICANT_BYTE_LAST", "OPAQUE", "UNDEFINED"]] = None
    native_declaration: Optional[str] = None


class AddElementByKeyConstantIn(BaseModel):
    """Request model for adding a ConstantSpecification into a package selected by key."""
    model_config = ConfigDict(extra="forbid")
    workspace_id: str = Field(..., min_length=5)
    package_key: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    # value can be int/float/str/list/tuple - matches autosar.xml.element.ValueSpecification.make_value inputs
    value: Any


class AddElementByKeyUnitIn(BaseModel):
    """Request model for adding a Unit into a package selected by key."""
    model_config = ConfigDict(extra="forbid")
    workspace_id: str = Field(..., min_length=5)
    package_key: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    display_name: Optional[str] = None
    factor: Optional[float] = None
    offset: Optional[float] = None
    physical_dimension_ref: Optional[str] = None
