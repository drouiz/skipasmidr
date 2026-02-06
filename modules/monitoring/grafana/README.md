# Grafana

Plataforma de visualizacion y dashboards.

## Descripcion

Grafana es la plataforma de observabilidad. Conecta con Prometheus, Loki, Tempo
y otras fuentes de datos para visualizar metricas, logs y trazas.

## Acceso

- **URL**: http://grafana.127.0.0.1.traefik.me:9000

## Credenciales por defecto

```
Grafana:
  - Usuario: admin
  - Password: admin123
```

## Variables de entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| GRAFANA_VERSION | latest | Version de Grafana |
| GRAFANA_USER | admin | Usuario admin |
| GRAFANA_PASSWORD | admin123 | Password |

## Data Sources recomendados

Configura estos data sources cuando esten activos:

| Tipo | URL | Descripcion |
|------|-----|-------------|
| Prometheus | http://prometheus:9090 | Metricas |
| Loki | http://loki:3100 | Logs |
| Tempo | http://tempo:3200 | Trazas |

## Dashboards recomendados

Importar desde Grafana.com:

| ID | Nombre | Descripcion |
|----|--------|-------------|
| 1860 | Node Exporter Full | Metricas de sistema |
| 13639 | Docker Containers | Metricas Docker |
| 12611 | Loki Dashboard | Logs con Loki |

## Provisioning

La carpeta `provisioning/` permite configurar automaticamente:
- `datasources/`: Data sources
- `dashboards/`: Dashboards
- `alerting/`: Reglas de alertas

## Volumenes

- `grafana-data`: Dashboards, usuarios, configuracion

## Documentacion

- https://grafana.com/docs/grafana/latest/
