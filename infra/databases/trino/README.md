# Trino (antes Presto)

Motor de consultas SQL distribuido.

## Descripcion

Trino es un motor de consultas SQL distribuido disenado para
consultar grandes datasets distribuidos en una o mas fuentes
de datos heterogeneas.

## Acceso

- **Web UI**: http://trino.127.0.0.1.traefik.me:9000

## Caracteristicas

- Consultas SQL sobre multiples fuentes de datos
- Soporta: PostgreSQL, MySQL, MongoDB, S3, HDFS, etc.
- Alto rendimiento para analytics
- Federacion de datos

## Uso

```bash
# Cliente CLI
docker exec -it trino trino

# Query
trino> SHOW CATALOGS;
trino> SELECT * FROM system.runtime.nodes;
```

## Conectores comunes

- PostgreSQL
- MySQL
- MongoDB
- Elasticsearch
- S3 / MinIO
- Kafka

## Documentacion

- https://trino.io/docs/current/
