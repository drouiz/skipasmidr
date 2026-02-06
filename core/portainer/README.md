# Portainer

Gestion visual de contenedores Docker.

## Descripcion

Portainer proporciona una interfaz web para gestionar contenedores Docker,
imagenes, volumenes, redes y mas.

## Acceso

- **URL**: http://portainer.127.0.0.1.traefik.me:9000

## Primera vez

1. Accede a la URL
2. Crea un usuario administrador
3. Selecciona "Docker" como entorno
4. Conecta al socket local

## Caracteristicas

- Gestion de contenedores (start, stop, logs, exec)
- Gestion de imagenes (pull, push, build)
- Gestion de volumenes y redes
- Stacks (docker-compose desde la UI)
- Templates de aplicaciones
- Control de acceso basado en roles

## Volumenes

- `portainer-data`: Configuracion y datos de Portainer

## Seguridad

En produccion, considera:
- Habilitar HTTPS
- Configurar autenticacion LDAP/OAuth
- Restringir acceso al socket Docker

## Documentacion

- https://docs.portainer.io/
