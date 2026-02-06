# n8n

Plataforma de automatizacion de workflows.

## Descripcion

n8n es una herramienta de automatizacion extensible. Conecta APIs, bases de datos
y servicios con una interfaz visual.

## Acceso

- **URL**: http://n8n.127.0.0.1.traefik.me:9000

## Credenciales por defecto

```
n8n:
  - Usuario: admin
  - Password: admin123
```

## Dependencias

- PostgreSQL (para persistencia)

## Variables de entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| N8N_VERSION | latest | Version |
| N8N_USER | admin | Usuario |
| N8N_PASSWORD | admin123 | Password |
| N8N_DB | n8n | Base de datos |

## Crear base de datos

Si PostgreSQL ya esta corriendo:

```sql
CREATE DATABASE n8n;
```

## Caracteristicas

- 350+ integraciones nativas
- Webhooks
- Ejecucion programada (cron)
- Logica condicional
- Loops y branches
- Codigo JavaScript/Python custom
- API REST

## Casos de uso

- Sincronizacion de datos entre sistemas
- Automatizacion de marketing
- Alertas y notificaciones
- ETL ligero
- Integracion con LLMs

## Webhooks

Crear webhook en n8n y usar:
```
http://n8n.127.0.0.1.traefik.me:9000/webhook/mi-webhook
```

## Community nodes

Instalar nodes adicionales via UI o:
```bash
docker exec -it n8n npm install n8n-nodes-nombre
```

## Volumenes

- `n8n-data`: Workflows, credenciales, configuracion

## Documentacion

- https://docs.n8n.io/
