"""
PostgreSQL MCP Server.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from loguru import logger

try:
    import asyncpg
except ImportError:
    asyncpg = None

from libs.mcp.database.base import DatabaseMCP


class PostgresMCP(DatabaseMCP):
    """
    PostgreSQL MCP server.

    Environment variables:
        POSTGRES_HOST: Database host (default: localhost)
        POSTGRES_PORT: Database port (default: 5432)
        POSTGRES_USER: Database user (default: admin)
        POSTGRES_PASSWORD: Database password
        POSTGRES_DB: Default database (default: postgres)
    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
    ):
        super().__init__(
            host=host or os.getenv("POSTGRES_HOST", "localhost"),
            port=port or int(os.getenv("POSTGRES_PORT", "5432")),
            user=user or os.getenv("POSTGRES_USER", "admin"),
            password=password or os.getenv("POSTGRES_PASSWORD", ""),
            database=database or os.getenv("POSTGRES_DB", "postgres"),
        )
        self._pool: Optional[asyncpg.Pool] = None

    @property
    def name(self) -> str:
        return "postgres-mcp"

    async def connect(self) -> None:
        """Create connection pool."""
        if asyncpg is None:
            raise ImportError("asyncpg not installed. Run: uv add asyncpg")

        logger.info(f"Connecting to PostgreSQL: {self.host}:{self.port}/{self.database}")
        self._pool = await asyncpg.create_pool(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            min_size=1,
            max_size=5,
        )
        logger.success("PostgreSQL connected")

    async def disconnect(self) -> None:
        """Close connection pool."""
        if self._pool:
            await self._pool.close()
            logger.info("PostgreSQL disconnected")

    async def _execute_query(self, sql: str, database: Optional[str] = None) -> List[Dict[str, Any]]:
        """Execute a SELECT query."""
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(sql)
            return [dict(row) for row in rows]

    async def _execute_statement(self, sql: str, database: Optional[str] = None) -> str:
        """Execute a non-SELECT statement."""
        async with self._pool.acquire() as conn:
            result = await conn.execute(sql)
            return f"Executed: {result}"

    async def _get_databases(self) -> List[str]:
        """List all databases."""
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT datname FROM pg_database WHERE datistemplate = false ORDER BY datname"
            )
            return [row["datname"] for row in rows]

    async def _get_tables(self, database: Optional[str] = None, schema: Optional[str] = None) -> List[Dict[str, Any]]:
        """List tables in a database."""
        schema = schema or "public"
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT table_name, table_type
                FROM information_schema.tables
                WHERE table_schema = $1
                ORDER BY table_name
                """,
                schema,
            )
            return [{"name": row["table_name"], "type": row["table_type"]} for row in rows]

    async def _get_table_schema(self, table: str, database: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get table schema."""
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = $1
                ORDER BY ordinal_position
                """,
                table,
            )
            return [
                {
                    "column": row["column_name"],
                    "type": row["data_type"],
                    "nullable": row["is_nullable"],
                    "default": row["column_default"],
                }
                for row in rows
            ]


# Entry point for running directly
if __name__ == "__main__":
    PostgresMCP().start()
