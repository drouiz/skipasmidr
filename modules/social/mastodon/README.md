# Mastodon

Red social federada del Fediverse.

## Descripcion

Mastodon es una red social descentralizada compatible con ActivityPub.

## Acceso

- **URL**: http://mastodon.127.0.0.1.traefik.me:9000

## Dependencias

- PostgreSQL
- Redis
- Elasticsearch (opcional, para busqueda)

## Variables de entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| MASTODON_VERSION | latest | Version |
| MASTODON_DB | mastodon | Base de datos |

## Crear base de datos

```sql
CREATE DATABASE mastodon;
```

## Configuracion inicial

1. Ejecutar setup:
```bash
docker exec -it mastodon rails db:setup
docker exec -it mastodon rails db:migrate
```

2. Crear usuario admin:
```bash
docker exec -it mastodon tootctl accounts create admin --email admin@example.com --confirmed --role Admin
```

## Nota

Esta es una configuracion simplificada para desarrollo.
Para produccion, usar la guia oficial completa.

## Documentacion

- https://docs.joinmastodon.org/
