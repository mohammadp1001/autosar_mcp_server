import autosar.xml
import autosar.xml.element as ar_element
import autosar.xml.reader as ar_reader
import os
import logging

logger = logging.getLogger("workspace_manager")

class WorkspaceManager:
    def __init__(self):
        self.workspace = autosar.xml.Workspace()
        self.files_loaded = []

    def clear(self):
        """Resets the workspace."""
        self.workspace = autosar.xml.Workspace()
        self.files_loaded = []

    def load_files(self, files: list[str]):
        """Loads ARXML files into the workspace."""
        reader = ar_reader.Reader()
        for file_path in files:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            logger.info(f"Reading {file_path}")
            # Reader.read_file returns a Document object
            document = reader.read_file(file_path)
            
            # Merge document packages into workspace
            for package in document.packages:
                self._merge_package(self.workspace, package)
                
            self.files_loaded.append(file_path)

    def _merge_package(self, parent_collection, source_package):
        """
        Recursively merges source_package into parent_collection.
        parent_collection can be Workspace, Document, or Package.
        """
        # check if package already exists in parent
        existing_package = parent_collection.find(source_package.name)
        
        if existing_package is None:
            # If not exists, just append the whole source package tree
            # clone? or just move? Moving is safer providing source_document is discarded.
            # But we need to be careful about parenting. append() sets parent.
            parent_collection.append(source_package)
        elif isinstance(existing_package, ar_element.Package):
            # If exists and is a package, recurse
            # 1. Merge sub-packages
            for sub_package in source_package.packages:
                self._merge_package(existing_package, sub_package)
            
            # 2. Merge elements
            for element in source_package.elements:
                existing_element = existing_package.find(element.name)
                if existing_element is None:
                    existing_package.append(element)
                else:
                    # Logic for duplicate elements:
                    # For now, warn and skip.
                    logger.warning(f"Duplicate element '{element.name}' in package '{existing_package.name}'. Skipping.")
        else:
             logger.error(f"Conflict: '{source_package.name}' exists but is not a package.")

    def save(self, target_directory: str, version: int):
        """Saves documents to the target directory."""
        self.workspace.set_document_root(target_directory)
        
        # Auto-create documents for all root packages
        # If no documents are defined, nothing is written.
        # Strategy: Create one document per root package causing duplication if not handled carefully.
        # Better: Create a document mapping that maps all packages.
        
        # Clear existing configs to avoid duplication on repeated saves
        self.workspace.documents.clear()
        self.workspace.document_mappings.clear()

        for package in self.workspace.packages:
            # Simple strategy: One matching document for each package found
            filename = f"{package.name}.arxml"
            self.workspace.create_document(filename, packages=str(package.ref()))

        self.workspace.write_documents(schema_version=version)

    def list_content(self, path: str) -> str:
        """Lists content of a package."""
        element = self.get_element(path)
        
        if isinstance(element, (autosar.xml.Workspace, ar_element.Package)):
            lines = []
            lines.append(f"Contents of {path}:")
             # List Sub-packages
            if hasattr(element, 'packages') and element.packages:
                lines.append("\nPackages:")
                for pkg in element.packages:
                    lines.append(f"  [PKG] {pkg.name}")
            
            # List Elements
            if hasattr(element, 'elements') and element.elements:
                lines.append("\nElements:")
                for elem in element.elements:
                    lines.append(f"  [{type(elem).__name__}] {elem.name}")
            
            if not hasattr(element, 'packages') and not hasattr(element, 'elements'):
                 lines.append("  (Empty or not a container)")
            
            return "\n".join(lines)
        else:
            return f"Element at {path} is not a package/workspace. It is {type(element).__name__}."

    def get_element_str(self, path: str) -> str:
        """Gets string representation of an element."""
        element = self.get_element(path)
        if element is None:
             return f"Element not found: {path}"
        
        # Simple string representation for now.
        # Ideally we'd dump XML, but Writer writes to file.
        # We can inspect properties.
        return str(vars(element))

    def get_element(self, path: str):
        """Helper to find element by path."""
        if path == "/":
            return self.workspace
        
        # Workspace.find requires package_key if using package_map, 
        # but Workspace also inherits PackageCollection.find(ref)
        # usage: workspace.find('/Pkg/SubPkg/Elem')
        return self.workspace.find(path)
