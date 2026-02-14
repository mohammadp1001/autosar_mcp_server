# AUTOSAR MCP Server 🚗⚙️

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![MCP](https://img.shields.io/badge/MCP-compatible-green.svg)
![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)

An **AUTOSAR MCP Server** that equips your LLM 
to modify/generate AUTOSAR ARXML files using safe, high-level tools.

This server wraps the `autosar` Python library and exposes
domain-specific tools through MCP.

The current version only supports AUTOSAR classic.

<!-- autosar_mcp: io.github.mohammadp1001/autosar_mcp_server -->
------------------------------------------------------------------------

## ✨ Features

-    Create AUTOSAR packages
-    Create SW Base Types & Implementation Data Types
-    Create Sender-Receiver & Client-Server Interfaces
-    Create Software Components
-    Create Ports (P / R / PR)
-    Create Internal Behavior (Runnables, Events)
-    Split output into multiple ARXML files


------------------------------------------------------------------------

## Architecture

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
    └── prompts/ 

------------------------------------------------------------------------

## 🔒 Safety Model

-   LLM never receives raw AUTOSAR objects
-   All objects stored in ObjectRegistry
-   Access controlled via workspace_id
-   Tools return JSON-safe responses

------------------------------------------------------------------------

## 📄 License

MIT License
