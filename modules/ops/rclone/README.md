# Rclone

Sincronizacion con servicios cloud.

## Descripcion

Rclone sincroniza archivos con 70+ servicios cloud: S3, Google Drive,
Dropbox, OneDrive, etc.

## Acceso

- **Web GUI**: http://rclone.127.0.0.1.traefik.me:9000

## Credenciales

```
Usuario: admin
Password: admin123
```

## Configurar remotes

Via CLI:
```bash
docker exec -it rclone rclone config
```

O via Web GUI.

## Remotes comunes

- Amazon S3
- Google Drive
- Dropbox
- OneDrive
- MinIO (local)
- SFTP

## Comandos

```bash
# Listar remotes
docker exec rclone rclone listremotes

# Sync
docker exec rclone rclone sync /data/local remote:bucket

# Copy
docker exec rclone rclone copy /data/local remote:bucket

# Mount (como disco)
docker exec rclone rclone mount remote:bucket /mnt/cloud
```

## Volumenes

- `rclone-config`: Configuracion de remotes
- `rclone-data`: Datos locales

## Documentacion

- https://rclone.org/docs/
