#!/usr/bin/env python3
"""
Traefik MCP Server entry point.

Run with: uv run python core/traefik/mcp.py
"""

import sys
from pathlib import Path

# Add libs to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from libs.mcp.http import TraefikMCP

if __name__ == "__main__":
    TraefikMCP().start()
