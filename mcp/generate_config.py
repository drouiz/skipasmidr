#!/usr/bin/env python3
"""
Generate Claude Desktop MCP configuration for this infrastructure.

Usage:
  python generate_config.py

Outputs claude_desktop_config.json that can be merged with your Claude Desktop config.
"""

import json
import os
import sys
from pathlib import Path

from loguru import logger

# Get paths
SCRIPT_DIR = Path(__file__).parent.resolve()
BASE_DIR = SCRIPT_DIR.parent
CONFIG_DIR = BASE_DIR / "config"


# Load environment
def load_env():
    env = {}
    env_file = CONFIG_DIR / "credentials.env"
    if env_file.exists():
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    # Handle variable references
                    if value.startswith("${") and value.endswith("}"):
                        ref = value[2:-1]
                        value = env.get(ref, value)
                    env[key] = value
    return env


def generate_config():
    env = load_env()

    # Check if MCP is enabled
    mcp_enabled = env.get("MCP_ENABLED", "false").lower() == "true"

    config = {
        "mcpServers": {}
    }

    python_path = sys.executable

    # PostgreSQL MCP Server
    config["mcpServers"]["infra-postgres"] = {
        "command": python_path,
        "args": [str(SCRIPT_DIR / "postgres_server.py")],
        "env": {
            "POSTGRES_HOST": "localhost",
            "POSTGRES_PORT": env.get("EXPOSE_POSTGRES_PORT", "5432").split(":")[-1],
            "POSTGRES_USER": env.get("POSTGRES_USER", "admin"),
            "POSTGRES_PASSWORD": env.get("POSTGRES_PASSWORD", "admin123"),
            "POSTGRES_DB": "postgres"
        }
    }

    # Docker MCP Server
    config["mcpServers"]["infra-docker"] = {
        "command": python_path,
        "args": [str(SCRIPT_DIR / "docker_server.py")]
    }

    # MariaDB MCP Server (if created)
    mariadb_server = SCRIPT_DIR / "mariadb_server.py"
    if mariadb_server.exists():
        config["mcpServers"]["infra-mariadb"] = {
            "command": python_path,
            "args": [str(mariadb_server)],
            "env": {
                "MYSQL_HOST": "localhost",
                "MYSQL_PORT": "3306",
                "MYSQL_USER": env.get("MYSQL_USER", "admin"),
                "MYSQL_PASSWORD": env.get("MYSQL_PASSWORD", "admin123")
            }
        }

    # Redis MCP Server (if created)
    redis_server = SCRIPT_DIR / "redis_server.py"
    if redis_server.exists():
        config["mcpServers"]["infra-redis"] = {
            "command": python_path,
            "args": [str(redis_server)],
            "env": {
                "REDIS_HOST": "localhost",
                "REDIS_PORT": "6379",
                "REDIS_PASSWORD": env.get("REDIS_PASSWORD", "admin123")
            }
        }

    # Output path
    output_file = SCRIPT_DIR / "claude_desktop_config.json"

    with open(output_file, "w") as f:
        json.dump(config, f, indent=2)

    logger.success(f"Generated: {output_file}")
    logger.info("To use with Claude Desktop:")
    logger.info("  1. Open Claude Desktop settings")
    logger.info("  2. Go to Developer > Edit Config")
    logger.info("  3. Merge the contents of claude_desktop_config.json")
    logger.info("Or manually add to your config file at:")
    logger.info("  Windows: %APPDATA%\\Claude\\claude_desktop_config.json")
    logger.info("  macOS: ~/Library/Application Support/Claude/claude_desktop_config.json")

    if not mcp_enabled:
        logger.warning("MCP is currently disabled in credentials.env")
        logger.info("Set MCP_ENABLED=true to enable MCP servers")

    return config


if __name__ == "__main__":
    config = generate_config()
    logger.info("Generated config:")
    logger.debug(json.dumps(config, indent=2))
