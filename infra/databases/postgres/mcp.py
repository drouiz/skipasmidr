#!/usr/bin/env python3
"""
PostgreSQL MCP Server entry point.

Run with: uv run python infra/databases/postgres/mcp.py
"""

import sys
from pathlib import Path

# Add libs to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from libs.mcp.database import PostgresMCP

if __name__ == "__main__":
    PostgresMCP().start()
