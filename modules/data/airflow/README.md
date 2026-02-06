# Apache Airflow

Plataforma de orquestacion de workflows.

## Descripcion

Airflow es el orquestador de workflows mas popular. Define DAGs
(Directed Acyclic Graphs) en Python.

## Acceso

- **URL**: http://airflow.127.0.0.1.traefik.me:9000

## Credenciales por defecto

```
Airflow:
  - Usuario: admin
  - Password: admin123
```

## Dependencias

- PostgreSQL

## Variables de entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| AIRFLOW_VERSION | 2.8.0 | Version |
| AIRFLOW_DB | airflow | Base de datos |
| AIRFLOW_USER | admin | Usuario |
| AIRFLOW_PASSWORD | admin123 | Password |

## Crear base de datos

```sql
CREATE DATABASE airflow;
```

## Crear DAGs

Crear archivos Python en la carpeta `dags/`:

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def hello():
    print("Hello Airflow!")

with DAG(
    dag_id="hello_dag",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False
) as dag:
    task = PythonOperator(
        task_id="hello_task",
        python_callable=hello
    )
```

## Conceptos

- **DAG**: Grafo de tareas
- **Operator**: Tipo de tarea (Python, Bash, SQL, etc.)
- **Task**: Instancia de un operator
- **XCom**: Comunicacion entre tasks
- **Connection**: Credenciales externas

## Operators comunes

- PythonOperator
- BashOperator
- PostgresOperator
- S3ToRedshiftOperator
- DockerOperator

## Volumenes

- `airflow-logs`: Logs de ejecucion
- `./dags`: DAGs (montado localmente)

## Documentacion

- https://airflow.apache.org/docs/
