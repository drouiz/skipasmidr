# Redis + Redis Commander

Base de datos en memoria key-value con interfaz de administracion.

## Descripcion

Redis es un almacen de estructuras de datos en memoria. Se usa como cache,
broker de mensajes, y base de datos.

## Acceso

- **Redis Commander URL**: http://redis.127.0.0.1.traefik.me:9000
- **Redis**: localhost:6379 (si EXPOSE_REDIS_PORT esta habilitado)

## Credenciales por defecto

```
Redis:
  - Password: admin123
```

## Variables de entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| REDIS_VERSION | 7 | Version de Redis |
| REDIS_PASSWORD | admin123 | Password |
| EXPOSE_REDIS_PORT | 127.0.0.1:6379 | Puerto expuesto |

## Conexion desde otros servicios

```yaml
environment:
  REDIS_URL: redis://:admin123@redis:6379/0
```

## Casos de uso

- **Cache**: Almacenar datos frecuentemente accedidos
- **Sesiones**: Almacenar sesiones de usuario
- **Colas**: Broker para tareas asincronas (Celery, Bull)
- **Pub/Sub**: Mensajeria en tiempo real
- **Rate limiting**: Control de peticiones

## Volumenes

- `redis-data`: Datos persistentes de Redis

## Comandos utiles

```bash
# Conectar al CLI
docker exec -it redis redis-cli -a admin123

# Comandos basicos
SET key "value"
GET key
KEYS *
FLUSHALL  # Borrar todo (cuidado!)
```

## Documentacion

- https://redis.io/docs/
- https://github.com/joeferner/redis-commander
