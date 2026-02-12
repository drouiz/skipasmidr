# Appsmith

Framework open source para apps internas.

## Descripcion

Appsmith es una plataforma para construir dashboards,
admin panels y aplicaciones internas.

## Acceso

- **URL**: http://appsmith.127.0.0.1.traefik.me:9000

## Primera configuracion

1. Acceder a la URL
2. Crear cuenta de admin

## Variables de entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| APPSMITH_VERSION | latest | Version |

## Caracteristicas

- Editor drag-and-drop
- 45+ widgets
- Conexion a APIs y DBs
- JavaScript en todas partes
- Git sync
- RBAC

## Data Sources

- PostgreSQL, MySQL, MongoDB
- REST API, GraphQL
- Google Sheets
- Firestore
- S3, Airtable
- Y mas...

## Widgets

- Table, List, Chart
- Form, Input, Select
- Button, Modal, Tabs
- Container, Image
- Y 40+ mas...

## JavaScript

```javascript
// Acceder a datos
{{ Table1.selectedRow.id }}

// Llamar API
{{ Api1.run() }}

// Logica condicional
{{ Input1.text.length > 0 ? "Valid" : "Invalid" }}
```

## Volumenes

- `appsmith-data`: Apps, configuracion

## Documentacion

- https://docs.appsmith.com/
