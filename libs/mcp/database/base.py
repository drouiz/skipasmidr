"""
Base Database MCP Server.

Provides common functionality for database MCP servers.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any, Dict, List, Optional

from libs.mcp.base import BaseMCP


class DatabaseMCP(BaseMCP):
    """
    Base class for database MCP servers.

    Provides common database operations:
    - query: Execute SELECT queries
    - execute: Execute non-SELECT statements
    - list_databases: List all databases
    - list_tables: List tables in a database
    - describe_table: Get table schema

    Subclasses must implement:
    - name: Server name
    - connect(): Establish database connection
    - disconnect(): Close database connection
    - _execute_query(): Run a query and return results
    - _execute_statement(): Run a statement
    - _get_databases(): List databases
    - _get_tables(): List tables
    - _get_table_schema(): Get table structure
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        user: str = "admin",
        password: str = "",
        database: str = "",
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self._connection = None
        super().__init__()

    async def setup(self) -> None:
        """Initialize connection and register tools."""
        await self.connect()
        self._register_database_tools()

    async def cleanup(self) -> None:
        """Close database connection."""
        await self.disconnect()

    def _register_database_tools(self) -> None:
        """Register common database tools."""
        self.register_tool(
            name="query",
            description="Execute a SELECT query and return results as JSON",
            handler=self._tool_query,
            properties={
                "sql": {"type": "string", "description": "SQL SELECT query"},
                "database": {"type": "string", "description": "Database name (optional)"},
            },
            required=["sql"],
        )

        self.register_tool(
            name="execute",
            description="Execute a non-SELECT SQL statement (INSERT, UPDATE, DELETE, CREATE, etc.)",
            handler=self._tool_execute,
            properties={
                "sql": {"type": "string", "description": "SQL statement"},
                "database": {"type": "string", "description": "Database name (optional)"},
            },
            required=["sql"],
        )

        self.register_tool(
            name="list_databases",
            description="List all databases",
            handler=self._tool_list_databases,
            properties={},
        )

        self.register_tool(
            name="list_tables",
            description="List all tables in a database",
            handler=self._tool_list_tables,
            properties={
                "database": {"type": "string", "description": "Database name (optional)"},
                "schema": {"type": "string", "description": "Schema name (optional)"},
            },
        )

        self.register_tool(
            name="describe_table",
            description="Get table schema/structure",
            handler=self._tool_describe_table,
            properties={
                "table": {"type": "string", "description": "Table name"},
                "database": {"type": "string", "description": "Database name (optional)"},
            },
            required=["table"],
        )

    async def _tool_query(self, sql: str, database: Optional[str] = None) -> Any:
        """Execute a SELECT query."""
        sql_upper = sql.strip().upper()
        if not sql_upper.startswith("SELECT") and not sql_upper.startswith("WITH"):
            raise ValueError("Only SELECT queries allowed. Use 'execute' for other statements.")
        return await self._execute_query(sql, database)

    async def _tool_execute(self, sql: str, database: Optional[str] = None) -> Any:
        """Execute a non-SELECT statement."""
        return await self._execute_statement(sql, database)

    async def _tool_list_databases(self) -> Any:
        """List all databases."""
        return await self._get_databases()

    async def _tool_list_tables(self, database: Optional[str] = None, schema: Optional[str] = None) -> Any:
        """List tables in a database."""
        return await self._get_tables(database, schema)

    async def _tool_describe_table(self, table: str, database: Optional[str] = None) -> Any:
        """Get table schema."""
        return await self._get_table_schema(table, database)

    # Abstract methods to implement in subclasses
    @abstractmethod
    async def connect(self) -> None:
        """Establish database connection."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close database connection."""
        pass

    @abstractmethod
    async def _execute_query(self, sql: str, database: Optional[str] = None) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results."""
        pass

    @abstractmethod
    async def _execute_statement(self, sql: str, database: Optional[str] = None) -> str:
        """Execute a non-SELECT statement and return status."""
        pass

    @abstractmethod
    async def _get_databases(self) -> List[str]:
        """List all databases."""
        pass

    @abstractmethod
    async def _get_tables(self, database: Optional[str] = None, schema: Optional[str] = None) -> List[Dict[str, Any]]:
        """List tables in a database."""
        pass

    @abstractmethod
    async def _get_table_schema(self, table: str, database: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get table schema."""
        pass
