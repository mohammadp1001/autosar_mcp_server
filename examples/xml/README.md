# AUTOSAR MCP Server

An MCP (Model Context Protocol) server that enables LLMs (e.g., GitHub Copilot in Agent mode) to build AUTOSAR ARXML models programmatically using structured tools instead of writing raw XML.

This server wraps the `autosar` Python library and exposes safe, high-level tools for:

- Creating packages
- Creating base types and implementation data types
- Creating port interfaces
- Creating software components
- Creating ports
- Creating internal behavior (runnables, events)
- Splitting output into multiple ARXML documents

---

# Architecture

LLM (Copilot / Agent)
↓
MCP tools (tools.py)
↓
WorkspaceManager
↓
autosar.xml library
↓
Generated ARXML files

yaml
Copy code

### Design Principles

- Tools are thin wrappers
- All AUTOSAR logic lives in `WorkspaceManager`
- ObjectRegistry protects internal objects from LLM access
- Multiple ARXML files supported via document mapping

---

# Project Structure

autosar_mcp/
│
├── core/
│ ├── workspace_manager.py
│ └── registry.py
│
├── tools.py
├── server.py
└── prompts/ (optional)

yaml
Copy code

---

# Installation

```bash
pip install -r requirements.txt
Ensure the following dependencies are installed:

autosar

mcp

pydantic

Running the MCP Server
Run locally:

bash
Copy code
python -m autosar_mcp.server
or

bash
Copy code
python autosar_mcp/server.py
The server communicates via stdio, which is required for GitHub Copilot MCP integration.

Connecting to GitHub Copilot (VS Code)
Create .vscode/mcp.json in your project:

json
Copy code
{
  "servers": {
    "autosar-mcp": {
      "command": "python",
      "args": ["-m", "autosar_mcp.server"]
    }
  }
}
Then:

Open VS Code

Open Copilot Chat

Switch to Agent mode

Start the autosar-mcp server

Copilot can now call your AUTOSAR tools

Supported Capabilities
Platform Modeling
Create SW base types

Create ImplementationDataTypes

Create Units

Create Constants

Interfaces
Create SenderReceiverInterface

Create ClientServerInterface

Create DataElements

Create Operations

Components
Create ApplicationSoftwareComponentType

Create CompositionSwComponentType

Create Ports (P, R, PR)

Create Internal Behavior

Create Runnables

Create Events

Multi-File Output
Set document root

Create document definitions

Create document mappings

Write multiple ARXML files automatically

Example Workflow (LLM)
Typical build order:

create_workspace

create_package_map

Create base types

Create implementation data types

Create port interfaces

Create components

Create ports

Create internal behavior

set_document_root

create_document

create_document_mapping

write_documents

Multi-File Generation
The server supports splitting into:

platform.arxml

portinterfaces.arxml

constants.arxml

Component-specific ARXML files

Using:

python
Copy code
set_document_root(...)
create_document(...)
create_document_mapping(...)
write_documents(...)
Safety Model
LLM never receives raw AUTOSAR objects

All objects are stored in ObjectRegistry

Access is controlled via workspace_id

Tools return JSON-safe responses

Limitations
Only ApplicationSoftwareComponentType and CompositionSwComponentType are supported

Some advanced AUTOSAR categories are not implemented in the underlying library

Base type linking for ImplementationDataTypes is minimal (can be extended)

Future Improvements
Full ComSpec configuration tools

ModeSwitch refinements

Better validation feedback

Structured tool result schemas

Example orchestration prompts