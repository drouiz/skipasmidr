"""
Base HTTP/Reverse Proxy MCP Server.

Provides common functionality for HTTP service MCP servers.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any, Dict, List, Optional

from libs.mcp.base import BaseMCP


class HttpMCP(BaseMCP):
    """
    Base class for HTTP/reverse proxy MCP servers.

    Provides common HTTP operations:
    - list_routers: List HTTP routers/routes
    - list_services: List backend services
    - list_middlewares: List middlewares
    - get_router: Get router details
    - get_service: Get service details
    - health_check: Check service health

    Subclasses must implement the abstract methods.
    """

    def __init__(
        self,
        api_url: str = "http://localhost:8080",
        api_user: Optional[str] = None,
        api_password: Optional[str] = None,
    ):
        self.api_url = api_url.rstrip("/")
        self.api_user = api_user
        self.api_password = api_password
        super().__init__()

    async def setup(self) -> None:
        """Register HTTP tools."""
        self._register_http_tools()

    def _register_http_tools(self) -> None:
        """Register common HTTP proxy tools."""
        self.register_tool(
            name="list_routers",
            description="List all HTTP routers/routes",
            handler=self._tool_list_routers,
            properties={
                "provider": {"type": "string", "description": "Filter by provider (optional)"},
            },
        )

        self.register_tool(
            name="list_services",
            description="List all backend services",
            handler=self._tool_list_services,
            properties={
                "provider": {"type": "string", "description": "Filter by provider (optional)"},
            },
        )

        self.register_tool(
            name="list_middlewares",
            description="List all middlewares",
            handler=self._tool_list_middlewares,
            properties={},
        )

        self.register_tool(
            name="get_router",
            description="Get router details",
            handler=self._tool_get_router,
            properties={
                "name": {"type": "string", "description": "Router name"},
            },
            required=["name"],
        )

        self.register_tool(
            name="get_service",
            description="Get service details",
            handler=self._tool_get_service,
            properties={
                "name": {"type": "string", "description": "Service name"},
            },
            required=["name"],
        )

        self.register_tool(
            name="health_check",
            description="Check health of all services",
            handler=self._tool_health_check,
            properties={},
        )

    # Tool handlers
    async def _tool_list_routers(self, provider: Optional[str] = None) -> Any:
        return await self._list_routers(provider)

    async def _tool_list_services(self, provider: Optional[str] = None) -> Any:
        return await self._list_services(provider)

    async def _tool_list_middlewares(self) -> Any:
        return await self._list_middlewares()

    async def _tool_get_router(self, name: str) -> Any:
        return await self._get_router(name)

    async def _tool_get_service(self, name: str) -> Any:
        return await self._get_service(name)

    async def _tool_health_check(self) -> Any:
        return await self._health_check()

    # Abstract methods
    @abstractmethod
    async def _list_routers(self, provider: Optional[str] = None) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def _list_services(self, provider: Optional[str] = None) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def _list_middlewares(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def _get_router(self, name: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def _get_service(self, name: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def _health_check(self) -> Dict[str, Any]:
        pass
