"""
Base MCP Server class.

Provides core functionality for all MCP servers.
"""

from __future__ import annotations

import asyncio
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Awaitable, Dict, List, Optional

from loguru import logger

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    logger.error("MCP package not installed. Install with: uv add mcp")
    raise


@dataclass
class MCPTool:
    """Definition of an MCP tool."""

    name: str
    description: str
    handler: Callable[..., Awaitable[Any]]
    input_schema: Dict[str, Any] = field(default_factory=lambda: {"type": "object", "properties": {}})
    required: List[str] = field(default_factory=list)


class BaseMCP(ABC):
    """
    Base class for all MCP servers.

    Provides:
    - Tool registration and management
    - Server lifecycle (start, stop)
    - Common utilities (JSON responses, error handling)

    Subclasses should:
    - Override `name` property
    - Call `register_tool()` to add tools
    - Optionally override `setup()` for initialization
    """

    def __init__(self):
        self._tools: Dict[str, MCPTool] = {}
        self._server = Server(self.name)
        self._setup_handlers()

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name for this MCP server."""
        pass

    def _setup_handlers(self):
        """Setup MCP server handlers."""

        @self._server.list_tools()
        async def list_tools():
            return [
                Tool(
                    name=tool.name,
                    description=tool.description,
                    inputSchema={
                        "type": "object",
                        "properties": tool.input_schema.get("properties", {}),
                        "required": tool.required,
                    },
                )
                for tool in self._tools.values()
            ]

        @self._server.call_tool()
        async def call_tool(name: str, arguments: dict) -> List[TextContent]:
            return await self._handle_tool_call(name, arguments)

    def register_tool(
        self,
        name: str,
        description: str,
        handler: Callable[..., Awaitable[Any]],
        properties: Optional[Dict[str, Any]] = None,
        required: Optional[List[str]] = None,
    ) -> None:
        """
        Register a tool with this MCP server.

        Args:
            name: Tool name (unique identifier)
            description: Human-readable description
            handler: Async function to handle tool calls
            properties: JSON Schema properties for input
            required: List of required parameter names
        """
        self._tools[name] = MCPTool(
            name=name,
            description=description,
            handler=handler,
            input_schema={"type": "object", "properties": properties or {}},
            required=required or [],
        )
        logger.debug(f"Registered tool: {name}")

    async def _handle_tool_call(self, name: str, arguments: dict) -> List[TextContent]:
        """Handle a tool call."""
        if name not in self._tools:
            return [self.error_response(f"Unknown tool: {name}")]

        tool = self._tools[name]
        try:
            result = await tool.handler(**arguments)
            return [self.text_response(result)]
        except Exception as e:
            logger.exception(f"Tool {name} failed")
            return [self.error_response(str(e))]

    @staticmethod
    def text_response(data: Any) -> TextContent:
        """Create a text response from data."""
        if isinstance(data, (dict, list)):
            text = json.dumps(data, indent=2, default=str)
        else:
            text = str(data)
        return TextContent(type="text", text=text)

    @staticmethod
    def error_response(message: str) -> TextContent:
        """Create an error response."""
        return TextContent(type="text", text=f"Error: {message}")

    async def setup(self) -> None:
        """
        Initialize the MCP server.

        Override in subclasses to:
        - Establish connections
        - Register tools
        - Load configuration
        """
        pass

    async def cleanup(self) -> None:
        """
        Cleanup resources.

        Override in subclasses to:
        - Close connections
        - Release resources
        """
        pass

    async def run(self) -> None:
        """Run the MCP server."""
        logger.info(f"Starting MCP server: {self.name}")
        try:
            await self.setup()
            async with stdio_server() as (read_stream, write_stream):
                await self._server.run(
                    read_stream,
                    write_stream,
                    self._server.create_initialization_options(),
                )
        finally:
            await self.cleanup()
            logger.info(f"MCP server stopped: {self.name}")

    def start(self) -> None:
        """Start the MCP server (blocking)."""
        asyncio.run(self.run())
