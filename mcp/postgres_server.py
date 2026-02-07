#!/usr/bin/env python3
"""
PostgreSQL MCP Server
Exposes PostgreSQL database capabilities to Claude via MCP.

Usage:
  python postgres_server.py

Environment variables:
  POSTGRES_HOST - Database host (default: localhost)
  POSTGRES_PORT - Database port (default: 5432)
  POSTGRES_USER - Database user (default: admin)
  POSTGRES_PASSWORD - Database password (default: admin123)
  POSTGRES_DB - Default database (default: postgres)
"""

import os
import json
import asyncio
import subprocess
import sys
from typing import Any

from loguru import logger

try:
    import asyncpg
except ImportError:
    logger.error("asyncpg not installed. Run: uv add asyncpg")
    sys.exit(1)

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    logger.error("MCP package not installed. Run: uv add mcp")
    sys.exit(1)


# Configuration from environment
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_USER = os.getenv("POSTGRES_USER", "admin")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "admin123")
POSTGRES_DB = os.getenv("POSTGRES_DB", "postgres")

# Create MCP server
server = Server("postgres-infra")

# Connection pool
pool = None


async def get_pool():
    global pool
    if pool is None:
        pool = await asyncpg.create_pool(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            database=POSTGRES_DB,
            min_size=1,
            max_size=5
        )
    return pool


@server.list_tools()
async def list_tools():
    """List available tools."""
    return [
        Tool(
            name="query",
            description="Execute a SELECT query on PostgreSQL. Returns results as JSON.",
            inputSchema={
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "SQL SELECT query to execute"
                    },
                    "database": {
                        "type": "string",
                        "description": "Database name (optional, uses default if not specified)"
                    }
                },
                "required": ["sql"]
            }
        ),
        Tool(
            name="list_databases",
            description="List all databases in PostgreSQL",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="list_tables",
            description="List all tables in a database",
            inputSchema={
                "type": "object",
                "properties": {
                    "database": {
                        "type": "string",
                        "description": "Database name (optional)"
                    },
                    "schema": {
                        "type": "string",
                        "description": "Schema name (default: public)"
                    }
                }
            }
        ),
        Tool(
            name="describe_table",
            description="Get table schema/structure",
            inputSchema={
                "type": "object",
                "properties": {
                    "table": {
                        "type": "string",
                        "description": "Table name"
                    },
                    "database": {
                        "type": "string",
                        "description": "Database name (optional)"
                    }
                },
                "required": ["table"]
            }
        ),
        Tool(
            name="execute",
            description="Execute a non-SELECT SQL statement (INSERT, UPDATE, DELETE, CREATE, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "SQL statement to execute"
                    },
                    "database": {
                        "type": "string",
                        "description": "Database name (optional)"
                    }
                },
                "required": ["sql"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute a tool."""
    try:
        p = await get_pool()

        if name == "query":
            sql = arguments.get("sql", "")
            if not sql.strip().upper().startswith("SELECT"):
                return [TextContent(type="text", text="Error: Only SELECT queries allowed. Use 'execute' for other statements.")]

            async with p.acquire() as conn:
                rows = await conn.fetch(sql)
                result = [dict(row) for row in rows]
                return [TextContent(type="text", text=json.dumps(result, default=str, indent=2))]

        elif name == "list_databases":
            async with p.acquire() as conn:
                rows = await conn.fetch("SELECT datname FROM pg_database WHERE datistemplate = false ORDER BY datname")
                databases = [row["datname"] for row in rows]
                return [TextContent(type="text", text=json.dumps(databases, indent=2))]

        elif name == "list_tables":
            schema = arguments.get("schema", "public")
            async with p.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT table_name, table_type
                    FROM information_schema.tables
                    WHERE table_schema = $1
                    ORDER BY table_name
                """, schema)
                tables = [{"name": row["table_name"], "type": row["table_type"]} for row in rows]
                return [TextContent(type="text", text=json.dumps(tables, indent=2))]

        elif name == "describe_table":
            table = arguments.get("table", "")
            async with p.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_name = $1
                    ORDER BY ordinal_position
                """, table)
                columns = [
                    {
                        "column": row["column_name"],
                        "type": row["data_type"],
                        "nullable": row["is_nullable"],
                        "default": row["column_default"]
                    }
                    for row in rows
                ]
                return [TextContent(type="text", text=json.dumps(columns, indent=2))]

        elif name == "execute":
            sql = arguments.get("sql", "")
            async with p.acquire() as conn:
                result = await conn.execute(sql)
                return [TextContent(type="text", text=f"Executed successfully: {result}")]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
