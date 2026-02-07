"""
MariaDB/MySQL MCP Server.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from loguru import logger

try:
    import aiomysql
except ImportError:
    aiomysql = None

from libs.mcp.database.base import DatabaseMCP


class MariaDBMCP(DatabaseMCP):
    """
    MariaDB/MySQL MCP server.

    Environment variables:
        MYSQL_HOST: Database host (default: localhost)
        MYSQL_PORT: Database port (default: 3306)
        MYSQL_USER: Database user (default: admin)
        MYSQL_PASSWORD: Database password
        MYSQL_DB: Default database (optional)
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
            host=host or os.getenv("MYSQL_HOST", "localhost"),
            port=port or int(os.getenv("MYSQL_PORT", "3306")),
            user=user or os.getenv("MYSQL_USER", "admin"),
            password=password or os.getenv("MYSQL_PASSWORD", ""),
            database=database or os.getenv("MYSQL_DB", ""),
        )
        self._pool: Optional[aiomysql.Pool] = None

    @property
    def name(self) -> str:
        return "mariadb-mcp"

    async def connect(self) -> None:
        """Create connection pool."""
        if aiomysql is None:
            raise ImportError("aiomysql not installed. Run: uv add aiomysql")

        logger.info(f"Connecting to MariaDB: {self.host}:{self.port}")
        self._pool = await aiomysql.create_pool(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            db=self.database or None,
            minsize=1,
            maxsize=5,
            autocommit=True,
        )
        logger.success("MariaDB connected")

    async def disconnect(self) -> None:
        """Close connection pool."""
        if self._pool:
            self._pool.close()
            await self._pool.wait_closed()
            logger.info("MariaDB disconnected")

    async def _execute_query(self, sql: str, database: Optional[str] = None) -> List[Dict[str, Any]]:
        """Execute a SELECT query."""
        async with self._pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                if database:
                    await cur.execute(f"USE {database}")
                await cur.execute(sql)
                rows = await cur.fetchall()
                return list(rows)

    async def _execute_statement(self, sql: str, database: Optional[str] = None) -> str:
        """Execute a non-SELECT statement."""
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cur:
                if database:
                    await cur.execute(f"USE {database}")
                await cur.execute(sql)
                return f"Executed: {cur.rowcount} rows affected"

    async def _get_databases(self) -> List[str]:
        """List all databases."""
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SHOW DATABASES")
                rows = await cur.fetchall()
                return [row[0] for row in rows]

    async def _get_tables(self, database: Optional[str] = None, schema: Optional[str] = None) -> List[Dict[str, Any]]:
        """List tables in a database."""
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cur:
                if database:
                    await cur.execute(f"USE {database}")
                await cur.execute("SHOW TABLES")
                rows = await cur.fetchall()
                return [{"name": row[0], "type": "TABLE"} for row in rows]

    async def _get_table_schema(self, table: str, database: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get table schema."""
        async with self._pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                if database:
                    await cur.execute(f"USE {database}")
                await cur.execute(f"DESCRIBE {table}")
                rows = await cur.fetchall()
                return [
                    {
                        "column": row["Field"],
                        "type": row["Type"],
                        "nullable": row["Null"],
                        "default": row["Default"],
                        "key": row["Key"],
                    }
                    for row in rows
                ]


# Entry point for running directly
if __name__ == "__main__":
    MariaDBMCP().start()
