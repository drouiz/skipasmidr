# Dagster

Plataforma de orquestacion de datos.

## Descripcion

Dagster es un orquestador de datos moderno. Define pipelines como codigo
con un enfoque en assets y data lineage.

## Acceso

- **URL**: http://dagster.127.0.0.1.traefik.me:9000

## Dependencias

- PostgreSQL

## Variables de entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| DAGSTER_VERSION | latest | Version |
| DAGSTER_DB | dagster | Base de datos |

## Crear base de datos

```sql
CREATE DATABASE dagster;
```

## Configuracion

Editar `workspace.yaml` para cargar tu codigo:

```yaml
load_from:
  - python_file: /path/to/repository.py
  # o
  - python_module: my_module
```

## Ejemplo de asset

```python
from dagster import asset

@asset
def mi_asset():
    return {"data": [1, 2, 3]}

@asset
def asset_dependiente(mi_asset):
    return len(mi_asset["data"])
```

## Conceptos

- **Asset**: Unidad de dato producida por un pipeline
- **Op**: Operacion individual
- **Job**: Conjunto de ops
- **Schedule**: Ejecucion programada
- **Sensor**: Ejecucion basada en eventos

## Volumenes

- `dagster-data`: Dagster home, logs, storage

## Documentacion

- https://docs.dagster.io/
