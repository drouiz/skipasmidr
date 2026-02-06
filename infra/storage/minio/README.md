# MinIO

Almacenamiento de objetos compatible con S3.

## Descripcion

MinIO es un servidor de almacenamiento de objetos de alto rendimiento,
compatible con la API de Amazon S3.

## Acceso

- **Console UI**: http://minio.127.0.0.1.traefik.me:9000
- **S3 API**: http://s3.127.0.0.1.traefik.me:9000
- **API local**: localhost:9100 (si EXPOSE_MINIO_API esta habilitado)

## Credenciales por defecto

```
MinIO:
  - Usuario: admin
  - Password: admin123456  (minimo 8 caracteres)
```

## Variables de entorno

| Variable | Default | Descripcion |
|----------|---------|-------------|
| MINIO_VERSION | latest | Version de MinIO |
| MINIO_USER | admin | Usuario root |
| MINIO_PASSWORD | admin123456 | Password root |
| EXPOSE_MINIO_API | 127.0.0.1:9100 | Puerto S3 API |

## Conexion desde otros servicios

```yaml
environment:
  AWS_ACCESS_KEY_ID: admin
  AWS_SECRET_ACCESS_KEY: admin123456
  AWS_ENDPOINT_URL: http://minio:9000
  AWS_S3_ENDPOINT: http://minio:9000
```

## Casos de uso

- Almacenamiento de archivos
- Backups
- Data lakes
- Artifacts de CI/CD
- Media storage

## mc CLI

```bash
# Configurar alias
mc alias set local http://localhost:9100 admin admin123456

# Crear bucket
mc mb local/mi-bucket

# Subir archivo
mc cp archivo.txt local/mi-bucket/

# Listar
mc ls local/mi-bucket
```

## Python (boto3)

```python
import boto3

s3 = boto3.client('s3',
    endpoint_url='http://localhost:9100',
    aws_access_key_id='admin',
    aws_secret_access_key='admin123456'
)

# Crear bucket
s3.create_bucket(Bucket='mi-bucket')

# Subir archivo
s3.upload_file('archivo.txt', 'mi-bucket', 'archivo.txt')
```

## Volumenes

- `minio-data`: Datos almacenados

## Documentacion

- https://min.io/docs/minio/container/index.html
