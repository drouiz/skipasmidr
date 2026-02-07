"""
MongoDB MCP Server.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from loguru import logger

try:
    from motor.motor_asyncio import AsyncIOMotorClient
except ImportError:
    AsyncIOMotorClient = None

from libs.mcp.database.base import DatabaseMCP


class MongoMCP(DatabaseMCP):
    """
    MongoDB MCP server.

    Environment variables:
        MONGO_HOST: Database host (default: localhost)
        MONGO_PORT: Database port (default: 27017)
        MONGO_USER: Database user (optional)
        MONGO_PASSWORD: Database password (optional)
        MONGO_DB: Default database (default: admin)
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
            host=host or os.getenv("MONGO_HOST", "localhost"),
            port=port or int(os.getenv("MONGO_PORT", "27017")),
            user=user or os.getenv("MONGO_USER", ""),
            password=password or os.getenv("MONGO_PASSWORD", ""),
            database=database or os.getenv("MONGO_DB", "admin"),
        )
        self._client: Optional[AsyncIOMotorClient] = None
        self._register_mongo_tools()

    @property
    def name(self) -> str:
        return "mongo-mcp"

    def _register_mongo_tools(self) -> None:
        """Register MongoDB-specific tools."""
        self.register_tool(
            name="find",
            description="Find documents in a collection",
            handler=self._tool_find,
            properties={
                "collection": {"type": "string", "description": "Collection name"},
                "filter": {"type": "object", "description": "Query filter (optional)"},
                "limit": {"type": "integer", "description": "Max documents to return (default: 100)"},
                "database": {"type": "string", "description": "Database name (optional)"},
            },
            required=["collection"],
        )

        self.register_tool(
            name="insert",
            description="Insert documents into a collection",
            handler=self._tool_insert,
            properties={
                "collection": {"type": "string", "description": "Collection name"},
                "documents": {"type": "array", "description": "Documents to insert"},
                "database": {"type": "string", "description": "Database name (optional)"},
            },
            required=["collection", "documents"],
        )

        self.register_tool(
            name="list_collections",
            description="List collections in a database",
            handler=self._tool_list_collections,
            properties={
                "database": {"type": "string", "description": "Database name (optional)"},
            },
        )

    async def connect(self) -> None:
        """Create MongoDB client."""
        if AsyncIOMotorClient is None:
            raise ImportError("motor not installed. Run: uv add motor")

        # Build connection URI
        if self.user and self.password:
            uri = f"mongodb://{self.user}:{self.password}@{self.host}:{self.port}"
        else:
            uri = f"mongodb://{self.host}:{self.port}"

        logger.info(f"Connecting to MongoDB: {self.host}:{self.port}")
        self._client = AsyncIOMotorClient(uri)

        # Test connection
        await self._client.admin.command("ping")
        logger.success("MongoDB connected")

    async def disconnect(self) -> None:
        """Close MongoDB client."""
        if self._client:
            self._client.close()
            logger.info("MongoDB disconnected")

    def _get_db(self, database: Optional[str] = None):
        """Get database instance."""
        db_name = database or self.database
        return self._client[db_name]

    async def _tool_find(
        self,
        collection: str,
        filter: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        database: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Find documents in a collection."""
        db = self._get_db(database)
        cursor = db[collection].find(filter or {}).limit(limit)
        docs = await cursor.to_list(length=limit)
        # Convert ObjectId to string
        for doc in docs:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
        return docs

    async def _tool_insert(
        self,
        collection: str,
        documents: List[Dict[str, Any]],
        database: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Insert documents into a collection."""
        db = self._get_db(database)
        if len(documents) == 1:
            result = await db[collection].insert_one(documents[0])
            return {"inserted_id": str(result.inserted_id)}
        else:
            result = await db[collection].insert_many(documents)
            return {"inserted_ids": [str(id) for id in result.inserted_ids]}

    async def _tool_list_collections(self, database: Optional[str] = None) -> List[str]:
        """List collections in a database."""
        db = self._get_db(database)
        return await db.list_collection_names()

    # Implement abstract methods (adapted for MongoDB)
    async def _execute_query(self, sql: str, database: Optional[str] = None) -> List[Dict[str, Any]]:
        """MongoDB doesn't use SQL. Use find() instead."""
        raise NotImplementedError("Use 'find' tool for MongoDB queries")

    async def _execute_statement(self, sql: str, database: Optional[str] = None) -> str:
        """MongoDB doesn't use SQL. Use insert() instead."""
        raise NotImplementedError("Use specific MongoDB tools for operations")

    async def _get_databases(self) -> List[str]:
        """List all databases."""
        return await self._client.list_database_names()

    async def _get_tables(self, database: Optional[str] = None, schema: Optional[str] = None) -> List[Dict[str, Any]]:
        """List collections (tables) in a database."""
        collections = await self._tool_list_collections(database)
        return [{"name": c, "type": "COLLECTION"} for c in collections]

    async def _get_table_schema(self, table: str, database: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get collection schema by sampling documents."""
        db = self._get_db(database)
        # Sample one document to infer schema
        doc = await db[table].find_one()
        if not doc:
            return []
        return [
            {"field": key, "type": type(value).__name__}
            for key, value in doc.items()
        ]


# Entry point for running directly
if __name__ == "__main__":
    MongoMCP().start()
