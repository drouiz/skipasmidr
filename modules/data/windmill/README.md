# Windmill

Plataforma de scripts y workflows.

## Descripcion

Windmill permite crear y ejecutar scripts, workflows y apps internas.
Soporta Python, TypeScript, Go, Bash y SQL.

## Acceso

- **URL**: http://windmill.127.0.0.1.traefik.me:9000

## Primera configuracion

1. Acceder a la URL
2. Crear cuenta de admin

## Dependencias

- PostgreSQL

## Variables de entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| WINDMILL_VERSION | latest | Version |
| WINDMILL_DB | windmill | Base de datos |

## Crear base de datos

```sql
CREATE DATABASE windmill;
```

## Lenguajes soportados

- Python 3
- TypeScript/JavaScript (Deno/Bun)
- Go
- Bash
- SQL
- GraphQL

## Caracteristicas

- Editor de codigo integrado
- Versionado de scripts
- Schedules (cron)
- Webhooks
- Flows (workflows visuales)
- Apps (UI low-code)
- Variables y secrets

## Ejemplo script

```python
# Script: hello_world
def main(name: str = "World"):
    return f"Hello, {name}!"
```

## Flows

Conectar scripts visualmente:
1. Create > Flow
2. Arrastrar scripts
3. Conectar inputs/outputs
4. Deploy

## Apps

Crear UIs internas:
1. Create > App
2. Arrastrar componentes
3. Conectar con scripts
4. Deploy

## Volumenes

- `windmill-data`: Cache de ejecuciones

## Documentacion

- https://www.windmill.dev/docs/
