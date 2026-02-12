
import os
import sys

# Ensure local autosar library is found
# This is a hack for the local development environment
# In a real package, autosar would be a dependency installed in site-packages
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
lib_path = os.path.join(project_root, "autosar_cogu_analysis", "src")
if os.path.exists(lib_path) and lib_path not in sys.path:
    sys.path.insert(0, lib_path)
