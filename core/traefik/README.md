# Traefik

Proxy inverso y load balancer moderno para microservicios.

## Descripcion

Traefik es el punto de entrada de toda la infraestructura. Gestiona el routing automatico
de todos los servicios basandose en labels de Docker.

## Acceso

- **URL**: http://traefik.127.0.0.1.traefik.me:9000
- **Dashboard**: http://traefik.127.0.0.1.traefik.me:9000/dashboard/

## Puerto

Este servicio expone el puerto **9000** que es el punto de entrada para todos los servicios.

## Configuracion

Traefik detecta automaticamente los servicios Docker con labels:

```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.mi-servicio.rule=Host(`mi-servicio.127.0.0.1.traefik.me`)"
  - "traefik.http.services.mi-servicio.loadbalancer.server.port=8080"
```

## Caracteristicas

- Descubrimiento automatico de servicios Docker
- SSL/TLS automatico con Let's Encrypt
- Dashboard de monitorizacion
- Middlewares (auth, rate-limit, headers, etc.)
- Health checks automaticos

## Volumenes

- `traefik-certs`: Certificados SSL

## Red

Usa la red `infra-network` compartida por todos los servicios.

## Documentacion

- https://doc.traefik.io/traefik/
