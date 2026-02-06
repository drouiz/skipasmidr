# CrowdSec

Sistema de deteccion de intrusiones colaborativo.

## Descripcion

CrowdSec analiza logs, detecta comportamientos maliciosos y comparte
inteligencia con la comunidad.

## Variables de entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| CROWDSEC_VERSION | latest | Version |

## CLI

```bash
# Ver decisiones activas
docker exec crowdsec cscli decisions list

# Ver alertas
docker exec crowdsec cscli alerts list

# Añadir IP a whitelist
docker exec crowdsec cscli decisions add --ip 1.2.3.4 --type ban

# Instalar coleccion
docker exec crowdsec cscli collections install crowdsecurity/nginx
```

## Integracion con Traefik

1. Instalar bouncer de Traefik
2. Configurar middleware en Traefik
3. CrowdSec bloqueara IPs maliciosas

## Colecciones

- crowdsecurity/traefik
- crowdsecurity/nginx
- crowdsecurity/apache2
- crowdsecurity/linux
- crowdsecurity/http-cve

## Dashboard

Registrar en https://app.crowdsec.net para dashboard cloud.

## Documentacion

- https://docs.crowdsec.net/
