# Prometheus

Sistema de monitorizacion y alertas.

## Descripcion

Prometheus recolecta metricas de targets configurados mediante scraping.
Es el backend de metricas para Grafana.

## Acceso

- **URL**: http://prometheus.127.0.0.1.traefik.me:9000

## Variables de entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| PROMETHEUS_VERSION | latest | Version |

## Configuracion

Editar `prometheus.yml` para añadir targets:

```yaml
scrape_configs:
  - job_name: 'mi-app'
    static_configs:
      - targets: ['mi-app:8080']
```

Recargar configuracion:
```bash
curl -X POST http://prometheus.127.0.0.1.traefik.me:9000/-/reload
```

## Targets por defecto

- prometheus (self-monitoring)
- node-exporter (metricas de sistema)

## PromQL basico

```promql
# CPU usage
100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Memory usage
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# Disk usage
(1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100
```

## Instrumentar aplicacion

### Python
```python
from prometheus_client import Counter, start_http_server

REQUEST_COUNT = Counter('requests_total', 'Total requests')

@app.route('/')
def hello():
    REQUEST_COUNT.inc()
    return 'Hello'

start_http_server(8000)  # /metrics endpoint
```

## Volumenes

- `prometheus-data`: Time series data

## Documentacion

- https://prometheus.io/docs/
