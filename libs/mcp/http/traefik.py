"""
Traefik MCP Server.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from loguru import logger

try:
    import httpx
except ImportError:
    httpx = None

from libs.mcp.http.base import HttpMCP


class TraefikMCP(HttpMCP):
    """
    Traefik MCP server.

    Provides Traefik reverse proxy management via API.

    Environment variables:
        TRAEFIK_API_URL: Traefik API URL (default: http://localhost:8080)
        TRAEFIK_API_USER: API username (optional)
        TRAEFIK_API_PASSWORD: API password (optional)
    """

    def __init__(
        self,
        api_url: Optional[str] = None,
        api_user: Optional[str] = None,
        api_password: Optional[str] = None,
    ):
        super().__init__(
            api_url=api_url or os.getenv("TRAEFIK_API_URL", "http://localhost:8080"),
            api_user=api_user or os.getenv("TRAEFIK_API_USER"),
            api_password=api_password or os.getenv("TRAEFIK_API_PASSWORD"),
        )
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def name(self) -> str:
        return "traefik-mcp"

    async def setup(self) -> None:
        """Initialize HTTP client and register tools."""
        if httpx is None:
            raise ImportError("httpx not installed. Run: uv add httpx")

        # Create HTTP client
        auth = None
        if self.api_user and self.api_password:
            auth = httpx.BasicAuth(self.api_user, self.api_password)

        self._client = httpx.AsyncClient(
            base_url=self.api_url,
            auth=auth,
            timeout=10.0,
        )

        # Test connection
        try:
            response = await self._client.get("/api/version")
            response.raise_for_status()
            version = response.json()
            logger.info(f"Traefik version: {version.get('Version', 'unknown')}")
        except Exception as e:
            logger.warning(f"Could not connect to Traefik API: {e}")

        # Register tools from parent
        await super().setup()

        # Register Traefik-specific tools
        self._register_traefik_tools()

    async def cleanup(self) -> None:
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            logger.info("Traefik client closed")

    def _register_traefik_tools(self) -> None:
        """Register Traefik-specific tools."""
        self.register_tool(
            name="get_version",
            description="Get Traefik version info",
            handler=self._tool_get_version,
            properties={},
        )

        self.register_tool(
            name="list_entrypoints",
            description="List Traefik entrypoints",
            handler=self._tool_list_entrypoints,
            properties={},
        )

        self.register_tool(
            name="get_overview",
            description="Get Traefik dashboard overview",
            handler=self._tool_get_overview,
            properties={},
        )

    async def _api_get(self, path: str) -> Any:
        """Make GET request to Traefik API."""
        response = await self._client.get(path)
        response.raise_for_status()
        return response.json()

    # Implement abstract methods
    async def _list_routers(self, provider: Optional[str] = None) -> List[Dict[str, Any]]:
        """List HTTP routers."""
        routers = await self._api_get("/api/http/routers")

        if provider:
            routers = [r for r in routers if r.get("provider") == provider]

        # Simplify output
        return [
            {
                "name": r.get("name"),
                "rule": r.get("rule"),
                "service": r.get("service"),
                "entryPoints": r.get("entryPoints", []),
                "status": r.get("status"),
            }
            for r in routers
        ]

    async def _list_services(self, provider: Optional[str] = None) -> List[Dict[str, Any]]:
        """List backend services."""
        services = await self._api_get("/api/http/services")

        if provider:
            services = [s for s in services if s.get("provider") == provider]

        # Simplify output
        return [
            {
                "name": s.get("name"),
                "type": s.get("type"),
                "status": s.get("status"),
                "serverStatus": s.get("serverStatus", {}),
            }
            for s in services
        ]

    async def _list_middlewares(self) -> List[Dict[str, Any]]:
        """List middlewares."""
        middlewares = await self._api_get("/api/http/middlewares")
        return [
            {
                "name": m.get("name"),
                "type": m.get("type"),
                "status": m.get("status"),
            }
            for m in middlewares
        ]

    async def _get_router(self, name: str) -> Dict[str, Any]:
        """Get router details."""
        return await self._api_get(f"/api/http/routers/{name}")

    async def _get_service(self, name: str) -> Dict[str, Any]:
        """Get service details."""
        return await self._api_get(f"/api/http/services/{name}")

    async def _health_check(self) -> Dict[str, Any]:
        """Check health of all services."""
        services = await self._api_get("/api/http/services")

        healthy = 0
        unhealthy = 0
        unknown = 0
        details = []

        for svc in services:
            status = svc.get("serverStatus", {})
            svc_name = svc.get("name")

            for server, server_status in status.items():
                if server_status == "UP":
                    healthy += 1
                elif server_status == "DOWN":
                    unhealthy += 1
                    details.append({"service": svc_name, "server": server, "status": "DOWN"})
                else:
                    unknown += 1

        return {
            "healthy": healthy,
            "unhealthy": unhealthy,
            "unknown": unknown,
            "unhealthy_details": details,
        }

    # Traefik-specific tools
    async def _tool_get_version(self) -> Dict[str, Any]:
        """Get Traefik version."""
        return await self._api_get("/api/version")

    async def _tool_list_entrypoints(self) -> List[Dict[str, Any]]:
        """List entrypoints."""
        return await self._api_get("/api/entrypoints")

    async def _tool_get_overview(self) -> Dict[str, Any]:
        """Get dashboard overview."""
        return await self._api_get("/api/overview")


# Entry point for running directly
if __name__ == "__main__":
    TraefikMCP().start()
