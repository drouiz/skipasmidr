# Restic REST Server

Backend de backups Restic.

## Descripcion

Servidor REST para almacenar backups de Restic. Permite hacer backups
incrementales, encriptados y eficientes.

## Acceso

- **API**: http://restic.127.0.0.1.traefik.me:9000

## Uso con cliente Restic

```bash
# Instalar restic
# Windows: scoop install restic / choco install restic
# Linux: apt install restic

# Inicializar repositorio
restic -r rest:http://restic.127.0.0.1.traefik.me:9000/mi-backup init

# Hacer backup
restic -r rest:http://restic.127.0.0.1.traefik.me:9000/mi-backup backup /ruta/a/datos

# Listar snapshots
restic -r rest:http://restic.127.0.0.1.traefik.me:9000/mi-backup snapshots

# Restaurar
restic -r rest:http://restic.127.0.0.1.traefik.me:9000/mi-backup restore latest --target /ruta/destino
```

## Variables

```bash
export RESTIC_REPOSITORY=rest:http://restic.127.0.0.1.traefik.me:9000/mi-backup
export RESTIC_PASSWORD=mi-password
```

## Caracteristicas

- Backups incrementales
- Deduplicacion
- Encriptacion
- Compresion
- Multiples backends

## Volumenes

- `restic-data`: Repositorios de backup

## Documentacion

- https://restic.readthedocs.io/
