from .server import mcp
from .logging_conf import setup_logging

def main():
    setup_logging()
    # FastMCP.run() automatically handles stdio transport
    mcp.run()

if __name__ == "__main__":
    main()
