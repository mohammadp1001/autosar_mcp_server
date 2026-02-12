import logging
import os
import sys

# Add project root to path to access src
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(root_dir)

# Add local autosar library to path
sys.path.append(os.path.join(root_dir, "autosar_cogu_analysis", "src"))

import autosar.xml.element as ar_element
from src.workspace_manager import WorkspaceManager

# Setup logging
logging.basicConfig(level=logging.INFO)

def verify():
    print("--- Starting Verification ---")
    
    # 1. Initialize Manager
    manager = WorkspaceManager()
    
    # 2. Load ARXML
    test_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "data", "test.arxml"))
    
    if not os.path.exists(test_file):
        print(f"ERROR: Test file not found at {test_file}")
        return

    print(f"Loading {test_file}...")
    try:
        manager.load_files([test_file])
        print("Load successful.")
    except Exception as e:
        print(f"ERROR loading file: {e}")
        return

    # 3. List Content
    print("\n--- Listing Content of /MyPackages ---")
    print(manager.list_content("/MyPackages"))

    # 4. Simulate Tools (Modification)
    print("\n--- Simulating Modifications ---")
    try:
        # Create Package
        root = manager.get_element("/")
        pkg = root.create_package("NewPackage")
        print(f"Created package: {pkg.name}")

        # Create Interface in NewPackage
        interface = ar_element.SenderReceiverInterface("MyInterface")
        pkg.append(interface)
        print(f"Created interface: {interface.name}")

        # Create Component
        comp = ar_element.ApplicationSoftwareComponentType("MyComponent")
        pkg.append(comp)
        print(f"Created component: {comp.name}")
        
        # Create Port
        comp.create_p_port("MyPort", interface)
        print(f"Created port: MyPort")

    except Exception as e:
        print(f"ERROR during modification: {e}")
        import traceback
        traceback.print_exc()

    # 5. Save
    print("\n--- Saving Workspace ---")
    output_dir = os.path.abspath("output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    try:
        manager.save(output_dir, version=50) # R21-11
        print(f"Saved to {output_dir}")
    except Exception as e:
        print(f"ERROR saving: {e}")
        import traceback
        traceback.print_exc()

    # 6. Verify Output Exists
    expected_file = os.path.join(output_dir, "MyPackages.arxml") # Config mapping might affect this
    # Default behavior of write_documents without config might be tricky.
    # checking what files were created
    print("Files in output directory:")
    for f in os.listdir(output_dir):
        print(f" - {f}")

if __name__ == "__main__":
    verify()
