#!/usr/bin/env python3
"""
MongoDB MCP Server entry point.

Run with: uv run python infra/databases/mongo/mcp.py
"""

import sys
from pathlib import Path

# Add libs to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from libs.mcp.database import MongoMCP

if __name__ == "__main__":
    MongoMCP().start()
