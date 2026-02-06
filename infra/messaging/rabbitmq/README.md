# RabbitMQ

Broker de mensajes con interfaz de gestion.

## Descripcion

RabbitMQ es un broker de mensajes que implementa AMQP. Ideal para
comunicacion asincrona entre servicios.

## Acceso

- **Management UI**: http://rabbitmq.127.0.0.1.traefik.me:9000
- **AMQP**: localhost:5672 (si EXPOSE_RABBITMQ_PORT esta habilitado)

## Credenciales por defecto

```
RabbitMQ:
  - Usuario: admin
  - Password: admin123
```

## Variables de entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| RABBITMQ_VERSION | 3 | Version de RabbitMQ |
| RABBITMQ_USER | admin | Usuario |
| RABBITMQ_PASSWORD | admin123 | Password |
| EXPOSE_RABBITMQ_PORT | 127.0.0.1:5672 | Puerto AMQP |

## Conexion desde otros servicios

```yaml
environment:
  RABBITMQ_URL: amqp://admin:admin123@rabbitmq:5672/
```

## Casos de uso

- Colas de trabajo
- Pub/Sub
- RPC
- Tareas asincronas (Celery)
- Event-driven architecture

## Patrones comunes

### Work Queue
Distribuir tareas entre workers.

### Pub/Sub
Broadcast a multiples consumidores.

### Routing
Enviar a colas especificas segun routing key.

### Topics
Routing con patrones wildcards.

## Volumenes

- `rabbitmq-data`: Datos y configuracion

## Documentacion

- https://www.rabbitmq.com/documentation.html
