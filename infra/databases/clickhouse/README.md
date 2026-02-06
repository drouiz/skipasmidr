# ClickHouse

Base de datos columnar de alto rendimiento para analytics.

## Descripcion

ClickHouse es una base de datos OLAP columnar de codigo abierto,
optimizada para consultas analiticas en tiempo real sobre grandes
volumenes de datos.

## Acceso

- **HTTP Interface**: http://clickhouse.127.0.0.1.traefik.me:9000
- **Usuario**: admin
- **Password**: admin123

## Uso

```bash
# Query via HTTP
curl "http://clickhouse.127.0.0.1.traefik.me:9000/?query=SELECT+1"

# Con autenticacion
curl "http://clickhouse.127.0.0.1.traefik.me:9000/?user=admin&password=admin123&query=SHOW+DATABASES"
```

## Casos de uso

- Analytics en tiempo real
- Log analysis
- Time series data
- Business intelligence
- Data warehousing

## Documentacion

- https://clickhouse.com/docs
