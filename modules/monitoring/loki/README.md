# Loki

Sistema de agregacion de logs.

## Descripcion

Loki es un sistema de logs inspirado en Prometheus. Indexa solo metadatos
(labels) para eficiencia. Se visualiza en Grafana.

## Acceso

- **API**: http://loki.127.0.0.1.traefik.me:9000

## Variables de entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| LOKI_VERSION | latest | Version |

## Arquitectura

```
Aplicaciones → Promtail → Loki → Grafana
```

## Enviar logs

### Con Promtail (recomendado)
Usa el modulo promtail para recoger logs de Docker.

### Directo via API
```bash
curl -X POST http://loki:3100/loki/api/v1/push \
  -H "Content-Type: application/json" \
  -d '{
    "streams": [{
      "stream": {"job": "test"},
      "values": [["'$(date +%s)000000000'", "log message"]]
    }]
  }'
```

### Python
```python
import logging
import logging_loki

handler = logging_loki.LokiHandler(
    url="http://loki:3100/loki/api/v1/push",
    tags={"application": "mi-app"},
)
logger = logging.getLogger()
logger.addHandler(handler)
```

## LogQL basico

En Grafana, seleccionar Loki como data source:

```logql
# Todos los logs de un job
{job="mi-app"}

# Filtrar por texto
{job="mi-app"} |= "error"

# Regex
{job="mi-app"} |~ "error|warn"

# Parsear JSON
{job="mi-app"} | json | level="error"
```

## Volumenes

- `loki-data`: Logs almacenados

## Documentacion

- https://grafana.com/docs/loki/latest/
