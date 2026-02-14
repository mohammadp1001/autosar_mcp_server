# AUTOSAR MCP Server 🚗⚙️

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![MCP](https://img.shields.io/badge/MCP-compatible-green.svg)
![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)

An **AUTOSAR Model Context Protocol (MCP) Server** that allows Large
Language Models (LLMs) --- such as **GitHub Copilot (Agent Mode)** ---
to generate structured AUTOSAR ARXML models using safe, high-level tools
instead of manually writing XML.

This server wraps the `autosar` Python library and exposes
domain-specific tools through MCP.

------------------------------------------------------------------------

## ✨ Features

-   🔧 Create AUTOSAR packages
-   🧱 Create SW Base Types & Implementation Data Types
-   🔌 Create Sender-Receiver & Client-Server Interfaces
-   🧩 Create Software Components
-   🚪 Create Ports (P / R / PR)
-   🏗 Create Internal Behavior (Runnables, Events)
-   📦 Split output into multiple ARXML files
-   🔐 Safe architecture via ObjectRegistry

------------------------------------------------------------------------

## 🏗 Architecture

    LLM (Copilot / Agent Mode)
            ↓
    MCP Tools (tools.py)
            ↓
    WorkspaceManager
            ↓
    autosar.xml
            ↓
    Generated ARXML files

------------------------------------------------------------------------

## 📁 Project Structure

    autosar_mcp/
    │
    ├── core/
    │   ├── workspace_manager.py
    │   └── registry.py
    │
    ├── tools.py
    ├── server.py
    └── prompts/ (optional)

------------------------------------------------------------------------

## 🚀 Installation

``` bash
pip install -r requirements.txt
```

Dependencies: - autosar - mcp - pydantic

------------------------------------------------------------------------

## ▶ Running the Server

``` bash
python -m autosar_mcp.server
```

The server communicates over **stdio**, required for GitHub Copilot MCP
integration.

------------------------------------------------------------------------

## 🤖 Using with GitHub Copilot (VS Code)

Create `.vscode/mcp.json`:

``` json
{
  "servers": {
    "autosar-mcp": {
      "command": "python",
      "args": ["-m", "autosar_mcp.server"]
    }
  }
}
```

Then: 1. Open VS Code 2. Open Copilot Chat 3. Switch to Agent Mode 4.
Start the autosar-mcp server 5. Copilot can now call AUTOSAR tools
directly

------------------------------------------------------------------------

## 🧠 Typical LLM Workflow

1.  create_workspace
2.  create_package_map
3.  Create base types
4.  Create implementation data types
5.  Create port interfaces
6.  Create components
7.  Create ports
8.  Create internal behavior
9.  set_document_root
10. create_document
11. create_document_mapping
12. write_documents

------------------------------------------------------------------------

## 🔒 Safety Model

-   LLM never receives raw AUTOSAR objects
-   All objects stored in ObjectRegistry
-   Access controlled via workspace_id
-   Tools return JSON-safe responses

------------------------------------------------------------------------

## 📄 License

MIT License
