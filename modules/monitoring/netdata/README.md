# Netdata

Monitorizacion del sistema en tiempo real.

## Descripcion

Netdata es un monitor de sistema con dashboards en tiempo real. Recolecta
miles de metricas por segundo con muy bajo overhead.

## Acceso

- **URL**: http://netdata.127.0.0.1.traefik.me:9000

## Variables de entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| NETDATA_VERSION | latest | Version |

## Caracteristicas

- Metricas en tiempo real (1 segundo de granularidad)
- Auto-descubrimiento de servicios
- Alertas predefinidas
- Muy bajo uso de recursos
- Dashboard interactivo

## Metricas incluidas

- CPU, memoria, disco, red
- Procesos y aplicaciones
- Contenedores Docker
- Bases de datos (si estan accesibles)
- Web servers
- Y cientos mas...

## Collectors

Netdata detecta automaticamente:
- Docker containers
- MySQL/MariaDB
- PostgreSQL
- Redis
- MongoDB
- Nginx
- Apache
- Y muchos mas

## Alertas

Ver alertas activas en: `http://netdata...:9000/api/v1/alarms`

Configurar en `/etc/netdata/health.d/`

## Integracion con otros

Netdata puede enviar metricas a:
- Prometheus (endpoint /api/v1/allmetrics)
- Graphite
- InfluxDB
- Cloud (netdata.cloud)

## Volumenes

- `netdata-config`: Configuracion
- `netdata-lib`: Datos internos
- `netdata-cache`: Cache de metricas

## Documentacion

- https://learn.netdata.cloud/
