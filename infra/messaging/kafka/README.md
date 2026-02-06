# Kafka + Kafka UI

Plataforma de streaming distribuido con interfaz web.

## Descripcion

Apache Kafka es una plataforma de streaming de eventos distribuida.
Usa KRaft (sin Zookeeper) para simplicidad.

## Acceso

- **Kafka UI**: http://kafka.127.0.0.1.traefik.me:9000
- **Kafka**: localhost:9094 (si EXPOSE_KAFKA_PORT esta habilitado)

## Variables de entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| KAFKA_VERSION | 3.6 | Version de Kafka |
| EXPOSE_KAFKA_PORT | 127.0.0.1:9094 | Puerto externo |

## Conexion desde otros servicios

```yaml
environment:
  KAFKA_BOOTSTRAP_SERVERS: kafka:9092
```

## Desde fuera de Docker

```yaml
environment:
  KAFKA_BOOTSTRAP_SERVERS: localhost:9094
```

## Casos de uso

- Event streaming
- Log aggregation
- Stream processing
- Event sourcing
- CDC (Change Data Capture)

## Conceptos clave

- **Topic**: Canal de mensajes
- **Partition**: Division de un topic para paralelismo
- **Consumer Group**: Grupo de consumidores que comparten trabajo
- **Offset**: Posicion en una particion

## Comandos utiles

```bash
# Crear topic
docker exec kafka kafka-topics.sh --create --topic mi-topic --bootstrap-server localhost:9092

# Listar topics
docker exec kafka kafka-topics.sh --list --bootstrap-server localhost:9092

# Producir mensajes
docker exec -it kafka kafka-console-producer.sh --topic mi-topic --bootstrap-server localhost:9092

# Consumir mensajes
docker exec kafka kafka-console-consumer.sh --topic mi-topic --from-beginning --bootstrap-server localhost:9092
```

## Volumenes

- `kafka-data`: Datos de Kafka

## Documentacion

- https://kafka.apache.org/documentation/
- https://github.com/provectus/kafka-ui
