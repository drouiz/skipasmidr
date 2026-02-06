# Node Exporter

Exportador de metricas del sistema para Prometheus.

## Descripcion

Node Exporter expone metricas del host (CPU, memoria, disco, red) para
que Prometheus las recolecte.

## Acceso

- **Metrics**: http://node-exporter.127.0.0.1.traefik.me:9000/metrics

## Variables de entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| NODE_EXPORTER_VERSION | latest | Version |

## Metricas principales

| Metrica | Descripcion |
|---------|-------------|
| node_cpu_seconds_total | Uso de CPU |
| node_memory_MemTotal_bytes | Memoria total |
| node_memory_MemAvailable_bytes | Memoria disponible |
| node_filesystem_size_bytes | Tamaño de disco |
| node_filesystem_avail_bytes | Espacio disponible |
| node_network_receive_bytes_total | Bytes recibidos |
| node_network_transmit_bytes_total | Bytes enviados |
| node_load1 | Load average 1 min |

## Configurar en Prometheus

Ya incluido en la configuracion por defecto de Prometheus.

```yaml
scrape_configs:
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
```

## Dashboard en Grafana

Importar dashboard ID: **1860** (Node Exporter Full)

## PromQL ejemplos

```promql
# CPU usage %
100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Memory usage %
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# Disk usage %
(1 - (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"})) * 100
```

## Nota Windows

En Windows, Node Exporter no funciona directamente. Alternativas:
- windows_exporter: https://github.com/prometheus-community/windows_exporter
- Ejecutar en WSL2

## Documentacion

- https://prometheus.io/docs/guides/node-exporter/
