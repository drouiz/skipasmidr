# MCP Servers for Docker Infrastructure

MCP (Model Context Protocol) servers that allow Claude to interact with your infrastructure.

## Architecture

```
libs/mcp/
├── base.py              # BaseMCP - core functionality
├── builder.py           # MCPBuilder - create from YAML
├── database/
│   ├── base.py          # DatabaseMCP
│   ├── postgres.py      # PostgresMCP
│   ├── mariadb.py       # MariaDBMCP
│   └── mongo.py         # MongoMCP
├── container/
│   ├── base.py          # ContainerMCP
│   └── docker.py        # DockerMCP
└── http/
    ├── base.py          # HttpMCP
    └── traefik.py       # TraefikMCP
```

## Available MCP Servers

| Location | Type | Description |
|----------|------|-------------|
| `core/portainer/mcp.py` | Docker | Container management |
| `core/traefik/mcp.py` | Traefik | Reverse proxy management |
| `infra/databases/postgres/mcp.py` | PostgreSQL | Database queries |
| `infra/databases/mariadb/mcp.py` | MariaDB | Database queries |
| `infra/databases/mongo/mcp.py` | MongoDB | Document queries |

## Setup

### 1. Install Dependencies

```bash
uv sync --group mcp
```

### 2. Configuration

Edit `config/mcp/mcp.yaml` to enable/disable MCPs:

```yaml
enabled: true

core:
  docker:
    enabled: true
  traefik:
    enabled: true

databases:
  postgres:
    enabled: true
  mariadb:
    enabled: true
```

Individual MCP configs are in `config/mcp/<service>.mcp.yaml`.

### 3. Run MCP Servers

```bash
# Run directly
uv run python core/portainer/mcp.py
uv run python infra/databases/postgres/mcp.py

# Or use the builder
uv run python -c "from libs.mcp import MCPBuilder; MCPBuilder.create('docker').start()"
```

### 4. Configure Claude Desktop

Add to your Claude Desktop config:

```json
{
  "mcpServers": {
    "infra-docker": {
      "command": "uv",
      "args": ["run", "python", "path/to/core/portainer/mcp.py"]
    },
    "infra-postgres": {
      "command": "uv",
      "args": ["run", "python", "path/to/infra/databases/postgres/mcp.py"],
      "env": {
        "POSTGRES_HOST": "localhost",
        "POSTGRES_PORT": "5432",
        "POSTGRES_USER": "admin",
        "POSTGRES_PASSWORD": "admin123"
      }
    }
  }
}
```

## Usage Examples

Once configured, ask Claude:

- "List all running containers"
- "Show me the logs for n8n-infra"
- "What tables exist in the n8n database?"
- "Query the users table in PostgreSQL"
- "What's the memory usage of my containers?"
- "Show me all Traefik routers"

## Creating Custom MCP Servers

### Using Classes

```python
from libs.mcp.base import BaseMCP

class MyServiceMCP(BaseMCP):
    @property
    def name(self) -> str:
        return "my-service-mcp"

    async def setup(self):
        self.register_tool(
            name="my_action",
            description="Does something",
            handler=self._my_action,
            properties={"param": {"type": "string"}},
            required=["param"],
        )

    async def _my_action(self, param: str):
        return f"Did something with {param}"

if __name__ == "__main__":
    MyServiceMCP().start()
```

### Using YAML + Builder

Create `config/mcp/myservice.mcp.yaml`:

```yaml
type: postgres  # or any registered type
config:
  host: ${MY_HOST}
  port: 5432
```

Then run:

```python
from libs.mcp import MCPBuilder
MCPBuilder.from_yaml("config/mcp/myservice.mcp.yaml").start()
```

## Security Notes

- MCP servers have access to your infrastructure
- Only enable MCP servers you trust
- Be careful with write operations in production
- Use read-only credentials when possible
- Database MCPs restrict SELECT queries by default
