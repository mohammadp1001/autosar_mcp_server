from __future__ import annotations
from autosar_mcp.server import create_app

def main() -> None:
   

    app = create_app()
    app.run()


if __name__ == "__main__":
    main()
