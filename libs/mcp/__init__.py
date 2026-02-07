"""
MCP (Model Context Protocol) server framework.

Provides base classes for creating MCP servers:
- BaseMCP: Core MCP functionality
- DatabaseMCP: Database-specific operations (postgres, mariadb, mongo)
- ContainerMCP: Container management (docker)
- HttpMCP: HTTP/reverse proxy operations (traefik)

Usage:
    from libs.mcp import MCPBuilder

    # Create from type
    mcp = MCPBuilder.create("postgres", host="localhost")
    mcp.start()

    # Create from YAML config
    mcp = MCPBuilder.from_yaml("config/mcp/postgres.mcp.yaml")
    mcp.start()
"""

from libs.mcp.base import BaseMCP
from libs.mcp.builder import MCPBuilder

__all__ = ["BaseMCP", "MCPBuilder"]
