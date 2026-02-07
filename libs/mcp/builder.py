"""
MCP Builder - Create MCP servers from YAML configuration.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Type, Union

import yaml
from loguru import logger

from libs.mcp.base import BaseMCP
from libs.mcp.database import PostgresMCP, MariaDBMCP, MongoMCP
from libs.mcp.container import DockerMCP
from libs.mcp.http import TraefikMCP


# Registry of available MCP types
MCP_REGISTRY: Dict[str, Type[BaseMCP]] = {
    # Databases
    "postgres": PostgresMCP,
    "postgresql": PostgresMCP,
    "mariadb": MariaDBMCP,
    "mysql": MariaDBMCP,
    "mongo": MongoMCP,
    "mongodb": MongoMCP,
    # Containers
    "docker": DockerMCP,
    # HTTP
    "traefik": TraefikMCP,
}


class MCPBuilder:
    """
    Build MCP servers from YAML configuration.

    Usage:
        # From config file
        mcp = MCPBuilder.from_yaml("config/mcp/postgres.yaml")
        mcp.start()

        # From type and env
        mcp = MCPBuilder.create("postgres")
        mcp.start()
    """

    @staticmethod
    def create(mcp_type: str, **kwargs) -> BaseMCP:
        """
        Create an MCP server by type.

        Args:
            mcp_type: Type of MCP (postgres, docker, traefik, etc.)
            **kwargs: Arguments to pass to the MCP constructor

        Returns:
            Configured MCP server instance
        """
        mcp_type_lower = mcp_type.lower()
        if mcp_type_lower not in MCP_REGISTRY:
            raise ValueError(
                f"Unknown MCP type: {mcp_type}. "
                f"Available: {', '.join(MCP_REGISTRY.keys())}"
            )

        mcp_class = MCP_REGISTRY[mcp_type_lower]
        logger.info(f"Creating MCP: {mcp_type} ({mcp_class.__name__})")

        return mcp_class(**kwargs)

    @staticmethod
    def from_yaml(config_path: Union[Path, str]) -> BaseMCP:
        """
        Create an MCP server from a YAML config file.

        YAML format:
        ```yaml
        type: postgres
        config:
          host: localhost
          port: 5432
          user: admin
          password: ${POSTGRES_PASSWORD}
          database: postgres
        ```

        Environment variables can be referenced with ${VAR_NAME}.
        """
        config_path = Path(config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"Config not found: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        mcp_type = config.get("type")
        if not mcp_type:
            raise ValueError(f"Missing 'type' in config: {config_path}")

        # Resolve environment variables in config
        mcp_config = config.get("config", {})
        resolved_config = MCPBuilder._resolve_env_vars(mcp_config)

        logger.debug(f"Loaded config from: {config_path}")
        return MCPBuilder.create(mcp_type, **resolved_config)

    @staticmethod
    def from_env(mcp_type: str, prefix: str = "") -> BaseMCP:
        """
        Create an MCP server using environment variables.

        Args:
            mcp_type: Type of MCP
            prefix: Environment variable prefix (e.g., "POSTGRES_")

        The MCP will use its default environment variable names,
        optionally with a custom prefix.
        """
        return MCPBuilder.create(mcp_type)

    @staticmethod
    def _resolve_env_vars(config: dict) -> dict:
        """Resolve ${VAR_NAME} references in config values."""
        resolved = {}
        for key, value in config.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                var_name = value[2:-1]
                resolved[key] = os.getenv(var_name, "")
            elif isinstance(value, dict):
                resolved[key] = MCPBuilder._resolve_env_vars(value)
            else:
                resolved[key] = value
        return resolved

    @staticmethod
    def list_types() -> List[str]:
        """List available MCP types."""
        return sorted(set(MCP_REGISTRY.keys()))

    @staticmethod
    def get_class(mcp_type: str) -> Type[BaseMCP]:
        """Get the class for an MCP type."""
        mcp_type_lower = mcp_type.lower()
        if mcp_type_lower not in MCP_REGISTRY:
            raise ValueError(f"Unknown MCP type: {mcp_type}")
        return MCP_REGISTRY[mcp_type_lower]

    @staticmethod
    def register(name: str, mcp_class: Type[BaseMCP]) -> None:
        """Register a custom MCP type."""
        MCP_REGISTRY[name.lower()] = mcp_class
        logger.debug(f"Registered MCP type: {name}")


def discover_mcp_configs(config_dir: Path) -> List[Path]:
    """
    Discover MCP configuration files in a directory.

    Looks for:
    - *.mcp.yaml files
    - mcp.yaml files

    Args:
        config_dir: Directory to search

    Returns:
        List of config file paths
    """
    configs = []

    if not config_dir.exists():
        return configs

    # Look for mcp.yaml files
    for mcp_file in config_dir.glob("**/mcp.yaml"):
        configs.append(mcp_file)

    # Look for *.mcp.yaml files
    for mcp_file in config_dir.glob("**/*.mcp.yaml"):
        configs.append(mcp_file)

    return configs


def load_mcp_config(base_dir: Path) -> dict:
    """
    Load the main MCP configuration.

    Reads config/mcp/mcp.yaml for global settings.
    """
    config_file = base_dir / "config" / "mcp" / "mcp.yaml"
    if not config_file.exists():
        return {
            "enabled": False,
            "core_mcps": ["docker", "traefik"],
            "services": {},
        }

    with open(config_file, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}
