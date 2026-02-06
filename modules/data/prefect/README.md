# Prefect

Plataforma de orquestacion de workflows.

## Descripcion

Prefect es un orquestador moderno para pipelines de datos. Define flows
en Python con minimo boilerplate.

## Acceso

- **URL**: http://prefect.127.0.0.1.traefik.me:9000

## Dependencias

- PostgreSQL

## Variables de entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| PREFECT_VERSION | 2-latest | Version |
| PREFECT_DB | prefect | Base de datos |

## Crear base de datos

```sql
CREATE DATABASE prefect;
```

## Ejemplo de flow

```python
from prefect import flow, task

@task
def extract():
    return [1, 2, 3]

@task
def transform(data):
    return [x * 2 for x in data]

@task
def load(data):
    print(f"Loaded: {data}")

@flow
def etl_flow():
    data = extract()
    transformed = transform(data)
    load(transformed)

if __name__ == "__main__":
    etl_flow()
```

## Configurar cliente

```bash
# Apuntar al servidor
prefect config set PREFECT_API_URL=http://prefect.127.0.0.1.traefik.me:9000/api
```

## Conceptos

- **Flow**: Contenedor de tareas
- **Task**: Unidad de trabajo
- **Deployment**: Flow listo para ejecutar
- **Work Pool**: Pool de workers
- **Agent**: Ejecuta deployments

## Volumenes

- `prefect-data`: Configuracion, logs

## Documentacion

- https://docs.prefect.io/
