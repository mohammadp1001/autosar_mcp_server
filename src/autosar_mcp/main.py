from autosar_mcp.server import mcp
from autosar_mcp.logging_conf import setup_logging

from autosar_mcp.config import load_settings
from autosar_mcp.logging_conf import setup_logging, get_logger

settings = load_settings()
setup_logging(settings)
logger = get_logger(__name__)

def main():
    setup_logging(settings)
    mcp.run()

if __name__ == "__main__":
    main()
