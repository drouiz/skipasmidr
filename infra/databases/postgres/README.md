# PostgreSQL + pgAdmin

Base de datos relacional PostgreSQL con interfaz de administracion pgAdmin.

## Descripcion

PostgreSQL es la base de datos principal de la infraestructura. Es utilizada por
multiples servicios como Odoo, n8n, Keycloak, Airflow, etc.

## Acceso

- **pgAdmin URL**: http://pgadmin.127.0.0.1.traefik.me:9000
- **PostgreSQL**: localhost:5432 (si EXPOSE_POSTGRES_PORT esta habilitado)

## Credenciales por defecto

```
PostgreSQL:
  - Usuario: admin
  - Password: admin123
  - Database: postgres

pgAdmin:
  - Email: admin@admin.com
  - Password: admin123
```

## Crear base de datos para un servicio

Cada servicio crea su propia base de datos. Puedes crearlas manualmente:

```sql
CREATE DATABASE odoo;
CREATE DATABASE n8n;
CREATE DATABASE keycloak;
```

O desde pgAdmin en la UI.

## Variables de entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| POSTGRES_VERSION | 16 | Version de PostgreSQL |
| POSTGRES_USER | admin | Usuario administrador |
| POSTGRES_PASSWORD | admin123 | Password |
| POSTGRES_DB | postgres | Base de datos inicial |
| EXPOSE_POSTGRES_PORT | 127.0.0.1:5432 | Puerto expuesto |
| PGADMIN_EMAIL | admin@admin.com | Email de pgAdmin |
| PGADMIN_PASSWORD | admin123 | Password de pgAdmin |

## Conexion desde otros servicios

```yaml
environment:
  DATABASE_URL: postgresql://admin:admin123@postgres:5432/mi_db
```

## Volumenes

- `postgres-data`: Datos de PostgreSQL
- `pgadmin-data`: Configuracion de pgAdmin

## Backups

```bash
# Backup
docker exec postgres pg_dump -U admin mi_db > backup.sql

# Restore
docker exec -i postgres psql -U admin mi_db < backup.sql
```

## Documentacion

- https://www.postgresql.org/docs/
- https://www.pgadmin.org/docs/
