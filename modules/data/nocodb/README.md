# NocoDB

Alternativa open source a Airtable.

## Descripcion

NocoDB convierte cualquier base de datos en una spreadsheet inteligente.
Interfaz similar a Airtable con API REST automatica.

## Acceso

- **URL**: http://nocodb.127.0.0.1.traefik.me:9000

## Primera configuracion

1. Acceder a la URL
2. Crear cuenta de admin
3. Conectar base de datos o crear nueva

## Dependencias

- PostgreSQL (recomendado) o SQLite

## Variables de entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| NOCODB_VERSION | latest | Version |
| NOCODB_DB | nocodb | Base de datos |

## Crear base de datos

```sql
CREATE DATABASE nocodb;
```

## Caracteristicas

- Vistas: Grid, Gallery, Kanban, Form, Calendar
- Campos: Text, Number, Date, Attachment, Lookup, Formula
- Relaciones entre tablas
- API REST automatica
- Webhooks
- Colaboracion en tiempo real

## API REST

Cada tabla tiene endpoints automaticos:

```bash
# Listar registros
GET /api/v1/db/data/noco/{base}/{tabla}

# Crear registro
POST /api/v1/db/data/noco/{base}/{tabla}

# Actualizar
PATCH /api/v1/db/data/noco/{base}/{tabla}/{id}
```

## Conectar base de datos externa

1. Create Base > Connect to external database
2. Introducir conexion (PostgreSQL, MySQL, etc.)
3. NocoDB creara interfaz sobre tablas existentes

## Volumenes

- `nocodb-data`: Attachments, configuracion

## Documentacion

- https://docs.nocodb.com/
