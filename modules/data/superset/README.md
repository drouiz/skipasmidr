# Apache Superset

Plataforma de exploracion y visualizacion de datos.

## Descripcion

Superset es una herramienta de BI moderna. Permite crear dashboards,
explorar datos y crear visualizaciones interactivas.

## Acceso

- **URL**: http://superset.127.0.0.1.traefik.me:9000

## Credenciales por defecto

```
Superset:
  - Usuario: admin
  - Password: admin123
```

## Dependencias

- PostgreSQL
- Redis (para cache/celery)

## Variables de entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| SUPERSET_VERSION | latest | Version |
| SUPERSET_DB | superset | Base de datos |
| SUPERSET_SECRET | random | Secret key |

## Crear base de datos

```sql
CREATE DATABASE superset;
```

## Conectar fuentes de datos

1. Settings > Database Connections
2. Add Database
3. Usar SQLAlchemy URI:

```
# PostgreSQL
postgresql://user:pass@postgres:5432/database

# MySQL
mysql://user:pass@mariadb:3306/database

# Otros
Ver documentacion de drivers
```

## Caracteristicas

- SQL Lab (editor SQL interactivo)
- Charts (40+ tipos de graficos)
- Dashboards
- Alertas y reportes
- Control de acceso granular

## Volumenes

- `superset-data`: Configuracion, metadatos

## Documentacion

- https://superset.apache.org/docs/
