"""
Docker MCP Server.
"""

from __future__ import annotations

import asyncio
import json
import subprocess
from typing import Any, Dict, List, Optional, Tuple

from loguru import logger

from libs.mcp.container.base import ContainerMCP


class DockerMCP(ContainerMCP):
    """
    Docker MCP server.

    Provides Docker container management via CLI.
    No additional dependencies required (uses docker CLI).
    """

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        super().__init__()

    @property
    def name(self) -> str:
        return "docker-mcp"

    async def setup(self) -> None:
        """Verify Docker is available and register tools."""
        # Check Docker is available
        ok, output = await self._run_docker(["version", "--format", "json"])
        if not ok:
            raise RuntimeError(f"Docker not available: {output}")

        version_info = json.loads(output)
        logger.info(f"Docker version: {version_info.get('Client', {}).get('Version', 'unknown')}")

        # Register tools from parent
        await super().setup()

        # Register additional Docker-specific tools
        self._register_docker_tools()

    def _register_docker_tools(self) -> None:
        """Register Docker-specific tools."""
        self.register_tool(
            name="compose_ps",
            description="List containers from a compose project",
            handler=self._tool_compose_ps,
            properties={
                "project": {"type": "string", "description": "Compose project name"},
            },
            required=["project"],
        )

        self.register_tool(
            name="compose_logs",
            description="Get logs from a compose project",
            handler=self._tool_compose_logs,
            properties={
                "project": {"type": "string", "description": "Compose project name"},
                "service": {"type": "string", "description": "Service name (optional)"},
                "tail": {"type": "integer", "description": "Number of lines (default: 100)"},
            },
            required=["project"],
        )

    async def _run_docker(self, args: List[str]) -> Tuple[bool, str]:
        """Run a docker command."""
        try:
            proc = await asyncio.create_subprocess_exec(
                "docker",
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=self.timeout,
            )

            if proc.returncode == 0:
                return True, stdout.decode()
            else:
                return False, stderr.decode()
        except asyncio.TimeoutError:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)

    def _parse_json_lines(self, output: str) -> List[Dict[str, Any]]:
        """Parse JSON lines output from Docker."""
        result = []
        for line in output.strip().split("\n"):
            if line:
                try:
                    result.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        return result

    # Implement abstract methods
    async def _list_containers(self, all: bool = False, filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """List Docker containers."""
        args = ["ps", "--format", "json"]
        if all:
            args.insert(1, "-a")

        ok, output = await self._run_docker(args)
        if not ok:
            raise RuntimeError(output)

        containers = self._parse_json_lines(output)

        if filter:
            filter_lower = filter.lower()
            containers = [c for c in containers if filter_lower in c.get("Names", "").lower()]

        return containers

    async def _get_logs(self, container: str, tail: int = 100) -> str:
        """Get container logs."""
        ok, output = await self._run_docker(["logs", "--tail", str(tail), container])
        if not ok:
            raise RuntimeError(output)
        return output

    async def _get_stats(self, container: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get container stats."""
        args = ["stats", "--no-stream", "--format", "json"]
        if container:
            args.append(container)

        ok, output = await self._run_docker(args)
        if not ok:
            raise RuntimeError(output)

        return self._parse_json_lines(output)

    async def _inspect(self, container: str) -> Dict[str, Any]:
        """Inspect a container."""
        ok, output = await self._run_docker(["inspect", container])
        if not ok:
            raise RuntimeError(output)
        return json.loads(output)

    async def _restart(self, container: str) -> str:
        """Restart a container."""
        ok, output = await self._run_docker(["restart", container])
        if not ok:
            raise RuntimeError(output)
        return f"Restarted: {container}"

    async def _exec(self, container: str, command: str) -> str:
        """Execute command in container."""
        ok, output = await self._run_docker(["exec", container, "sh", "-c", command])
        if not ok:
            raise RuntimeError(output)
        return output

    async def _list_images(self) -> List[Dict[str, Any]]:
        """List Docker images."""
        ok, output = await self._run_docker(["images", "--format", "json"])
        if not ok:
            raise RuntimeError(output)
        return self._parse_json_lines(output)

    async def _list_networks(self) -> List[Dict[str, Any]]:
        """List Docker networks."""
        ok, output = await self._run_docker(["network", "ls", "--format", "json"])
        if not ok:
            raise RuntimeError(output)
        return self._parse_json_lines(output)

    async def _list_volumes(self) -> List[Dict[str, Any]]:
        """List Docker volumes."""
        ok, output = await self._run_docker(["volume", "ls", "--format", "json"])
        if not ok:
            raise RuntimeError(output)
        return self._parse_json_lines(output)

    # Docker Compose specific tools
    async def _tool_compose_ps(self, project: str) -> List[Dict[str, Any]]:
        """List containers from a compose project."""
        ok, output = await self._run_docker([
            "compose", "-p", project, "ps", "--format", "json"
        ])
        if not ok:
            raise RuntimeError(output)
        return self._parse_json_lines(output)

    async def _tool_compose_logs(
        self,
        project: str,
        service: Optional[str] = None,
        tail: int = 100,
    ) -> str:
        """Get logs from a compose project."""
        args = ["compose", "-p", project, "logs", "--tail", str(tail)]
        if service:
            args.append(service)

        ok, output = await self._run_docker(args)
        if not ok:
            raise RuntimeError(output)
        return output


# Entry point for running directly
if __name__ == "__main__":
    DockerMCP().start()
