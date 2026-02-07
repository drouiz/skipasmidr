"""
Base Container MCP Server.

Provides common functionality for container management MCP servers.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any, Dict, List, Optional, Tuple

from libs.mcp.base import BaseMCP


class ContainerMCP(BaseMCP):
    """
    Base class for container MCP servers.

    Provides common container operations:
    - list_containers: List containers
    - container_logs: Get container logs
    - container_stats: Get resource usage
    - container_inspect: Get detailed info
    - restart_container: Restart a container
    - exec_command: Execute command in container
    - list_images: List images
    - list_networks: List networks
    - list_volumes: List volumes

    Subclasses must implement:
    - name: Server name
    - _list_containers(): List containers
    - _get_logs(): Get container logs
    - _get_stats(): Get container stats
    - _inspect(): Inspect container
    - _restart(): Restart container
    - _exec(): Execute command
    - _list_images(): List images
    - _list_networks(): List networks
    - _list_volumes(): List volumes
    """

    def __init__(self):
        super().__init__()

    async def setup(self) -> None:
        """Register container tools."""
        self._register_container_tools()

    def _register_container_tools(self) -> None:
        """Register common container tools."""
        self.register_tool(
            name="list_containers",
            description="List containers",
            handler=self._tool_list_containers,
            properties={
                "all": {"type": "boolean", "description": "Show all containers (default: running only)"},
                "filter": {"type": "string", "description": "Filter by name pattern"},
            },
        )

        self.register_tool(
            name="container_logs",
            description="Get logs from a container",
            handler=self._tool_container_logs,
            properties={
                "container": {"type": "string", "description": "Container name or ID"},
                "tail": {"type": "integer", "description": "Number of lines (default: 100)"},
            },
            required=["container"],
        )

        self.register_tool(
            name="container_stats",
            description="Get resource usage stats for containers",
            handler=self._tool_container_stats,
            properties={
                "container": {"type": "string", "description": "Container name or ID (optional)"},
            },
        )

        self.register_tool(
            name="container_inspect",
            description="Get detailed information about a container",
            handler=self._tool_container_inspect,
            properties={
                "container": {"type": "string", "description": "Container name or ID"},
            },
            required=["container"],
        )

        self.register_tool(
            name="restart_container",
            description="Restart a container",
            handler=self._tool_restart_container,
            properties={
                "container": {"type": "string", "description": "Container name or ID"},
            },
            required=["container"],
        )

        self.register_tool(
            name="exec_command",
            description="Execute a command inside a container",
            handler=self._tool_exec_command,
            properties={
                "container": {"type": "string", "description": "Container name or ID"},
                "command": {"type": "string", "description": "Command to execute"},
            },
            required=["container", "command"],
        )

        self.register_tool(
            name="list_images",
            description="List container images",
            handler=self._tool_list_images,
            properties={},
        )

        self.register_tool(
            name="list_networks",
            description="List networks",
            handler=self._tool_list_networks,
            properties={},
        )

        self.register_tool(
            name="list_volumes",
            description="List volumes",
            handler=self._tool_list_volumes,
            properties={},
        )

    # Tool handlers that call abstract methods
    async def _tool_list_containers(self, all: bool = False, filter: Optional[str] = None) -> Any:
        return await self._list_containers(all, filter)

    async def _tool_container_logs(self, container: str, tail: int = 100) -> Any:
        return await self._get_logs(container, tail)

    async def _tool_container_stats(self, container: Optional[str] = None) -> Any:
        return await self._get_stats(container)

    async def _tool_container_inspect(self, container: str) -> Any:
        return await self._inspect(container)

    async def _tool_restart_container(self, container: str) -> Any:
        return await self._restart(container)

    async def _tool_exec_command(self, container: str, command: str) -> Any:
        return await self._exec(container, command)

    async def _tool_list_images(self) -> Any:
        return await self._list_images()

    async def _tool_list_networks(self) -> Any:
        return await self._list_networks()

    async def _tool_list_volumes(self) -> Any:
        return await self._list_volumes()

    # Abstract methods to implement in subclasses
    @abstractmethod
    async def _list_containers(self, all: bool = False, filter: Optional[str] = None) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def _get_logs(self, container: str, tail: int = 100) -> str:
        pass

    @abstractmethod
    async def _get_stats(self, container: Optional[str] = None) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def _inspect(self, container: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def _restart(self, container: str) -> str:
        pass

    @abstractmethod
    async def _exec(self, container: str, command: str) -> str:
        pass

    @abstractmethod
    async def _list_images(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def _list_networks(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def _list_volumes(self) -> List[Dict[str, Any]]:
        pass
