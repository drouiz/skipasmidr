#!/usr/bin/env python3
"""
Docker MCP Server
Exposes Docker management capabilities to Claude via MCP.

Usage:
  python docker_server.py
"""

import os
import json
import asyncio
import subprocess
import sys
from typing import Any

from loguru import logger

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    logger.error("MCP package not installed. Run: uv add mcp")
    sys.exit(1)


# Create MCP server
server = Server("docker-infra")


def run_docker_command(args: list) -> tuple[bool, str]:
    """Run a docker command and return output."""
    try:
        result = subprocess.run(
            ["docker"] + args,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr
    except Exception as e:
        return False, str(e)


@server.list_tools()
async def list_tools():
    """List available tools."""
    return [
        Tool(
            name="list_containers",
            description="List Docker containers",
            inputSchema={
                "type": "object",
                "properties": {
                    "all": {
                        "type": "boolean",
                        "description": "Show all containers (default shows only running)"
                    },
                    "filter": {
                        "type": "string",
                        "description": "Filter by name pattern"
                    }
                }
            }
        ),
        Tool(
            name="container_logs",
            description="Get logs from a container",
            inputSchema={
                "type": "object",
                "properties": {
                    "container": {
                        "type": "string",
                        "description": "Container name or ID"
                    },
                    "tail": {
                        "type": "integer",
                        "description": "Number of lines to show (default: 100)"
                    }
                },
                "required": ["container"]
            }
        ),
        Tool(
            name="container_stats",
            description="Get resource usage stats for containers",
            inputSchema={
                "type": "object",
                "properties": {
                    "container": {
                        "type": "string",
                        "description": "Container name or ID (optional, shows all if not specified)"
                    }
                }
            }
        ),
        Tool(
            name="container_inspect",
            description="Get detailed information about a container",
            inputSchema={
                "type": "object",
                "properties": {
                    "container": {
                        "type": "string",
                        "description": "Container name or ID"
                    }
                },
                "required": ["container"]
            }
        ),
        Tool(
            name="list_images",
            description="List Docker images",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="list_networks",
            description="List Docker networks",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="list_volumes",
            description="List Docker volumes",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="restart_container",
            description="Restart a container",
            inputSchema={
                "type": "object",
                "properties": {
                    "container": {
                        "type": "string",
                        "description": "Container name or ID"
                    }
                },
                "required": ["container"]
            }
        ),
        Tool(
            name="exec_command",
            description="Execute a command inside a container",
            inputSchema={
                "type": "object",
                "properties": {
                    "container": {
                        "type": "string",
                        "description": "Container name or ID"
                    },
                    "command": {
                        "type": "string",
                        "description": "Command to execute"
                    }
                },
                "required": ["container", "command"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute a tool."""
    try:
        if name == "list_containers":
            args = ["ps", "--format", "json"]
            if arguments.get("all", False):
                args.insert(1, "-a")

            ok, output = run_docker_command(args)
            if ok:
                # Parse JSON lines
                containers = []
                for line in output.strip().split("\n"):
                    if line:
                        containers.append(json.loads(line))

                filter_pattern = arguments.get("filter", "")
                if filter_pattern:
                    containers = [c for c in containers if filter_pattern.lower() in c.get("Names", "").lower()]

                return [TextContent(type="text", text=json.dumps(containers, indent=2))]
            else:
                return [TextContent(type="text", text=f"Error: {output}")]

        elif name == "container_logs":
            container = arguments.get("container", "")
            tail = arguments.get("tail", 100)
            ok, output = run_docker_command(["logs", "--tail", str(tail), container])
            return [TextContent(type="text", text=output if ok else f"Error: {output}")]

        elif name == "container_stats":
            container = arguments.get("container", "")
            args = ["stats", "--no-stream", "--format", "json"]
            if container:
                args.append(container)

            ok, output = run_docker_command(args)
            if ok:
                stats = []
                for line in output.strip().split("\n"):
                    if line:
                        stats.append(json.loads(line))
                return [TextContent(type="text", text=json.dumps(stats, indent=2))]
            else:
                return [TextContent(type="text", text=f"Error: {output}")]

        elif name == "container_inspect":
            container = arguments.get("container", "")
            ok, output = run_docker_command(["inspect", container])
            return [TextContent(type="text", text=output if ok else f"Error: {output}")]

        elif name == "list_images":
            ok, output = run_docker_command(["images", "--format", "json"])
            if ok:
                images = []
                for line in output.strip().split("\n"):
                    if line:
                        images.append(json.loads(line))
                return [TextContent(type="text", text=json.dumps(images, indent=2))]
            else:
                return [TextContent(type="text", text=f"Error: {output}")]

        elif name == "list_networks":
            ok, output = run_docker_command(["network", "ls", "--format", "json"])
            if ok:
                networks = []
                for line in output.strip().split("\n"):
                    if line:
                        networks.append(json.loads(line))
                return [TextContent(type="text", text=json.dumps(networks, indent=2))]
            else:
                return [TextContent(type="text", text=f"Error: {output}")]

        elif name == "list_volumes":
            ok, output = run_docker_command(["volume", "ls", "--format", "json"])
            if ok:
                volumes = []
                for line in output.strip().split("\n"):
                    if line:
                        volumes.append(json.loads(line))
                return [TextContent(type="text", text=json.dumps(volumes, indent=2))]
            else:
                return [TextContent(type="text", text=f"Error: {output}")]

        elif name == "restart_container":
            container = arguments.get("container", "")
            ok, output = run_docker_command(["restart", container])
            return [TextContent(type="text", text=f"Restarted {container}" if ok else f"Error: {output}")]

        elif name == "exec_command":
            container = arguments.get("container", "")
            command = arguments.get("command", "")
            ok, output = run_docker_command(["exec", container, "sh", "-c", command])
            return [TextContent(type="text", text=output if ok else f"Error: {output}")]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
