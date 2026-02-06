# AdGuard Home

Servidor DNS con bloqueo de anuncios y tracking.

## Descripcion

AdGuard Home es un servidor DNS que bloquea anuncios, trackers y malware
a nivel de red.

## Acceso

- **URL**: http://adguard.127.0.0.1.traefik.me:9000

## Primera configuracion

1. Acceder a la URL
2. Completar wizard de configuracion
3. Configurar DNS en tu red

## Variables de entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| ADGUARD_VERSION | latest | Version |

## Usar como DNS

Configurar tu router o dispositivos para usar:
- DNS: IP_DEL_HOST:53

## Listas de bloqueo recomendadas

- AdGuard DNS filter
- EasyList
- EasyPrivacy
- Steven Black's hosts

## Caracteristicas

- Bloqueo de anuncios
- Bloqueo de trackers
- Proteccion contra phishing
- Control parental
- DNS-over-HTTPS/TLS
- Estadisticas de consultas

## Volumenes

- `adguard-work`: Base de datos, estadisticas
- `adguard-conf`: Configuracion

## Documentacion

- https://github.com/AdguardTeam/AdGuardHome/wiki
