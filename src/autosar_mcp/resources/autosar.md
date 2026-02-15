# AUTOSAR Python Package -- Technical Summary

The `autosar` (cogu/autosar) Python package is a structured object model
for AUTOSAR ARXML. It allows programmatic creation, modification,
reading, and writing of AUTOSAR system descriptions.

------------------------------------------------------------------------

## Core Architecture

Reader → XML → Python objects\
Workspace → In-memory AUTOSAR model\
Writer → Python objects → XML\


Most interaction happens through **Workspace**.

------------------------------------------------------------------------

## 1. Workspace

Global in-memory AUTOSAR model container.

Responsibilities: - Stores packages and elements - Provides search
(`find`) - Manages package map - Handles multi-document output -
Controls behavior settings

Think of it as the root AUTOSAR project model.

------------------------------------------------------------------------

## 2. Document

Represents a physical ARXML file.

Used for: - Writing XML - Splitting model into multiple files

------------------------------------------------------------------------

## 3. Package (AR-PACKAGE)

Namespace container in AUTOSAR.

Example path:

    /AUTOSAR_Platform/BaseTypes

Packages: - Can be nested - Contain elements - Identified by
hierarchical paths

------------------------------------------------------------------------

## 4. Package Map

Developer convenience feature mapping keys to package paths.

Example:

    workspace.create_package_map({
        "PlatformBaseTypes": "AUTOSAR_Platform/BaseTypes"
    })

Not part of AUTOSAR standard.

Package paths: /AUTOSAR_Platform/..., /PortInterfaces, /Constants, /ComponentTypes
Interface names: *_I, constants: *_IV, impl types: uint16, uint32, boolean

------------------------------------------------------------------------

## 5. AUTOSAR Elements

Each AUTOSAR XML tag corresponds to a Python class.

Examples:

  XML Tag                         Python Class
  ------------------------------- ----------------------------------
  AR-PACKAGE                      Package
  SW-BASE-TYPE                    SwBaseType
  IMPLEMENTATION-DATA-TYPE        ImplementationDataType
  SENDER-RECEIVER-INTERFACE       SenderReceiverInterface
  APPLICATION-SW-COMPONENT-TYPE   ApplicationSoftwareComponentType
  COMPOSITION-SW-COMPONENT-TYPE   CompositionSwComponentType

Located in:

    autosar.xml.element

------------------------------------------------------------------------

## 6. References (REF)

AUTOSAR uses reference strings internally.

Example:

    base_type_ref = base_type.ref()

Elements reference each other via `.ref()`.

------------------------------------------------------------------------

## 7. Port Interfaces

Supported types: - SenderReceiverInterface - ClientServerInterface

Define data elements and operations.

------------------------------------------------------------------------

## 8. Software Components (SWC)

Supported types: - ApplicationSoftwareComponentType -
CompositionSwComponentType

Application SWC: - Contains behavior - Defines runnables and events

Composition SWC: - Connects components via connectors

------------------------------------------------------------------------

## 9. Internal Behavior

Created via:

    behavior = swc.create_internal_behavior()

Defines: - Runnables - Events - Port API options - Access points

------------------------------------------------------------------------

## 10. ComSpec

Communication specification for ports.

Defines: - Queue length - Init value - Alive timeout - Update rules

------------------------------------------------------------------------

## 11. Multi-Document Output

Split model into multiple ARXML files:

    workspace.set_document_root(...)
    workspace.create_document(...)
    workspace.create_document_mapping(...)
    workspace.write_documents()

------------------------------------------------------------------------

## Required Knowledge Before Use

You must understand: 1. AUTOSAR hierarchical package structure 2.
Reference-based linking 3. Build order dependencies 4. SWC types
(Application vs Composition) 5. Behavior and event model 6.
Multi-document writing mechanism

------------------------------------------------------------------------

## Typical Build Flow

1.  Create Workspace
2.  Create Package Map
3.  Create Base Types
4.  Create Implementation Data Types
5.  Create Port Interfaces
6.  Create Constants
7.  Create Components
8.  Create Ports
9.  Create Behavior + Runnables + Events
10. Configure Documents
11. Write ARXML

------------------------------------------------------------------------

## What This Library Is Not

-   Not a full AUTOSAR validator
-   Not a graphical modeling tool
-   Not a complete RTE generator

It is a structured XML modeling library.
