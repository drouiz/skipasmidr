# Technitium DNS Server

Servidor DNS completo con interfaz web.

## Descripcion

Technitium es un servidor DNS autoritativo y recursivo con
bloqueo de anuncios, DNSSEC, DoH/DoT y mas.

## Acceso

- **Web UI**: http://dns.127.0.0.1.traefik.me:9000
- **DNS**: localhost:53

## Primera configuracion

1. Acceder a la URL
2. Crear password de admin
3. Configurar zonas DNS

## Caracteristicas

- DNS autoritativo y recursivo
- Bloqueo de anuncios (listas)
- DNSSEC
- DNS-over-HTTPS (DoH)
- DNS-over-TLS (DoT)
- Zonas personalizadas
- Logs y estadisticas
- API REST

## Casos de uso

- DNS interno para desarrollo
- Split-horizon DNS
- Bloqueo de ads a nivel DNS
- Resolucion de nombres locales

## Configurar como DNS local

Apuntar tu router o PC a: IP_HOST:53

## Crear zona local

1. Dashboard > Zones > Add Zone
2. Tipo: Primary Zone
3. Nombre: local.dev
4. Añadir registros A, CNAME, etc.

## Volumenes

- `technitium-data`: Configuracion, zonas, logs

## Documentacion

- https://technitium.com/dns/help.html
