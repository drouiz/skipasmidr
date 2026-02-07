#!/usr/bin/env python3
"""
MariaDB MCP Server entry point.

Run with: uv run python infra/databases/mariadb/mcp.py
"""

import sys
from pathlib import Path

# Add libs to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from libs.mcp.database import MariaDBMCP

if __name__ == "__main__":
    MariaDBMCP().start()
